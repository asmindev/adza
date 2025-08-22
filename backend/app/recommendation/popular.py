"""
Popular Food Recommender
"""

from sqlalchemy import func
from app.utils import training_logger as logger
from app import db
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating


class PopularFoodRecommender:
    @staticmethod
    def get_popular_foods(n=10):
        """
        Get most popular foods based on rating count and average rating

        Args:
            n: Number of foods to return

        Returns:
            List of food dictionaries with popularity scores
        """
        logger.info(f"Mengambil {n} makanan terpopuler")

        # Calculate average rating and count for each food
        food_stats = (
            db.session.query(
                FoodRating.food_id,
                func.avg(FoodRating.rating).label("avg_rating"),
                func.count(FoodRating.id).label("rating_count"),
            )
            .group_by(FoodRating.food_id)
            .all()
        )

        # Calculate popularity score
        if not food_stats:
            logger.warning("Tidak ada data rating untuk menentukan popularitas")
            return []

        max_count = max(stats.rating_count for stats in food_stats)

        food_scores = []
        for stats in food_stats:
            normalized_count = stats.rating_count / max_count
            # Popularity score = average rating * 0.7 + normalized count * 0.3
            popularity_score = (stats.avg_rating / 5) * 0.7 + normalized_count * 0.3
            food_scores.append(
                (stats.food_id, stats.avg_rating, stats.rating_count, popularity_score)
            )

        # Sort by popularity score and get top n
        sorted_foods = sorted(food_scores, key=lambda x: x[3], reverse=True)[:n]

        # Get food details
        popular_foods = []
        for food_id, avg_rating, rating_count, popularity_score in sorted_foods:
            food = Food.query.get(food_id)
            if food:
                food_dict = food.to_dict()
                food_dict["average_rating"] = round(avg_rating, 1)
                food_dict["rating_count"] = rating_count
                food_dict["popularity_score"] = round(popularity_score, 2)
                popular_foods.append(food_dict)

        logger.info(f"Berhasil mengambil {len(popular_foods)} makanan terpopuler")
        # sort by popularity score
        popular_foods.sort(key=lambda x: x["popularity_score"], reverse=True)
        return popular_foods
