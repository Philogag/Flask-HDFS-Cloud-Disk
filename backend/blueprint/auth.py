from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user

from util.api_code import CodeResponse, CodeResponseError
import util.hdfs as hdfs

from model.User import DbUser as User
from model.File import Floder
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

## Login Module ##
class SessionUser(UserMixin):
    def __init__(self, userobj):
        super().__init__()
        self.uid = str(userobj.id)
        self.obj = userobj

    def get_id(self):
        return self.uid

login_manager = LoginManager()
login_manager.init_app(current_app)

@login_manager.user_loader
def load_user(user_id):
    try:
        print(user_id)
        return SessionUser(User.objects.get(id=user_id))
    except User.DoesNotExist:
        return None
## Urls ##

@auth.route('/check', methods=['GET', ])
@login_required
def check():
    return CodeResponse(200, "ok")

@auth.route('/login', methods=['POST'])
def login():
    userlogin = request.get_json()
    print(userlogin)
    try:
        userobj = User.objects.get(username=userlogin['username'])
        if userobj['password'] == userlogin['password']:
            userobj.last_login = datetime.now()
            userobj.save()
            login_user(SessionUser(userobj))

            response = jsonify({
                "code": 200,
                "msg": "Login successfully",
                "user": userobj, 
            })
            current_path_id = request.cookies.get('current_path_id')
            current_floder = None
            try:
                current_floder = Floder.objects.get(id=current_path_id)
                if current_floder.owner.id != current_user.uid:
                    raise "Permission denied."
            except BaseException:
                current_floder = Floder.objects(owner=current_user.obj, name='~').first()
            response.set_cookie('current_path_id', current_floder.id)
            return response
        else:
            return CodeResponse(403.2, 'Password dose not match.')
    except User.DoesNotExist:
        return CodeResponse(403.1, 'User not found.')

@auth.route('/regist', methods=['POST'])
def register():
    userreg = request.get_json()
    print(userreg)

    if User.objects(username=userreg['username']).count() > 0:
        return CodeResponse(403.1, 'User has been registered.')
    if userreg['password'] != userreg['password_confirm']:
        return CodeResponse(403.2, 'Confirm password dose not the same.')

    userobj = User(
        username=userreg['username'],
        password=userreg['password'],
        reg_time=datetime.now(),
        last_login=datetime.now()
    )
    userobj.save()
    try:
        hdfs.makehome(userobj.id)
    except CodeResponseError as e:
        # User.delete_one(userobj) # regist failed, remove from db
        raise e
    
    floder = Floder(owner=userobj, name="~", update_time=datetime.now()).save()
    login_user(SessionUser(userobj))
    response = jsonify({
                "code": 200,
                "msg": "Regist successfully.",
                # "user": userobj, 
            })
    response.set_cookie("current_path_id", floder.id)
    return response

@auth.route('/logout', methods=['GET', ])
@login_required
def logout():
    logout_user()
    return CodeResponse(200, "User is no longer login now.")