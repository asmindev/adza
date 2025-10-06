"""
Recommendation Service
Public API for the recommendation system
"""

from typing import List, Dict, Any
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
        include_scores: bool = False,
    ) -> Any:
        """
        Get food recommendations for a user

        Args:
            user_id: User ID to get recommendations for
            top_n: Number of recommendations to return
            include_scores: If True, include predicted ratings in response

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

            logger.info(
                f"Getting {top_n} recommendations for user {user_id} (include_scores={include_scores})"
            )

            # Get recommendations with or without scores
            if include_scores:
                detailed_recs = self.recommender.recommend_with_scores(user_id, top_n)

                if not detailed_recs:
                    return success_response(
                        {
                            "recommendations": [],
                            "count": 0,
                        }
                    )

                # Extract food IDs for getting details
                recommended_food_ids = [rec["food_id"] for rec in detailed_recs]

                # Get food details
                food_details = self._get_food_details(recommended_food_ids)

                # Merge food details with predicted ratings
                enriched_recommendations = []
                for rec in detailed_recs:
                    food_id = rec["food_id"]
                    # Find matching food detail
                    food_detail = next(
                        (f for f in food_details if f["id"] == food_id), None
                    )
                    if food_detail:
                        enriched_recommendations.append(
                            {
                                **food_detail,
                                "predicted_rating": rec["predicted_rating"],
                                "rank": rec["rank"],
                            }
                        )

                response_data = {
                    "recommendations": enriched_recommendations,
                    "count": len(enriched_recommendations),
                }
            else:
                # Legacy mode: only food IDs
                recommended_food_ids = self.recommender.recommend(user_id, top_n)

                if not recommended_food_ids:
                    return success_response(
                        {
                            "recommendations": [],
                            "count": 0,
                        }
                    )

                # Get food details
                food_details = self._get_food_details(recommended_food_ids)

                response_data = {
                    "recommendations": recommended_food_ids,
                    "food_details": food_details,
                    "count": len(recommended_food_ids),
                }

            logger.info(
                f"Successfully generated {response_data['count']} recommendations for user {user_id}"
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


# Create singleton instance
recommendation_service = RecommendationService()
