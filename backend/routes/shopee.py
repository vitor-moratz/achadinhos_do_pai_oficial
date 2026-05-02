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
_PARTNER_ID  = os.getenv("SHOPEE_PARTNER_ID", "").strip()
_PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY", "").strip()
_OPEN_API_BASE = "https://partner.shopeemobile.com"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://shopee.com.br/",
    "Cache-Control": "no-cache",
}

_API_HEADERS = {}  # não utilizado — mantido para compatibilidade

# ── Mapeamento Shopee categorias → nosso sistema ────────────

_SEGMENT_KEYWORDS = {
    "pet-shop":   ["animais domésticos", "pet", "cachorro", "gato", "aquário",
                   "pássaro", "ração", "petisco"],
    "ferramentas":["ferramentas", "construção", "fixadores", "solda", "medição",
                   "chave", "furadeira", "parafuso", "oficina"],
    "automotivo": ["automotivo", "automóveis", "veículos", "moto", "carro",
                   "pneu", "óleo"],
    "casa":       ["casa", "lar", "cozinha", "organização doméstica", "decoração",
                   "jardim", "limpeza doméstica", "móveis", "iluminação",
                   "utilidades domésticas"],
    "eletronicos":["eletrônicos", "computadores", "celulares", "smartphones",
                   "tablets", "câmeras", "áudio e vídeo", "tv", "wearables",
                   "acessórios para celular"],
    "games":      ["games", "videogame", "console", "drone", "impressão 3d",
                   "hobbies", "colecionáveis"],
    # moda ANTES de esporte — calçados/roupas devem bater aqui primeiro
    "moda":       ["moda", "roupas", "calçados", "calçado", "tênis", "sapato",
                   "sandália", "sandalia", "chinelo", "bota", "scarpin",
                   "relógios", "óculos", "bolsas", "acessórios de moda",
                   "masculino", "feminino", "vestuário"],
    "esporte":    ["esportes", "lazer", "fitness", "academia", "camping",
                   "pesca", "ciclismo", "futebol", "corrida"],
}

_CATEGORY_KEYWORDS = {
    "pet-shop": {
        "Comida":          ["ração", "alimento", "comida", "seca", "úmida"],
        "Petiscos":        ["petisco", "snack", "bifinho", "osso"],
        "Brinquedos":      ["brinquedo", "mordedor", "bolinha", "arranhador"],
        "Higiene":         ["higiene", "banho", "tosa", "shampoo", "escova",
                            "dental", "tapete higiênico"],
        "Cama e Descanso": ["cama", "descanso", "canil", "manta", "almofada"],
        "Transporte":      ["transporte", "caixa de transporte", "bolsa", "mochila"],
    },
    "ferramentas": {
        "Manuais":       ["chave", "alicate", "martelo", "manual", "serrote"],
        "Elétricas":     ["furadeira", "parafusadeira", "elétrica", "lixadeira",
                          "esmerilhadeira"],
        "Medição":       ["trena", "nível", "medição", "paquímetro", "régua"],
        "Fixadores":     ["parafuso", "prego", "bucha", "fixador", "rebite"],
        "Organização":   ["caixa", "organizador", "estojo", "bancada"],
        "Corte e Solda": ["serra", "solda", "corte", "disco", "estilete"],
    },
    "automotivo": {
        "Limpeza":     ["limpeza", "lavagem", "polimento", "cera"],
        "Acessórios":  ["acessório", "suporte", "tapete", "capa"],
        "Eletrônicos": ["gps", "câmera", "sensor", "eletrônico"],
        "Iluminação":  ["lâmpada", "led", "farol", "iluminação"],
        "Som":         ["som", "auto falante", "rádio", "amplificador"],
        "Manutenção":  ["óleo", "filtro", "correia", "manutenção"],
    },
    "casa": {
        "Cozinha":     ["cozinha", "panela", "frigideira", "utensílio"],
        "Churrasco":   ["churrasco", "grelha", "churrasqueira", "espeto"],
        "Organização": ["organização", "caixa", "prateleira", "armário"],
        "Limpeza":     ["limpeza", "vassoura", "rodo", "pano"],
        "Jardim":      ["jardim", "planta", "vaso", "regador"],
        "Iluminação":  ["lâmpada", "luminária", "iluminação"],
        "Decoração":   ["decoração", "quadro", "enfeite", "almofada"],
    },
    "eletronicos": {
        "Smartphones":          ["celular", "smartphone", "iphone", "android"],
        "Áudio":                ["fone", "caixa de som", "headphone", "áudio"],
        "Computadores":         ["notebook", "computador", "monitor", "teclado"],
        "Câmeras":              ["câmera", "fotografia", "lente", "tripé"],
        "Cabos e Carregadores": ["cabo", "carregador", "adaptador", "hub"],
        "Smart Home":           ["smart home", "alexa", "automação", "lâmpada inteligente"],
    },
    "esporte": {
        "Fitness":  ["fitness", "academia", "haltere", "musculação"],
        "Camping":  ["camping", "barraca", "mochila", "lanterna"],
        "Pesca":    ["pesca", "anzol", "vara", "isca"],
        "Ciclismo": ["bicicleta", "ciclismo", "capacete"],
        "Futebol":  ["futebol", "chuteira", "bola"],
    },
    "games": {
        "Controles":    ["controle", "joystick", "gamepad"],
        "Impressão 3D": ["impressão 3d", "filamento", "impressora 3d"],
        "Drones":       ["drone", "fpv", "helicóptero"],
        "Board Games":  ["board game", "jogo de tabuleiro", "card game"],
    },
    "moda": {
        "Camisetas": ["camiseta", "camisa", "polo", "blusa", "regata", "moletom"],
        "Calçados":  ["tênis", "sapato", "sandália", "sandalia", "chinelo",
                      "bota", "calçado", "scarpin", "mocassim", "sapatilha"],
        "Relógios":  ["relógio", "smartwatch"],
        "Óculos":    ["óculos", "lente"],
        "Bolsas":    ["bolsa", "mochila", "carteira", "nécessaire"],
        "Acessórios":["cinto", "colar", "brinco", "pulseira", "anel"],
    },
}


# ── Mapeamento categorias Shopee → nosso sistema ─────────────

def _map_to_segment_category(shopee_categories: list) -> tuple[str | None, str | None]:
    """
    Recebe lista de strings ou dicts (breadcrumb da Shopee).
    Retorna (segment_slug, category_name) do nosso sistema.
    """
    # Normaliza para lista de strings
    names = []
    for c in shopee_categories:
        if isinstance(c, str):
            names.append(c)
        elif isinstance(c, dict):
            names.append(c.get("display_name") or c.get("name") or "")
    cat_text = " ".join(names).lower()

    # Detecta segmento
    segment = None
    for seg_slug, keywords in _SEGMENT_KEYWORDS.items():
        if any(kw in cat_text for kw in keywords):
            segment = seg_slug
            break

    # Detecta categoria dentro do segmento
    category = None
    if segment and segment in _CATEGORY_KEYWORDS:
        for cat_name, keywords in _CATEGORY_KEYWORDS[segment].items():
            if any(kw in cat_text for kw in keywords):
                category = cat_name
                break

    return segment, category


# ── Scraping SSR via facebookexternalhit ─────────────────────

_UA_BOT = (
    "facebookexternalhit/1.1 "
    "(+http://www.facebook.com/externalhit_uatext.php)"
)

def _fetch_via_ssr(
    session: requests.Session, shop_id: int, item_id: int
) -> dict | None:
    """
    Busca dados do produto usando User-Agent facebookexternalhit.
    A Shopee serve SSR (og: meta + JSON-LD breadcrumb) para bots sociais.
    Funciona com a URL canônica /product/{shop_id}/{item_id}.
    """
    try:
        url = f"https://shopee.com.br/product/{shop_id}/{item_id}"
        resp = session.get(url, headers={
            "User-Agent": _UA_BOT,
            "Accept": "text/html,*/*",
            "Accept-Language": "pt-BR,pt;q=0.9",
        }, timeout=15, allow_redirects=True)

        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "lxml")

        def og(prop):
            tag = soup.find("meta", property=f"og:{prop}")
            return tag.get("content", "").strip() if tag else None

        title       = og("title")
        image_url   = og("image")
        description = og("description")

        # Limpa sufixo "| Shopee Brasil" do título
        if title:
            title = re.sub(r'\s*\|\s*Shopee.*$', '', title).strip()

        # Imagem: busca qualquer arquivo susercontent (prefixos br-, sg-, th-, etc.)
        # Prefere .webp pois tende a ser a imagem real do produto.
        real_imgs = re.findall(
            r'https://[a-z.-]*susercontent\.com/file/([a-z]{2}-[a-zA-Z0-9._-]+)',
            resp.text,
        )
        if real_imgs:
            # 1ª escolha: webp de qualquer origem
            webp = next((f for f in real_imgs if f.endswith(".webp")), None)
            # 2ª escolha: qualquer imagem que não seja banner promo (evita "promo-dim")
            non_promo = next(
                (f for f in real_imgs if "promo" not in f and "banner" not in f),
                None,
            )
            best = webp or non_promo or real_imgs[0]
            image_url = f"https://down-br.img.susercontent.com/file/{best}"

        # Preço: tenta extrair do HTML (R$XX,XX ou R$X.XXX,XX)
        price_brl = None
        pm = re.search(r'R\$\s*([\d]+(?:\.\d{3})*,\d{2})', soup.get_text())
        if pm:
            raw_p = pm.group(1).replace('.', '').replace(',', '.')
            try:
                float(raw_p)
                price_brl = pm.group(1)  # mantém formato "11,59"
            except ValueError:
                pass

        # Categorias via BreadcrumbList JSON-LD
        breadcrumb_names = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if data.get("@type") == "BreadcrumbList":
                    for item in data.get("itemListElement", []):
                        name = item.get("item", {}).get("name") or item.get("name")
                        if name and name.lower() != "shopee":
                            breadcrumb_names.append(name)
                    break
            except Exception:
                continue

        segment, category = _map_to_segment_category(breadcrumb_names)

        if not title and not image_url:
            return None

        return {
            "title":       title,
            "image_url":   image_url,
            "description": description,
            "promo_price": price_brl,
            "segment":     segment,
            "category":    category,
        }
    except Exception:
        return None


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
    Preserva query params (contêm rastreamento de afiliado).
    """
    try:
        # Passo 1: tenta sem follow redirects (pega Location do 301)
        resp = session.get(url, headers=_HEADERS, timeout=10, allow_redirects=False)
        if resp.is_redirect:
            location = resp.headers.get("Location", "")
            if "shopee.com.br" in location:
                return location   # mantém query params

        # Passo 2: segue redirects e usa a URL final
        resp = session.get(url, headers=_HEADERS, timeout=10, allow_redirects=True)
        if "shopee.com.br" in resp.url:
            return resp.url      # mantém query params

        # Passo 3: fallback — extrai httpUrl do CONFIG JS (links mais antigos)
        m = re.search(
            r'httpUrl\s*:\s*"(https:\\\/\\\/shopee\.com\.br\\\/[^"]+)"',
            resp.text,
        )
        if m:
            raw = m.group(1).replace("\\/", "/").replace("\\u0026", "&")
            return raw
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

        shop_id, item_id = _extract_ids_from_url(product_url)

        # ── Passo 2: SSR via facebookexternalhit (sempre disponível) ──
        if shop_id and item_id:
            result = _fetch_via_ssr(session, shop_id, item_id)
            if result and result.get("title"):
                result["final_url"] = product_url
                return jsonify(result)

        # ── Passo 3: Open Platform API (se credenciais existem) ─
        if shop_id and item_id:
            api_result = _fetch_via_open_api(shop_id, item_id)
            if api_result and api_result.get("title"):
                api_result["final_url"] = product_url
                api_result.setdefault("segment", None)
                api_result.setdefault("category", None)
                return jsonify(api_result)

        # ── Passo 4: fallback — scraping da página ────────────
        resp      = session.get(product_url, headers=_HEADERS, timeout=15, allow_redirects=True)
        final_url = resp.url
        soup      = BeautifulSoup(resp.text, "lxml")

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
                        if not title:
                            title = item.get("name")
                        if not image:
                            imgs  = item.get("image")
                            image = imgs[0] if isinstance(imgs, list) else imgs
                        if not description:
                            description = item.get("description")
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
            "segment":     None,
            "category":    None,
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Tempo esgotado. Preencha manualmente."}), 504
    except Exception:
        return jsonify({"error": "Não foi possível buscar. Preencha manualmente."}), 502
