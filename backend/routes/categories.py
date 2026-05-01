from flask import Blueprint, request, jsonify
from database import db
from models.category import Category, slugify

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@categories_bp.route("/", methods=["GET"])
def list_categories():
    segment = request.args.get("segment")
    q = Category.query
    if segment:
        q = q.filter_by(segment_slug=segment)
    cats = q.order_by(Category.is_custom, Category.name).all()
    return jsonify([c.to_dict() for c in cats])


@categories_bp.route("/", methods=["POST"])
def create_category():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    icon = (data.get("icon") or "📦").strip()
    if not name:
        return jsonify({"error": "Nome obrigatório"}), 400

    slug = slugify(name)
    if Category.query.filter((Category.name == name) | (Category.slug == slug)).first():
        return jsonify({"error": "Categoria já existe"}), 409

    cat = Category(name=name, icon=icon, is_custom=True)
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201
