from datetime import timedelta
import os

#
SECRET_KEY = 'asgwesvrery]p'
HASH_SALT="qwwgawegxdf+w36_" # 16位加密用于密码哈希

# 文件(夹)名黑名单字符
BANNED_CHARSET = """/\:*?"<>|"""

# 登陆设置
PERMANENT_SESSION_LIFETIME = timedelta(days=1) # 登录过期时间 
REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True # 自动刷新时长

# 数据库配置
MONGODB_SETTINGS = {
    "db": 'cloud_disk',
    'host': '192.168.10.5',
    'port': 27017,
    'connect': False,
    'username': 'root',
    'password': 'passwd',
    "authentication_source":'admin',
}

# HDFS 设置
HADOOP_MASTER = [
    "192.168.10.5:50070",
]
HADOOP_USER_NAME='root'
HDFS_HOME = '/cloud'  # hdfs中的根目录

# HBASE 设置
# HBASE_MASTER = "192.168.10.5:60000"
