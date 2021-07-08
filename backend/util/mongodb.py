from flask import current_app
from pymongo import MongoClient

config = current_app.config['MONGO_DB']


mongo = MongoClient('mongodb://{USER}:{PASSWORD}@{HOST}:{PORT}'.format(**config), connect=False)

db = mongo.get_database(config['DB'])
