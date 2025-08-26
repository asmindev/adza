from flask import Blueprint, request, g
from app.modules.review.service import ReviewService
from app.modules.rating.service import RatingService
from app.utils import api_logger as logger
from app.utils.response import ResponseHelper
from app.utils.auth import token_required

review_blueprint = Blueprint("review", __name__)


@review_blueprint.route("/foods/<string:food_id>/reviews", methods=["GET"])
@token_required
def get_food_reviews(food_id):
    """
    Get all reviews for a specific food with pagination.

    Args:
        food_id (str): Food ID

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)

    Returns:
        JSON response with paginated food reviews
    """
    logger.info(
        f"GET /foods/{food_id}/reviews - Mengambil review makanan dengan pagination"
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
        # Get reviews with pagination
        result = ReviewService.get_food_reviews(food_id, page=page, limit=limit)

        reviews = result["items"]
        logger.info(
            f"Berhasil mengambil {len(reviews)} review untuk makanan {food_id} dari total {result['total']}"
        )

        # Return custom structured response
        return ResponseHelper.success(
            data={
                "food_id": food_id,
                "reviews": [review.to_dict() for review in reviews],
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            },
            message="Food reviews retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil review makanan {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve food reviews")


@review_blueprint.route("/users/<string:user_id>/reviews", methods=["GET"])
@token_required
def get_user_reviews(user_id):
    """
    Get all reviews written by a specific user with pagination.

    Args:
        user_id (str): User ID

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)

    Returns:
        JSON response with paginated user reviews
    """
    logger.info(
        f"GET /users/{user_id}/reviews - Mengambil review pengguna dengan pagination"
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
        # Get reviews with pagination
        result = ReviewService.get_user_reviews(user_id, page=page, limit=limit)

        reviews = result["items"]
        logger.info(
            f"Berhasil mengambil {len(reviews)} review dari pengguna {user_id} dari total {result['total']}"
        )

        # Return custom structured response
        return ResponseHelper.success(
            data={
                "user_id": user_id,
                "reviews": [review.to_dict() for review in reviews],
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            },
            message="User reviews retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil review pengguna {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve user reviews")


@review_blueprint.route("/reviews", methods=["POST", "PUT"])
@token_required
def review_food():
    """
    Create or update a review for a food with mandatory rating.

    Expected JSON payload:
    {
        "food_id": "string",
        "rating": float (1-5),
        "content": "string"
    }

    Returns:
        JSON response with review and rating data
    """
    # Verify that the authenticated user is the one making the review
    data = request.get_json()
    user_id = g.user_id
    food_id = data.get("food_id") if data else None
    rating = data.get("rating") if data else None
    content = data.get("content") if data else None

    logger.info(f"User ID from token: {user_id}")
    logger.info(f"Food ID from request: {food_id}")
    logger.info(f"Rating from request: {rating}")
    logger.info(f"Content from request: {content}")

    method = request.method
    logger.info(
        f"{method} /reviews - {'Membuat' if method == 'POST' else 'Memperbarui'} review dengan rating"
    )

    # Validasi input
    if not data:
        logger.warning("Permintaan tidak valid: data tidak diberikan")
        return ResponseHelper.validation_error("Request data is required")

    if not food_id:
        logger.warning("Permintaan tidak valid: food_id tidak diberikan")
        return ResponseHelper.validation_error("Food ID is required")

    if not content or not content.strip():
        logger.warning("Permintaan tidak valid: teks review tidak diberikan")
        return ResponseHelper.validation_error("Review content is required")

    if not rating or not isinstance(rating, (int, float)) or not (1 <= rating <= 5):
        logger.warning(f"Permintaan tidak valid: rating tidak valid {rating}")
        return ResponseHelper.validation_error(
            "Rating is required and must be between 1 and 5"
        )

    try:
        # Import services here to avoid circular imports
        from app.modules.rating.service import RatingService

        # Create or update rating first
        rating_result = RatingService.create_rating(user_id, food_id, rating)
        if not rating_result:
            logger.error("Gagal membuat/memperbarui rating")
            return ResponseHelper.internal_server_error("Failed to save rating")

        # Create or update review
        review = ReviewService.create_or_update_review(
            user_id, food_id, content.strip()
        )
        if not review:
            logger.error("Gagal membuat/memperbarui review")
            return ResponseHelper.internal_server_error("Failed to save review")

        logger.info(
            f"Berhasil {'membuat' if method == 'POST' else 'memperbarui'} review dan rating"
        )

        return ResponseHelper.success(
            data={"review": review.to_dict(), "rating": rating_result},
            message=f"Review and rating {'added' if method == 'POST' else 'updated'} successfully",
            status_code=201 if method == "POST" else 200,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(
            f"Gagal {'membuat' if method == 'POST' else 'memperbarui'} review dan rating: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            f"Failed to {'create' if method == 'POST' else 'update'} review and rating"
        )


@review_blueprint.route(
    "/users/<string:user_id>/foods/<string:food_id>/review", methods=["GET"]
)
@token_required
def get_user_food_review(user_id, food_id):
    """
    Get user's review and rating for a specific food.

    Args:
        user_id (str): User ID
        food_id (str): Food ID

    Returns:
        JSON response with user's review and rating for the food
    """
    # Verify that the authenticated user is the one requesting the review
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to access review of user {user_id}")
        return ResponseHelper.forbidden("You can only access your own reviews")

    logger.info(
        f"GET /users/{user_id}/foods/{food_id}/review - Mengambil review dan rating user"
    )

    try:
        # Get review
        review = ReviewService.get_review(user_id, food_id)

        # Get rating
        from app.modules.rating.service import RatingService

        rating = RatingService.get_user_food_rating(user_id, food_id)

        response_data = {
            "user_id": user_id,
            "food_id": food_id,
            "review": review.to_dict() if review else None,
            "rating": rating if rating else None,
        }

        logger.info(
            f"Berhasil mengambil data review dan rating untuk user {user_id} dan food {food_id}"
        )
        return ResponseHelper.success(
            data=response_data, message="Review and rating retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Gagal mengambil review dan rating: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get review and rating")


@review_blueprint.route(
    "/users/<string:user_id>/foods/<string:food_id>/review", methods=["DELETE"]
)
@token_required
def delete_review(user_id, food_id):
    """
    Delete a review but keep the rating.

    Args:
        user_id (str): User ID
        food_id (str): Food ID

    Returns:
        JSON response confirming deletion
    """
    # Verify that the authenticated user is the one deleting the review
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to delete review of user {user_id}")
        return ResponseHelper.forbidden("You can only delete your own reviews")

    logger.info(f"DELETE /users/{user_id}/foods/{food_id}/review - Menghapus review")

    try:
        result = ReviewService.delete_review(user_id, food_id)
        if not result:
            logger.warning(
                f"Review tidak ditemukan untuk pengguna {user_id} dan makanan {food_id}"
            )
            return ResponseHelper.not_found("Review")

        logger.info(
            f"Review berhasil dihapus untuk pengguna {user_id} dan makanan {food_id}"
        )
        return ResponseHelper.success(message="Review deleted successfully")
    except Exception as e:
        logger.error(f"Gagal menghapus review: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete review")
