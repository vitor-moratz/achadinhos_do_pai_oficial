"""
Testa queries reais com os campos corretos.
"""
import hashlib, json, time, requests

APP_ID = "18362881015"
SECRET = "PDJ2WIOKXYGN7YXXP3SYLADQ4U735M2A"
BASE   = "https://open-api.affiliate.shopee.com.br"


def call(label, q):
    ts  = int(time.time())
    payload = {"query": q}
    sig = hashlib.sha256(f"{APP_ID}{ts}{json.dumps(payload)}{SECRET}".encode()).hexdigest()
    hdr = {
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={APP_ID}, Signature={sig}, Timestamp={ts}",
    }
    r = requests.post(f"{BASE}/graphql", headers=hdr, json=payload, timeout=15)
    print(f"\n=== {label} ===")
    try:
        d = r.json()
        print(json.dumps(d, ensure_ascii=False, indent=2)[:2000])
    except Exception:
        print(r.text[:500])


# ProductOfferV2 - todos os campos
call("ProductOfferV2 ALL fields",
     '{ __type(name: "ProductOfferV2") { fields { name } } }')

# ItemFeedListConnection - estrutura
call("ItemFeedListConnection fields",
     '{ __type(name: "ItemFeedListConnection") { fields { name type { name kind ofType { name } } } } }')

# ItemFeed fields
call("ItemFeed fields",
     '{ __type(name: "ItemFeed") { fields { name type { name kind ofType { name } } } } }')

# productOfferV2 com campos corretos
call("productOfferV2 REAL",
     """
     query {
         productOfferV2(limit: 5, page: 1) {
             nodes {
                 itemId
                 commissionRate
                 productName
                 productCatIds
                 priceMin
                 priceMax
                 imageUrl
                 productLink
                 offerLink
                 shopId
             }
             pageInfo {
                 page
                 limit
                 hasNextPage
             }
         }
     }
     """)

# shopeeOfferV2 - curated list
call("shopeeOfferV2 REAL",
     """
     query {
         shopeeOfferV2(limit: 5, page: 1) {
             nodes {
                 offerName
                 imageUrl
                 offerLink
                 originalLink
                 commissionRate
                 categoryId
             }
             pageInfo {
                 page
                 limit
                 hasNextPage
             }
         }
     }
     """)
