

from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, current_user

import os
import math
import hashlib
import json
from datetime import datetime

from blueprint.file import get_current_path

from util.api_code import CodeResponse, CodeResponseError
from util.crypto import random_aes_key, random_string, aes_encrypt, aes_decrypt
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

        task = UploadTask(
            owner=current_user.obj,
            folder=folder,
            create_t=datetime.now(),
            size=meta['size'],
            name=meta['name']
        )
        if 'aes' in meta.keys() and meta['aes'] == True:
            task.aes_key = random_aes_key()
            task.aes_shake_hand = False
            task.aes_shake_raw = random_string(64)
            task.aes_shake_crypto = aes_encrypt(task.aes_key, task.aes_shake_raw.encode(), 0)
        task.chunk_cnt = math.ceil(task.size / MAX_CHUNK_SIZE)
        task.chunk_status = [False for _ in range(task.chunk_cnt)]
        task.save()

        os.makedirs("./cache/" + str(task.id), exist_ok=True)
        return jsonify({
            "code": 200,
            "max_chunk_size": MAX_CHUNK_SIZE,
            "detial": task.get_info()
        })
    except KeyError:
        raise CodeResponseError(403.20001, 'Args loss. Need name,folder,size at least.')
    except Folder.DoesNotExist:
        raise CodeResponseError(403.10001, 'Current folder not exist.') 

    
@login_required
@io.route('/upload/aes_shakehand', methods=['POST', ])
def aes_shakehand():
    pass

# meta = {
#   "task_id": task id,
#   "meta":{
#        "id":   chunk id, begin at 0.
#        "size": real size in chunk.
#        "md5":  md5 of raw data.
#   }
#   "chunk_data": bytes.
# }
@login_required
@io.route('/upload/chunk', methods=['POST',])
def upload_chunk():
    try:
        task_id = request.form['task_id']
        meta = json.loads(request.form['meta'])
        data = request.files['chunk_data'].read()
        print(task_id, meta, len(data))

        task = UploadTask.objects.get(id=task_id)
        if not task.aes_key is None and not task.aes_shake_hand:
            raise CodeResponseError(403.20004, "Aes key need validation.")

        if not task.aes_key is None:
            data = aes_decrypt(task.aes_key, data, meta['id'])

        # data = data[: meta['size']]
        # print(len(data))

        # md5 = hashlib.md5(data).hexdigest()
        # if md5 != meta['meta']['md5'].supper():
        #     raise CodeResponseError(406.20005, "Chunk md5 wrong.")
        print(type(data))
        with open(os.path.join("./cache/", str(task.id), "block_" + str(meta['id'])), 'wb+') as f:
            print(data)
            f.write(data)
        
        task.chunk_status[meta['id']] = True
        task.save()

        return jsonify({
            "code": 200,
            "msg": "ok",
            "detial": task.get_info()
        })
    except UploadTask.DoesNotExist:
        raise CodeResponseError(403.10002, 'Task dose not exist.')
        
# Args:
#   "task_id": task id,
#   "md5":     md5 of total file.
@login_required
@io.route('/upload/finish', methods=['GET',])
def upload_finish():
    try:
        task_id = request.args.get("task_id")
        
        task = UploadTask.objects.get(id=task_id)

        if False in task.chunk_status :
            raise CodeResponseError(406.20006, "Lost some chunk!")
        
        realname = os.path.join("./cache/", str(task.id), task.name)
        with open(realname, 'wb+') as o_f:
            for i in range(task.chunk_cnt):
                chunkname = os.path.join("./cache/", str(task.id), "block_" + str(i))
                with open(chunkname, 'rb+') as i_f:
                    o_f.write(i_f.read())
        
        info = task.get_info()
        task.delete()

        return jsonify({
            "code": 200,
            "msg": "Upload task done.",
            "detial": info,
        })
    except KeyError:
        raise CodeResponseError(403.20001, 'Args loss. Need name,folder,size at least.')
    except Folder.DoesNotExist:
        raise CodeResponseError(403.10001, 'Current folder not exist.') 
