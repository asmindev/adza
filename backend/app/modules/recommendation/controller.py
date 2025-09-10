from flask import Blueprint, request, g
from app.recommendation.service import Recomendations
from app.recommendation.config import RecommendationConfig
from app.utils import api_logger as logger
from app.utils.auth import token_required
from app.utils.response import ResponseHelper

recommendation_blueprint = Blueprint("recommendation", __name__)


@recommendation_blueprint.route("/recommendation", methods=["GET"])
@token_required
def get_recommendations():
    """Get personalized food recommendations using enhanced collaborative filtering"""
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
        "alpha", default=RecommendationConfig.DEFAULT_ALPHA, type=float
    )
    beta = request.args.get(
        "beta", default=RecommendationConfig.DEFAULT_BETA, type=float
    )
    gamma = request.args.get(
        "gamma", default=RecommendationConfig.DEFAULT_GAMMA, type=float
    )

    # Get price preference parameters
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    preferred_price = request.args.get("preferred_price", type=float)

    logger.debug(f"Parameter: limit={limit}, alpha={alpha}, beta={beta}, gamma={gamma}")
    logger.debug(
        f"Price preference: min_price={min_price}, max_price={max_price}, preferred_price={preferred_price}"
    )

    # Validate limit using config values
    if (
        limit < RecommendationConfig.MIN_RECOMMENDATIONS
        or limit > RecommendationConfig.MAX_RECOMMENDATIONS
    ):
        return ResponseHelper.validation_error(
            f"Limit must be between {RecommendationConfig.MIN_RECOMMENDATIONS} and {RecommendationConfig.MAX_RECOMMENDATIONS}"
        )

    # # Validate enhancement parameters using config method
    # is_valid, error_msg = RecommendationConfig.validate_enhancement_params(
    #     alpha, beta, gamma
    # )
    # if not is_valid:
    #     return ResponseHelper.validation_error(error_msg)

    try:
        # Calculate user price preferences
        user_price_preferences = {}
        price_filter = {}

        # Option 1: User provides specific preferred price
        if preferred_price:
            user_price_preferences[user_id] = preferred_price
            logger.info(f"Using user specified preferred price: {preferred_price}")

        # Option 2: User provides price range (min and max)
        elif min_price and max_price:
            if min_price > max_price:
                return ResponseHelper.validation_error(
                    "min_price cannot be greater than max_price"
                )

            # Calculate preferred price as the middle of the range
            calculated_preferred_price = (min_price + max_price) / 2
            user_price_preferences[user_id] = calculated_preferred_price
            # Set price filter for recommendations
            price_filter = {"min_price": min_price, "max_price": max_price}
            logger.info(
                f"Calculated preferred price from range {min_price}-{max_price}: {calculated_preferred_price}"
            )
            logger.info(f"Set price filter: {price_filter}")

        # Option 3: Only min_price provided
        elif min_price:
            # Use min_price + 25% as preferred
            calculated_preferred_price = min_price * 1.25
            user_price_preferences[user_id] = calculated_preferred_price
            price_filter = {"min_price": min_price}
            logger.info(
                f"Calculated preferred price from min_price {min_price}: {calculated_preferred_price}"
            )
            logger.info(f"Set price filter: {price_filter}")

        # Option 4: Only max_price provided
        elif max_price:
            # Use max_price - 25% as preferred
            calculated_preferred_price = max_price * 0.75
            user_price_preferences[user_id] = calculated_preferred_price
            price_filter = {"max_price": max_price}
            logger.info(
                f"Calculated preferred price from max_price {max_price}: {calculated_preferred_price}"
            )
            logger.info(f"Set price filter: {price_filter}")

        else:
            # No price preference provided, beta parameter will not be effective
            logger.info("No price preference provided, using empty preferences")

        # Call the unified get_recommendations method
        rec_system = Recomendations(alpha=alpha)
        # Train the system first
        train_results = rec_system.train_full_system()

        if not train_results["success"]:
            logger.error(
                f"Failed to train recommendation system: {train_results['error']}"
            )
            return ResponseHelper.internal_server_error(
                "Recommendation system training failed"
            )

        recommendations = rec_system.get_recommendations(
            user_id=user_id,
            user_price_preferences=user_price_preferences,
            price_filter=price_filter,
            n=limit,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )
        logger.info(recommendations)

        if recommendations is None:
            logger.warning(f"User {user_id} tidak ditemukan")
            return ResponseHelper.not_found("User")

        if len(recommendations) == 0:
            logger.info(
                f"Tidak ada rekomendasi untuk user {user_id}, menggunakan makanan populer"
            )
            # Fallback to popular foods
            rec_system_fallback = Recomendations()
            popular_foods = rec_system_fallback.get_popular_foods(n=limit)
            logger.info(popular_foods)
            if popular_foods:
                return ResponseHelper.success(
                    data={
                        "recommendations": popular_foods,
                        "fallback": True,
                        "message": "Menggunakan makanan populer karena tidak ada rekomendasi personal",
                    }
                )
            else:
                return ResponseHelper.not_found("No recommendations available")

        logger.info(
            f"Mengembalikan {len(recommendations)} rekomendasi untuk user {user_id}"
        )

        return ResponseHelper.success(
            data={
                "recommendations": recommendations,
                "fallback": False,
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
        # Get top-rated foods using the service
        rec_system_top = Recomendations()
        top_rated_foods = rec_system_top.get_popular_foods(
            n=RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
        )
        if not top_rated_foods:
            logger.info("Tidak ada makanan teratas ditemukan")
            return ResponseHelper.not_found("No top-rated foods found")

        return ResponseHelper.success(data={"top_rated": top_rated_foods})

    except Exception as e:
        logger.error(f"Error getting top-rated foods: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get top-rated foods")
