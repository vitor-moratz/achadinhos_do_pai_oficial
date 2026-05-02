from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from database import get_db
from models.product  import make_product, product_to_dict
from notifications   import notify_new_product

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

    seg_slugs = {p["segment"] for p in products if p.get("segment")}
    seg_map   = {}
    if seg_slugs:
        seg_map = {s["slug"]: s["name"] for s in db.segments.find({"slug": {"$in": list(seg_slugs)}})}

    result = []
    for p in products:
        d = product_to_dict(p)
        d["tag_label"]     = tag_map.get(p.get("tag"), p.get("tag")) if p.get("tag") else None
        d["segment_name"]  = seg_map.get(p.get("segment")) if p.get("segment") else None
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
    required = ["title", "price_from", "affiliate_link"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing)}"}), 400

    doc    = make_product(data)
    result = db.products.insert_one(doc)
    doc["_id"] = result.inserted_id

    notify_new_product(doc)

    return jsonify(product_to_dict(doc)), 201


@products_bp.route("/<product_id>", methods=["PUT"])
def update_product(product_id):
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400

    data      = request.get_json()
    updatable = ["title", "description", "price_from", "price_to",
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
