from flask import Blueprint, request, jsonify
import requests
import json
import re
import hmac
import hashlib
import time
import os
from bs4 import BeautifulSoup

shopee_bp = Blueprint("shopee", __name__, url_prefix="/api/shopee")

# ── Shopee Open Platform credentials (opcional) ─────────────
# Preencha .env com SHOPEE_PARTNER_ID e SHOPEE_PARTNER_KEY
# para ativar a busca via API oficial (mais confiável).
# Sem as credenciais, o sistema usa scraping como fallback.
_PARTNER_ID  = os.getenv("SHOPEE_PARTNER_ID", "").strip()
_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY", "").strip()
_OPEN_API_BASE = "https://partner.shopeemobile.com"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.6367.82 Mobile Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://shopee.com.br/",
    "Cache-Control": "no-cache",
}


# ── Shopee Open API helpers ──────────────────────────────────

def _open_api_sign(path: str, timestamp: int) -> str:
    """Gera assinatura HMAC-SHA256 para a Shopee Open Platform API."""
    base_string = f"{_PARTNER_ID}{path}{timestamp}"
    return hmac.new(
        _PARTNER_KEY.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _fetch_via_open_api(shop_id: int, item_id: int) -> dict | None:
    """
    Busca dados do produto pela Shopee Open Platform API.
    Retorna dict com title/image_url/description/promo_price ou None em falha.
    Docs: https://open.shopee.com/documents/v2/v2.product.get_item_base_info
    """
    if not _PARTNER_ID or not _PARTNER_KEY:
        return None

    path = "/api/v2/product/get_item_base_info"
    ts   = int(time.time())
    sign = _open_api_sign(path, ts)

    params = {
        "partner_id":   _PARTNER_ID,
        "timestamp":    ts,
        "sign":         sign,
        "shop_id":      shop_id,
        "item_id_list": item_id,
        # access_token não é necessário para dados públicos de produto
    }

    try:
        r = requests.get(
            _OPEN_API_BASE + path,
            params=params,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()

        # Estrutura de resposta: data.response.item_list[0]
        response  = data.get("response") or {}
        item_list = response.get("item_list") or []
        if not item_list:
            return None

        item = item_list[0]

        # Preço: a API retorna em centavos × 100000 (ex: 1990000 = R$ 19,90)
        price_info = item.get("price_info") or [{}]
        raw_price  = price_info[0].get("current_price") or price_info[0].get("original_price")
        price_brl  = f"{raw_price / 100000:.2f}".replace(".", ",") if raw_price else None

        # Imagem principal
        images   = item.get("image") or {}
        img_list = images.get("image_url_list") or []
        image    = img_list[0] if img_list else None

        return {
            "title":       item.get("item_name"),
            "image_url":   image,
            "description": item.get("description"),
            "promo_price": price_brl,
        }
    except Exception:
        return None


def _resolve_short_url(session: requests.Session, url: str) -> str:
    """
    Resolve link afiliado curto (s.shopee.com.br) para URL real do produto.
    Extrai httpUrl do objeto CONFIG embutido no JavaScript da página.
    Retorna a URL base do produto (sem query params de rastreamento).
    """
    try:
        resp = session.get(url, headers=_HEADERS, timeout=10, allow_redirects=True)
        m = re.search(
            r'httpUrl\s*:\s*"(https:\\\/\\\/shopee\.com\.br\\\/[^"]+)"',
            resp.text,
        )
        if m:
            raw = m.group(1).replace("\\/", "/").replace("\\u0026", "&")
            return raw.split("?")[0]
    except Exception:
        pass
    return url


def _extract_ids_from_url(url: str) -> tuple[int | None, int | None]:
    """
    Extrai (shop_id, item_id) de URLs Shopee nos formatos:
      - shopee.com.br/{user}/{shop_id}/{item_id}
      - shopee.com.br/{slug}-i.{shop_id}.{item_id}
      - shopee.com.br/product-i.{shop_id}.{item_id}
    """
    # Formato /{user}/{shop_id}/{item_id}
    m = re.search(r'shopee\.com\.br/[^/]+/(\d+)/(\d+)', url)
    if m:
        return int(m.group(1)), int(m.group(2))
    # Formato -i.{shop_id}.{item_id}
    m = re.search(r'-i\.(\d+)\.(\d+)', url)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


# ── Endpoint principal ───────────────────────────────────────

@shopee_bp.route("/fetch", methods=["GET"])
def fetch_product():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL obrigatória"}), 400
    if not url.startswith("http"):
        return jsonify({"error": "URL inválida"}), 400

    try:
        session = requests.Session()

        # ── Passo 1: resolve link afiliado curto ─────────────
        product_url = url
        if "s.shopee.com.br" in url:
            product_url = _resolve_short_url(session, url)

        # ── Passo 2: tenta API oficial (se credenciais existem) ─
        shop_id, item_id = _extract_ids_from_url(product_url)
        if shop_id and item_id:
            api_result = _fetch_via_open_api(shop_id, item_id)
            if api_result and api_result.get("title"):
                api_result["final_url"] = product_url
                return jsonify(api_result)

        # ── Passo 3: fallback — scraping da página ────────────
        resp       = session.get(product_url, headers=_HEADERS, timeout=15, allow_redirects=True)
        final_url  = resp.url
        soup       = BeautifulSoup(resp.text, "lxml")

        def og(prop):
            tag = (soup.find("meta", property=f"og:{prop}") or
                   soup.find("meta", attrs={"name": f"og:{prop}"}))
            return tag.get("content", "").strip() if tag else None

        title       = og("title")
        image       = og("image")
        description = og("description")
        price       = None

        if not title:
            t = soup.find("title")
            if t:
                raw   = t.get_text(strip=True)
                title = re.sub(r'\s*[\|\-–]\s*(Shopee|shopee).*$', '', raw).strip() or raw

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data  = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") in ("Product", "product"):
                        if not title:       title       = item.get("name")
                        if not image:
                            imgs  = item.get("image")
                            image = imgs[0] if isinstance(imgs, list) else imgs
                        if not description: description = item.get("description")
                        offers = item.get("offers") or item.get("Offers")
                        if offers and not price:
                            o     = offers[0] if isinstance(offers, list) else offers
                            price = str(o.get("price", ""))
                        break
            except Exception:
                continue

        if not price:
            pm = soup.find("meta", property="product:price:amount")
            if pm:
                price = pm.get("content", "")

        if not price:
            m = re.search(r'R\$\s*([\d.,]+)', resp.text)
            if m:
                raw_p = m.group(1).replace('.', '').replace(',', '.')
                try:
                    float(raw_p)
                    price = raw_p
                except ValueError:
                    pass

        return jsonify({
            "title":       title,
            "image_url":   image,
            "description": description,
            "promo_price": price or None,
            "final_url":   final_url,
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Tempo esgotado. Preencha manualmente."}), 504
    except Exception:
        return jsonify({"error": "Não foi possível buscar. Preencha manualmente."}), 502
