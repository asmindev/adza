"""
User data service for handling complex user data operations
This handles data aggregation and business logic related to user data presentation
"""

from app.modules.user.models import User
from app.modules.user.repository import UserRepository
from app.utils import get_logger
logger = get_logger(__name__)
from typing import Dict, Any, List, Optional


class UserDataService:
    """Service for handling user data aggregation and complex operations"""

    @staticmethod
    def get_user_with_aggregated_data(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user with aggregated data (reviews, ratings, etc.)
        This handles the business logic for data aggregation that was previously in models
        """
        logger.debug(f"Getting user with aggregated data for ID: {user_id}")

        user = UserRepository.get_by_id(user_id)
        if not user:
            return None

        # Get base user data
        user_data = user.to_dict()

        try:
            # Safely get and process reviews with detailed information
            reviews = []
            if hasattr(user, "reviews") and user.reviews:
                for review in user.reviews:
                    review_dict = review.to_dict()
                    # Add food details if available
                    if hasattr(review, "food") and review.food:
                        food_data = review.food.to_dict()
                        # Add restaurant info to food data if available
                        if (
                            hasattr(review.food, "restaurant")
                            and review.food.restaurant
                        ):
                            food_data["restaurant"] = review.food.restaurant.to_dict()
                        review_dict["food"] = food_data
                    # Add restaurant details if available (for direct restaurant reviews)
                    if hasattr(review, "restaurant") and review.restaurant:
                        review_dict["restaurant"] = review.restaurant.to_dict()
                    reviews.append(review_dict)

                # Sort reviews by created_at (most recent first)
                reviews = sorted(
                    reviews, key=lambda x: x.get("created_at", ""), reverse=True
                )

            # Safely get and process ratings with detailed information
            food_ratings = []
            restaurant_ratings = []

            if hasattr(user, "food_ratings") and user.food_ratings:
                for rating in user.food_ratings:
                    rating_dict = rating.to_dict()
                    # Add food details
                    if hasattr(rating, "food") and rating.food:
                        food_data = rating.food.to_dict()
                        # Add restaurant info to food data if available
                        if (
                            hasattr(rating.food, "restaurant")
                            and rating.food.restaurant
                        ):
                            food_data["restaurant"] = rating.food.restaurant.to_dict()
                        rating_dict["food"] = food_data
                    food_ratings.append(rating_dict)

            if hasattr(user, "restaurant_ratings") and user.restaurant_ratings:
                for rating in user.restaurant_ratings:
                    rating_dict = rating.to_dict()
                    # Add restaurant details
                    if hasattr(rating, "restaurant") and rating.restaurant:
                        rating_dict["restaurant"] = rating.restaurant.to_dict()
                    restaurant_ratings.append(rating_dict)

            # Combine all ratings and sort (keep detailed information)
            all_ratings = []

            # Add food ratings with type identifier
            for rating in food_ratings:
                rating["rating_type"] = "food"
                all_ratings.append(rating)

            # Add restaurant ratings with type identifier
            for rating in restaurant_ratings:
                rating["rating_type"] = "restaurant"
                all_ratings.append(rating)

            # Sort by created_at (most recent first)
            all_ratings = sorted(
                all_ratings, key=lambda x: x.get("created_at", ""), reverse=True
            )

            # Safely get favorite categories
            favorite_categories = []
            if hasattr(user, "favorite_categories") and user.favorite_categories:
                favorite_categories = [
                    fav.category.to_dict()
                    for fav in user.favorite_categories
                    if hasattr(fav, "category") and fav.category
                ]

            # Add aggregated data to user_data
            user_data.update(
                {
                    "reviews": reviews,
                    "ratings": all_ratings,
                    "food_ratings": food_ratings,
                    "restaurant_ratings": restaurant_ratings,
                    "favorite_categories": favorite_categories,
                    # Add counts for convenience
                    "review_count": len(reviews),
                    "rating_count": len(all_ratings),
                    "favorite_category_count": len(favorite_categories),
                }
            )

            logger.info(f"Successfully aggregated data for user {user_id}")
            return user_data

        except Exception as e:
            logger.error(f"Error aggregating data for user {user_id}: {str(e)}")
            # Return basic user data if aggregation fails
            return user_data

    @staticmethod
    def get_users_with_basic_data(
        page: int = 1, limit: int = 10, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get users with basic data (no relations) for listing purposes
        """
        logger.debug(f"Getting users list: page={page}, limit={limit}, search={search}")

        result = UserRepository.get_all(page=page, limit=limit, search=search)

        # Convert users to basic dict format
        users_data = [user.to_dict() for user in result["items"]]

        return {
            "items": users_data,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }

    @staticmethod
    def get_user_statistics(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user statistics (counts, averages, etc.)
        """
        logger.debug(f"Getting statistics for user {user_id}")

        user = UserRepository.get_by_id(user_id)
        if not user:
            return None

        try:
            stats = {
                "user_id": user_id,
                "review_count": 0,
                "food_rating_count": 0,
                "restaurant_rating_count": 0,
                "favorite_category_count": 0,
                "average_food_rating": 0.0,
                "average_restaurant_rating": 0.0,
            }

            # Count reviews
            if hasattr(user, "reviews") and user.reviews:
                stats["review_count"] = len(user.reviews)

            # Count and calculate food ratings
            if hasattr(user, "food_ratings") and user.food_ratings:
                food_ratings = user.food_ratings
                stats["food_rating_count"] = len(food_ratings)
                if food_ratings:
                    total_rating = sum(
                        rating.rating
                        for rating in food_ratings
                        if hasattr(rating, "rating")
                    )
                    stats["average_food_rating"] = round(
                        total_rating / len(food_ratings), 2
                    )

            # Count and calculate restaurant ratings
            if hasattr(user, "restaurant_ratings") and user.restaurant_ratings:
                restaurant_ratings = user.restaurant_ratings
                stats["restaurant_rating_count"] = len(restaurant_ratings)
                if restaurant_ratings:
                    total_rating = sum(
                        rating.rating
                        for rating in restaurant_ratings
                        if hasattr(rating, "rating")
                    )
                    stats["average_restaurant_rating"] = round(
                        total_rating / len(restaurant_ratings), 2
                    )

            # Count favorite categories
            if hasattr(user, "favorite_categories") and user.favorite_categories:
                stats["favorite_category_count"] = len(user.favorite_categories)

            logger.info(f"Successfully calculated statistics for user {user_id}")
            return stats

        except Exception as e:
            logger.error(f"Error calculating statistics for user {user_id}: {str(e)}")
            return None
