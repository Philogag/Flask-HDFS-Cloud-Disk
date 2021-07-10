from model.db import db

from model.User import User
from model.File import Folder

class UploadTask(db.Document):
    meta = {
        'indexes': [
            {'fields': ['create_t'], 'expireAfterSeconds': 7 * 24 * 3600 }
        ]
    }
    create_t = db.DateTimeField(required=True)
    owner = db.LazyReferenceField(User)

    name = db.StringField()
    folder = db.LazyReferenceField(Folder)
    size = db.LongField()

    # aes加密相关
    aes_key = db.BinaryField()          # 密钥
    aes_shake_hand = db.BooleanField()  # 握手成功标记
    aes_shake_raw = db.StringField()    # 握手明文
    aes_shake_crypto = db.BinaryField() # 握手密文

    chunk_cnt = db.IntField()
    chunk_status = db.ListField(db.BooleanField())

    def get_info(self):
        return {
            "id": str(self.id),
            "size": self.size,
            "name": self.name,
            "folder": str(self.folder.id),
            "aes_key": self.aes_key,
            "chunk_cnt": self.chunk_cnt,
            "chunk_status": self.chunk_status,
        }