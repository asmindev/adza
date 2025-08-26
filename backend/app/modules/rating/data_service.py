"""
Rating data service for handling complex rating data operations
This handles data aggregation and business logic related to rating data presentation
"""

from .models import FoodRating, RestaurantRating
from .repository import FoodRatingRepository, RestaurantRatingRepository
from app.extensions import db
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class RatingDataService:
    """Service for handling rating data aggregation and complex operations"""

    @staticmethod
    def get_food_rating_statistics(food_id: str) -> Dict[str, Any]:
        """
        Get comprehensive rating statistics for a food

        Args:
            food_id: Food ID

        Returns:
            dict: Rating statistics including average, count, distribution
        """
        logger.debug(f"Getting rating statistics for food: {food_id}")

        try:
            # Get basic stats
            average_rating = FoodRatingRepository.get_food_average_rating(food_id)
            rating_count = FoodRatingRepository.get_food_rating_count(food_id)

            # Get rating distribution
            distribution = RatingDataService._get_food_rating_distribution(food_id)

            return {
                "food_id": food_id,
                "average_rating": round(average_rating, 2) if average_rating else 0.0,
                "total_ratings": rating_count,
                "rating_distribution": distribution,
                "has_ratings": rating_count > 0,
            }

        except Exception as e:
            logger.error(
                f"Error getting rating statistics for food {food_id}: {str(e)}"
            )
            return {
                "food_id": food_id,
                "average_rating": 0.0,
                "total_ratings": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "has_ratings": False,
            }

    @staticmethod
    def get_restaurant_rating_statistics(restaurant_id: str) -> Dict[str, Any]:
        """
        Get comprehensive rating statistics for a restaurant

        Args:
            restaurant_id: Restaurant ID

        Returns:
            dict: Rating statistics including average, count, distribution
        """
        logger.debug(f"Getting rating statistics for restaurant: {restaurant_id}")

        try:
            # Get basic stats
            average_rating = RestaurantRatingRepository.get_restaurant_average_rating(
                restaurant_id
            )
            rating_count = RestaurantRatingRepository.get_restaurant_rating_count(
                restaurant_id
            )

            # Get rating distribution
            distribution = RatingDataService._get_restaurant_rating_distribution(
                restaurant_id
            )

            return {
                "restaurant_id": restaurant_id,
                "average_rating": round(average_rating, 2) if average_rating else 0.0,
                "total_ratings": rating_count,
                "rating_distribution": distribution,
                "has_ratings": rating_count > 0,
            }

        except Exception as e:
            logger.error(
                f"Error getting rating statistics for restaurant {restaurant_id}: {str(e)}"
            )
            return {
                "restaurant_id": restaurant_id,
                "average_rating": 0.0,
                "total_ratings": 0,
                "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                "has_ratings": False,
            }

    @staticmethod
    def get_user_rating_summary(user_id: str) -> Dict[str, Any]:
        """
        Get summary of all ratings given by a user

        Args:
            user_id: User ID

        Returns:
            dict: User rating summary
        """
        logger.debug(f"Getting rating summary for user: {user_id}")

        try:
            # Get food ratings
            food_ratings = FoodRatingRepository.get_by_user_id(user_id)

            # Get restaurant ratings
            restaurant_ratings = RestaurantRatingRepository.get_by_user_id(user_id)

            # Calculate summary statistics
            total_food_ratings = len(food_ratings)
            total_restaurant_ratings = len(restaurant_ratings)

            avg_food_rating = 0.0
            if food_ratings:
                avg_food_rating = sum(r.rating for r in food_ratings) / len(
                    food_ratings
                )

            avg_restaurant_rating = 0.0
            if restaurant_ratings:
                avg_restaurant_rating = sum(r.rating for r in restaurant_ratings) / len(
                    restaurant_ratings
                )

            return {
                "user_id": user_id,
                "total_ratings": total_food_ratings + total_restaurant_ratings,
                "food_ratings": {
                    "count": total_food_ratings,
                    "average": round(avg_food_rating, 2),
                },
                "restaurant_ratings": {
                    "count": total_restaurant_ratings,
                    "average": round(avg_restaurant_rating, 2),
                },
                "is_active_rater": (total_food_ratings + total_restaurant_ratings) > 0,
            }

        except Exception as e:
            logger.error(f"Error getting rating summary for user {user_id}: {str(e)}")
            return {
                "user_id": user_id,
                "total_ratings": 0,
                "food_ratings": {"count": 0, "average": 0.0},
                "restaurant_ratings": {"count": 0, "average": 0.0},
                "is_active_rater": False,
            }

    @staticmethod
    def get_food_ratings_with_aggregation(
        food_id: str, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get food ratings with additional aggregation data

        Args:
            food_id: Food ID
            page: Page number
            limit: Items per page

        Returns:
            dict: Paginated ratings with aggregation data
        """
        logger.debug(f"Getting aggregated ratings for food: {food_id}")

        try:
            # Get paginated ratings
            result = FoodRatingRepository.get_by_food_id(
                food_id, page=page, limit=limit
            )

            # Get statistics
            statistics = RatingDataService.get_food_rating_statistics(food_id)

            # Convert ratings to dict format
            ratings_data = []
            for rating in result["items"]:
                rating_dict = rating.to_dict()
                # Add any additional user info if needed (could be expanded)
                ratings_data.append(rating_dict)

            return {
                "food_id": food_id,
                "statistics": statistics,
                "ratings": ratings_data,
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            }

        except Exception as e:
            logger.error(
                f"Error getting aggregated ratings for food {food_id}: {str(e)}"
            )
            return {
                "food_id": food_id,
                "statistics": RatingDataService.get_food_rating_statistics(food_id),
                "ratings": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0},
            }

    @staticmethod
    def get_restaurant_ratings_with_aggregation(
        restaurant_id: str, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get restaurant ratings with additional aggregation data

        Args:
            restaurant_id: Restaurant ID
            page: Page number
            limit: Items per page

        Returns:
            dict: Paginated ratings with aggregation data
        """
        logger.debug(f"Getting aggregated ratings for restaurant: {restaurant_id}")

        try:
            # Get paginated ratings
            result = RestaurantRatingRepository.get_by_restaurant_id(
                restaurant_id, page=page, limit=limit
            )

            # Get statistics
            statistics = RatingDataService.get_restaurant_rating_statistics(
                restaurant_id
            )

            # Convert ratings to dict format
            ratings_data = []
            for rating in result["items"]:
                rating_dict = rating.to_dict()
                ratings_data.append(rating_dict)

            return {
                "restaurant_id": restaurant_id,
                "statistics": statistics,
                "ratings": ratings_data,
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            }

        except Exception as e:
            logger.error(
                f"Error getting aggregated ratings for restaurant {restaurant_id}: {str(e)}"
            )
            return {
                "restaurant_id": restaurant_id,
                "statistics": RatingDataService.get_restaurant_rating_statistics(
                    restaurant_id
                ),
                "ratings": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0},
            }

    # Private helper methods
    @staticmethod
    def _get_food_rating_distribution(food_id: str) -> Dict[int, int]:
        """Get rating distribution (count per rating value) for a food"""
        try:
            # Initialize distribution
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            # Query database for rating counts
            from sqlalchemy import func

            results = (
                db.session.query(FoodRating.rating, func.count(FoodRating.rating))
                .filter_by(food_id=food_id)
                .group_by(FoodRating.rating)
                .all()
            )

            # Populate distribution
            for rating_value, count in results:
                rating_int = int(round(rating_value))
                if 1 <= rating_int <= 5:
                    distribution[rating_int] = count

            return distribution

        except Exception as e:
            logger.error(
                f"Error getting rating distribution for food {food_id}: {str(e)}"
            )
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    @staticmethod
    def _get_restaurant_rating_distribution(restaurant_id: str) -> Dict[int, int]:
        """Get rating distribution (count per rating value) for a restaurant"""
        try:
            # Initialize distribution
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            # Query database for rating counts
            from sqlalchemy import func

            results = (
                db.session.query(
                    RestaurantRating.rating, func.count(RestaurantRating.rating)
                )
                .filter_by(restaurant_id=restaurant_id)
                .group_by(RestaurantRating.rating)
                .all()
            )

            # Populate distribution
            for rating_value, count in results:
                rating_int = int(round(rating_value))
                if 1 <= rating_int <= 5:
                    distribution[rating_int] = count

            return distribution

        except Exception as e:
            logger.error(
                f"Error getting rating distribution for restaurant {restaurant_id}: {str(e)}"
            )
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
