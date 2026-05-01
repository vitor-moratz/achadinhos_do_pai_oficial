from flask import Blueprint, request, jsonify
from database import db
from models.product import Product

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


def _resolve_category_filter(slug_or_name: str):
    """Resolve um slug de categoria para (name, segment_slug) para filtrar produtos."""
    from models.category import Category
    cat = Category.query.filter_by(slug=slug_or_name).first()
    if cat:
        return cat.name, cat.segment_slug
    # fallback: match case-insensitivo pelo nome
    cat = Category.query.filter(
        db.func.lower(Category.name) == slug_or_name.lower()
    ).first()
    if cat:
        return cat.name, cat.segment_slug
    return slug_or_name, None


@products_bp.route("/", methods=["GET"])
def list_products():
    category = request.args.get("category")
    segment = request.args.get("segment")
    tag = request.args.get("tag")
    search = request.args.get("search")

    query = Product.query.filter_by(is_active=True)

    if category:
        cat_name, cat_seg = _resolve_category_filter(category)
        query = query.filter(Product.category == cat_name)
        if cat_seg:
            query = query.filter(Product.segment == cat_seg)
    if segment:
        query = query.filter(Product.segment == segment)
    if tag:
        query = query.filter(Product.tag == tag)
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))

    products = query.order_by(Product.created_at.desc()).all()

    # Enriquecer com tag_label
    from models.tag import Tag as TagModel
    tag_slugs = {p.tag for p in products if p.tag}
    tag_map = {}
    if tag_slugs:
        tag_map = {t.slug: t.label for t in TagModel.query.filter(TagModel.slug.in_(tag_slugs)).all()}

    result = []
    for p in products:
        d = p.to_dict()
        d["tag_label"] = tag_map.get(p.tag, p.tag) if p.tag else None
        result.append(d)

    return jsonify(result)



@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@products_bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json()
    required = ["title", "promo_price", "affiliate_link"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Campos obrigatórios: {', '.join(missing)}"}), 400

    product = Product(
        title=data["title"],
        description=data.get("description"),
        original_price=data.get("original_price"),
        promo_price=data["promo_price"],
        image_url=data.get("image_url"),
        affiliate_link=data["affiliate_link"],
        category=data.get("category"),
        segment=data.get("segment"),
        tag=data.get("tag"),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    updatable = ["title", "description", "original_price", "promo_price",
                 "image_url", "affiliate_link", "category", "segment", "tag", "is_active"]
    for field in updatable:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return jsonify(product.to_dict())


@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Produto removido com sucesso."})


@products_bp.route("/<int:product_id>/click", methods=["POST"])
def register_click(product_id):
    """Registra clique no link afiliado para métricas."""
    product = Product.query.get_or_404(product_id)
    product.clicks += 1
    db.session.commit()
    return jsonify({"affiliate_link": product.affiliate_link})


@products_bp.route("/categories", methods=["GET"])
def list_categories():
    rows = db.session.query(Product.category).filter(
        Product.is_active == True, Product.category != None
    ).distinct().all()
    return jsonify([r[0] for r in rows])
