from flask import Blueprint, request, g
from .service import CategoryService, UserFavoriteCategoryService
from app.utils.auth import token_required, admin_required
from app.utils.response import ResponseHelper
import logging

logger = logging.getLogger(__name__)

category_bp = Blueprint("category", __name__)


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Get all categories with optional search and stats.

    Query Parameters:
        search (str): Search term for category name
        include_stats (bool): Whether to include statistics (default: false)

    Returns:
        JSON response with categories list
    """
    try:
        search = request.args.get("search", "").strip()
        include_stats = request.args.get("include_stats", "false").lower() == "true"

        if search:
            result = CategoryService.search_categories(
                search, include_details=include_stats
            )
        else:
            result = CategoryService.get_all_categories(include_stats=include_stats)

        if result["success"]:
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/<category_id>", methods=["GET"])
def get_category(category_id):
    """
    Get category by ID.

    Args:
        category_id (str): Category ID

    Query Parameters:
        include_details (bool): Whether to include detailed information (default: false)

    Returns:
        JSON response with category data
    """
    try:
        include_details = request.args.get("include_details", "false").lower() == "true"
        result = CategoryService.get_category_by_id(
            category_id, include_details=include_details
        )

        if result["success"]:
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
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
        "name": "string",
        "description": "string (optional)",
        "icon": "string (optional)"
    }

    Returns:
        JSON response with created category data
    """
    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("Request data is required")

        result = CategoryService.create_category(data)

        if result["success"]:
            return ResponseHelper.success(
                data=result["data"], message=result["message"], status_code=201
            )
        else:
            return ResponseHelper.validation_error(result["message"])
    except Exception as e:
        logger.error(f"Error in create_category: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/<category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    """
    Update category (Admin only).

    Args:
        category_id (str): Category ID

    Expected JSON payload:
    {
        "name": "string (optional)",
        "description": "string (optional)",
        "icon": "string (optional)",
        "is_active": "boolean (optional)"
    }

    Returns:
        JSON response with updated category data
    """
    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("Request data is required")

        # Get current user for authorization (passed from admin_required decorator)
        current_user = getattr(g, "current_user", None)

        result = CategoryService.update_category(category_id, data, user=current_user)

        if result["success"]:
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.validation_error(result["message"])
    except Exception as e:
        logger.error(f"Error in update_category: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/<category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    """
    Delete category (Admin only).

    Args:
        category_id (str): Category ID

    Returns:
        JSON response confirming deletion
    """
    try:
        # Get current user for authorization (passed from admin_required decorator)
        current_user = getattr(g, "current_user", None)

        result = CategoryService.delete_category(category_id, user=current_user)

        if result["success"]:
            return ResponseHelper.success(message=result["message"])
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(f"Error in delete_category: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/most-favorite", methods=["GET"])
def get_most_favorite_categories():
    """
    Get most favorited categories.

    Query Parameters:
        limit (int): Maximum number of categories to return (default: 10)

    Returns:
        JSON response with most favorite categories
    """
    try:
        limit = request.args.get("limit", 10, type=int)
        result = UserFavoriteCategoryService.get_most_favorite_categories(limit)

        if result["success"]:
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(f"Error in get_most_favorite_categories: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")


@category_bp.route("/categories/<category_id>/restaurants", methods=["GET"])
def get_restaurants_by_category(category_id):
    """
    Get restaurants by category ID.
    Note: This endpoint should be moved to restaurant module to maintain proper separation

    Args:
        category_id (str): Category ID

    Returns:
        JSON response indicating this endpoint should be accessed through restaurant module
    """
    try:
        # Check if category exists first
        category_result = CategoryService.get_category_by_id(category_id)
        if not category_result["success"]:
            return ResponseHelper.not_found("Category", category_id)

        # Return message directing to proper endpoint
        return ResponseHelper.success(
            data={
                "category": category_result["data"],
                "redirect_to": f"/restaurants?category_id={category_id}",
                "message": "Please use the restaurants endpoint with category_id parameter",
            },
            message="Category found. Use restaurant endpoints for restaurant data.",
        )

    except Exception as e:
        logger.error(f"Error in get_restaurants_by_category: {str(e)}")
        return ResponseHelper.internal_server_error(f"Internal server error: {str(e)}")
