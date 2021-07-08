
from model.db import db

class DbUser(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    reg_time = db.DateTimeField(required=True)

    last_login = db.DateTimeField(required=True)
