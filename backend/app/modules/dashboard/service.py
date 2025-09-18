from app.extensions import db
from app.modules.user.models import User
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from sqlalchemy import func
from app.utils import db_logger as logger


class DashboardService:
    """Service class for dashboard statistics and analytics."""

    @staticmethod
    def get_stats():
        """
        Get comprehensive dashboard statistics.

        Returns:
            dict: Dictionary containing all dashboard statistics
        """
        try:
            logger.info("Fetching dashboard statistics")

            # Get basic counts
            user_count = User.query.count()
            restaurant_count = Restaurant.query.count()
            food_count = Food.query.count()
            total_ratings = FoodRating.query.count()

            # Get average rating across all foods
            avg_rating_result = db.session.query(func.avg(FoodRating.rating)).scalar()
            avg_rating = (
                round(float(avg_rating_result), 2) if avg_rating_result else 0.0
            )

            # Get popular foods by rating count (top 10)
            popular_foods = (
                db.session.query(
                    Food.id,
                    Food.name,
                    Food.description,
                    Food.price,
                    func.count(FoodRating.id).label("rating_count"),
                    func.avg(FoodRating.rating).label("avg_rating"),
                )
                .join(FoodRating, Food.id == FoodRating.food_id)
                .group_by(Food.id, Food.name, Food.description, Food.price)
                .order_by(func.count(FoodRating.id).desc())
                .limit(10)
                .all()
            )

            # Format popular foods data
            popular_foods_data = []
            for food in popular_foods:
                popular_foods_data.append(
                    {
                        "id": food.id,
                        "name": food.name,
                        "description": food.description,
                        "price": food.price,
                        "rating_count": food.rating_count,
                        "avg_rating": (
                            round(float(food.avg_rating), 2) if food.avg_rating else 0.0
                        ),
                    }
                )

            # Get top rated foods (minimum 5 ratings, ordered by average rating)
            top_rated_foods = (
                db.session.query(
                    Food.id,
                    Food.name,
                    Food.description,
                    Food.price,
                    func.count(FoodRating.id).label("rating_count"),
                    func.avg(FoodRating.rating).label("avg_rating"),
                )
                .join(FoodRating, Food.id == FoodRating.food_id)
                .group_by(Food.id, Food.name, Food.description, Food.price)
                .having(func.count(FoodRating.id) >= 5)
                .order_by(func.avg(FoodRating.rating).desc())
                .limit(10)
                .all()
            )

            # Format top rated foods data
            top_rated_foods_data = []
            for food in top_rated_foods:
                top_rated_foods_data.append(
                    {
                        "id": food.id,
                        "name": food.name,
                        "description": food.description,
                        "price": food.price,
                        "rating_count": food.rating_count,
                        "avg_rating": (
                            round(float(food.avg_rating), 2) if food.avg_rating else 0.0
                        ),
                    }
                )

            stats = {
                "overview": {
                    "total_users": user_count,
                    "total_restaurants": restaurant_count,
                    "total_foods": food_count,
                    "total_ratings": total_ratings,
                    "average_rating": avg_rating,
                },
                "popular_foods": popular_foods_data,
                "top_rated_foods": top_rated_foods_data,
            }

            logger.info(
                f"Successfully fetched dashboard statistics: {user_count} users, {restaurant_count} restaurants, {food_count} foods"
            )
            return stats

        except Exception as e:
            logger.error(f"Error fetching dashboard statistics: {str(e)}")
            raise e
