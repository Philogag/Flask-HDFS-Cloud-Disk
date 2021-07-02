from pyhdfs import HdfsClient
from flask import current_app
from pathlib import Path

from util.api_code import CodeResponseError

import os
client = HdfsClient('192.168.10.5:50070', user_name=current_app.config['HADOOP_USER_NAME'])

global_home = os.path.join('/', current_app.config['HDFS_HOME'])


def fix_path_join(*path):
    return Path(os.path.join(*path)).as_posix()

def hello():
    if not client.exists(global_home):
        client.mkdirs(global_home)
    return True

def exists(path):
    return client.exists(fix_path_join(global_home, path))

def mkdirs(user_path):
    if not client.mkdirs(fix_path_join(global_home, user_path)):
        raise CodeResponseError(10001, 'Cannot create directory.')

def makehome(userId):
    try:
        mkdirs(str(userId))
    except CodeResponseError as e:
        if e.code == 10001:
            raise CodeResponseError(10001.1, "Cannot create user's home.")

def walk(path):
    root, dirs, files = client.walk(fix_path_join(global_home, path))
    return dirs, files