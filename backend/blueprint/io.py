

from flask import Blueprint, current_app, request, jsonify, make_response
from flask_login import login_required, current_user

import os
import math
import hashlib
import json
from datetime import datetime

from blueprint.file import get_current_path

from util.api_code import CodeResponse, CodeResponseError
from util.crypto import random_aes_key, random_string, aes_encrypt, aes_decrypt

from util.FileThread import FilePush, hdfs_delete, fix_path_join
from model.File import File, Folder
from model.IOTask import UploadTask



MAX_CHUNK_SIZE = current_app.config['MAX_CHUNK_SIZE']
BANNED_CHARSET=current_app.config['BANNED_CHARSET'].strip()

io = Blueprint("io", __name__, url_prefix='/api/io')

# meta = {
#   "name":   filename,
#   "folder": folder id,
#   "size":   file size in B
#   "aes":    None or True
# }
@login_required
@io.route('/upload/start', methods=['POST', ])
def upload_start_meta():
    try:
        meta = request.get_json()
        
        folder = Folder.objects.get(id=meta["folder"])
        if folder.owner != current_user.obj:
            raise CodeResponseError(403.10002, 'Permission denied. This is not your folder')
        
        if len(set(meta["name"]) & set(BANNED_CHARSET)) > 0:
            raise CodeResponseError(400.10004, "Illegal name, you cannot use \"" + BANNED_CHARSET + "\"")
        try:
            file = File.objects.get(parent_folder = folder, name="name").first()
            raise CodeResponseError(400.10004, "The file with same name has exist.")
        except File.DoesNotExist:
            pass

        task = UploadTask(
            owner=current_user.obj,
            folder=folder,
            meta_created=datetime.now(),
            meta_size=meta['size'],
            meta_name=meta['name'],
        )
        if 'aes' in meta.keys() and meta['aes'] == True:
            task.aes_key = random_aes_key()
            task.aes_shake_hand = False
            task.aes_shake_raw = random_string(64)
            task.aes_shake_crypto = aes_encrypt(task.aes_key, task.aes_shake_raw.encode(), 0)
        
        task.meta_chunks = math.ceil(task.meta_size / MAX_CHUNK_SIZE)
        task.upload_chunks = [False for i in range(task.meta_chunks)]
        task.save()

        os.makedirs("./cache/" + str(task.id), exist_ok=True)
        return jsonify({
            "code": 200,
            "chunk_size": MAX_CHUNK_SIZE,
            "detial": task.get_detial()
        })
    except KeyError:
        raise CodeResponseError(403.20001, 'Args loss. Need name,folder,size at least.')
    except Folder.DoesNotExist:
        raise CodeResponseError(403.10001, 'Current folder not exist.') 

    
@login_required
@io.route('/aes_shakehand', methods=['POST', ])
def aes_shakehand():
    pass

# meta = {
#   "task_id": task id,
#   "meta":{
#        "id":   chunk id, begin at 0.
#        "size": real size in chunk.
#        "md5":  md5 of raw data.
#   }
#   "file": bytes.
# }
@login_required
@io.route('/upload/chunk', methods=['POST',])
def upload_chunk():
    try:
        task_id = request.form.get('task_id')
        chunk_id = int(request.form.get('chunk', 0))
        data = request.files['file'].read()
        print(task_id, chunk_id, len(data))

        task = UploadTask.objects.get(id=task_id)
        if not task.aes_key is None and not task.aes_shake_hand:
            raise CodeResponseError(403.20004, "Aes key need validation.")

        if not task.aes_key is None:
            data = aes_decrypt(task.aes_key, data, chunk_id)

        # md5 = hashlib.md5(data).hexdigest()
        # print(md5)
        # if md5 != meta['md5']:
        #     raise CodeResponseError(406.20005, "Chunk md5 wrong.")
        
        with open(os.path.join("./cache/", str(task.id), "block_" + str(chunk_id)), 'wb+') as f:
            f.write(data)
        
        task.upload_chunks[chunk_id] = True
        task.save()

        return jsonify({
            "code": 200,
            "msg": "ok",
            "detial": task.get_detial()
        })
    except UploadTask.DoesNotExist:
        raise CodeResponseError(403.10002, 'Task dose not exist.')

# Args:
#   "task_id": task id,
#   "md5":     md5 of total file.

@login_required
@io.route('/upload/merge', methods=['GET',])
def upload_merge():
    try:
        task_id = request.args.get("task_id")
        md5 = request.args.get("md5")

        task = UploadTask.objects.get(id=task_id)
        if False in task.upload_chunks:
            raise CodeResponseError(406.20006, "Lost some chunk!")

        if not task.merge_doing:
            if task.meta_size >= 16 * 1024 * 1024:
                task.system = "hdfs" 
            else:
                task.system = "hdfs" # All to hdfs ,may be hbase later
            task.merge_doing = True
            task.meta_md5 = md5
            task.save()
            current_app.thread_map[str(task.id)] = FilePush(task)
            current_app.thread_map[str(task.id)].start()
        
        status = {
            "done": task.merge_done,
            "success": task.merge_success,
            "merged": task.merge_count,
            "total": task.meta_chunks
        }
        print(status)
        if task.merge_done and task.merge_success:
            try:
                cachepath = './cache/' + str(task.id)
                for f in os.listdir(cachepath):
                    os.remove(os.path.join(cachepath, f))
                os.rmdir(cachepath)
            except BaseException:
                pass
            info = task.file.fetch().get_info()
            md5check = task.meta_md5 == task.file.fetch().md5
            task.delete()
            return jsonify({
                "code": 200,
                "msg": "success",
                "status": status,
                "file": info,
                "md5check": md5check,
            })
        else:
            return jsonify({
                "code": 200,
                "status": {
                    "done": task.merge_done,
                    "success": task.merge_success,
                    "merged": task.merge_count,
                    "total": task.meta_chunks
                },
            })

    except KeyError:
        raise CodeResponseError(403.20001, 'Args loss. Need name,folder,size at least.')
    except UploadTask.DoesNotExist:
        raise CodeResponseError(403.10001, 'Task not exist.') 


@login_required
@io.route('/upload/cancel_upload', methods=['GET',])
def upload_release():
    try:
        task_id = request.args.get("task_id")
        task = UploadTask.objects.get(id=task_id)

        try:
            cachepath = './cache/' + str(task.id)
            for f in os.listdir(cachepath):
                os.remove(os.path.join(cachepath, f))
            os.rmdir(cachepath)
        except BaseException:
            pass
            
        task.delete()
    
    except KeyError:
        raise CodeResponseError(403.20001, 'Args loss. Need name,folder,size at least.')
    except Folder.DoesNotExist:
        raise CodeResponseError(403.10001, 'Current folder not exist.') 


# Args:
#    file: file id
# Header:
#    Range: bytes range 
# @login_required
from urllib.parse import quote
from util.FileThread import hdfs_read, hdfs_reader
from flask import Response
@io.route('/download', methods=["GET"])
def download_chunkable():
    try:
        file_id = request.args.get("file")

        file = File.objects.get(id=file_id)
        # chunk_range = request.headers.get('Range')
        # print(chunk_range)
        # real_chunk_range = [0, 0]
        # res = None
        # if chunk_range: # Request中带分段
        #     l, r = chunk_range.split('=')[-1].split('-')
        #     l = int(l)
        #     if r == '':
        #         r = file.size;
        #     else:
        #         r = int(r)
        #     if r - l > 1024:
        #         r = l + 1024
        #     real_chunk_range = [l, r]
        #     chunk_data = hdfs_read(str(file.id), *real_chunk_range)
        #     res = make_response(chunk_data, 206)
        #     res.headers["Content-Type"] = 'application/octet-stream'
        #     res.headers["Content-Disposition"] = "attachment; filename* = UTF-8''%s" % quote(file.name)
        #     res.headers["Content-Range"] = 'bytes=%d-%d/%d' % (*real_chunk_range, file.size)
            
        # else: # 流式读取全文
        res = Response(hdfs_reader(str(file.id), 1024), 200)
        res.headers["Content-Type"]    = 'application/octet-stream'
        res.headers["Content-Disposition"] = "attachment; filename* = UTF-8''%s" % quote(file.name)
        res.headers["Content-length"]  = file.size
        return res
    except File.DoesNotExist:
        raise CodeResponseError(404.20001, 'Args loss. Need name,folder,size at least.')
