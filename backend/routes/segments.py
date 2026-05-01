from flask import Blueprint, jsonify

segments_bp = Blueprint("segments", __name__, url_prefix="/api/segments")


@segments_bp.route("/", methods=["GET"])
def list_segments():
    from models.segment import Segment
    segs = Segment.query.all()
    return jsonify([s.to_dict() for s in segs])


@segments_bp.route("/<slug>/categories", methods=["GET"])
def segment_categories(slug):
    from models.category import Category
    cats = Category.query.filter_by(segment_slug=slug).order_by(Category.name).all()
    return jsonify([c.to_dict() for c in cats])
