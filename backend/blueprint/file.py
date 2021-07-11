from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, current_user

import os
from datetime import datetime

from util.api_code import CodeResponse, CodeResponseError
from model.File import File, Folder

fs = Blueprint('fs', __name__, url_prefix='/api/fs')

BANNED_CHARSET=current_app.config['BANNED_CHARSET'].strip()

def get_current_path():
    try:
        folder_id = request.cookies.get('current_path_id')
        folder = Folder.objects.get(id=folder_id)
        if folder.owner != current_user.obj:
            raise CodeResponseError(403.10002, 'Permission denied. This is not your folder')
        return folder
    except Folder.DoesNotExist:
        raise CodeResponseError(403.10001, 'Current folder not exist.')


@login_required
@fs.route('/refresh', methods=['GET',])
@fs.route('/list', methods=['GET', ])
def list():
    folder = get_current_path()
    detial = folder.get_detial()
    response = jsonify({
        "code": "200",
        "detial": detial,
    })
    return response


@login_required
@fs.route('/mkdir', methods=['GET', ])
def mkdir():
    name = request.args.get('name')
    if not name:
        raise CodeResponseError(400.10003, "Empty folder name is not allowed.")
    # print(name, (set(name) & set(BANNED_CHARSET)))
    if len(set(name) & set(BANNED_CHARSET)) > 0:
        raise CodeResponseError(400.10004, "Illegal name, you cannot use \"" + BANNED_CHARSET + "\"")
    
    current_folder = get_current_path()
    check = Folder.objects(name=name, parent_folder=current_folder).first()
    if check:
        raise CodeResponseError(400.10005, "Folder has beem created.")
    new_folder = Folder(
        owner=current_user.obj,
        name=name,
        update_time=datetime.now(),
        parent_folder=current_folder
    )
    new_folder.save()
    return jsonify({
        "code": "200",
        "msg": "ok",
        "new_id": str(new_folder.id),
    })


@login_required
@fs.route('/cd', methods=['GET', ])
def cd():
    try:
        folder_id = request.args.get('id')
        folder = Folder.objects.get(id=folder_id)

        if folder.owner.id != current_user.obj.id:
            raise CodeResponseError(403.10002, 'Permission denied. This is not your folder')
        detial = folder.get_detial()
        response = jsonify({
            "code": "200",
            "detial": detial,
        })
        response.set_cookie('current_path_id', str(folder.id))
        return response
    except Folder.DoesNotExist:
        raise CodeResponseError(404.10001, 'Current folder not exist.')


@login_required
@fs.route("/move", methods=['GET', ])
def move():
    otype = request.args.get('type')
    oid = request.args.get('id')
    target_id = request.args.get('target')
    if not otype or not oid or not target_id:
        raise CodeResponseError(403.10000, "Need {type, id, target}")
    if not otype == "file" and not otype == "folder":
        raise CodeResponseError(403.10000, "type must be \"file\" or \"folder\".")

    obj = None
    try:
        if otype == "file":
            obj = File.objects.get(id=oid)
        else:
            obj = Folder.objects.get(id=oid)
        target = Folder.objects.get(id=target_id)
    except File.DoesNotExist or Folder.DoesNotExist:
        raise CodeResponseError(404.10001, "Item not exist.")

    if obj.owner != current_user.obj or target.owner != current_user.obj:
        raise CodeResponseError(403.10002, 'Permission denied.')

    old_root = set(obj.walk_to_root())
    new_root = set(target.walk_to_root())

    [f.add_size(-obj.size).save() for f in old_root - new_root] # 旧文件夹去除文件size
    [f.add_size( obj.size).save() for f in new_root - old_root] # 新文件夹去除文件size
    obj.parent_folder = target
    obj.update_time = datetime.now()
    obj.save()

    return jsonify({
        "code": 200,
    })


@login_required
@fs.route("/rename", methods=['GET', ])
def rename():
    otype = request.args.get('type')
    oid = request.args.get('id')
    new_name = request.args.get('name')
    if not otype or not oid or not new_name:
        raise CodeResponseError(403.10000, "Need {type, id, name}")
    if not otype == "file" and not otype == "folder":
        raise CodeResponseError(403.10000, "Type must be \"file\" or \"folder\".")
    if len(set(new_name) & set(BANNED_CHARSET)) > 0:
        raise CodeResponseError(400.10004, "Illegal name, you cannot use \"" + BANNED_CHARSET + "\"")

    obj = None
    try:
        if otype == "file":
            obj = File.objects.get(id=oid)
        else:
            obj = Folder.objects.get(id=oid)
    except File.DoesNotExist or Folder.DoesNotExist:
        raise CodeResponseError(404.10001, "Item not exist.")

    if obj.owner != current_user.obj:
        raise CodeResponseError(403.10002, 'Permission denied.')
    if type(obj) is Folder and obj.isroot:
        raise CodeResponseError(403.10002, 'Permission denied.User\'s root cannot rename.')
    obj.name = new_name
    obj.save()

    return CodeResponse(200, "ok")

import queue

@login_required
@fs.route('/delete', methods=['GET',])
def delete():
    otype = request.args.get('type')
    oid = request.args.get('id')
    if not oid or not otype:
        raise CodeResponseError(403.10000, "Need args {type, id}")
    if not otype == "file" and not otype == "folder":
        raise CodeResponseError(403.10000, "Type must be \"file\" or \"folder\".")

    obj = None
    try:
        if otype == "file":
            obj = File.objects.get(id=oid)
        else:
            obj = Folder.objects.get(id=oid)
    except File.DoesNotExist or Folder.DoesNotExist:
        raise CodeResponseError(404.10001, "Item not exist.")

    if obj.owner != current_user.obj:
        raise CodeResponseError(403.10002, 'Permission denied.')
    if otype == "folder" and obj.isroot:
        raise CodeResponseError(403.10002, 'Permission denied.User\'s root cannot rename.')
    # Do delete
    info = obj.get_info()
    obj.delete()

    return jsonify({
        "code": 200,
        "msg": "Delete ? folders, ? files. ? MB in total.",
        "info": info,
    })