from model.db import db

from model.User import User
from model.File import Folder, File
from datetime import datetime

class UploadTask(db.Document):
    meta = {
        'indexes': [
            {'fields': ['meta_created'], 'expireAfterSeconds': 7 * 24 * 3600 }
        ]
    }
    ## Refrence
    owner = db.LazyReferenceField(User)
    folder = db.LazyReferenceField(Folder)
    file = db.LazyReferenceField(File)

    ## Meta
    meta_created = db.DateTimeField(required=True)
    meta_chunks = db.IntField()
    meta_size = db.LongField()
    meta_name = db.StringField()
    meta_md5 = db.StringField()

    ### aes加密相关
    aes_use  = db.BooleanField(default=False)
    aes_key = db.BinaryField()          # 密钥
    aes_shake_hand = db.BooleanField()  # 握手成功标记
    aes_shake_raw = db.StringField()    # 握手明文
    aes_shake_crypto = db.BinaryField()  # 握手密文

    ### Upload
    upload_done = db.BooleanField(default=False)
    upload_chunks = db.ListField(db.BooleanField())
    
    ### Merge
    merge_doing = db.BooleanField(default=False)
    merge_done = db.BooleanField(default=False)
    merge_success = db.BooleanField(default=False)
    merge_count = db.IntField(default=0)

    call_cancle = db.BooleanField(default=False)

    def get_detial(self):
        return {
            "id": str(self.id),
            "meta": {
                "created": self.meta_created,
                "size": self.meta_size,
                "name": self.meta_name,
            },
            "chunks": {
                "count": self.meta_chunks,
                "status": self.upload_chunks,
            },
            "aes_use": self.aes_use,
            "aes": {
                "key": self.aes_key,
                "shake_hand": self.aes_shake_hand,
                "shake_crypto": self.aes_shake_crypto
            }
        }
    
    def File(self):
        file = File(
            name = self.meta_name,
            owner = self.owner,
            parent_folder = self.folder,
            size = self.meta_size,
            upload_time = self.meta_created,
        )
        return file

            