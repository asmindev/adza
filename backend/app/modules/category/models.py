from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
import uuid

# Association table for many-to-many relationship between Restaurant and Category
restaurant_categories = db.Table(
    "restaurant_categories",
    db.Column(
        "restaurant_id",
        db.String(36),
        db.ForeignKey("restaurants.id"),
        primary_key=True,
    ),
    db.Column(
        "category_id", db.String(36), db.ForeignKey("categories.id"), primary_key=True
    ),
    db.Column(
        "created_at",
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("UTC_TIMESTAMP()"),
    ),
)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(255), nullable=True)  # untuk icon/image category
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("UTC_TIMESTAMP()"),
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("UTC_TIMESTAMP()"),
    )

    # Relationships
    restaurants = db.relationship(
        "Restaurant",
        secondary=restaurant_categories,
        lazy="subquery",
        backref=db.backref("categories", lazy=True),
    )
    user_favorites = db.relationship(
        "UserFavoriteCategory",
        backref="category",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(Category, self).__init__(**kwargs)

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }


class UserFavoriteCategory(db.Model):
    __tablename__ = "user_favorite_categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(
        db.String(36), db.ForeignKey("categories.id"), nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("UTC_TIMESTAMP()"),
    )

    # Unique constraint untuk mencegah duplikasi
    __table_args__ = (db.UniqueConstraint("user_id", "category_id"),)

    def __init__(self, **kwargs):
        # Remove created_at from kwargs if they exist
        kwargs.pop("created_at", None)
        # Don't manually set id - let autoincrement handle it
        kwargs.pop("id", None)
        super(UserFavoriteCategory, self).__init__(**kwargs)

    def __repr__(self):
        return f"<UserFavoriteCategory User:{self.user_id} Category:{self.category_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
        }
