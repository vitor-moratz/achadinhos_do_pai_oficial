import requests, re, json
from bs4 import BeautifulSoup

session = requests.Session()
shop_id = 1179428231
item_id = 23294839659

HEADERS = {"User-Agent": "facebookexternalhit/1.1", "Accept-Language": "pt-BR,pt;q=0.9"}
resp = session.get(f"https://shopee.com.br/product/{shop_id}/{item_id}", headers=HEADERS, timeout=15)
soup = BeautifulSoup(resp.text, "lxml")

# Metas de preço
for tag in soup.find_all("meta"):
    name = tag.get("property","") + tag.get("name","")
    content = tag.get("content","")
    if "price" in name.lower() or "amount" in name.lower():
        print(f"meta {name}: {content}")

# JSON-LD completo
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string or "")
        print("JSON-LD type:", data.get("@type"), "| keys:", list(data.keys()))
        if "offer" in str(data.get("@type","")).lower() or "product" in str(data.get("@type","")).lower():
            print(json.dumps(data, ensure_ascii=False, indent=2)[:800])
    except: pass




