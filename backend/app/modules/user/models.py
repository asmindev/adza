from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
import uuid


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

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
    food_ratings = db.relationship(
        "FoodRating", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    restaurant_ratings = db.relationship(
        "RestaurantRating", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    reviews = db.relationship(
        "Review", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    favorite_categories = db.relationship(
        "UserFavoriteCategory", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(User, self).__init__(**kwargs)

    def to_dict(self):
        def safe_created_at_key(item):
            return item.get("created_at", "") or ""

        reviews = [review.to_dict() for review in self.reviews] if self.reviews else []
        reviews = (
            sorted(reviews, key=safe_created_at_key, reverse=True) if reviews else []
        )

        # Combine food ratings and restaurant ratings
        food_ratings = (
            [rating.to_dict() for rating in self.food_ratings]
            if self.food_ratings
            else []
        )
        restaurant_ratings = (
            [rating.to_dict() for rating in self.restaurant_ratings]
            if self.restaurant_ratings
            else []
        )
        all_ratings = food_ratings + restaurant_ratings
        all_ratings = (
            sorted(all_ratings, key=safe_created_at_key, reverse=True)
            if all_ratings
            else []
        )

        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "reviews": reviews,
            "ratings": all_ratings,
            "food_ratings": food_ratings,
            "restaurant_ratings": restaurant_ratings,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }

    @property
    def is_admin(self):
        """Helper property to easily check if user is an admin"""
        return self.role == "admin"
