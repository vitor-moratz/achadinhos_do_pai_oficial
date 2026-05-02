import sys
sys.path.insert(0, '/home/moratz/achadinhos_do_pai_oficial/backend')

from flask import Flask
from config import Config
from database import get_db

app = Flask(__name__)
app.config.from_object(Config)

with app.app_context():
    db = get_db()
    cats = list(db.categories.find({"segment_slug": "eletronicos"}).sort("name", 1))
    print(f"Total no banco para eletronicos: {len(cats)}")
    for c in cats:
        print(f"  slug={c.get('slug')} | name={c.get('name')} | segment_slug={c.get('segment_slug')}")
    print()
    print("Todos com name 'Cabos e Carregadores':")
    dupes = list(db.categories.find({"name": {"$regex": "Cabos", "$options": "i"}}))
    for c in dupes:
        print(f"  _id={c['_id']} slug={c.get('slug')} segment_slug={c.get('segment_slug')}")
