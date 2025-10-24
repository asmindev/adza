from flask import Blueprint, request, g
from app.modules.rating.service import FoodRatingService, RestaurantRatingService
from app.utils import get_logger
logger = get_logger(__name__)
from app.utils.response import ResponseHelper
from app.utils.auth import token_required

rating_blueprint = Blueprint("rating", __name__)


@rating_blueprint.route("/foods/<string:food_id>/ratings", methods=["GET"])
def get_food_ratings(food_id):
    """
    Get all ratings for a specific food with pagination.

    Args:
        food_id (str): Food ID

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)

    Returns:
        JSON response with paginated food ratings and statistics
    """
    logger.info(
        f"GET /foods/{food_id}/ratings - Retrieving food ratings with pagination"
    )

    try:
        # Get query parameters - let service handle validation
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        logger.info(f"Pagination parameters: page={page}, limit={limit}")

        # Use service layer - it will handle validation and aggregation
        result = FoodRatingService.get_food_ratings(food_id, page=page, limit=limit)

        logger.info(
            f"Successfully retrieved {len(result['ratings'])} ratings for food {food_id}"
        )

        # Return structured response using data from service
        return ResponseHelper.success(
            data={
                "food_id": result["food_id"],
                "statistics": result["statistics"],
                "ratings": result["ratings"],
                "pagination": result["pagination"],
            },
            message="Food ratings retrieved successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve food ratings {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve food ratings")


@rating_blueprint.route("/users/<string:user_id>/ratings", methods=["GET"])
@token_required
def get_user_ratings(user_id):
    """
    Get all ratings given by a specific user.

    Args:
        user_id (str): User ID

    Returns:
        JSON response with user's ratings and summary
    """
    logger.info(f"GET /users/{user_id}/ratings - Retrieving user ratings")

    try:
        # Use service layer for validation and data retrieval
        ratings = FoodRatingService.get_user_ratings(user_id)
        summary = FoodRatingService.get_user_rating_summary(user_id)

        logger.info(f"Successfully retrieved {len(ratings)} ratings for user {user_id}")

        return ResponseHelper.success(
            data={
                "user_id": user_id,
                "summary": summary,
                "ratings": ratings,
            },
            message="User ratings retrieved successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve user ratings {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve user ratings")


@rating_blueprint.route("/ratings", methods=["POST", "PUT"])
@token_required
def rate_food():
    """
    Create or update a rating (standalone rating without review).

    Expected JSON payload (New detailed rating format):
    {
        "food_id": "string",
        "rating_details": {
            "flavor": float (1-5),
            "serving": float (1-5),
            "price": float (1-5),
            "place": float (1-5)
        }
    }

    Legacy format (still supported):
    {
        "food_id": "string",
        "rating": float (1-5)
    }

    Returns:
        JSON response with rating data
    """
    user_id = g.user_id
    method = request.method
    logger.info(
        f"{method} /ratings - {'Creating' if method == 'POST' else 'Updating'} food rating"
    )

    try:
        # Get request data
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("No data provided")

        food_id = data.get("food_id")
        rating_details = data.get("rating_details")  # New detailed rating format
        rating_value = data.get("rating")  # Legacy format

        # Use service layer - it will handle all validation
        rating = FoodRatingService.create_or_update_rating(
            user_id=user_id,
            food_id=food_id,
            rating_details=rating_details,
            rating_value=rating_value,
        )

        logger.info(
            f"Successfully {'created' if method == 'POST' else 'updated'} rating for user {user_id} and food {food_id}"
        )

        return ResponseHelper.success(
            data=rating,
            message=f"Rating {'added' if method == 'POST' else 'updated'} successfully",
            status_code=201 if method == "POST" else 200,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(
            f"Failed to {'create' if method == 'POST' else 'update'} rating: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            f"Failed to {'create' if method == 'POST' else 'update'} rating"
        )


@rating_blueprint.route(
    "/ratings/users/<string:user_id>/foods/<string:food_id>", methods=["DELETE"]
)
@token_required
def delete_rating(user_id, food_id):
    """
    Delete a rating.

    Args:
        user_id (str): User ID
        food_id (str): Food ID

    Returns:
        JSON response confirming deletion
    """
    # Verify that the authenticated user is the one deleting the rating
    if g.user_id != user_id and not getattr(g, "is_admin", False):
        logger.warning(f"User {g.user_id} attempted to delete rating of user {user_id}")
        return ResponseHelper.forbidden("You can only delete your own ratings")

    logger.info(f"DELETE /ratings/users/{user_id}/foods/{food_id} - Deleting rating")

    try:
        # Use service layer for validation and deletion
        result = FoodRatingService.delete_rating(user_id, food_id)

        if not result:
            logger.warning(f"Rating not found for user {user_id} and food {food_id}")
            return ResponseHelper.not_found("Rating")

        logger.info(
            f"Rating successfully deleted for user {user_id} and food {food_id}"
        )
        return ResponseHelper.success(message="Rating deleted successfully")

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to delete rating: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete rating")


# Restaurant Rating endpoints
@rating_blueprint.route("/restaurants/<string:restaurant_id>/ratings", methods=["GET"])
def get_restaurant_ratings(restaurant_id):
    """
    Get all ratings for a specific restaurant with pagination.

    Args:
        restaurant_id (str): Restaurant ID

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)

    Returns:
        JSON response with paginated restaurant ratings and statistics
    """
    logger.info(
        f"GET /restaurants/{restaurant_id}/ratings - Retrieving restaurant ratings"
    )

    try:
        # Get query parameters - let service handle validation
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        logger.info(f"Pagination parameters: page={page}, limit={limit}")

        # Use service layer - it will handle validation and aggregation
        result = RestaurantRatingService.get_restaurant_ratings(
            restaurant_id, page=page, limit=limit
        )

        logger.info(
            f"Successfully retrieved {len(result['ratings'])} ratings for restaurant {restaurant_id}"
        )

        # Return structured response using data from service
        return ResponseHelper.success(
            data={
                "restaurant_id": result["restaurant_id"],
                "statistics": result["statistics"],
                "ratings": result["ratings"],
                "pagination": result["pagination"],
            },
            message="Restaurant ratings retrieved successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve restaurant ratings {restaurant_id}: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to retrieve restaurant ratings"
        )


@rating_blueprint.route("/users/<string:user_id>/restaurant-ratings", methods=["GET"])
@token_required
def get_user_restaurant_ratings(user_id):
    """
    Get all restaurant ratings given by a specific user.

    Args:
        user_id (str): User ID

    Returns:
        JSON response with user's restaurant ratings
    """
    logger.info(
        f"GET /users/{user_id}/restaurant-ratings - Retrieving user restaurant ratings"
    )

    try:
        # Use service layer for validation and data retrieval
        ratings = RestaurantRatingService.get_user_restaurant_ratings(user_id)

        logger.info(
            f"Successfully retrieved {len(ratings)} restaurant ratings for user {user_id}"
        )

        return ResponseHelper.success(
            data={
                "user_id": user_id,
                "restaurant_ratings": ratings,
            },
            message="User restaurant ratings retrieved successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve user restaurant ratings {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to retrieve user restaurant ratings"
        )


@rating_blueprint.route("/restaurant-ratings", methods=["POST", "PUT"])
@token_required
def rate_restaurant():
    """
    Create or update a restaurant rating.

    Expected JSON payload:
    {
        "restaurant_id": "string",
        "rating": float (1-5),
        "comment": "string (optional)"
    }

    Returns:
        JSON response with restaurant rating data
    """
    user_id = g.user_id
    method = request.method
    logger.info(
        f"{method} /restaurant-ratings - {'Creating' if method == 'POST' else 'Updating'} restaurant rating"
    )

    try:
        # Get request data
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("No data provided")

        restaurant_id = data.get("restaurant_id")
        rating_value = data.get("rating")
        comment = data.get("comment")

        # Use service layer - it will handle all validation
        rating = RestaurantRatingService.create_or_update_rating(
            user_id, restaurant_id, rating_value, comment
        )

        logger.info(
            f"Successfully {'created' if method == 'POST' else 'updated'} restaurant rating for user {user_id}"
        )

        return ResponseHelper.success(
            data=rating,
            message=f"Restaurant rating {'added' if method == 'POST' else 'updated'} successfully",
            status_code=201 if method == "POST" else 200,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(
            f"Failed to {'create' if method == 'POST' else 'update'} restaurant rating: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            f"Failed to {'create' if method == 'POST' else 'update'} restaurant rating"
        )


@rating_blueprint.route(
    "/restaurant-ratings/users/<string:user_id>/restaurants/<string:restaurant_id>",
    methods=["DELETE"],
)
@token_required
def delete_restaurant_rating(user_id, restaurant_id):
    """
    Delete a restaurant rating.

    Args:
        user_id (str): User ID
        restaurant_id (str): Restaurant ID

    Returns:
        JSON response confirming deletion
    """
    # Verify that the authenticated user is the one deleting the rating
    if g.user_id != user_id and not getattr(g, "is_admin", False):
        logger.warning(
            f"User {g.user_id} attempted to delete restaurant rating of user {user_id}"
        )
        return ResponseHelper.forbidden("You can only delete your own ratings")

    logger.info(
        f"DELETE /restaurant-ratings/users/{user_id}/restaurants/{restaurant_id} - Deleting restaurant rating"
    )

    try:
        # Use service layer for validation and deletion
        result = RestaurantRatingService.delete_rating(user_id, restaurant_id)

        if not result:
            logger.warning(
                f"Restaurant rating not found for user {user_id} and restaurant {restaurant_id}"
            )
            return ResponseHelper.not_found("Restaurant rating")

        logger.info(
            f"Restaurant rating successfully deleted for user {user_id} and restaurant {restaurant_id}"
        )
        return ResponseHelper.success(message="Restaurant rating deleted successfully")

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to delete restaurant rating: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to delete restaurant rating"
        )


@rating_blueprint.route(
    "/restaurants/<string:restaurant_id>/ratings/stats", methods=["GET"]
)
def get_restaurant_rating_stats(restaurant_id):
    """
    Get restaurant rating statistics only.

    Args:
        restaurant_id (str): Restaurant ID

    Returns:
        JSON response with restaurant rating statistics
    """
    logger.info(
        f"GET /restaurants/{restaurant_id}/ratings/stats - Retrieving restaurant rating statistics"
    )

    try:
        # Use service layer for validation and statistics
        stats = RestaurantRatingService.get_restaurant_rating_statistics(restaurant_id)

        logger.info(
            f"Successfully retrieved rating statistics for restaurant {restaurant_id}"
        )

        return ResponseHelper.success(
            data=stats,
            message="Restaurant rating statistics retrieved successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(
            f"Failed to retrieve restaurant rating statistics {restaurant_id}: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            "Failed to retrieve restaurant rating statistics"
        )
