from flask import Blueprint, request, jsonify, g
from app.modules.review.service import ReviewService
from app.modules.rating.service import RatingService
from app.utils import api_logger as logger
from app.utils.auth import token_required

review_blueprint = Blueprint("review", __name__)


@review_blueprint.route("/foods/<string:food_id>/reviews", methods=["GET"])
@token_required
def get_food_reviews(food_id):
    """Get all reviews for a specific food with pagination"""
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

    # Get reviews with pagination
    result = ReviewService.get_food_reviews(food_id, page=page, limit=limit)

    reviews = result["items"]
    logger.info(
        f"Berhasil mengambil {len(reviews)} review untuk makanan {food_id} dari total {result['total']}"
    )

    # Return paginated response
    return (
        jsonify(
            {
                "error": False,
                "data": {
                    "food_id": food_id,
                    "reviews": [review.to_dict() for review in reviews],
                    "pagination": {
                        "page": result["page"],
                        "limit": result["limit"],
                        "total": result["total"],
                        "pages": result["pages"],
                    },
                },
            }
        ),
        200,
    )


@review_blueprint.route("/users/<string:user_id>/reviews", methods=["GET"])
@token_required
def get_user_reviews(user_id):
    """Get all reviews written by a specific user with pagination"""
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

    # Get reviews with pagination
    result = ReviewService.get_user_reviews(user_id, page=page, limit=limit)

    reviews = result["items"]
    logger.info(
        f"Berhasil mengambil {len(reviews)} review dari pengguna {user_id} dari total {result['total']}"
    )

    # Return paginated response
    return (
        jsonify(
            {
                "error": False,
                "data": {
                    "user_id": user_id,
                    "reviews": [review.to_dict() for review in reviews],
                    "pagination": {
                        "page": result["page"],
                        "limit": result["limit"],
                        "total": result["total"],
                        "pages": result["pages"],
                    },
                },
            }
        ),
        200,
    )


@review_blueprint.route("/reviews", methods=["POST", "PUT"])
@token_required
def review_food():
    """Create or update a review for a food with mandatory rating"""
    # Verify that the authenticated user is the one making the review
    data = request.get_json()
    user_id = g.user_id
    food_id = data.get("food_id")
    rating = data.get("rating")
    content = data.get("content")
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
        return jsonify({"error": True, "message": "Request data is required"}), 400

    if not food_id:
        logger.warning("Permintaan tidak valid: food_id tidak diberikan")
        return jsonify({"error": True, "message": "Food ID is required"}), 400

    if not content or not content.strip():
        logger.warning("Permintaan tidak valid: teks review tidak diberikan")
        return jsonify({"error": True, "message": "Review content is required"}), 400

    if not rating or not isinstance(rating, (int, float)) or not (1 <= rating <= 5):
        logger.warning(f"Permintaan tidak valid: rating tidak valid {rating}")
        return (
            jsonify(
                {
                    "error": True,
                    "message": "Rating is required and must be between 1 and 5",
                }
            ),
            400,
        )

    try:
        # Import services here to avoid circular imports
        from app.modules.rating.service import RatingService

        # Create or update rating first
        rating_result = RatingService.create_rating(user_id, food_id, rating)
        if not rating_result:
            logger.error("Gagal membuat/memperbarui rating")
            return jsonify({"error": True, "message": "Failed to save rating"}), 500

        # Create or update review
        review = ReviewService.create_or_update_review(
            user_id, food_id, content.strip()
        )
        if not review:
            logger.error("Gagal membuat/memperbarui review")
            return jsonify({"error": True, "message": "Failed to save review"}), 500

        logger.info(
            f"Berhasil {'membuat' if method == 'POST' else 'memperbarui'} review dan rating"
        )

        return jsonify(
            {
                "error": False,
                "message": f"Review and rating {'added' if method == 'POST' else 'updated'} successfully",
                "data": {"review": review.to_dict(), "rating": rating_result},
            }
        ), (201 if method == "POST" else 200)

    except Exception as e:
        logger.error(
            f"Gagal {'membuat' if method == 'POST' else 'memperbarui'} review dan rating: {str(e)}"
        )
        return (
            jsonify(
                {
                    "error": True,
                    "message": f"Failed to {'create' if method == 'POST' else 'update'} review and rating",
                }
            ),
            500,
        )


@review_blueprint.route(
    "/users/<string:user_id>/foods/<string:food_id>/review", methods=["GET"]
)
@token_required
def get_user_food_review(user_id, food_id):
    """Get user's review and rating for a specific food"""
    # Verify that the authenticated user is the one requesting the review
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to access review of user {user_id}")
        return (
            jsonify({"error": True, "message": "You can only access your own reviews"}),
            403,
        )

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
        return jsonify({"error": False, "data": response_data}), 200

    except Exception as e:
        logger.error(f"Gagal mengambil review dan rating: {str(e)}")
        return (
            jsonify({"error": True, "message": "Failed to get review and rating"}),
            500,
        )


@review_blueprint.route(
    "/users/<string:user_id>/foods/<string:food_id>/review", methods=["DELETE"]
)
@token_required
def delete_review(user_id, food_id):
    """Delete a review but keep the rating"""
    # Verify that the authenticated user is the one deleting the review
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to delete review of user {user_id}")
        return (
            jsonify({"error": True, "message": "You can only delete your own reviews"}),
            403,
        )

    logger.info(f"DELETE /users/{user_id}/foods/{food_id}/review - Menghapus review")

    try:
        result = ReviewService.delete_review(user_id, food_id)
        if not result:
            logger.warning(
                f"Review tidak ditemukan untuk pengguna {user_id} dan makanan {food_id}"
            )
            return jsonify({"error": True, "message": "Review not found"}), 404

        logger.info(
            f"Review berhasil dihapus untuk pengguna {user_id} dan makanan {food_id}"
        )
        return jsonify({"error": False, "message": "Review deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Gagal menghapus review: {str(e)}")
        return jsonify({"error": True, "message": "Failed to delete review"}), 500
