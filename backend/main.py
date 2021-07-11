from flask import Flask, jsonify

from concurrent.futures import ThreadPoolExecutor

## Config ##
class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self._create_threadpoll()

    def _create_threadpoll(self):
        self.thread_map = {}
    
    def __del__(self):
        for k, v in self.thread_map:
            pass
    
app = FlaskApp('PocketLibrary_backend')
app.app_context().push()
app.config.from_pyfile('config.py')

## Session on DB ##
from flask_session import Session
from pymongo import MongoClient
from model.db import db

__mongo_settings_copy = app.config['MONGODB_SETTINGS'].copy()
del __mongo_settings_copy['db']
del __mongo_settings_copy['authentication_source']
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = MongoClient(**__mongo_settings_copy)
app.config['SESSION_MONGODB_DB'] = app.config['MONGODB_SETTINGS']['db']
app.config['SESSION_KEY_PREFIX'] = 'session:'
Session(app)

## HDFS Hello ##
from util.FileThread import hello as hdfs_hello
hdfs_hello()

## Root ##
@app.route('/api/hello', methods=['GET', ])
def api_hello():
    return jsonify({'code': 200, 'msg': "hello"})

## Modules ##
from blueprint.view import view

from blueprint.auth import auth
from blueprint.file import fs
from blueprint.io import io
modules = [
    view,

    auth,
    fs,
    io
]

for m in modules:
    app.register_blueprint(m)
