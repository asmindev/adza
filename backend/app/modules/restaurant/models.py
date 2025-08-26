from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy import func
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

    def calculate_rating_average(self):
        """Calculate average rating from restaurant_ratings table"""
        if not self.restaurant_ratings:
            return 0.0

        total_ratings = sum(rating.rating for rating in self.restaurant_ratings)
        count = len(self.restaurant_ratings)
        return round(total_ratings / count, 2) if count > 0 else 0.0

    def update_rating_average(self):
        """Update the rating_average field with calculated value from restaurant_ratings"""
        self.rating_average = self.calculate_rating_average()
        db.session.commit()

    @classmethod
    def get_avg_rating_from_db(cls, restaurant_id):
        """Get average rating directly from database query"""
        from app.modules.rating.models import RestaurantRating

        result = (
            db.session.query(
                func.avg(RestaurantRating.rating).label("avg_rating"),
                func.count(RestaurantRating.id).label("total_ratings"),
            )
            .filter(RestaurantRating.restaurant_id == restaurant_id)
            .first()
        )

        if result and result.avg_rating:
            return {
                "average_rating": round(float(result.avg_rating), 2),
                "total_ratings": result.total_ratings,
            }
        return {"average_rating": 0.0, "total_ratings": 0}

    def get_rating_details(self):
        """Get detailed rating information including all ratings array"""
        from app.modules.rating.models import RestaurantRating

        # Get all ratings for this restaurant
        ratings = (
            db.session.query(RestaurantRating)
            .filter(RestaurantRating.restaurant_id == self.id)
            .order_by(RestaurantRating.created_at.desc())
            .all()
        )

        # Convert ratings to list of dictionaries
        rating_list = []
        for rating in ratings:
            rating_list.append(
                {
                    "id": rating.id,
                    "user_id": rating.user_id,
                    "rating": rating.rating,
                    "comment": rating.comment,
                    "created_at": (
                        rating.created_at.isoformat() + "Z"
                        if rating.created_at
                        else None
                    ),
                }
            )

        # Calculate average and total
        total = len(rating_list)
        average = (
            round(sum(r["rating"] for r in rating_list) / total, 2)
            if total > 0
            else 0.0
        )

        return {"rating": rating_list, "average": average, "total": total}

    def to_dict(self):
        def safe_created_at_key(item):
            return item.get("created_at", "") or ""

        # Get detailed rating information
        rating_details = self.get_rating_details()

        # Include categories info (many-to-many)
        categories_info = []
        if self.categories:
            for category in self.categories:
                categories_info.append(
                    {
                        "id": category.id,
                        "name": category.name,
                        "description": category.description,
                    }
                )

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "categories": categories_info,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rating": rating_details,
            "is_active": self.is_active,
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

    @property
    def list_restaurant(self):
        """Helper property to get restaurant details as a list"""
        return dict(id=self.id, name=self.name)
