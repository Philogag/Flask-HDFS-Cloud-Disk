from pyhdfs import HdfsClient
from flask import current_app
from pathlib import Path
from threading import Thread, Lock

from model.IOTask import UploadTask
from model.File import File, Folder, SavePosition

import os
import hashlib
client = HdfsClient(current_app.config['HADOOP_MASTER'], user_name=current_app.config['HADOOP_USER_NAME'])

global_home = os.path.join('/', current_app.config['HDFS_HOME'])

def fix_path_join(*path):
    return Path(os.path.join(*path)).as_posix()

def hello():
    if not client.exists(global_home):
        client.mkdirs(global_home)
    return True

class FilePush(Thread):
    def __init__(self, task):
        super(FilePush, self).__init__()
        self.task = task
        self.collected = 0
        print("Init merge task:", self.task.id)

    def run(self):
        print(self.task.id, "Start merge task")
        md5 = hashlib.md5()
        self.file = self.task.File()
        if self.task.system == 'hdfs':
            self.file.save_position = SavePosition.HDFS
            if not hello():
                self.task.merge_status = {
                    "done": True,
                    "success": False,
                    "status": "error",
                    "msg": "Hdfs connection failed."
                }
                self.task.save()
                return
            hdfs_path = fix_path_join(global_home, str(self.task.id))
            print(hdfs_path)
            try:
                if client.exists(hdfs_path):
                    client.delete(hdfs_path)
                client.create(hdfs_path, b'')

                for i in range(self.task.chunk_cnt):
                    print(self.task.id, "Write chunk", i)
                    with open(os.path.join('./cache', str(self.task.id), 'block_' + str(i)), 'rb') as f:
                        buff = f.read()
                        md5.update(buff)
                        client.append(hdfs_path, buff)
                        
                    self.collected = i + 1
                    self.task.merge_status["collected"] = self.collected
                    self.task.save()
                
                self.file.md5 = md5.hexdigest()
                self.file.save()
                client.rename(hdfs_path, fix_path_join(global_home, str(self.file.id)))
                self.task.file = self.file
                self.task.merge_status = {
                    "done": True,
                    "success": True,
                    "msg": "Ok."
                }
                self.task.save()
                return
            except BaseException as e:
                print(e)
                self.task.merge_status = {
                    "done": True,
                    "success": False,
                    "msg": str(e)
                }
                self.task.save()
        else:           # hbase
            self.file.save_position = SavePosition.HBASE

        print(self.task.id, "Merge task done.")
        
        
            
