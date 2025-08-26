from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
from flask import current_app, url_for
import uuid
from app.utils import db_logger as logger


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    restaurant_id = db.Column(
        db.String(36), db.ForeignKey("restaurants.id"), nullable=True
    )

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
    # Note: restaurant relationship is defined via backref in Restaurant model
    ratings = db.relationship(
        "FoodRating", backref="food", lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", backref="food", lazy=True, cascade="all, delete-orphan"
    )
    images = db.relationship(
        "FoodImage", backref="food", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(Food, self).__init__(**kwargs)

    def to_dict(self):
        """Simple ORM serialization - no business logic"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "restaurant_id": self.restaurant_id,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }


class FoodImage(db.Model):
    __tablename__ = "food_images"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    food_id = db.Column(db.String(36), db.ForeignKey("foods.id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    is_main = db.Column(db.Boolean, default=False, nullable=False)
    filename = db.Column(db.String(255), nullable=True)

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

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(FoodImage, self).__init__(**kwargs)

    def to_dict(self):
        """Simple ORM serialization with URL generation"""
        # Generate appropriate URL based on image_url format
        if self.image_url and self.image_url.startswith("http"):
            image_url = self.image_url
        elif self.filename:
            try:
                from flask import url_for

                image_url = url_for(
                    "food.serve_static", filename=self.filename, _external=True
                )
            except Exception:
                # Fallback if url_for fails
                image_url = self.image_url or self.filename
        else:
            image_url = self.image_url

        return {
            "id": self.id,
            "food_id": self.food_id,
            "image_url": image_url,
            "is_main": self.is_main,
            "filename": self.filename,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }
