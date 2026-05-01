"""
get_shop_detail v4 funciona — testa v4/item/get com mesmos parâmetros exatos
"""
import requests
import re
import json

s = requests.Session()

shop_id = 1179428231
item_id = 23294839659

# Exatamente os mesmos headers que get_shop_detail funcionou
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Accept': 'application/json',
    'Accept-Language': 'pt-BR',
    'x-api-source': 'rn',
    # SEM Referer desta vez
}

tests = [
    f'https://shopee.com.br/api/v4/shop/get_item_list?shopid={shop_id}&sortby=pop&limit=10&offset=0&item_card=1&requires_login=0',
    f'https://shopee.com.br/api/v4/search/search_items?by=relevancy&keyword=produto&limit=10&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2',
]

for url in tests:
    r = s.get(url, headers=headers, timeout=10)
    print(f'{r.status_code} {url[-65:]}')
    if r.status_code == 200:
        try:
            d = r.json()
            items = d.get('data', {}).get('item', []) or d.get('items', [])
            if items:
                first = items[0]
                print(f'  first item name: {first.get("name", "")[:80]}')
                print(f'  first item images: {(first.get("images") or [])[:1]}')
        except:
            print(f'  raw: {r.text[:200]}')
