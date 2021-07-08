from enum import Enum
from model.db import db
from model.User import User

class SavePosition(Enum):
    HDFS = 'hdfs'
    HBASE = 'hbase'

class Folder(db.Document):
    name = db.StringField(required=True)
    size = db.LongField(required=True, default=0)  # B
    update_time = db.DateTimeField(required=True)

    # 3=DENY: Prevent the deletion of the reference object.
    # 禁止删除非空文件夹对象
    parent_floder = db.LazyReferenceField("self", reverse_delete_rule = 3) 
    owner = db.LazyReferenceField(User, required=True)  # 权限保护

    # 包含子文件夹 通过 parent_floder       反查
    # 包含子文件   通过 File.parent_floder  反查
    
    def walk_to_root(self):
        current = self.parent_floder.fetch()
        ret = []
        while current and current.name != "~":
            ret.append(current.get_info())
            current = current.parent_floder.fetch()
        ret.append(current.get_info())  # This is ~
        ret.reverse()
        return ret

    def get_detial(self):
        son_folders = Folder.objects(parent_floder=self).all()
        son_files = File.objects(parent_floder=self).all()
        return {
            "id": str(self.id),
            "name": self.name,
            "update_time": self.update_time,
            "size": self.size,
            "root": self.walk_to_root(),
            "sons": {
                "folders": [ f.get_info() for f in list(son_folders) ],
                "files": [ f.get_info() for f in list(son_files) ]
            }
        }

    def get_info(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "update_time": self.update_time,
            "size": self.size,
        }


class File(db.Document):
    name = db.StringField(required=True)
    upload_time = db.DateTimeField(required=True)
    size = db.LongField(required=True) # B
    md5 = db.StringField()

    save_position = db.EnumField(SavePosition, default=SavePosition.HBASE)

    # 3=DENY: Prevent the deletion of the reference object.
    # 禁止删除非空文件夹对象
    parent_floder = db.LazyReferenceField(Folder, required=True)
    owner = db.LazyReferenceField(User, required=True)
    
    def get_info(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "update_time": self.update_time,
            "size": self.size,
            "md5": self.md5,
        }