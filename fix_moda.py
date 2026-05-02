import os, sys
sys.path.insert(0, '/home/moratz/achadinhos_do_pai_oficial/backend')
from dotenv import load_dotenv
load_dotenv('/home/moratz/achadinhos_do_pai_oficial/backend/.env')
from database import get_db
db = get_db()
result = db.segments.update_one(
    {'slug': 'moda'},
    {'$set': {'name': 'Moda', 'description': 'Roupas, calçados e acessórios para todos os estilos'}}
)
print('matched:', result.matched_count, 'modified:', result.modified_count)
