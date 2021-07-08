from flask import Flask, jsonify

## Config ##
app = Flask('PocketLibrary_backend')
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
import util.hdfs as hdfs
hdfs.hello()

## Root ##
@app.route('/api/hello', methods=['GET', ])
def api_hello():
    return jsonify({'code': 200, 'msg': "hello"})

## Modules ##
from blueprint.auth import auth
from blueprint.view import view
modules = [
    auth,
    view
]

for m in modules:
    app.register_blueprint(m)
