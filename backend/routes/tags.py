from flask import Blueprint, request, jsonify
from database import db
from models.tag import Tag

tags_bp = Blueprint("tags", __name__, url_prefix="/api/tags")


@tags_bp.route("/", methods=["GET"])
def list_tags():
    tags = Tag.query.order_by(Tag.is_custom, Tag.label).all()
    return jsonify([t.to_dict() for t in tags])


@tags_bp.route("/", methods=["POST"])
def create_tag():
    data = request.get_json()
    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "Label obrigatório"}), 400

    slug = label.lower().strip()
    # normalize to slug
    import re, unicodedata
    slug = unicodedata.normalize('NFKD', slug).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '_', slug).strip('_')

    if Tag.query.filter((Tag.slug == slug) | (Tag.label == label)).first():
        return jsonify({"error": "Tag já existe"}), 409

    tag = Tag(slug=slug, label=label, is_custom=True)
    db.session.add(tag)
    db.session.commit()
    return jsonify(tag.to_dict()), 201
