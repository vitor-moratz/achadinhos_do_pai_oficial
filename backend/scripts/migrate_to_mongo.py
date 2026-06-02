"""
Script de migração: substitui arquivos do backend para usar PyMongo.
Rodar uma única vez: python migrate_to_mongo.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

files = {}

# ── database.py ──────────────────────────────────────────────
files["database.py"] = """\
from pymongo import MongoClient
from pymongo.database import Database
import os

_client = None


def get_db() -> Database:
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/achadinhos")
        _client = MongoClient(uri)
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/achadinhos")
    db_name = uri.rsplit("/", 1)[-1].split("?")[0] if "/" in uri else "achadinhos"
    return _client[db_name]
"""

# ── models/product.py ────────────────────────────────────────
files["models/product.py"] = """\
from datetime import datetime, timezone


def make_product(data: dict, now=None) -> dict:
    now = now or datetime.now(timezone.utc)
    return {
        "title":          data["title"],
        "description":    data.get("description"),
        "original_price": data.get("original_price"),
        "promo_price":    data["promo_price"],
        "image_url":      data.get("image_url"),
        "affiliate_link": data["affiliate_link"],
        "category":       data.get("category"),
        "segment":        data.get("segment"),
        "tag":            data.get("tag"),
        "is_active":      True,
        "clicks":         0,
        "created_at":     now,
        "updated_at":     now,
    }


def product_to_dict(doc: dict) -> dict:
    return {
        "id":             str(doc["_id"]),
        "title":          doc.get("title"),
        "description":    doc.get("description"),
        "original_price": doc.get("original_price"),
        "promo_price":    doc.get("promo_price"),
        "image_url":      doc.get("image_url"),
        "affiliate_link": doc.get("affiliate_link"),
        "category":       doc.get("category"),
        "segment":        doc.get("segment"),
        "tag":            doc.get("tag"),
        "is_active":      doc.get("is_active", True),
        "clicks":         doc.get("clicks", 0),
        "created_at":     doc["created_at"].isoformat() if doc.get("created_at") else None,
        "updated_at":     doc["updated_at"].isoformat() if doc.get("updated_at") else None,
    }
"""

# ── models/category.py ───────────────────────────────────────
files["models/category.py"] = """\
import re
import unicodedata


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\\w\\s-]", "", text)
    text = re.sub(r"[-\\s]+", "-", text)
    return text.strip("-")


def category_to_dict(doc: dict) -> dict:
    return {
        "id":           str(doc["_id"]),
        "name":         doc.get("name"),
        "slug":         doc.get("slug"),
        "icon":         doc.get("icon", "📦"),
        "segment_slug": doc.get("segment_slug"),
        "is_custom":    doc.get("is_custom", False),
    }
"""

# ── models/segment.py ────────────────────────────────────────
files["models/segment.py"] = """\
def segment_to_dict(doc: dict) -> dict:
    return {
        "id":          str(doc["_id"]),
        "name":        doc.get("name"),
        "slug":        doc.get("slug"),
        "icon":        doc.get("icon", "📦"),
        "description": doc.get("description"),
    }
"""

# ── models/tag.py ────────────────────────────────────────────
files["models/tag.py"] = """\
def tag_to_dict(doc: dict) -> dict:
    return {
        "id":        str(doc["_id"]),
        "slug":      doc.get("slug"),
        "label":     doc.get("label"),
        "is_custom": doc.get("is_custom", False),
    }
"""

# ── models/__init__.py ───────────────────────────────────────
files["models/__init__.py"] = """\
from models.product  import product_to_dict, make_product
from models.category import category_to_dict, slugify
from models.segment  import segment_to_dict
from models.tag      import tag_to_dict
"""

# ── routes/products.py ───────────────────────────────────────
files["routes/products.py"] = """\
from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from database import get_db
from models.product  import make_product, product_to_dict

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


def _resolve_category_filter(slug_or_name: str):
    db = get_db()
    cat = db.categories.find_one({"slug": slug_or_name})
    if cat:
        return cat["name"], cat.get("segment_slug")
    cat = db.categories.find_one(
        {"name": {"$regex": f"^{re.escape(slug_or_name)}$", "$options": "i"}}
    )
    if cat:
        return cat["name"], cat.get("segment_slug")
    return slug_or_name, None


import re as _re

def _resolve_category_filter(slug_or_name: str):
    db = get_db()
    cat = db.categories.find_one({"slug": slug_or_name})
    if cat:
        return cat["name"], cat.get("segment_slug")
    cat = db.categories.find_one(
        {"name": {"$regex": f"^{_re.escape(slug_or_name)}$", "$options": "i"}}
    )
    if cat:
        return cat["name"], cat.get("segment_slug")
    return slug_or_name, None


@products_bp.route("/", methods=["GET"])
def list_products():
    db = get_db()
    category = request.args.get("category")
    segment  = request.args.get("segment")
    tag      = request.args.get("tag")
    search   = request.args.get("search")

    query = {"is_active": True}

    if category:
        cat_name, cat_seg = _resolve_category_filter(category)
        query["category"] = cat_name
        if cat_seg:
            query["segment"] = cat_seg
    if segment:
        query["segment"] = segment
    if tag:
        query["tag"] = tag
    if search:
        query["title"] = {"$regex": _re.escape(search), "$options": "i"}

    products = list(db.products.find(query).sort("created_at", -1))

    tag_slugs = {p["tag"] for p in products if p.get("tag")}
    tag_map   = {}
    if tag_slugs:
        tag_map = {t["slug"]: t["label"] for t in db.tags.find({"slug": {"$in": list(tag_slugs)}})}

    result = []
    for p in products:
        d = product_to_dict(p)
        d["tag_label"] = tag_map.get(p.get("tag"), p.get("tag")) if p.get("tag") else None
        result.append(d)

    return jsonify(result)


@products_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400
    product = db.products.find_one({"_id": oid})
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404
    return jsonify(product_to_dict(product))


@products_bp.route("/", methods=["POST"])
def create_product():
    db   = get_db()
    data = request.get_json()
    required = ["title", "promo_price", "affiliate_link"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing)}"}), 400

    doc    = make_product(data)
    result = db.products.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(product_to_dict(doc)), 201


@products_bp.route("/<product_id>", methods=["PUT"])
def update_product(product_id):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400

    data      = request.get_json()
    updatable = ["title", "description", "original_price", "promo_price",
                 "image_url", "affiliate_link", "category", "segment", "tag", "is_active"]
    updates   = {k: data[k] for k in updatable if k in data}
    updates["updated_at"] = datetime.now(timezone.utc)

    result = db.products.find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        return jsonify({"error": "Produto não encontrado"}), 404
    return jsonify(product_to_dict(result))


@products_bp.route("/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400
    result = db.products.delete_one({"_id": oid})
    if result.deleted_count == 0:
        return jsonify({"error": "Produto não encontrado"}), 404
    return jsonify({"message": "Produto removido com sucesso."})


@products_bp.route("/<product_id>/click", methods=["POST"])
def register_click(product_id):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400
    result = db.products.find_one_and_update(
        {"_id": oid},
        {"$inc": {"clicks": 1}},
        return_document=True,
    )
    if not result:
        return jsonify({"error": "Produto não encontrado"}), 404
    return jsonify({"affiliate_link": result["affiliate_link"]})


@products_bp.route("/categories", methods=["GET"])
def list_categories():
    db   = get_db()
    cats = db.products.distinct("category", {"is_active": True, "category": {"$ne": None}})
    return jsonify(cats)
"""

# ── routes/categories.py ─────────────────────────────────────
files["routes/categories.py"] = """\
from flask import Blueprint, request, jsonify
from database import get_db
from models.category import slugify, category_to_dict

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories_bp.route("/", methods=["GET"])
def list_categories():
    db      = get_db()
    segment = request.args.get("segment")
    query   = {"segment_slug": segment} if segment else {}
    cats    = list(db.categories.find(query).sort([("is_custom", 1), ("name", 1)]))
    return jsonify([category_to_dict(c) for c in cats])


@categories_bp.route("/", methods=["POST"])
def create_category():
    db   = get_db()
    data = request.get_json()
    name = (data.get("name") or "").strip()
    icon = (data.get("icon") or "📦").strip()
    segment_slug = (data.get("segment_slug") or "").strip() or None
    if not name:
        return jsonify({"error": "Nome obrigatório"}), 400

    slug = f"{segment_slug}-{slugify(name)}" if segment_slug else slugify(name)

    if db.categories.find_one({"$or": [{"name": name, "segment_slug": segment_slug}, {"slug": slug}]}):
        return jsonify({"error": "Categoria já existe"}), 409

    doc = {
        "name":         name,
        "slug":         slug,
        "icon":         icon,
        "segment_slug": segment_slug,
        "is_custom":    True,
    }
    result = db.categories.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(category_to_dict(doc)), 201
"""

# ── routes/segments.py ───────────────────────────────────────
files["routes/segments.py"] = """\
from flask import Blueprint, jsonify
from database import get_db
from models.segment  import segment_to_dict
from models.category import category_to_dict

segments_bp = Blueprint("segments", __name__, url_prefix="/api/segments")


@segments_bp.route("/", methods=["GET"])
def list_segments():
    db   = get_db()
    segs = list(db.segments.find())
    return jsonify([segment_to_dict(s) for s in segs])


@segments_bp.route("/<slug>/categories", methods=["GET"])
def segment_categories(slug):
    db   = get_db()
    cats = list(db.categories.find({"segment_slug": slug}).sort("name", 1))
    return jsonify([category_to_dict(c) for c in cats])
"""

# ── routes/tags.py ───────────────────────────────────────────
files["routes/tags.py"] = """\
import re
import unicodedata
from flask import Blueprint, request, jsonify
from database import get_db
from models.tag import tag_to_dict

tags_bp = Blueprint("tags", __name__, url_prefix="/api/tags")


@tags_bp.route("/", methods=["GET"])
def list_tags():
    db   = get_db()
    tags = list(db.tags.find().sort([("is_custom", 1), ("label", 1)]))
    return jsonify([tag_to_dict(t) for t in tags])


@tags_bp.route("/", methods=["POST"])
def create_tag():
    db    = get_db()
    data  = request.get_json()
    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "Label obrigatório"}), 400

    slug = unicodedata.normalize("NFKD", label.lower())
    slug = slug.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^\\w\\s-]", "", slug)
    slug = re.sub(r"[-\\s]+", "_", slug).strip("_")

    if db.tags.find_one({"$or": [{"slug": slug}, {"label": label}]}):
        return jsonify({"error": "Tag já existe"}), 409

    doc = {"slug": slug, "label": label, "is_custom": True}
    result = db.tags.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(tag_to_dict(doc)), 201
"""

# ── app.py ───────────────────────────────────────────────────
files["app.py"] = '''\
from flask import Flask
from flask_cors import CORS
from config import Config
from database import get_db

DEFAULT_SEGMENTS = [
    ("ferramentas", "Ferramentas & Manutenção", "🔧", "Ferramentas, reparos e tudo para a oficina em casa"),
    ("automotivo",  "Automotivo",               "🚗", "Acessórios e cuidados para seu veículo"),
    ("pet-shop",    "Pet Shop",                 "🐾", "O melhor para seus bichinhos"),
    ("casa",        "Casa",                     "🏠", "Organização, cozinha e tudo para o lar"),
    ("eletronicos", "Eletrônicos",              "⚡", "Gadgets e tecnologia com custo-benefício"),
    ("esporte",     "Esporte e Lazer",          "💪", "Para quem curte atividade física e aventura"),
    ("games",       "Games e Hobbies",          "🎮", "Entretenimento e passatempos"),
    ("moda",        "Moda Masculina",           "👔", "Estilo e acessórios para o homem"),
]

DEFAULT_CATEGORIES = {
    "ferramentas": [("Manuais","🔨"),("Elétricas","🔌"),("Medição","📏"),("Fixadores","🔩"),("Organização","🗂️"),("Corte e Solda","✂️")],
    "automotivo":  [("Limpeza","🧽"),("Acessórios","🔧"),("Eletrônicos","📡"),("Iluminação","💡"),("Som","🔊"),("Manutenção","🛠️")],
    "pet-shop":    [("Comida","🍖"),("Petiscos","🦴"),("Brinquedos","🎾"),("Higiene","🛁"),("Cama e Descanso","😴"),("Transporte","🎒")],
    "casa":        [("Cozinha","🍳"),("Churrasco","🔥"),("Organização","📦"),("Limpeza","🧹"),("Jardim","🌱"),("Iluminação","💡"),("Decoração","🖼️")],
    "eletronicos": [("Smartphones","📱"),("Áudio","🎧"),("Computadores","💻"),("Câmeras","📷"),("Cabos e Carregadores","🔌"),("Smart Home","🏠")],
    "esporte":     [("Fitness","🏋️"),("Camping","⛺"),("Pesca","🎣"),("Ciclismo","🚴"),("Futebol","⚽")],
    "games":       [("Controles","🎮"),("Impressão 3D","🖨️"),("Drones","🚁"),("Board Games","🎲")],
    "moda":        [("Camisetas","👕"),("Calçados","👟"),("Relógios","⌚"),("Óculos","🕶️")],
}

DEFAULT_TAGS = [
    ("destaque",     "Em Destaque"),
    ("novo",         "Recém Chegado"),
    ("recomendado",  "Recomendado pelo Pai"),
    ("melhor_custo", "Melhor Custo-Benefício"),
    ("mais_vendido", "Mais Vendido"),
    ("queima",       "Queima de Estoque"),
    ("limitado",     "Estoque Limitado"),
    ("imperdivel",   "Imperdível"),
]


def _seed_defaults(db):
    from models.category import slugify

    for slug, name, icon, desc in DEFAULT_SEGMENTS:
        db.segments.update_one(
            {"slug": slug},
            {"$setOnInsert": {"slug": slug, "name": name, "icon": icon, "description": desc}},
            upsert=True,
        )

    for seg_slug, cats in DEFAULT_CATEGORIES.items():
        for name, icon in cats:
            cat_slug = f"{seg_slug}-{slugify(name)}"
            db.categories.update_one(
                {"slug": cat_slug},
                {"$setOnInsert": {"name": name, "slug": cat_slug, "icon": icon,
                                  "segment_slug": seg_slug, "is_custom": False}},
                upsert=True,
            )

    for slug, label in DEFAULT_TAGS:
        db.tags.update_one(
            {"slug": slug},
            {"$setOnInsert": {"slug": slug, "label": label, "is_custom": False}},
            upsert=True,
        )


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=app.config["CORS_ORIGINS"])

    from routes.products   import products_bp
    from routes.categories import categories_bp
    from routes.tags       import tags_bp
    from routes.shopee     import shopee_bp
    from routes.segments   import segments_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(shopee_bp)
    app.register_blueprint(segments_bp)

    with app.app_context():
        db = get_db()
        # Cria índices para performance
        db.products.create_index([("is_active", 1), ("created_at", -1)])
        db.products.create_index([("segment", 1)])
        db.products.create_index([("category", 1)])
        db.categories.create_index([("slug", 1)], unique=True)
        db.segments.create_index([("slug", 1)], unique=True)
        db.tags.create_index([("slug", 1)], unique=True)
        _seed_defaults(db)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
'''

# ── Escreve todos os arquivos ────────────────────────────────
for rel_path, content in files.items():
    full_path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {rel_path}")

print("\nMigração concluída!")
