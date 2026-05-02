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
