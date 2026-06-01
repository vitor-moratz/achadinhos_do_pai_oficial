import hashlib, json, time, requests
APP_ID = '18362881015'
SECRET = 'PDJ2WIOKXYGN7YXXP3SYLADQ4U735M2A'
BASE = 'https://open-api.affiliate.shopee.com.br'
def gql(q):
    pl = {'query': q}
    ts = int(time.time())
    sig = hashlib.sha256(f'{APP_ID}{ts}{json.dumps(pl)}{SECRET}'.encode()).hexdigest()
    hdr = {'Content-Type': 'application/json', 'Authorization': f'SHA256 Credential={APP_ID}, Signature={sig}, Timestamp={ts}'}
    return requests.post(f'{BASE}/graphql', headers=hdr, json=pl, timeout=15).json()

# Inspeciona campos do PageInfo
d = gql('{ __type(name: "ProductOfferPageInfo") { fields { name } } }')
print('PageInfo fields:', d)

# Faz query real pra ver o que vem no pageInfo
d2 = gql('query { productOfferV2(limit: 5, page: 1) { pageInfo { page limit hasNextPage } } }')
print('pageInfo sample:', d2)
