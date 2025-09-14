from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
import uuid


class FoodRating(db.Model):
    __tablename__ = "food_ratings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    food_id = db.Column(
        db.String(36), db.ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
    rating = db.Column(db.Float, nullable=False)  # Rating from 1-5

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

    # Enforce unique constraint to prevent duplicate ratings
    __table_args__ = (
        db.UniqueConstraint("user_id", "food_id", name="uq_user_food_rating"),
    )

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(FoodRating, self).__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "food_id": self.food_id,
            "rating": self.rating,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }


class RestaurantRating(db.Model):
    __tablename__ = "restaurant_ratings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    restaurant_id = db.Column(
        db.String(36),
        db.ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating = db.Column(db.Float, nullable=False)  # Rating from 1-5
    comment = db.Column(db.Text, nullable=True)  # Optional comment about service

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

    # Enforce unique constraint to prevent duplicate ratings
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "restaurant_id", name="uq_user_restaurant_rating"
        ),
    )

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(RestaurantRating, self).__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "restaurant_id": self.restaurant_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }
