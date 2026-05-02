import sys
sys.path.insert(0, '/home/moratz/achadinhos_do_pai_oficial/backend')
from database import get_db

def dedup(db, collection, key):
    pipeline = [
        {"$group": {"_id": f"${key}", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    total = 0
    for group in db[collection].aggregate(pipeline):
        ids_to_delete = group["ids"][1:]
        db[collection].delete_many({"_id": {"$in": ids_to_delete}})
        print(f"  [{collection}] removidos {len(ids_to_delete)} duplicatas de slug={group['_id']}")
        total += len(ids_to_delete)
    if total == 0:
        print(f"  [{collection}] sem duplicatas")

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    db = get_db()
    dedup(db, 'categories', 'slug')
    dedup(db, 'segments', 'slug')
    dedup(db, 'tags', 'slug')
    print("Done.")
