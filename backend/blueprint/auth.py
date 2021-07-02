from flask import Blueprint, current_app, request
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user
from bson.objectid import ObjectId

from util.api_code import CodeResponse, CodeResponseError
from util.mongodb import db
import util.hdfs as hdfs
auth = Blueprint('auth', __name__, url_prefix='/api/auth')

User = db.User
Floder = db.Floder

## Login Module ##
class SessionUser(UserMixin):
    def __init__(self, userobj):
        super().__init__()
        self.uid = str(userobj['_id'])
        try:
            self.curr_path = userobj['data']['curr_path']
        except KeyError:
            self.curr_path = '/'

    def get_id(self):
        return self.uid

login_manager = LoginManager()
login_manager.init_app(current_app)

@login_manager.user_loader
def load_user(user_id):
    return SessionUser(User.find_one({"_id": ObjectId(user_id)}))
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
            login_user(SessionUser(userobj))
            hdfs.makehome(userobj['_id'])
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
    
    User.insert_one(clean_data)
    userobj = User.find_one({"username": userreg['username']})
    try:
        hdfs.makehome(userobj['_id'])
    except CodeResponseError as e:
        User.delete_one(userobj) # regist failed, remove from db
        raise e

    login_user(SessionUser(userobj))

    return CodeResponse(200, 'Regist successfully.')

@auth.route('/logout', methods=['GET', ])
@login_required
def logout():
    logout_user()
    return CodeResponse(200, "User is no longer login now.")