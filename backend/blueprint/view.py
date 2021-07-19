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


@view.route("/register", methods=['GET'])
def regist_view():
    return render_template('register.html')


@view.route("/login", methods=['GET'])
def login_view():
    return render_template('login.html')


@view.route("/main", methods=['GET'])
def main_view():
    return render_template('main.html')

