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
