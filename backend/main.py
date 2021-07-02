from flask import Flask, jsonify

## Config ##
app = Flask('PocketLibrary_backend')
app.app_context().push()
app.config.from_pyfile('config.py')

## Session on DB ##
from flask_session import Session
from util.mongodb import mongo, db
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = mongo
app.config['SESSION_MONGODB_DB'] = 'session'
app.config['SESSION_KEY_PREFIX'] = 'session:'
Session(app)

## Root ##
@app.route('/api/hello', methods=['GET', ])
def api_hello():
    return jsonify({'code': 200, 'msg': "hello"})

## Modules ##
from blueprint.auth import auth
modules = [
    auth
]

for m in modules:
    app.register_blueprint(m)
