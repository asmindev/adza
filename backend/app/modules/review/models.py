from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import func, text
import uuid


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(
        db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    food_id = db.Column(
        db.String(36), db.ForeignKey("foods.id", ondelete="CASCADE"), nullable=False
    )
    content = db.Column(db.Text, nullable=False)  # Review content

    # Menggunakan UTC secara eksplisit
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

    # Enforce unique constraint to prevent duplicate reviews
    __table_args__ = (
        db.UniqueConstraint("user_id", "food_id", name="uq_user_food_review"),
    )

    def __init__(self, **kwargs):
        # Generate UUID if not provided
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        # remove created_at and updated_at from kwargs if they exist
        kwargs.pop("created_at", None)
        kwargs.pop("updated_at", None)
        super(Review, self).__init__(**kwargs)

    def to_dict(self):
        user = {
            "id": self.user_id,
            "username": self.user.username if self.user else None,
            "name": self.user.name if self.user else None,
        }
        return {
            "id": self.id,
            "food_id": self.food_id,
            "user": user,
            "content": self.content,
            "created_at": (
                self.created_at.isoformat() + "Z" if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() + "Z" if self.updated_at else None
            ),
        }
