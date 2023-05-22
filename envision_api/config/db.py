import pymongo.database
from pymongo import MongoClient

from config.constants import MONGODB_USER, MONGODB_PASSWD, MONGO_URI_TEST, CURRENT_ENVIRONMENT, EnvironmentEnum

if CURRENT_ENVIRONMENT != EnvironmentEnum.test:
    _client = MongoClient(f'mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWD}@serverlessinstance0.xa0bq.mongodb.net/test')
else:
    _client = MongoClient(MONGO_URI_TEST)

conn: pymongo.database.Database = _client[CURRENT_ENVIRONMENT.name]
