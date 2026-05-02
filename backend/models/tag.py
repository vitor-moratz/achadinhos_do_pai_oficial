def tag_to_dict(doc: dict) -> dict:
    return {
        "id":        str(doc["_id"]),
        "slug":      doc.get("slug"),
        "label":     doc.get("label"),
        "is_custom": doc.get("is_custom", False),
    }
