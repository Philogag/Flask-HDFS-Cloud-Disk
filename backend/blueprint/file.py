from flask import Blueprint, current_app, request
from flask_login import login_required, current_user

import os

from util.api_code import CodeResponse, CodeResponseError
import util.hdfs as hdfs
file = Blueprint('file', __name__, url_prefix='/api/file')

# @login_required
# @file.route('/list')
# def list_floder():

        