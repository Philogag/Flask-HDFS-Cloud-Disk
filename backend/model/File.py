from enum import Enum
from datetime import datetime

from model.db import db
from model.User import User
from model.ReCycle import RecycleTask

class SavePosition(Enum):
    HDFS = 'hdfs'
    HBASE = 'hbase'

class Folder(db.Document):
    name = db.StringField(required=True)
    size = db.LongField(required=True, default=0)  # B
    update_time = db.DateTimeField(required=True)
    isroot = db.BooleanField(default=False)
    # 2=CASCADE: 连锁删除
    parent_folder = db.LazyReferenceField("self", reverse_delete_rule = 2) 
    owner = db.LazyReferenceField(User, required=True)  # 权限保护

    # recycle_task = db.LazyReferenceField(RecycleTask, reverse_delete_rule=2)
    # recycle_ttl  = db.DateTimeField()
    # 包含子文件夹 通过 parent_folder       反查
    # 包含子文件   通过 File.parent_folder  反查
    
    def walk_to_root(self):
        if self.parent_folder is None:
            return []
        current = self.parent_folder.fetch()
        ret = []
        while current and current.name != "~":
            ret.append(current)
            current = current.parent_folder.fetch()
        ret.append(current)  # This is ~
        ret.reverse()
        return ret

    def get_detial(self):
        son_folders = Folder.objects(parent_folder=self).all()
        son_files = File.objects(parent_folder=self).all()
        return {
            "id": str(self.id),
            "name": self.name,
            "update_time": self.update_time,
            "size": self.size,
            "root": [ f.get_info() for f in self.walk_to_root() ],
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
    
    def add_size(self, size):
        self.size = self.size + size
        self.update_time = datetime.now()
        return self


class File(db.Document):
    name = db.StringField(required=True)
    upload_time = db.DateTimeField(required=True)
    size = db.LongField(required=True) # B
    md5 = db.StringField()

    save_position = db.EnumField(SavePosition, default=SavePosition.HBASE)

    # 2=CASCADE: 连锁删除
    parent_folder = db.LazyReferenceField(Folder, required=True, reverse_delete_rule = 2)
    owner = db.LazyReferenceField(User, required=True)
    
    # recycle_task = db.LazyReferenceField(RecycleTask, reverse_delete_rule = 2)
    # recycle_ttl  = db.DateTimeField()
    def get_root(self):
        parent = self.parent_folder.fetch()
        root = parent.get_root()
        root.append(parent)
        return root

    def get_info(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "update_time": self.update_time,
            "size": self.size,
            "md5": self.md5,
        }