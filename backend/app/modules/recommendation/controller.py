from flask import Blueprint, request, g
from app.recommendation.recommender import Recommendations
from app.recommendation.config import RecommendationConfig
from app.utils import api_logger as logger
from app.utils.auth import token_required
from app.utils.response import ResponseHelper

recommendation_blueprint = Blueprint("recommendation", __name__)

# Initialize recommendation system singleton
_recommender = None


def get_recommender():
    """Get or create recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = Recommendations()
        RecommendationConfig.initialize()
    return _recommender


@recommendation_blueprint.route("/recommendation", methods=["GET"])
@token_required
def get_recommendations():
    """Get personalized food recommendations using SVD collaborative filtering"""
    # Get user_id from the request context from jwt token
    user_id = g.user_id

    logger.info(
        f"GET /recommendations - Permintaan rekomendasi makanan untuk user {user_id}"
    )

    # Get query parameters with config defaults
    limit = request.args.get(
        "limit", default=RecommendationConfig.DEFAULT_RECOMMENDATIONS, type=int
    )
    include_scores = (
        request.args.get("include_scores", default="false", type=str).lower() == "true"
    )

    logger.debug(f"Parameter: limit={limit}, include_scores={include_scores}")

    # Validate limit using config values
    if (
        limit < RecommendationConfig.MIN_RECOMMENDATIONS
        or limit > RecommendationConfig.MAX_RECOMMENDATIONS
    ):
        return ResponseHelper.validation_error(
            f"Limit must be between {RecommendationConfig.MIN_RECOMMENDATIONS} and {RecommendationConfig.MAX_RECOMMENDATIONS}"
        )

    try:
        # Get recommender instance
        recommender = get_recommender()

        # Import utility functions
        from .utils import get_food_details_batch, format_foods_response

        if include_scores:
            # Get recommendations with predicted ratings
            detailed_recommendations = recommender.recommend_with_scores(
                user_id=user_id, top_n=limit
            )

            if not detailed_recommendations:
                logger.warning(f"No recommendations found for user {user_id}")
                return ResponseHelper.success(
                    data={
                        "recommendations": [],
                        "count": 0,
                    }
                )

            # Extract food IDs
            recommended_food_ids = [rec["food_id"] for rec in detailed_recommendations]

            # Get complete food details for recommendations
            foods_data = get_food_details_batch(recommended_food_ids)
            if not foods_data:
                logger.warning("Failed to get food details for recommendations")
                return ResponseHelper.success(
                    data={
                        "recommendations": [],
                        "count": 0,
                    }
                )

            # Format response and merge with predicted ratings
            formatted_foods = format_foods_response(foods_data)

            # Create food_id to index mapping for easy lookup
            food_id_map = {food["id"]: food for food in formatted_foods}

            # Enrich with predicted ratings
            enriched_recommendations = []
            for rec in detailed_recommendations:
                food_id = rec["food_id"]
                if food_id in food_id_map:
                    food_data = food_id_map[food_id].copy()
                    food_data["predicted_rating"] = rec["predicted_rating"]
                    food_data["rank"] = rec["rank"]
                    enriched_recommendations.append(food_data)

            logger.info(
                f"Mengembalikan {len(enriched_recommendations)} rekomendasi dengan predicted ratings untuk user {user_id}"
            )

            return ResponseHelper.success(
                data={
                    "recommendations": enriched_recommendations,
                    "count": len(enriched_recommendations),
                }
            )

        else:
            # Legacy mode: only food IDs without scores
            recommended_food_ids = recommender.recommend(user_id=user_id, top_n=limit)

            if not recommended_food_ids:
                logger.warning(f"No recommendations found for user {user_id}")
                return ResponseHelper.success(
                    data={
                        "recommendations": [],
                        "count": 0,
                    }
                )

            # Get complete food details for recommendations
            foods_data = get_food_details_batch(recommended_food_ids)
            if not foods_data:
                logger.warning("Failed to get food details for recommendations")
                return ResponseHelper.success(
                    data={
                        "recommendations": [],
                        "count": 0,
                    }
                )

            # Format response
            formatted_foods = format_foods_response(foods_data)

            logger.info(
                f"Mengembalikan {len(recommended_food_ids)} rekomendasi untuk user {user_id}"
            )

            return ResponseHelper.success(
                data={
                    "recommendations": formatted_foods,
                    "count": len(recommended_food_ids),
                }
            )

    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get recommendations")


@recommendation_blueprint.route("/popular", methods=["GET"])
def get_popular_foods():
    """Get popular foods based on rating count and total ratings"""
    try:
        # Get query parameters
        limit = request.args.get("limit", default=10, type=int)
        min_ratings = request.args.get("min_ratings", default=5, type=int)

        # Validate limit
        if limit < 1 or limit > 50:
            return ResponseHelper.validation_error("Limit must be between 1 and 50")

        logger.info(
            f"GET /popular - Getting popular foods with limit={limit}, min_ratings={min_ratings}"
        )

        # Import utility functions
        from .utils import (
            get_popular_foods_data,
            format_foods_response,
            get_food_details_batch,
        )

        # Get popular foods data
        popular_foods_data = get_popular_foods_data(
            limit=limit, min_ratings=min_ratings
        )

        if not popular_foods_data:
            logger.info("No popular foods found")
            return ResponseHelper.success(
                data={
                    "popular_foods": [],
                    "count": 0,
                }
            )

        # Extract food IDs and popularity metrics
        food_ids = [food["id"] for food in popular_foods_data]
        popularity_metrics = {
            food["id"]: {
                "rating_count": food["rating_count"],
                "average_rating": food["average_rating"],
                "total_rating_score": food["total_rating_score"],
            }
            for food in popular_foods_data
        }

        # Get complete food details
        foods_data = get_food_details_batch(food_ids)
        if not foods_data:
            logger.warning("Failed to get food details for popular foods")
            return ResponseHelper.success(
                data={
                    "popular_foods": [],
                    "count": 0,
                }
            )

        # Format response
        formatted_foods = format_foods_response(foods_data)

        # Add popularity metrics to each food
        for food in formatted_foods:
            metrics = popularity_metrics.get(food["id"], {})
            food["rating_count"] = metrics.get("rating_count", 0)
            food["average_rating"] = metrics.get("average_rating", 0.0)
            food["total_rating_score"] = metrics.get("total_rating_score", 0.0)

        logger.info(f"Returning {len(formatted_foods)} popular foods")

        return ResponseHelper.success(
            data={
                "popular_foods": formatted_foods,
                "count": len(formatted_foods),
            }
        )

    except Exception as e:
        logger.error(f"Error getting popular foods: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get popular foods")
