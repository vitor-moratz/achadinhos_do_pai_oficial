from pymongo import MongoClient
from pymongo.database import Database
import os

_client = None


def get_db() -> Database:
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/achadinhos")
        _client = MongoClient(uri)
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/achadinhos")
    db_name = uri.rsplit("/", 1)[-1].split("?")[0] if "/" in uri else "achadinhos"
    return _client[db_name]
