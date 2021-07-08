from datetime import timedelta
import os

#
SECRET_KEY = 'asgwesvrery]p'

# 登陆设置
PERMANENT_SESSION_LIFETIME = timedelta(days=1) # 登录过期时间 
REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True # 自动刷新时长

# 数据库配置
MONGO_DB = {
    "HOST": '192.168.10.5',
    "PORT": 27017,
    "USER": 'root',
    "PASSWORD":'passwd',
    "DB":'cloud_disk',
}

# HDFS 设置
HADOOP_MASTER = [
    "192.168.10.5:50070",
]
HADOOP_USER_NAME='root'
HDFS_HOME = '/cloud'  # hdfs中的根目录

# HBASE 设置
# HBASE_MASTER = "192.168.10.5:60000"
