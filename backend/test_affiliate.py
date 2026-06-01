import hmac, hashlib, time, uuid, requests, json

APP_ID = '18362881015'
SECRET = 'PDJ2WIOKXYGN7YXXP3SYLADQ4U735M2A'
BASE   = 'https://open-api.affiliate.shopee.com.br/api/v1/product/search'
s = requests.Session()
ts = str(int(time.time()))
tsms = str(int(time.time()*1000))
n = uuid.uuid4().hex[:8]

def chk(label, auth, ts_used, n_used):
    hdr = {'Content-Type':'application/json','Authorization':auth}
    r = s.get(BASE, headers=hdr, params={'page_size':3}, timeout=10)
    js = r.json()
    code = js.get('errors',[{}])[0].get('extensions',{}).get('code','OK') if 'errors' in js else 'OK'
    print(f'  {label} -> {code}')

print('=== Separador & no header ===')
for order, msg in [
    ('appid&nonce&ts',  f'{APP_ID}&{n}&{ts}'),
    ('appid&ts&nonce',  f'{APP_ID}&{ts}&{n}'),
    ('nonce&appid&ts',  f'{n}&{APP_ID}&{ts}'),
]:
    sign = hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    auth = f'SHA256 Credential={APP_ID}&Timestamp={ts}&Nonce={n}&Signature={sign}'
    chk(f'& hdr | {order}', auth, ts, n)

print()
print('=== Sem nonce na mensagem ===')
for msg, label in [
    (APP_ID+ts,      'appid+ts'),
    (ts+APP_ID,      'ts+appid'),
    (APP_ID+ts+n,    'appid+ts+n normal hdr'),
]:
    sign = hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    auth = f'SHA256 Credential={APP_ID}, Timestamp={ts}, Nonce={n}, Signature={sign}'
    chk(label, auth, ts, n)

print()
print('=== Timestamp em milissegundos ===')
for msg, label in [
    (APP_ID+n+tsms,  'appid+nonce+tsms'),
    (APP_ID+tsms+n,  'appid+tsms+nonce'),
]:
    sign = hmac.new(SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    auth = f'SHA256 Credential={APP_ID}, Timestamp={tsms}, Nonce={n}, Signature={sign}'
    chk(f'ms | {label}', auth, tsms, n)

print()
print('=== HMAC-SHA512 ===')
msg = APP_ID+n+ts
sign = hmac.new(SECRET.encode(), msg.encode(), hashlib.sha512).hexdigest()
auth = f'SHA256 Credential={APP_ID}, Timestamp={ts}, Nonce={n}, Signature={sign}'
chk('HMAC-SHA512', auth, ts, n)

print()
print('=== SHA256 da key antes de usar ===')
derived_key = hashlib.sha256(SECRET.encode()).digest()
sign = hmac.new(derived_key, (APP_ID+n+ts).encode(), hashlib.sha256).hexdigest()
auth = f'SHA256 Credential={APP_ID}, Timestamp={ts}, Nonce={n}, Signature={sign}'
chk('derived key SHA256', auth, ts, n)
