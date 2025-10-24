from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
from flask import current_app, url_for
import uuid
from app.utils import get_logger
logger = get_logger(__name__)


class Food(db.Model):
    __tablename__ = "foods"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    restaurant_id = db.Column(
        db.String(36),
        db.ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=True,
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
        # Get main image URL
        main_image = None
        all_images = []

        # Query images directly to avoid relationship loading issues
        try:
            food_images = db.session.query(FoodImage).filter_by(food_id=self.id).all()

            for image in food_images:
                image_dict = image.to_dict()
                all_images.append(image_dict)
                if image.is_main and main_image is None:
                    main_image = image_dict["image_url"]

            # If no main image is set, use the first image as main
            if main_image is None and all_images:
                main_image = all_images[0]["image_url"]
        except Exception as e:
            logger.warning(f"Error loading images for food {self.id}: {str(e)}")
            main_image = None
            all_images = []

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "restaurant_id": self.restaurant_id,
            "image_url": main_image,
            "images": all_images,
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
    food_id = db.Column(
        db.String(36), db.ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
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
