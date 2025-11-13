"""
Service for food statistics and analytics
"""

from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.extensions import db
from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone
from app.utils import get_logger

logger = get_logger(__name__)


class FoodStatsService:
    """Service for handling food statistics"""

    @staticmethod
    def get_food_statistics():
        """
        Get comprehensive food statistics

        Returns:
            Dictionary with statistics:
            - total_foods: Total number of foods
            - new_foods_last_7_days: Foods added in last 7 days
            - average_rating: Average rating across all foods
            - foods_with_ratings: Count of foods that have ratings
            - foods_without_ratings: Count of foods without ratings
        """
        try:
            logger.info("Calculating food statistics")

            # Total foods
            total_foods = db.session.query(func.count(Food.id)).scalar() or 0

            # Foods added in last 7 days
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            new_foods_last_7_days = (
                db.session.query(func.count(Food.id))
                .filter(Food.created_at >= seven_days_ago)
                .scalar()
                or 0
            )

            # Average rating across all foods
            # Calculate from FoodRating table
            avg_rating_query = db.session.query(func.avg(FoodRating.rating)).scalar()
            average_rating = (
                round(float(avg_rating_query), 2) if avg_rating_query else 0.0
            )

            # Count foods with ratings
            # Get unique food_ids from FoodRating
            foods_with_ratings = (
                db.session.query(func.count(func.distinct(FoodRating.food_id))).scalar()
                or 0
            )

            # Foods without ratings
            foods_without_ratings = total_foods - foods_with_ratings

            stats = {
                "total_foods": total_foods,
                "new_foods_last_7_days": new_foods_last_7_days,
                "average_rating": average_rating,
                "foods_with_ratings": foods_with_ratings,
                "foods_without_ratings": foods_without_ratings,
            }

            logger.info(f"Food statistics calculated: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error calculating food statistics: {str(e)}")
            return {
                "total_foods": 0,
                "new_foods_last_7_days": 0,
                "average_rating": 0.0,
                "foods_with_ratings": 0,
                "foods_without_ratings": 0,
            }
