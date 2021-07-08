from enum import Enum
from model.db import db
from model.User import DbUser as User

class SavePosition(Enum):
    HDFS = 'hdfs'
    HBASE = 'hbase'

class Floder(db.Document):
    name = db.StringField(required=True)
    size = db.LongField(required=True, default=0)  # B
    owner = db.LazyReferenceField(User, required=True)  # 权限保护
    
    update_time = db.DateTimeField(required=True)

    # 3=DENY: Prevent the deletion of the reference object.
    # 禁止删除非空文件夹对象
    parent_floder = db.LazyReferenceField("self", reverse_delete_rule = 3) 
    
    # 包含子文件夹 通过 parent_floder       反查
    # 包含子文件   通过 File.parent_floder  反查

class File(db.Document):
    owner = db.LazyReferenceField(User, required=True)
    name = db.StringField(required=True)
    upload_time = db.DateTimeField(required=True)
    file_size = db.LongField(required=True) # B

    save_position = db.EnumField(SavePosition, default=SavePosition.HBASE)

    # 3=DENY: Prevent the deletion of the reference object.
    # 禁止删除非空文件夹对象
    parent_floder = db.LazyReferenceField(Floder, required=True)