from flask import Blueprint, request, g
from app.recommendation.recommender import Recommendations
from app.recommendation.config import RecommendationConfig
from app.utils import api_logger as logger
from app.utils.auth import token_required
from app.utils.response import ResponseHelper

recommendation_blueprint = Blueprint("recommendation", __name__)


@recommendation_blueprint.route("/recommendation", methods=["GET"])
@token_required
def get_recommendations():
    """Get personalized food recommendations using hybrid collaborative filtering"""
    # Get user_id from the request context from jwt token
    user_id = g.user_id

    logger.info(
        f"GET /recommendations - Permintaan rekomendasi makanan untuk user {user_id}"
    )

    # Get query parameters with config defaults
    limit = request.args.get(
        "limit", default=RecommendationConfig.DEFAULT_RECOMMENDATIONS, type=int
    )
    alpha = request.args.get(
        "alpha", default=RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA, type=float
    )
    enable_hybrid = (
        request.args.get("hybrid", default="true", type=str).lower() == "true"
    )

    logger.debug(f"Parameter: limit={limit}, alpha={alpha}, hybrid={enable_hybrid}")

    # Validate limit using config values
    if (
        limit < RecommendationConfig.MIN_RECOMMENDATIONS
        or limit > RecommendationConfig.MAX_RECOMMENDATIONS
    ):
        return ResponseHelper.validation_error(
            f"Limit must be between {RecommendationConfig.MIN_RECOMMENDATIONS} and {RecommendationConfig.MAX_RECOMMENDATIONS}"
        )

    # Validate alpha parameter (0.0 to 1.0)
    if not (0.0 <= alpha <= 1.0):
        return ResponseHelper.validation_error(
            "Alpha parameter must be between 0.0 and 1.0"
        )

    try:
        # Initialize recommendation system with hybrid scoring
        rec_system = Recommendations(alpha=alpha)

        # Configure hybrid scoring
        rec_system.enable_hybrid_scoring(enable_hybrid)

        logger.info(
            f"Hybrid scoring: {'enabled' if enable_hybrid else 'disabled'}, alpha={alpha}"
        )

        # Generate recommendations using the new API with scores
        recommendations, predicted_scores = rec_system.recommend_with_scores(
            user_id=user_id, top_n=limit
        )

        if recommendations is None or len(recommendations) == 0:
            logger.warning(f"User {user_id} tidak ditemukan atau tidak ada rekomendasi")
            # Fallback to popular foods using the data processor
            popular_food_ids = rec_system.data_processor.get_popular_foods(top_n=limit)
            logger.info(f"Generated {len(popular_food_ids)} popular foods as fallback")

            if popular_food_ids:
                # Import utility functions
                from .utils import get_food_details_batch, format_foods_response

                # Get complete food details for fallback
                foods_data = get_food_details_batch(popular_food_ids)
                fallback_scores = {food_id: 3.5 for food_id in popular_food_ids}
                formatted_foods = format_foods_response(foods_data, fallback_scores)

                return ResponseHelper.success(
                    data={
                        "recommendations": formatted_foods,
                        "fallback": True,
                        "hybrid_info": rec_system.get_hybrid_info(),
                        "system_stats": rec_system.get_system_stats(),
                        "message": "Menggunakan makanan populer karena tidak ada rekomendasi personal",
                    }
                )
            else:
                return ResponseHelper.not_found("No recommendations available")

        # Import utility functions
        from .utils import get_food_details_batch, format_foods_response

        # Get complete food details for recommendations
        foods_data = get_food_details_batch(recommendations)
        if not foods_data:
            logger.warning("Failed to get food details for recommendations")
            return ResponseHelper.not_found("No food details found")

        # Format response with predicted ratings
        formatted_foods = format_foods_response(foods_data, predicted_scores)

        # Get additional information about the recommendation process
        hybrid_info = rec_system.get_hybrid_info()
        system_stats = rec_system.get_system_stats()

        logger.info(
            f"Mengembalikan {len(recommendations)} rekomendasi untuk user {user_id}"
        )
        logger.info(f"Hybrid info: {hybrid_info}")
        logger.info(
            f"Restaurant coverage: {system_stats.get('hybrid_coverage', 0)*100:.1f}%"
        )

        return ResponseHelper.success(
            data={
                "recommendations": formatted_foods,
                "fallback": False,
                "hybrid_info": hybrid_info,
                "system_stats": system_stats,
            }
        )

    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get recommendations")


# before : top-rated
@recommendation_blueprint.route("/popular", methods=["GET"])
def get_popular():
    """Get popular foods based on user ratings"""
    logger.info("GET /popular - Mengambil makanan populer berdasarkan rating pengguna")
    try:
        # Import utility function
        from .utils import get_food_details_batch, format_foods_response

        # Get top-rated foods using the data processor
        rec_system_top = Recommendations()
        top_rated_food_ids = rec_system_top.data_processor.get_popular_foods(
            top_n=RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
        )
        if not top_rated_food_ids:
            logger.info("Tidak ada makanan teratas ditemukan")
            return ResponseHelper.not_found("No top-rated foods found")

        # Get complete food details
        foods_data = get_food_details_batch(top_rated_food_ids)
        if not foods_data:
            logger.warning("Failed to get food details for popular foods")
            return ResponseHelper.not_found("No food details found")

        # Format response as required
        formatted_foods = format_foods_response(foods_data)

        return ResponseHelper.success(data=formatted_foods)

    except Exception as e:
        logger.error(f"Error getting top-rated foods: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get top-rated foods")


@recommendation_blueprint.route("/hybrid-info", methods=["GET"])
def get_hybrid_info():
    """Get information about the hybrid scoring system"""
    logger.info("GET /hybrid-info - Mengambil informasi hybrid scoring system")
    try:
        # Get alpha parameter from query (optional)
        alpha = request.args.get(
            "alpha",
            default=RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA,
            type=float,
        )

        # Validate alpha parameter
        if not (0.0 <= alpha <= 1.0):
            return ResponseHelper.validation_error(
                "Alpha parameter must be between 0.0 and 1.0"
            )

        # Initialize recommendation system
        rec_system = Recommendations(alpha=alpha)

        # Get hybrid info and system stats
        hybrid_info = rec_system.get_hybrid_info()
        system_stats = rec_system.get_system_stats()

        # Get rating statistics from data processor
        rating_stats = rec_system.data_processor.get_rating_statistics()

        return ResponseHelper.success(
            data={
                "hybrid_info": hybrid_info,
                "system_stats": system_stats,
                "rating_statistics": rating_stats,
                "config": {
                    "default_alpha": RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA,
                    "min_recommendations": RecommendationConfig.MIN_RECOMMENDATIONS,
                    "max_recommendations": RecommendationConfig.MAX_RECOMMENDATIONS,
                    "default_recommendations": RecommendationConfig.DEFAULT_RECOMMENDATIONS,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting hybrid info: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get hybrid info")
