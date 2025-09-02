"""
Popular Food Recommender
"""

from sqlalchemy import func, and_
from app.utils import training_logger as logger
from app import db
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from typing import List, Dict, Any


class PopularFoodRecommender:
    @staticmethod
    def get_popular_foods(n=10) -> List[Dict[str, Any]]:
        """
        Get most popular foods based on rating count and average rating

        Args:
            n: Number of foods to return

        Returns:
            List of food dictionaries with popularity scores
        """
        logger.info(f"Mengambil {n} makanan terpopuler")

        try:
            # Calculate average rating and count for each food in a single query
            food_stats = (
                db.session.query(
                    Food.id,
                    Food.name,
                    Food.description,
                    Food.price,
                    Food.restaurant_id,
                    func.avg(FoodRating.rating).label("avg_rating"),
                    func.count(FoodRating.id).label("rating_count"),
                )
                .join(FoodRating, Food.id == FoodRating.food_id)
                .group_by(
                    Food.id, Food.name, Food.description, Food.price, Food.restaurant_id
                )
                .all()
            )

            # Calculate popularity score
            if not food_stats:
                logger.warning("Tidak ada data rating untuk menentukan popularitas")
                return []

            # Find max count for normalization
            max_count = max(stats.rating_count for stats in food_stats)
            if max_count == 0:
                logger.warning("Rating count maksimum adalah 0")
                return []

            food_scores = []
            for stats in food_stats:
                try:
                    # Ensure rating values are valid
                    avg_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
                    rating_count = int(stats.rating_count) if stats.rating_count else 0

                    # Skip foods with invalid ratings
                    if avg_rating <= 0 or rating_count <= 0:
                        continue

                    # Normalize count (0-1)
                    normalized_count = rating_count / max_count

                    # Normalize rating (0-1)
                    normalized_rating = (
                        avg_rating - 1.0
                    ) / 4.0  # Scale from 1-5 to 0-1

                    # Popularity score = weighted combination of rating quality and quantity
                    # 70% weight for average rating, 30% weight for rating count
                    popularity_score = normalized_rating * 0.7 + normalized_count * 0.3

                    food_scores.append(
                        {
                            "food_id": stats.id,
                            "name": stats.name,
                            "description": stats.description,
                            "price": stats.price,
                            "restaurant_id": stats.restaurant_id,
                            "avg_rating": round(avg_rating, 2),
                            "rating_count": rating_count,
                            "popularity_score": round(popularity_score, 3),
                        }
                    )

                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Error processing food stats for food {stats.id}: {str(e)}"
                    )
                    continue

            if not food_scores:
                logger.warning("Tidak ada food scores yang valid")
                return []

            # Sort by popularity score and get top n
            sorted_foods = sorted(
                food_scores, key=lambda x: x["popularity_score"], reverse=True
            )[:n]

            # Get complete food details
            popular_foods = []
            for food_data in sorted_foods:
                try:
                    food = Food.query.get(food_data["food_id"])
                    if food:
                        food_dict = food.to_dict()
                        food_dict.update(
                            {
                                "average_rating": food_data["avg_rating"],
                                "rating_count": food_data["rating_count"],
                                "popularity_score": food_data["popularity_score"],
                            }
                        )
                        popular_foods.append(food_dict)
                except Exception as e:
                    logger.warning(
                        f"Error getting food details for {food_data['food_id']}: {str(e)}"
                    )
                    continue

            logger.info(f"Berhasil mengambil {len(popular_foods)} makanan terpopuler")
            return popular_foods

        except Exception as e:
            logger.error(f"Error in get_popular_foods: {str(e)}")
            return []

    @staticmethod
    def get_popular_foods_by_category(category_id: str, n=10) -> List[Dict[str, Any]]:
        """
        Get popular foods filtered by category
        Note: This method needs proper category-food relationship implementation

        Args:
            category_id: ID of the category to filter by
            n: Number of foods to return

        Returns:
            List of food dictionaries with popularity scores
        """
        logger.info(f"Mengambil {n} makanan terpopuler untuk kategori {category_id}")
        logger.warning(
            "Category filtering not implemented yet - returning general popular foods"
        )

        # For now, return general popular foods
        # TODO: Implement proper category-food relationship
        return PopularFoodRecommender.get_popular_foods(n)

    @staticmethod
    def get_trending_foods(n=10, days=7) -> List[Dict[str, Any]]:
        """
        Get trending foods based on recent activity

        Args:
            n: Number of foods to return
            days: Number of recent days to consider

        Returns:
            List of food dictionaries with trending scores
        """
        logger.info(f"Mengambil {n} makanan trending dalam {days} hari terakhir")

        try:
            from datetime import datetime, timedelta

            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Get recent ratings
            recent_stats = (
                db.session.query(
                    Food.id,
                    func.avg(FoodRating.rating).label("avg_rating"),
                    func.count(FoodRating.id).label("rating_count"),
                )
                .join(FoodRating, Food.id == FoodRating.food_id)
                .filter(FoodRating.created_at >= cutoff_date)
                .group_by(Food.id)
                .all()
            )

            if not recent_stats:
                logger.warning(f"Tidak ada data rating dalam {days} hari terakhir")
                return []

            # Calculate trending scores
            max_count = max(stats.rating_count for stats in recent_stats)
            trending_foods = []

            for stats in recent_stats:
                try:
                    avg_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
                    rating_count = int(stats.rating_count) if stats.rating_count else 0

                    if avg_rating <= 0 or rating_count <= 0:
                        continue

                    # For trending, give more weight to recent activity
                    normalized_count = rating_count / max_count
                    normalized_rating = (avg_rating - 1.0) / 4.0
                    trending_score = (
                        normalized_rating * 0.4 + normalized_count * 0.6
                    )  # More weight on activity

                    food = Food.query.get(stats.id)
                    if food:
                        food_dict = food.to_dict()
                        food_dict.update(
                            {
                                "average_rating": round(avg_rating, 2),
                                "recent_rating_count": rating_count,
                                "trending_score": round(trending_score, 3),
                                "trending_period_days": days,
                            }
                        )
                        trending_foods.append(food_dict)

                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Error processing trending stats for food {stats.id}: {str(e)}"
                    )
                    continue

            # Sort by trending score
            trending_foods.sort(key=lambda x: x["trending_score"], reverse=True)
            result = trending_foods[:n]

            logger.info(f"Berhasil mengambil {len(result)} makanan trending")
            return result

        except Exception as e:
            logger.error(f"Error in get_trending_foods: {str(e)}")
            return []
