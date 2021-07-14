from pyhdfs import HdfsClient
from flask import current_app
from pathlib import Path
import threading

from model.IOTask import UploadTask
from model.File import File, Folder, SavePosition

import os
import hashlib

import ctypes

hdfs_client = HdfsClient(current_app.config['HADOOP_MASTER'], user_name=current_app.config['HADOOP_USER_NAME'])

global_home = os.path.join('/', current_app.config['HDFS_HOME'])

def fix_path_join(*path):
    return Path(os.path.join(*path)).as_posix()

def hdfs_hello():
    if not hdfs_client.exists(global_home):
        hdfs_client.mkdirs(global_home)
    return True

def hdfs_delete(path):
    if hdfs_client.exists(path):
        hdfs_client.delete(path)

class FilePush(threading.Thread):
    def __init__(self, task):
        super(FilePush, self).__init__()
        self.task = task
        self.collected = 0
        print("Init merge task:", self.task.id)

        self.exit_flag = threading.Event()

    def stop(self):
        self.exit_flag.set()

    def run(self):
        print(self.task.id, "Start merge task")
        md5 = hashlib.md5()
        self.file = self.task.File()
        if self.task.system == 'hdfs':
            self.file.save_position = SavePosition.HDFS
            if not hdfs_hello():
                self.task.merge_doing = False
                self.task.merge_done = True
                self.task.merge_success = False
                print("Hdfs Error.")
                self.task.save()
                return
            hdfs_path = fix_path_join(global_home, str(self.task.id))
            try:
                if hdfs_client.exists(hdfs_path):
                    hdfs_client.delete(hdfs_path)
                hdfs_client.create(hdfs_path, b'')

                for i in range(self.task.meta_chunks):
                    if self.exit_flag.isSet():
                        self.clean()
                        return
                    print(self.task.id, "Write chunk", i)
                    with open(os.path.join('./cache', str(self.task.id), 'block_' + str(i)), 'rb') as f:
                        buff = f.read()
                        md5.update(buff)
                        hdfs_client.append(hdfs_path, buff)
                        
                    self.collected = i + 1
                    self.task.merge_count = self.collected
                    self.task.save()
                
                if self.exit_flag.isSet():
                    self.clean()
                    return
                self.file.md5 = md5.hexdigest()
                print(self.task.meta_md5, self.file.md5, self.file.md5 == self.task.meta_md5)
                self.file.save()
                hdfs_client.rename(hdfs_path, fix_path_join(global_home, str(self.file.id)))
                self.task.file = self.file
                self.task.merge_doing = False
                self.task.merge_done = True
                self.task.merge_success = True
                self.task.save()
                return
            except BaseException as e:
                print(e)
                self.task.merge_doing = False
                self.task.merge_done = True
                self.task.merge_success = False
                self.task.save()
        else:           # hbase
            self.file.save_position = SavePosition.HBASE

        print(self.task.id, "Merge task done.")
        self.__del__()


def hdfs_read(file, l, r):
    size = r - l
    with hdfs_client.open(fix_path_join('/cloud', file), offset=l, length=size) as f:
        return f.read()

def hdfs_reader(file, chunk_size):
    with hdfs_client.open(fix_path_join('/cloud', file), buffer=chunk_size) as f:
        while True:
            chunk = f.read(chunk_size)
            if len(chunk) > 0:
                yield chunk
            else:
                break
