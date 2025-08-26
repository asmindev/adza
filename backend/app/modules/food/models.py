from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
from flask import current_app, url_for
import uuid


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
        images = [image.to_dict() for image in self.images] if self.images else []
        main_image = next((image for image in images if image["is_main"]), None)
        if not main_image:
            main_image = images[0] if images else None
            # update the main image to the first one if no main image is set
            if main_image:
                main_image["is_main"] = True
        ratings = [rating.to_dict() for rating in self.ratings]

        # Safer sorting that handles None values
        def safe_created_at_key(item):
            return item.get("created_at", "") or ""

        ratings = (
            sorted(ratings, key=safe_created_at_key, reverse=True) if ratings else []
        )
        ratings = {
            "average": (
                sum(r["rating"] for r in ratings) / len(ratings) if ratings else 0
            ),
            "count": len(ratings),
            "data": ratings,
        }
        reviews = [review.to_dict() for review in self.reviews] if self.reviews else []
        reviews = (
            sorted(reviews, key=safe_created_at_key, reverse=True) if reviews else []
        )
        reviews = {
            "review_count": len(reviews),
            "data": reviews,
        }

        # Include restaurant info if available
        restaurant_info = None
        category_info = None
        if self.restaurant_id:
            # Import here to avoid circular import
            from app.modules.restaurant.models import Restaurant

            restaurant = Restaurant.query.get(self.restaurant_id)
            if restaurant:
                restaurant_info = {
                    "id": restaurant.id,
                    "name": restaurant.name,
                    "address": restaurant.address,
                    "latitude": restaurant.latitude,
                    "longitude": restaurant.longitude,
                }

                # Get category from restaurant
                if restaurant.category_id:
                    from app.modules.category.models import Category

                    category = Category.query.get(restaurant.category_id)
                    if category:
                        category_info = {
                            "id": category.id,
                            "name": category.name,
                            "description": category.description,
                        }

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": category_info,
            "price": self.price,
            "restaurant_id": self.restaurant_id,
            "restaurant": restaurant_info,
            "main_image": main_image,
            "images": images,
            "ratings": ratings,
            "reviews": reviews,
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
        if self.image_url.startswith("http"):
            image_url = self.image_url
        else:
            image_url = url_for(
                "food.serve_static", filename=self.filename, _external=True
            )
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
