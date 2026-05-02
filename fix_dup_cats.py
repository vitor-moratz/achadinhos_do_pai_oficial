import sys
sys.path.insert(0, '/home/moratz/achadinhos_do_pai_oficial/backend')
from dotenv import load_dotenv
load_dotenv('/home/moratz/achadinhos_do_pai_oficial/backend/.env')
from database import get_db
db = get_db()

# Os slugs "antigos" são os que NÃO contêm hífen com o segmento prefixado.
# Estratégia: para cada segmento, manter apenas os docs com slug = "{seg}-{name}".
# Deletar todos os docs cujo slug NÃO começa com o slug do segmento.

segments = ['ferramentas', 'automotivo', 'pet-shop', 'casa', 'eletronicos', 'esporte', 'games', 'moda']

total_deleted = 0
for seg in segments:
    # Achar docs com segment_slug = seg cujo slug não começa com seg
    old_docs = list(db.categories.find({
        'segment_slug': seg,
        'slug': {'$not': {'$regex': f'^{seg}-'}}
    }, {'_id': 1, 'slug': 1, 'name': 1}))
    
    if old_docs:
        ids = [d['_id'] for d in old_docs]
        result = db.categories.delete_many({'_id': {'$in': ids}})
        total_deleted += result.deleted_count
        for d in old_docs:
            print(f'  deleted: [{seg}] {d["slug"]} ({d["name"]})')

print(f'\nTotal deleted: {total_deleted}')
