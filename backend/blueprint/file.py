from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, current_user

import os
from datetime import datetime

from util.api_code import CodeResponse, CodeResponseError
from model.File import File, Folder

file = Blueprint('file', __name__, url_prefix='/api/fs')

BANNED_CHARSET=current_app.config['BANNED_CHARSET'].strip()

def get_current_path():
    try:
        folder_id = request.cookies.get('current_path_id')
        folder = Folder.objects.get(id=folder_id)
        if folder.owner.id != current_user.obj.id:
            raise CodeResponseError(403.10002, 'Permission denied. This is not your folder')
        return folder
    except Folder.DoesNotExist:
        raise CodeResponseError(403.10001, 'Current folder not exist.')

@login_required
@file.route('/mkdir/', methods=['GET', ])
def mkdir():
    name = request.args.get('name')
    if not name:
        raise CodeResponseError(400.10003, "Empty folder name is not allowed.")
    # print(name, (set(name) & set(BANNED_CHARSET)))
    if len(set(name) & set(BANNED_CHARSET)) > 0:
        raise CodeResponseError(400.10004, "Illegal name, you cannot use \"" + BANNED_CHARSET + "\"")
    current_folder = get_current_path()
    new_folder = Folder(
        owner=current_user.obj,
        name=name,
        update_time=datetime.now(),
        parent_floder=current_folder
    )
    new_folder.save()
    return jsonify({
        "code": "200",
        "msg": "ok",
        "new_id": str(new_folder.id),
    })


@login_required
@file.route('/cd/', methods=['GET', ])
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
        raise CodeResponseError(403.10001, 'Current folder not exist.')
    
@login_required
@file.route('/refresh', methods=['GET',])
@file.route('/list', methods=['GET', ])
def list():
    folder = get_current_path()
    detial = folder.get_detial()
    response = jsonify({
        "code": "200",
        "detial": detial,
    })
    return response
    