from database import db


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    label = db.Column(db.String(100), nullable=False)
    is_custom = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "label": self.label,
            "is_custom": self.is_custom,
        }
