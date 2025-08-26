from flask import Blueprint, request, g
from app.modules.rating.service import FoodRatingService, RestaurantRatingService
from app.utils import api_logger as logger
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
        JSON response with paginated food ratings
    """
    logger.info(
        f"GET /foods/{food_id}/ratings - Mengambil rating makanan dengan pagination"
    )

    # Get query parameters with defaults
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    # Log the pagination parameters
    logger.info(f"Pagination parameters: page={page}, limit={limit}")

    try:
        # Get ratings with pagination
        result = FoodRatingService.get_food_ratings(food_id, page=page, limit=limit)
        avg_rating = FoodRatingService.get_food_average_rating(food_id)

        logger.info(
            f"Berhasil mengambil {len(result['items'])} rating untuk makanan {food_id} dari total {result['total']}"
        )

        # Return custom structured response
        return ResponseHelper.success(
            data={
                "food_id": food_id,
                "average_rating": avg_rating,
                "rating_count": result["total"],
                "ratings": result["items"],
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            },
            message="Food ratings retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil rating makanan {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve food ratings")


@rating_blueprint.route("/users/<string:user_id>/ratings", methods=["GET"])
@token_required
def get_user_ratings(user_id):
    """
    Get all ratings given by a specific user.

    Args:
        user_id (str): User ID

    Returns:
        JSON response with user's ratings
    """
    logger.info(f"GET /users/{user_id}/ratings - Mengambil semua rating pengguna")

    try:
        ratings = FoodRatingService.get_user_ratings(user_id)

        logger.info(
            f"Berhasil mengambil {len(ratings)} rating untuk pengguna {user_id}"
        )
        return ResponseHelper.success(
            data={
                "user_id": user_id,
                "ratings": [rating.to_dict() for rating in ratings],
            },
            message="User ratings retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil rating pengguna {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve user ratings")


# @rating_blueprint.route(
#     "/users/<int:user_id>/foods/<int:food_id>/rating", methods=["POST", "PUT"]
# )


@rating_blueprint.route("/ratings", methods=["POST", "PUT"])
@token_required
def rate_food():
    """
    Create or update a rating (standalone rating without review).

    Expected JSON payload:
    {
        "food_id": "string",
        "rating": float (1-5)
    }

    Note: It's recommended to use the /reviews endpoint which handles
    both rating and review together for better user experience.

    Returns:
        JSON response with rating data
    """
    # Verify that the authenticated user is the one making the rating
    user_id = g.user_id
    data = request.get_json()
    food_id = data.get("food_id") if data else None

    method = request.method
    logger.info(
        f"{method} /ratings - {'Membuat' if method == 'POST' else 'Memperbarui'} rating standalone"
    )

    if not data or "rating" not in data:
        logger.warning(f"Permintaan tidak valid: nilai rating tidak diberikan")
        return ResponseHelper.validation_error("Rating value is required")

    if not food_id:
        logger.warning(f"Permintaan tidak valid: food_id tidak diberikan")
        return ResponseHelper.validation_error("Food ID is required")

    rating_value = data["rating"]
    try:
        rating_value = float(rating_value)
        if not (1 <= rating_value <= 5):
            logger.warning(
                f"Nilai rating tidak valid: {rating_value} (harus antara 1 dan 5)"
            )
            return ResponseHelper.validation_error("Rating must be between 1 and 5")
    except ValueError:
        logger.warning(f"Nilai rating bukan angka: {rating_value}")
        return ResponseHelper.validation_error("Rating must be a number")

    try:
        rating = FoodRatingService.create_rating(
            user_id,
            food_id,
            rating_value,
        )

        if not rating:
            return ResponseHelper.not_found("User or food")

        logger.info(
            f"Berhasil {'membuat' if method == 'POST' else 'memperbarui'} rating pengguna {user_id} untuk makanan {food_id}"
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
            f"Gagal {'membuat' if method == 'POST' else 'memperbarui'} rating: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            f"Failed to {'create' if method == 'POST' else 'update'} rating"
        )


@rating_blueprint.route(
    "ratings/users/<string:user_id>/foods/<string:food_id>/rating", methods=["DELETE"]
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
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to delete rating of user {user_id}")
        return ResponseHelper.forbidden("You can only delete your own ratings")

    logger.info(f"DELETE /users/{user_id}/foods/{food_id}/rating - Menghapus rating")
    try:
        result = FoodRatingService.delete_rating(user_id, food_id)
        if not result:
            logger.warning(
                f"Rating tidak ditemukan untuk pengguna {user_id} dan makanan {food_id}"
            )
            return ResponseHelper.not_found("Rating")

        logger.info(
            f"Rating berhasil dihapus untuk pengguna {user_id} dan makanan {food_id}"
        )
        return ResponseHelper.success(message="Rating deleted successfully")
    except Exception as e:
        logger.error(f"Gagal menghapus rating: {str(e)}")
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
        JSON response with paginated restaurant ratings
    """
    logger.info(
        f"GET /restaurants/{restaurant_id}/ratings - Mengambil rating restaurant dengan pagination"
    )

    # Get query parameters with defaults
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    # Log the pagination parameters
    logger.info(f"Pagination parameters: page={page}, limit={limit}")

    try:
        # Get ratings with pagination
        result = RestaurantRatingService.get_restaurant_ratings(
            restaurant_id, page=page, limit=limit
        )
        stats = RestaurantRatingService.get_restaurant_rating_stats(restaurant_id)

        logger.info(
            f"Berhasil mengambil {len(result['items'])} rating untuk restaurant {restaurant_id} dari total {result['total']}"
        )

        # Return custom structured response
        return ResponseHelper.success(
            data={
                "restaurant_id": restaurant_id,
                "average_rating": stats["average_rating"],
                "rating_count": stats["total_ratings"],
                "ratings": [rating.to_dict() for rating in result["items"]],
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            },
            message="Restaurant ratings retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil rating restaurant {restaurant_id}: {str(e)}")
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
        f"GET /users/{user_id}/restaurant-ratings - Mengambil semua rating restaurant pengguna"
    )

    try:
        ratings = RestaurantRatingService.get_user_restaurant_ratings(user_id)

        logger.info(
            f"Berhasil mengambil {len(ratings)} rating restaurant untuk pengguna {user_id}"
        )
        return ResponseHelper.success(
            data={
                "user_id": user_id,
                "restaurant_ratings": [rating.to_dict() for rating in ratings],
            },
            message="User restaurant ratings retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil rating restaurant pengguna {user_id}: {str(e)}")
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
    data = request.get_json()
    restaurant_id = data.get("restaurant_id") if data else None
    comment = data.get("comment") if data else None

    method = request.method
    logger.info(
        f"{method} /restaurant-ratings - {'Membuat' if method == 'POST' else 'Memperbarui'} rating restaurant"
    )

    if not data or "rating" not in data or "restaurant_id" not in data:
        logger.warning(
            f"Permintaan tidak valid: nilai rating atau restaurant_id tidak diberikan"
        )
        return ResponseHelper.validation_error(
            "Rating value and restaurant_id are required"
        )

    rating_value = data["rating"]
    try:
        rating_value = float(rating_value)
        if not (1 <= rating_value <= 5):
            logger.warning(
                f"Nilai rating tidak valid: {rating_value} (harus antara 1 dan 5)"
            )
            return ResponseHelper.validation_error("Rating must be between 1 and 5")
    except ValueError:
        logger.warning(f"Nilai rating bukan angka: {rating_value}")
        return ResponseHelper.validation_error("Rating must be a number")

    try:
        rating = RestaurantRatingService.create_or_update_rating(
            user_id, restaurant_id, rating_value, comment
        )

        if not rating:
            return ResponseHelper.not_found("User or restaurant")

        logger.info(
            f"Berhasil {'membuat' if method == 'POST' else 'memperbarui'} rating restaurant {restaurant_id} dari pengguna {user_id}"
        )
        return ResponseHelper.success(
            data=rating.to_dict(),
            message=f"Restaurant rating {'added' if method == 'POST' else 'updated'} successfully",
            status_code=201 if method == "POST" else 200,
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(
            f"Gagal {'membuat' if method == 'POST' else 'memperbarui'} rating restaurant: {str(e)}"
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
    if g.user_id != user_id and not g.is_admin:
        logger.warning(
            f"User {g.user_id} attempted to delete restaurant rating of user {user_id}"
        )
        return ResponseHelper.forbidden("You can only delete your own ratings")

    logger.info(
        f"DELETE /restaurant-ratings/users/{user_id}/restaurants/{restaurant_id} - Menghapus rating restaurant"
    )
    try:
        result = RestaurantRatingService.delete_rating(user_id, restaurant_id)
        if not result:
            logger.warning(
                f"Rating restaurant tidak ditemukan untuk pengguna {user_id} dan restaurant {restaurant_id}"
            )
            return ResponseHelper.not_found("Restaurant rating")

        logger.info(
            f"Rating restaurant berhasil dihapus untuk pengguna {user_id} dan restaurant {restaurant_id}"
        )
        return ResponseHelper.success(message="Restaurant rating deleted successfully")
    except Exception as e:
        logger.error(f"Gagal menghapus rating restaurant: {str(e)}")
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
        f"GET /restaurants/{restaurant_id}/ratings/stats - Mengambil statistik rating restaurant"
    )

    try:
        stats = RestaurantRatingService.get_restaurant_rating_stats(restaurant_id)

        logger.info(
            f"Berhasil mengambil statistik rating untuk restaurant {restaurant_id}"
        )
        return ResponseHelper.success(
            data={
                "restaurant_id": restaurant_id,
                "average_rating": stats["average_rating"],
                "total_ratings": stats["total_ratings"],
            },
            message="Restaurant rating statistics retrieved successfully",
        )
    except Exception as e:
        logger.error(
            f"Gagal mengambil statistik rating restaurant {restaurant_id}: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            "Failed to retrieve restaurant rating statistics"
        )
