from flask import Blueprint, current_app, request
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user

from util.api_code import CodeResponse
from util.mongoutil import db
auth = Blueprint('auth', __name__, url_prefix='/api/auth')

User = db.User

## Login Module ##
class SessionUser(UserMixin):
    def __init__(self, username):
        super().__init__()
        self.username = username

    def get_id(self):
        return self.username

login_manager = LoginManager()
login_manager.init_app(current_app)

@login_manager.user_loader
def load_user(username):
    return SessionUser(username)

## Urls ##

@auth.route('/check', methods=['GET', ])
@login_required
def check():
    return CodeResponse(200, "ok")

@auth.route('/login', methods=['POST'])
def login():
    userlogin = request.get_json()
    print(userlogin)
    userobj = User.find_one({"username": userlogin['username']})
    if userobj:
        if userobj['password'] == userlogin['password']:
            login_user(SessionUser(userlogin['username']))
            return CodeResponse(200, "Login successfully.")
        else:
            return CodeResponse(403.2, 'Password dose not match.')
    else:
        return CodeResponse(403.1, 'User not found.')

@auth.route('/regist', methods=['POST'])
def register():
    userreg = request.get_json()
    print(userreg)
    if User.find_one({"username": userreg['username']}):
        return CodeResponse(403.1, 'User has been registered.')
    if userreg['password'] != userreg['password_confirm']:
        return CodeResponse(403.2, 'Confirm password dose not the same.')

    clean_data = {}
    keys = ['username', "password", "data"]
    for k in keys:
        clean_data[k] = userreg[k]
    User.insert(clean_data)

    login_user(SessionUser(userreg['username']))

    return CodeResponse(200, 'Regist successfully.')

@auth.route('/logout', methods=['GET', ])
@login_required
def logout():
    logout_user()
    return CodeResponse(200, "User is no longer login now.")