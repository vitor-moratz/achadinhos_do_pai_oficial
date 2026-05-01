from database import db
from datetime import datetime, timezone


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    original_price = db.Column(db.Float, nullable=True)
    promo_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    affiliate_link = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    segment = db.Column(db.String(100), nullable=True)
    tag = db.Column(db.String(100), nullable=True)   # ex: "queima", "imperdivel", "novo"
    is_active = db.Column(db.Boolean, default=True)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "original_price": self.original_price,
            "promo_price": self.promo_price,
            "image_url": self.image_url,
            "affiliate_link": self.affiliate_link,
            "category": self.category,
            "segment": self.segment,
            "tag": self.tag,
            "is_active": self.is_active,
            "clicks": self.clicks,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
