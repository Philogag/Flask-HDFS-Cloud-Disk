from flask import Blueprint, current_app, request
from flask_login import login_required, current_user

import os

from util.api_code import CodeResponse, CodeResponseError
from util.mongodb import db
import util.hdfs as hdfs
file = Blueprint('file', __name__, url_prefix='/api/file')

User = db.User

@login_required
@file.route('/view')
def list_floder():
    path = os.path.join(current_user.id, current_user.curr_path)
    print(path)
    objs = hdfs.walk(path)
        