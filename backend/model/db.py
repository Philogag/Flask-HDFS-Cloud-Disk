from flask import current_app
from flask_mongoengine import MongoEngine

db = MongoEngine(current_app)

