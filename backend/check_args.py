import hashlib, json, time, requests
APP_ID = '18362881015'
SECRET = 'PDJ2WIOKXYGN7YXXP3SYLADQ4U735M2A'
BASE   = 'https://open-api.affiliate.shopee.com.br'
def gql(q):
    pl = {'query': q}
    ts = int(time.time())
    sig = hashlib.sha256(f'{APP_ID}{ts}{json.dumps(pl)}{SECRET}'.encode()).hexdigest()
    hdr = {'Content-Type': 'application/json',
           'Authorization': f'SHA256 Credential={APP_ID}, Signature={sig}, Timestamp={ts}'}
    return requests.post(f'{BASE}/graphql', headers=hdr, json=pl, timeout=15).json()
d = gql('{ __type(name: "Query") { fields { name args { name } } } }')
for f in d['data']['__type']['fields']:
    if f['name'] == 'productOfferV2':
        print('productOfferV2 args:', [a['name'] for a in f['args']])
d2 = gql('query { productOfferV2(limit: 3, page: 1, keyword: "fone") { nodes { productName } } }')
if 'errors' in d2:
    print('keyword NAO suportado:', d2['errors'][0]['message'])
else:
    print('keyword OK -', len(d2.get('data',{}).get('productOfferV2',{}).get('nodes',[])), 'resultados')
