from flask import Flask, jsonify

## Config ##
app = Flask('PocketLibrary_backend')
app.app_context().push()
app.config.from_pyfile('config.py')

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
