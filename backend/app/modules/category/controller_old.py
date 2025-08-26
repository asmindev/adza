from flask import Blueprint, request, g
from .service import CategoryService, UserFavoriteCategoryService
from app.utils.auth import token_required, admin_required
from app.utils.response import ResponseHelper
from app.modules.user.service import UserService
import logging

logger = logging.getLogger(__name__)

category_bp = Blueprint("category", __name__)


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Get all categories with optional search.
    
    Query Parameters:
        search (str): Search term for category name
    
    Returns:
        JSON response with categories list
    """
    try:
        search = request.args.get("search", "")

        if search:
            result = CategoryService.search_categories(search)
        else:
            result = CategoryService.get_all_categories()

        if result["success"]:
            return ResponseHelper.success(
                data=result["data"],
                message=result["message"]
            )
        else:
            return ResponseHelper.error(
                message=result["message"],
                status_code=400
            )
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/<category_id>", methods=["GET"])
def get_category(category_id):
    """
    Get category by ID.
    
    Args:
        category_id (str): Category ID
    
    Returns:
        JSON response with category data
    """
    try:
        result = CategoryService.get_category_by_id(category_id)
        
        if result["success"]:
            return ResponseHelper.success(
                data=result["data"],
                message=result["message"]
            )
        else:
            return ResponseHelper.not_found("Category", category_id)
    except Exception as e:
        logger.error(f"Error in get_category: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories", methods=["POST"])
@admin_required
def create_category():
    """
    Create new category (Admin only).
    
    Expected JSON payload:
    {
        "name": "string"
    }
    
    Returns:
        JSON response with created category data
    """
    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("Request data is required")

        # Validate required fields
        required_fields = ["name"]
        for field in required_fields:
            if field not in data or not data[field]:
                return ResponseHelper.validation_error(f"{field} is required")

        result = CategoryService.create_category(data)
        
        if result["success"]:
            return ResponseHelper.success(
                data=result["data"],
                message=result["message"],
                status_code=201
            )
        else:
            return ResponseHelper.error(
                message=result["message"],
                status_code=400
            )
    except Exception as e:
        logger.error(f"Error in create_category: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/<category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    """Update category (Admin only)"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"success": False, "message": "Request data is required"}),
                400,
            )

        result = CategoryService.update_category(category_id, data)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in update_category: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Internal server error: {str(e)}"}),
            500,
        )


@category_bp.route("/categories/<category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    """Delete category (Admin only)"""
    try:
        result = CategoryService.delete_category(category_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in delete_category: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Internal server error: {str(e)}"}),
            500,
        )


@category_bp.route("/categories/most-favorite", methods=["GET"])
def get_most_favorite_categories():
    """Get most favorited categories"""
    try:
        limit = request.args.get("limit", 10, type=int)
        result = UserFavoriteCategoryService.get_most_favorite_categories(limit)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in get_most_favorite_categories: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "data": [],
                    "message": f"Internal server error: {str(e)}",
                }
            ),
            500,
        )


# User Favorite Categories endpoints
@category_bp.route("/categories/favorites", methods=["GET"])
@token_required
def get_user_favorite_categories():
    """Get current user's favorite categories"""
    try:
        result = UserFavoriteCategoryService.get_user_favorite_categories(g.user_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in get_user_favorite_categories: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "data": [],
                    "message": f"Internal server error: {str(e)}",
                }
            ),
            500,
        )


@category_bp.route("/categories/<category_id>/favorite", methods=["POST"])
@token_required
def add_favorite_category(category_id):
    """Add category to user favorites"""
    try:
        result = UserFavoriteCategoryService.add_favorite_category(
            g.user_id, category_id
        )
        return jsonify(result), 201 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in add_favorite_category: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Internal server error: {str(e)}"}),
            500,
        )


@category_bp.route("/categories/<category_id>/favorite", methods=["DELETE"])
@token_required
def remove_favorite_category(category_id):
    """Remove category from user favorites"""
    try:
        result = UserFavoriteCategoryService.remove_favorite_category(
            g.user_id, category_id
        )
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in remove_favorite_category: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Internal server error: {str(e)}"}),
            500,
        )


@category_bp.route("/categories/<category_id>/restaurants", methods=["GET"])
def get_restaurants_by_category(category_id):
    """Get restaurants by category ID"""
    try:
        from app.modules.restaurant.service import RestaurantService

        # Get category to ensure it exists
        category_result = CategoryService.get_category_by_id(category_id)
        if not category_result["success"]:
            return jsonify(category_result), 404

        # Get restaurants in this category
        restaurants = RestaurantService.get_restaurants_by_category(category_id)
        return jsonify(restaurants), 200 if restaurants["success"] else 400

    except Exception as e:
        logger.error(f"Error in get_restaurants_by_category: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "data": [],
                    "message": f"Internal server error: {str(e)}",
                }
            ),
            500,
        )


@category_bp.route("/categories/<category_id>/is-favorite", methods=["GET"])
@token_required
def check_is_favorite(category_id):
    """Check if category is in user favorites"""
    try:
        result = UserFavoriteCategoryService.check_is_favorite(g.user_id, category_id)
        return jsonify(result), 200 if result["success"] else 400
    except Exception as e:
        logger.error(f"Error in check_is_favorite: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "data": {"is_favorite": False},
                    "message": f"Internal server error: {str(e)}",
                }
            ),
            500,
        )
