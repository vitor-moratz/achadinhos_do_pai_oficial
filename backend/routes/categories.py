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
