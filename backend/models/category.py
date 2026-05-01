import re
import unicodedata
from database import db


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.UniqueConstraint("name", "segment_slug", name="uq_cat_name_segment"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    icon = db.Column(db.String(10), nullable=True, default='📦')
    segment_slug = db.Column(db.String(100), nullable=True)
    is_custom = db.Column(db.Boolean, default=False)

    def __init__(self, name, icon='📦', is_custom=False, segment_slug=None):
        self.name = name
        self.segment_slug = segment_slug
        self.slug = f"{segment_slug}-{slugify(name)}" if segment_slug else slugify(name)
        self.icon = icon
        self.is_custom = is_custom

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "icon": self.icon,
            "segment_slug": self.segment_slug,
            "is_custom": self.is_custom,
        }
