def segment_to_dict(doc: dict) -> dict:
    return {
        "id":          str(doc["_id"]),
        "name":        doc.get("name"),
        "slug":        doc.get("slug"),
        "icon":        doc.get("icon", "📦"),
        "description": doc.get("description"),
    }
