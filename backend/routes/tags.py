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
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "_", slug).strip("_")

    if db.tags.find_one({"$or": [{"slug": slug}, {"label": label}]}):
        return jsonify({"error": "Tag já existe"}), 409

    doc = {"slug": slug, "label": label, "is_custom": True}
    result = db.tags.insert_one(doc)
    doc["_id"] = result.inserted_id
    return jsonify(tag_to_dict(doc)), 201
