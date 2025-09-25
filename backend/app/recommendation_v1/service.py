"""
Recommendation Service
Public API for the recommendation system
"""

from typing import List, Dict, Optional, Any
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response
from app.modules.food.models import Food
from app.modules.user.models import User
from app.extensions import db

from .recommender import Recommendations
from .config import RecommendationConfig

# Setup logger
logger = get_logger(__name__)


class RecommendationService:
    """
    Service layer for recommendation system
    Provides clean API interface for the application
    """

    def __init__(self):
        """Initialize recommendation service"""
        self.recommender = Recommendations()
        RecommendationConfig.initialize()

    def get_recommendations(
        self,
        user_id: str,
        top_n: int = RecommendationConfig.DEFAULT_RECOMMENDATIONS,
        include_details: bool = True,
    ) -> Any:
        """
        Get food recommendations for a user

        Args:
            user_id: User ID to get recommendations for
            top_n: Number of recommendations to return
            include_details: Whether to include food details in response

        Returns:
            Dict[str, any]: Response with recommendations
        """
        try:
            # Validate input
            if not user_id:
                return error_response("User ID is required", 400)

            # Validate user exists
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                return error_response("User not found", 404)

            # Validate top_n parameter
            if top_n < RecommendationConfig.MIN_RECOMMENDATIONS:
                top_n = RecommendationConfig.MIN_RECOMMENDATIONS
            elif top_n > RecommendationConfig.MAX_RECOMMENDATIONS:
                top_n = RecommendationConfig.MAX_RECOMMENDATIONS

            logger.info(f"Getting {top_n} recommendations for user {user_id}")

            # Get recommendations
            recommended_food_ids = self.recommender.recommend(user_id, top_n)

            if not recommended_food_ids:
                return success_response(
                    {
                        "recommendations": [],
                        "count": 0,
                        "message": "No recommendations available at this time",
                    }
                )

            # Validate recommendations
            if not self.recommender.validate_recommendations(
                user_id, recommended_food_ids
            ):
                logger.warning(f"Recommendation validation failed for user {user_id}")
                # Try to get fallback recommendations
                recommended_food_ids = self.recommender._get_fallback_recommendations(
                    user_id,
                    top_n,
                    self.recommender._get_user_context(user_id)["rated_foods"],
                )

            # Prepare response
            response_data = {
                "recommendations": recommended_food_ids,
                "count": len(recommended_food_ids),
                "user_id": user_id,
            }

            # Include food details if requested
            if include_details and recommended_food_ids:
                food_details = self._get_food_details(recommended_food_ids)
                response_data["food_details"] = food_details

            # Include explanation if available
            explanation = self.recommender.get_recommendation_explanation(
                user_id, recommended_food_ids
            )
            if explanation and "error" not in explanation:
                response_data["explanation"] = explanation

            logger.info(
                f"Successfully generated {len(recommended_food_ids)} recommendations for user {user_id}"
            )

            return success_response(response_data)

        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {e}")
            return error_response(f"Failed to get recommendations: {str(e)}", 500)

    def _get_food_details(self, food_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information about foods

        Args:
            food_ids: List of food IDs

        Returns:
            List[Dict[str, any]]: List of food details
        """
        try:
            foods = db.session.query(Food).filter(Food.id.in_(food_ids)).all()

            # Maintain order based on input list
            food_dict = {food.id: food for food in foods}
            ordered_foods = [
                food_dict[food_id] for food_id in food_ids if food_id in food_dict
            ]

            food_details = []
            for food in ordered_foods:
                food_data = (
                    food.to_dict()
                    if hasattr(food, "to_dict")
                    else {
                        "id": food.id,
                        "name": food.name if hasattr(food, "name") else "Unknown",
                        "description": (
                            food.description if hasattr(food, "description") else ""
                        ),
                        "price": food.price if hasattr(food, "price") else 0,
                    }
                )
                food_details.append(food_data)

            return food_details

        except Exception as e:
            logger.error(f"Error getting food details: {e}")
            return []

    def get_popular_foods(
        self, top_n: int = RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
    ) -> Any:
        """
        Get most popular foods (most rated)

        Args:
            top_n: Number of popular foods to return

        Returns:
            Dict[str, any]: Response with popular foods
        """
        try:
            # Validate top_n parameter
            if top_n < 1:
                top_n = RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
            elif top_n > RecommendationConfig.MAX_RECOMMENDATIONS:
                top_n = RecommendationConfig.MAX_RECOMMENDATIONS

            logger.info(f"Getting {top_n} popular foods")

            # Load data if needed
            if not self.recommender._load_and_validate_data():
                return error_response("Unable to load recommendation data", 500)

            # Get popular foods
            popular_food_ids = self.recommender.data_processor.get_popular_foods(top_n)

            if not popular_food_ids:
                return success_response(
                    {
                        "popular_foods": [],
                        "count": 0,
                        "message": "No popular foods available",
                    }
                )

            # Get food details
            food_details = self._get_food_details(popular_food_ids)

            response_data = {
                "popular_foods": popular_food_ids,
                "food_details": food_details,
                "count": len(popular_food_ids),
            }

            logger.info(f"Successfully retrieved {len(popular_food_ids)} popular foods")

            return success_response(response_data)

        except Exception as e:
            logger.error(f"Error getting popular foods: {e}")
            return error_response(f"Failed to get popular foods: {str(e)}", 500)

    def get_user_profile(self, user_id: str) -> Any:
        """
        Get user's rating profile and preferences

        Args:
            user_id: User ID

        Returns:
            Dict[str, any]: User profile information
        """
        try:
            # Validate user exists
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                return error_response("User not found", 404)

            logger.info(f"Getting profile for user {user_id}")

            # Load data if needed
            if not self.recommender._load_and_validate_data():
                return error_response("Unable to load recommendation data", 500)

            # Get user context
            user_context = self.recommender._get_user_context(user_id)

            # Get rated foods details
            rated_food_details = []
            if user_context["rated_foods"]:
                rated_food_details = self._get_food_details(user_context["rated_foods"])

            profile_data = {
                "user_id": user_id,
                "rating_stats": {
                    "total_ratings": user_context["rating_count"],
                    "average_rating": round(user_context["avg_rating"], 2),
                    "is_new_user": user_context["is_new_user"],
                },
                "rated_foods": user_context["rated_foods"],
                "rated_food_details": rated_food_details,
            }

            logger.info(f"Successfully retrieved profile for user {user_id}")

            return success_response(profile_data)

        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            return error_response(f"Failed to get user profile: {str(e)}", 500)

    def get_system_status(self) -> Any:
        """
        Get recommendation system status and statistics

        Returns:
            Dict[str, any]: System status information
        """
        try:
            logger.info("Getting recommendation system status")

            # Get system statistics
            stats = self.recommender.get_system_stats()

            # Add configuration information
            status_data = {
                "system_stats": stats,
                "configuration": {
                    "min_recommendations": RecommendationConfig.MIN_RECOMMENDATIONS,
                    "max_recommendations": RecommendationConfig.MAX_RECOMMENDATIONS,
                    "default_recommendations": RecommendationConfig.DEFAULT_RECOMMENDATIONS,
                    "svd_n_factors": RecommendationConfig.SVD_N_FACTORS,
                    "svd_n_epochs": RecommendationConfig.SVD_N_EPOCHS,
                },
                "health": {
                    "status": (
                        "healthy"
                        if stats.get("is_initialized", False)
                        else "initializing"
                    ),
                    "data_available": stats.get("data_stats", {}).get(
                        "total_ratings", 0
                    )
                    > 0,
                },
            }

            return success_response(status_data)

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return error_response(f"Failed to get system status: {str(e)}", 500)

    def refresh_recommendations(self) -> Any:
        """
        Force refresh of recommendation data and models

        Returns:
            Dict[str, any]: Refresh status
        """
        try:
            logger.info("Refreshing recommendation system")

            # Reset data processor and model
            self.recommender.data_processor = type(self.recommender.data_processor)()
            self.recommender.svd_model = type(self.recommender.svd_model)()
            self.recommender.is_initialized = False
            self.recommender.last_data_load = 0

            # Load fresh data
            success = self.recommender._load_and_validate_data()

            if success:
                logger.info("Recommendation system refreshed successfully")
                return success_response(
                    {
                        "message": "Recommendation system refreshed successfully",
                        "timestamp": self.recommender.last_data_load,
                    }
                )
            else:
                logger.error("Failed to refresh recommendation system")
                return error_response("Failed to refresh recommendation system", 500)

        except Exception as e:
            logger.error(f"Error refreshing recommendations: {e}")
            return error_response(f"Failed to refresh recommendations: {str(e)}", 500)


# Create singleton instance
recommendation_service = RecommendationService()
