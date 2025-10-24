from flask import Blueprint, request, g
from app.modules.review.service import ReviewService
from app.modules.rating.service import RatingService
from app.utils import get_logger
logger = get_logger(__name__)
from app.utils.response import ResponseHelper
from app.utils.auth import token_required

review_blueprint = Blueprint("review", __name__)


@review_blueprint.route("/foods/<string:food_id>/reviews", methods=["GET"])
@token_required
def get_food_reviews(food_id):
    """Get all reviews for a specific food with pagination"""
    logger.info(f"GET /foods/{food_id}/reviews - Getting food reviews")

    # Parse query parameters
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        result = ReviewService.get_food_reviews(food_id, page=page, limit=limit)
        reviews = result["items"]

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
        logger.error(f"Failed to get food reviews: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve food reviews")


@review_blueprint.route("/users/<string:user_id>/reviews", methods=["GET"])
@token_required
def get_user_reviews(user_id):
    """Get all reviews written by a specific user with pagination"""
    logger.info(f"GET /users/{user_id}/reviews - Getting user reviews")

    # Parse query parameters
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        result = ReviewService.get_user_reviews(user_id, page=page, limit=limit)
        reviews = result["items"]

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
        logger.error(f"Failed to get user reviews: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve user reviews")


@review_blueprint.route("/reviews", methods=["POST", "PUT"])
@token_required
def review_food():
    """
    Create or update a review for a food with mandatory rating

    Expected JSON payload (Detailed rating format):
    {
        "food_id": "string",
        "content": "string",
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
        "content": "string",
        "rating": float (1-5)
    }
    """
    logger.info(f"{request.method} /reviews - Processing review request")

    # Parse request data
    data = request.get_json()
    if not data:
        return ResponseHelper.validation_error("Request data is required")

    user_id = g.user_id
    food_id = data.get("food_id")
    rating = data.get("rating")  # Legacy format
    rating_details = data.get("rating_details")  # New detailed format
    content = data.get("content")

    try:
        # Create or update rating first (support both formats)
        rating_result = RatingService.create_or_update_rating(
            user_id=user_id,
            food_id=food_id,
            rating_details=rating_details,
            rating_value=rating,
        )
        if not rating_result:
            return ResponseHelper.internal_server_error("Failed to save rating")

        # Create or update review
        review = ReviewService.create_or_update_review(
            user_id, food_id, content, rating
        )

        status_code = 201 if request.method == "POST" else 200
        message = f"Review and rating {'added' if request.method == 'POST' else 'updated'} successfully"

        return ResponseHelper.success(
            data={"review": review.to_dict(), "rating": rating_result},
            message=message,
            status_code=status_code,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to process review: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to process review")


@review_blueprint.route(
    "/users/<string:user_id>/foods/<string:food_id>/review", methods=["GET"]
)
@token_required
def get_user_food_review(user_id, food_id):
    """Get user's review and rating for a specific food"""
    logger.info(f"GET /users/{user_id}/foods/{food_id}/review - Getting user review")

    # Check authorization
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to access review of user {user_id}")
        return ResponseHelper.forbidden("You can only access your own reviews")

    try:
        # Get review
        review = ReviewService.get_review(user_id, food_id)

        # Get rating
        rating = RatingService.get_user_food_rating(user_id, food_id)

        response_data = {
            "user_id": user_id,
            "food_id": food_id,
            "review": review.to_dict() if review else None,
            "rating": rating if rating else None,
        }

        return ResponseHelper.success(
            data=response_data, message="Review and rating retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Failed to get review and rating: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get review and rating")


@review_blueprint.route(
    "/users/<string:user_id>/foods/<string:food_id>/review", methods=["DELETE"]
)
@token_required
def delete_review(user_id, food_id):
    """Delete a review but keep the rating"""
    logger.info(f"DELETE /users/{user_id}/foods/{food_id}/review - Deleting review")

    # Check authorization
    if g.user_id != user_id and not g.is_admin:
        logger.warning(f"User {g.user_id} attempted to delete review of user {user_id}")
        return ResponseHelper.forbidden("You can only delete your own reviews")

    try:
        result = ReviewService.delete_review(user_id, food_id)
        if not result:
            return ResponseHelper.not_found("Review")

        return ResponseHelper.success(message="Review deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete review: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete review")
