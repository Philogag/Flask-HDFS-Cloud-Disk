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


