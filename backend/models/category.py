import re
import unicodedata


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def category_to_dict(doc: dict) -> dict:
    return {
        "id":           str(doc["_id"]),
        "name":         doc.get("name"),
        "slug":         doc.get("slug"),
        "icon":         doc.get("icon", "📦"),
        "segment_slug": doc.get("segment_slug"),
        "is_custom":    doc.get("is_custom", False),
    }
