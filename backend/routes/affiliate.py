"""
Rotas da API de Afiliados da Shopee.

Autenticação: SHA256(app_id + timestamp + json_payload + secret)
Endpoint:     POST https://open-api.affiliate.shopee.com.br/graphql
Header:       SHA256 Credential={app_id}, Signature={sig}, Timestamp={ts}
"""
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from database import get_db
from models.product import make_product
from routes.shopee import _map_to_segment_category

affiliate_bp = Blueprint("affiliate", __name__, url_prefix="/api/affiliate")

_AFFILIATE_APP_ID = os.getenv("SHOPEE_AFFILIATE_APP_ID", "").strip()
_AFFILIATE_SECRET = os.getenv("SHOPEE_AFFILIATE_SECRET", "").strip()
_GRAPHQL_URL      = "https://open-api.affiliate.shopee.com.br/graphql"

# ── Shopee category ID → nosso segment slug ─────────────────
# IDs de nível 1 da árvore de categorias Shopee BR
_SHOPEE_CAT_SEGMENT = {
    # Fashion & Moda
    100009: "moda",   # Fashion Accessories
    100011: "moda",   # Men Clothes
    100012: "moda",   # Men Shoes
    100013: "moda",   # Women Clothes
    100014: "moda",   # Women Shoes
    100015: "moda",   # Bags & Wallets
    100016: "moda",   # Watches
    100017: "moda",   # Jewelry & Accessories

    # Eletrônicos
    100002: "eletronicos",  # Mobiles & Gadgets
    100006: "eletronicos",  # Computers & Peripherals
    100010: "eletronicos",  # Home Appliances  (some overlap)

    # Casa
    100003: "casa",  # Home & Living
    100004: "casa",  # Kitchen
    100010: "casa",  # Home Appliances

    # Esporte & Lazer
    100005: "esporte",  # Sports & Outdoors

    # Saúde
    100001: "casa",  # Health

    # Automotivo
    100020: "automotivo",  # Automotive
    102187: "automotivo",  # Automotivo BR (usado internamente)

    # Games & Hobbies
    100007: "games",  # Gaming & Consoles
    100008: "games",  # Toys & Collectibles

    # Pet
    100018: "pet-shop",  # Pet & Pet Care
}


# ── Helper de autenticação ───────────────────────────────────

def _graphql(payload: dict) -> dict:
    """Envia uma query GraphQL autenticada para a API de afiliados."""
    if not _AFFILIATE_APP_ID or not _AFFILIATE_SECRET:
        return {"errors": [{"message": "Credenciais SHOPEE_AFFILIATE não configuradas."}]}

    ts  = int(time.time())
    raw = f"{_AFFILIATE_APP_ID}{ts}{json.dumps(payload)}{_AFFILIATE_SECRET}"
    sig = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "Authorization": (
            f"SHA256 Credential={_AFFILIATE_APP_ID}, "
            f"Signature={sig}, Timestamp={ts}"
        ),
    }

    try:
        r = requests.post(_GRAPHQL_URL, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        return {"errors": [{"message": "Timeout ao conectar com a Shopee."}]}
    except Exception as exc:
        return {"errors": [{"message": str(exc)}]}


def _detect_segment_category(product_name: str, cat_ids: list) -> tuple[str | None, str | None]:
    """
    Detecta segmento e categoria do produto.
    Primeiro tenta pelos IDs de categoria Shopee, depois por palavras-chave.
    """
    # Tentativa 1 – IDs de categoria
    for cid in cat_ids:
        seg = _SHOPEE_CAT_SEGMENT.get(int(cid))
        if seg:
            # Detecta categoria via keyword no nome do produto
            _, cat = _map_to_segment_category([product_name])
            return seg, cat

    # Tentativa 2 – keywords no nome do produto
    segment, category = _map_to_segment_category([product_name])
    return segment, category


# ── Endpoint: contar total de páginas ────────────────────────

@affiliate_bp.route("/galeria/total-paginas", methods=["GET"])
@jwt_required()
def contar_paginas():
    """
    Percorre todas as páginas buscando apenas pageInfo (sem nodes) para
    descobrir o total de páginas com os filtros ativos.
    Query params: keyword (opcional), cat_id (opcional)
    Usa limit=50 para minimizar o número de requests necessários.
    """
    keyword = request.args.get("keyword", "").strip()
    cat_id  = request.args.get("cat_id", "").strip()
    limit   = 50
    page    = 1
    MAX_PAGES = 200

    while page <= MAX_PAGES:
        args_parts = [f"limit: {limit}", f"page: {page}"]
        if keyword:
            safe_keyword = keyword.replace('"', '\\"')
            args_parts.append(f'keyword: "{safe_keyword}"')
        if cat_id:
            args_parts.append(f"productCatId: {cat_id}")

        gql_query = f"""
        query {{
            productOfferV2({", ".join(args_parts)}) {{
                pageInfo {{ page limit hasNextPage }}
            }}
        }}
        """
        result = _graphql({"query": gql_query})

        if "errors" in result and "data" not in result:
            return jsonify({"error": result["errors"][0].get("message", "?")}), 502

        pg_info  = result.get("data", {}).get("productOfferV2", {}).get("pageInfo", {})
        has_next = pg_info.get("hasNextPage", False)

        if not has_next:
            # Última página encontrada — converte para base 20 (usado no frontend)
            # limit=50 → total_items ≈ page*50; total_pages com limit=20
            total_items  = (page - 1) * limit + pg_info.get("limit", limit)
            total_pages_20 = -(-total_items // 20)  # ceil division
            return jsonify({
                "total_pages":    total_pages_20,
                "total_items_est": total_items,
                "pages_counted":  page,
            })
        page += 1

    return jsonify({"total_pages": f"{MAX_PAGES}+", "total_items_est": None, "pages_counted": MAX_PAGES})


# ── Endpoint: listar galeria ─────────────────────────────────

@affiliate_bp.route("/galeria", methods=["GET"])
@jwt_required()
def listar_galeria():
    """
    Retorna produtos da galeria de afiliados da Shopee.
    Query params: page (default 1), limit (default 20), keyword (opcional), cat_id (opcional)
    """
    page    = max(1, int(request.args.get("page", 1)))
    limit   = min(50, max(1, int(request.args.get("limit", 20))))
    keyword = request.args.get("keyword", "").strip()
    cat_id  = request.args.get("cat_id", "").strip()

    # Constrói args da query
    args_parts = [f"limit: {limit}", f"page: {page}"]
    if keyword:
        # Escapa aspas no keyword para segurança
        safe_keyword = keyword.replace('"', '\\"')
        args_parts.append(f'keyword: "{safe_keyword}"')
    if cat_id:
        args_parts.append(f"productCatId: {cat_id}")
    args_str = ", ".join(args_parts)

    gql_query = f"""
    query {{
        productOfferV2({args_str}) {{
            nodes {{
                itemId
                shopId
                productName
                imageUrl
                offerLink
                productLink
                priceMin
                priceMax
                commissionRate
                ratingStar
                productCatIds
                shopName
            }}
            pageInfo {{
                page
                limit
                hasNextPage
            }}
        }}
    }}
    """

    result = _graphql({"query": gql_query})

    if "errors" in result and "data" not in result:
        return jsonify({"error": result["errors"][0].get("message", "Erro desconhecido")}), 502

    data    = result.get("data", {}).get("productOfferV2", {})
    nodes   = data.get("nodes", [])
    pg_info = data.get("pageInfo", {})

    # Enriquece com segment/category detectados e flag de já importado
    db = get_db()
    for node in nodes:
        offer_link = node.get("offerLink", "")
        item_id    = node.get("itemId")
        exists     = db.products.find_one(
            {"$or": [{"affiliate_link": offer_link}, {"shopee_item_id": item_id}]},
            {"_id": 1}
        ) if offer_link or item_id else None
        node["already_imported"] = exists is not None

        seg, cat = _detect_segment_category(
            node.get("productName", ""),
            node.get("productCatIds", [])
        )
        node["detected_segment"] = seg
        node["detected_category"] = cat

    return jsonify({
        "products": nodes,
        "page":     pg_info.get("page", page),
        "limit":    pg_info.get("limit", limit),
        "has_next": pg_info.get("hasNextPage", False),
    })


# ── Endpoint: importar produtos ──────────────────────────────

@affiliate_bp.route("/importar", methods=["POST"])
@jwt_required()
def importar_produtos():
    """
    Importa um ou mais produtos da galeria para o banco de dados.
    Body: { products: [ { itemId, productName, imageUrl, offerLink, priceMin, priceMax,
                          productCatIds, shopId, detected_segment, detected_category } ] }
    """
    body     = request.get_json(silent=True) or {}
    produtos = body.get("products", [])

    if not produtos:
        return jsonify({"error": "Lista de produtos vazia."}), 400

    db       = get_db()
    imported = 0
    skipped  = 0
    erros    = []

    for p in produtos:
        try:
            offer_link = p.get("offerLink", "")
            item_id    = p.get("itemId")

            # Evita duplicatas
            if offer_link and db.products.find_one({"affiliate_link": offer_link}):
                skipped += 1
                continue
            if item_id and db.products.find_one({"shopee_item_id": item_id}):
                skipped += 1
                continue

            segment  = p.get("detected_segment") or p.get("segment")
            category = p.get("detected_category") or p.get("category")

            # Se segment/category não detectados, tenta pelo nome
            if not segment:
                segment, category = _detect_segment_category(
                    p.get("productName", ""),
                    p.get("productCatIds", [])
                )

            price_min = p.get("priceMin")
            price_max = p.get("priceMax")

            product_doc = make_product({
                "title":          p.get("productName", "Produto Shopee"),
                "description":    None,
                "price_from":     float(price_min) if price_min else None,
                "price_to":       float(price_max) if price_max and price_max != price_min else None,
                "image_url":      p.get("imageUrl"),
                "affiliate_link": offer_link or p.get("productLink", ""),
                "segment":        segment,
                "category":       category,
                "tag":            None,
            })

            # Armazena o item_id da Shopee para deduplicação futura
            product_doc["shopee_item_id"] = item_id
            product_doc["shopee_shop_id"] = p.get("shopId")

            db.products.insert_one(product_doc)
            imported += 1

        except Exception as exc:
            erros.append(str(exc))

    return jsonify({
        "imported": imported,
        "skipped":  skipped,
        "errors":   erros[:5],
    })


# ── Endpoint: importar TUDO (todas as páginas) ───────────────

def _build_galeria_gql(limit: int, page: int, keyword: str, cat_id: str) -> str:
    args_parts = [f"limit: {limit}", f"page: {page}"]
    if keyword:
        safe_keyword = keyword.replace('"', '\\"')
        args_parts.append(f'keyword: "{safe_keyword}"')
    if cat_id:
        args_parts.append(f"productCatId: {cat_id}")
    return f"""
    query {{
        productOfferV2({", ".join(args_parts)}) {{
            nodes {{
                itemId shopId productName imageUrl offerLink productLink
                priceMin priceMax commissionRate ratingStar productCatIds shopName
            }}
            pageInfo {{ page limit hasNextPage }}
        }}
    }}
    """


@affiliate_bp.route("/importar-tudo", methods=["POST"])
@jwt_required()
def importar_tudo():
    """
    Busca TODAS as páginas da galeria com os filtros informados e importa tudo.
    Body: { keyword?: string, cat_id?: string }
    Retorna: { imported, skipped, total_fetched, pages_fetched, errors[] }
    """
    body    = request.get_json(silent=True) or {}
    keyword = body.get("keyword", "").strip()
    cat_id  = body.get("cat_id", "").strip()
    limit   = 50  # máximo permitido pela API

    db = get_db()
    imported = 0
    skipped  = 0
    erros    = []
    pages_fetched = 0
    page = 1
    MAX_PAGES = 200  # segurança

    while page <= MAX_PAGES:
        result = _graphql({"query": _build_galeria_gql(limit, page, keyword, cat_id)})

        if "errors" in result and "data" not in result:
            erros.append(f"p{page}: {result['errors'][0].get('message', '?')}")
            break

        offer_data = result.get("data", {}).get("productOfferV2", {})
        nodes      = offer_data.get("nodes", [])
        has_next   = offer_data.get("pageInfo", {}).get("hasNextPage", False)
        pages_fetched += 1

        for p in nodes:
            try:
                offer_link = p.get("offerLink", "")
                item_id    = p.get("itemId")

                if offer_link and db.products.find_one({"affiliate_link": offer_link}):
                    skipped += 1
                    continue
                if item_id and db.products.find_one({"shopee_item_id": item_id}):
                    skipped += 1
                    continue

                segment, category = _detect_segment_category(
                    p.get("productName", ""),
                    p.get("productCatIds", [])
                )
                price_min = p.get("priceMin")
                price_max = p.get("priceMax")

                product_doc = make_product({
                    "title":          p.get("productName", "Produto Shopee"),
                    "description":    None,
                    "price_from":     float(price_min) if price_min else None,
                    "price_to":       float(price_max) if price_max and price_max != price_min else None,
                    "image_url":      p.get("imageUrl"),
                    "affiliate_link": offer_link or p.get("productLink", ""),
                    "segment":        segment,
                    "category":       category,
                    "tag":            None,
                })
                product_doc["shopee_item_id"] = item_id
                product_doc["shopee_shop_id"] = p.get("shopId")

                db.products.insert_one(product_doc)
                imported += 1
            except Exception as exc:
                erros.append(str(exc))

        if not has_next:
            break
        page += 1

    return jsonify({
        "imported":      imported,
        "skipped":       skipped,
        "total_fetched": imported + skipped,
        "pages_fetched": pages_fetched,
        "errors":        erros[:10],
    })


# ── Endpoint: gerar link afiliado ────────────────────────────

@affiliate_bp.route("/link", methods=["GET"])
@jwt_required()
def gerar_link():
    """
    Gera um link afiliado curto para uma URL da Shopee.
    Query param: url
    """
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "Parâmetro 'url' obrigatório."}), 400

    payload = {
        "query": f"""
        mutation {{
            generateShortLink(input: {{
                originUrl: "{url}",
                subIds: []
            }}) {{
                shortLink
            }}
        }}
        """
    }

    result = _graphql(payload)

    if "errors" in result and "data" not in result:
        return jsonify({"error": result["errors"][0].get("message", "Erro")}), 502

    short_link = (
        result.get("data", {})
        .get("generateShortLink", {})
        .get("shortLink")
    )

    if not short_link:
        return jsonify({"error": "Não foi possível gerar o link."}), 502

    return jsonify({"shortLink": short_link})
