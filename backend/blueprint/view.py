from flask import Blueprint, current_app, render_template
# from flask_login import login_required, current_user

view = Blueprint('view', __name__, url_prefix='/view',
        static_url_path="/static",
        static_folder='../../frontend/static',
        template_folder="../../frontend"
    )

@view.route("/", methods=['GET'])
def index():
    return render_template('index.html')

# 主界面 
@view.route("/main", methods=['GET','POST'])
def view_main():
    return render_template('function.html')

# 登录界面 
@view.route("/login", methods=['GET'])
def view_login():
    return render_template('login.html')

# 注册界面 
@view.route("/register", methods=['GET','POST'])
def view_regist():
    return render_template('register.html')