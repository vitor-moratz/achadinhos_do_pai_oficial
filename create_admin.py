import sys, os
sys.path.insert(0, '/home/moratz/achadinhos_do_pai_oficial/backend')
os.environ['MONGODB_URI'] = 'mongodb+srv://achadinhosdopai:X26lef6zgQ6ZipuZ@achadinhosdopai.n2ajdnc.mongodb.net/achadinhos?retryWrites=true&w=majority&appName=achadinhosdopai'

import bcrypt
from database import get_db

db = get_db()

username = 'admin'
password = 'admin123'

existing = db.users.find_one({'username': username})
if existing:
    db.users.update_one({'username': username}, {'$set': {
        'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        'role': 'admin',
    }})
    print(f'Usuário "{username}" atualizado para role=admin com senha "{password}"')
else:
    db.users.insert_one({
        'username': username,
        'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
        'role': 'admin',
    })
    print(f'Usuário "{username}" criado com senha "{password}"')
