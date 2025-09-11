from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
import uuid


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rating_average = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

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
    foods = db.relationship(
        "Food", backref="restaurant", lazy=True, cascade="all, delete-orphan"
    )

    # Relationship with RestaurantRating
    restaurant_ratings = db.relationship(
        "RestaurantRating",
        backref="restaurant",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # Note: categories relationship is defined via backref in Category model

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(Restaurant, self).__init__(**kwargs)

    def to_dict(self):
        """Simple serialization of restaurant model"""
        # Get categories from many-to-many relationship
        categories_data = []
        try:
            # Query categories directly using the association table
            from app.modules.category.models import restaurant_categories, Category

            category_ids = db.session.execute(
                db.select(restaurant_categories.c.category_id).where(
                    restaurant_categories.c.restaurant_id == self.id
                )
            ).fetchall()

            if category_ids:
                categories = Category.query.filter(
                    Category.id.in_([cat_id[0] for cat_id in category_ids])
                ).all()
                categories_data = [cat.to_dict() for cat in categories]
        except Exception:
            # If there's any error, just return empty categories
            categories_data = []

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rating_average": self.rating_average,
            "is_active": self.is_active,
            "categories": categories_data,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }

    @property
    def location(self):
        """Helper property to get location as a dict"""
        return {"latitude": self.latitude, "longitude": self.longitude}
