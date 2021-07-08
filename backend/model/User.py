
from model.db import db

class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)

    reg_time = db.DateTimeField(required=True)
    last_login = db.DateTimeField(required=True)

    def get_info(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "regist_time": self.reg_time,
            "last_login": self.last_login
        }