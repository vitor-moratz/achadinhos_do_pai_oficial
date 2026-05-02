import urllib.request, json

url = 'http://localhost:5000/api/auth/users/000000000000000000000000'
req = urllib.request.Request(url, data=json.dumps({'role':'admin'}).encode(), method='PATCH')
req.add_header('Content-Type', 'application/json')
try:
    r = urllib.request.urlopen(req)
    print('HTTP', r.status)
except urllib.error.HTTPError as e:
    print('HTTP', e.code, e.read().decode())
except Exception as ex:
    print('ERR', ex)
