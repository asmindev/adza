from flask import Blueprint, request, jsonify, g
from app.modules.review.service import ReviewService
from app.modules.rating.service import RatingService
from app.utils import api_logger as logger
from app.utils.auth import token_required

review_blueprint = Blueprint("review", __name__)


@review_blueprint.route("/foods/<string:food_id>/reviews", methods=["GET"])
@token_required
def get_food_reviews(food_id):
    """Get all reviews for a specific food"""
    logger.info(f"GET /foods/{food_id}/reviews - Mengambil semua review makanan")
    reviews = ReviewService.get_food_reviews(food_id)

    logger.info(f"Berhasil mengambil {len(reviews)} review untuk makanan {food_id}")
    return (
        jsonify(
            {
                "error": False,
                "data": {
                    "food_id": food_id,
                    "reviews": [review.to_dict() for review in reviews],
                },
            }
        ),
        200,
    )


@review_blueprint.route("/users/<string:user_id>/reviews", methods=["GET"])
@token_required
def get_user_reviews(user_id):
    """Get all reviews written by a specific user"""
    logger.info(f"GET /users/{user_id}/reviews - Mengambil semua review pengguna")
    reviews = ReviewService.get_user_reviews(user_id)

    logger.info(f"Berhasil mengambil {len(reviews)} review dari pengguna {user_id}")
    return (
        jsonify(
            {
                "error": False,
                "data": {
                    "user_id": user_id,
                    "reviews": [review.to_dict() for review in reviews],
                },
            }
        ),
        200,
    )


@review_blueprint.route("/reviews", methods=["POST", "PUT"])
@token_required
def review_food():
    """Create or update a review for a food"""
    # Verify that the authenticated user is the one making the review
    data = request.get_json()
    user_id = g.user_id
    food_id = data.get("food_id")

    method = request.method
    logger.info(
        f"{method} /users/{g.user_id}/foods/{food_id}/review - {'Membuat' if method == 'POST' else 'Memperbarui'} review"
    )

    if not data or "content" not in data:
        logger.warning(f"Permintaan tidak valid: teks review tidak diberikan")
        return jsonify({"error": True, "message": "Review text is required"}), 400

    content = data["content"]

    try:
        review = ReviewService.create_or_update_review(user_id, food_id, content)

        if not review:
            return jsonify({"error": True, "message": "Could not add review"}), 400

        logger.info(
            f"Berhasil {'membuat' if method == 'POST' else 'memperbarui'} review"
        )

        return jsonify(
            {
                "error": False,
                "message": f"Review {'added' if method == 'POST' else 'updated'} successfully",
                "data": review.to_dict(),
            }
        ), (201 if method == "POST" else 200)

    except Exception as e:
        logger.error(
            f"Gagal {'membuat' if method == 'POST' else 'memperbarui'} review: {str(e)}"
        )
        return (
            jsonify(
                {
                    "error": True,
                    "message": f"Failed to {'create' if method == 'POST' else 'update'} review",
                }
            ),
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
