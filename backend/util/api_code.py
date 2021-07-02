from flask import current_app, jsonify, Response

app = current_app

def CodeResponse(code, msg=''):
    res = jsonify({
        "code": code,
        "msg": msg,
    })
    res.status_code = int(code)
    return res

class CodeResponseError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
    def json(self):
        return {"code": self.code, "msg": self.msg}

@app.errorhandler(CodeResponseError)
def handle_code_err(error):
    response = jsonify(error.json(),)
    response.status_code = int(error.code)
    return response

# get built-in 401
@app.errorhandler(401)
def handle_builtin_401(error):
    response = jsonify({"code": 401, "msg": str(error)})
    response.status_code = 401
    return response