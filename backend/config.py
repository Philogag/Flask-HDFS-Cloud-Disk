from datetime import timedelta
import os

SECRET_KEY = 'asgwesvrery]p'

# 登录过期时间 
PERMANENT_SESSION_LIFETIME = timedelta(days=1)

# 数据库配置
MONGO_DB = {
    "HOST":'192.168.1.200',
    "PORT":27017,
    "USER":'root',
    "PASSWORD":'passwd',
    "DB":'cloud_disk',
}