import sys
sys.path.insert(0, '/home/moratz/achadinhos_do_pai_oficial/backend')
from flask import Flask
from config import Config
from database import get_db

app = Flask(__name__)
app.config.from_object(Config)

NEW_DESC = "Dispositivos inteligentes e tecnologia com custo-benefício"

with app.app_context():
    db = get_db()
    result = db.segments.update_one(
        {"slug": "eletronicos"},
        {"$set": {"description": NEW_DESC}}
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
