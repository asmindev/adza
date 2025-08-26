from flask import Blueprint, request, send_from_directory, current_app, g
import json
from app.modules.food.service import FoodService
from app.utils import api_logger as logger
from app.utils.response import ResponseHelper
from app.utils.auth import has_login, token_required, admin_required

food_blueprint = Blueprint("food", __name__)


@food_blueprint.route("/foods", methods=["POST"])
@token_required
def create_food():
    """
    Create a new food item.

    Expected JSON payload or form data:
    {
        "name": "string",
        "description": "string (optional)",
        "price": "float (optional)",
        "restaurant_id": "string (optional)"
    }

    Also supports multipart/form-data for image upload.

    Returns:
        JSON response with created food data
    """
    logger.info("POST /foods - Creating new food")

    try:
        # Handle form data with images
        if request.content_type and "multipart/form-data" in request.content_type:
            logger.info("Processing multipart/form-data with images")
            form = request.form
            images = request.files.getlist("images")

            # Extract form data with validation
            name = form.get("name")
            if not name:
                return ResponseHelper.validation_error("Food name is required")

            description = form.get("description")
            restaurant_id = form.get("restaurant_id")
            price_str = form.get("price")

            # Convert price to float if provided
            price = None
            if price_str and price_str.strip():
                try:
                    price = float(price_str)
                except ValueError:
                    return ResponseHelper.validation_error("Invalid price format")
        else:
            # Handle direct JSON
            data = request.get_json()
            if not data:
                return ResponseHelper.validation_error("No data provided")

            name = data.get("name")
            if not name:
                return ResponseHelper.validation_error("Food name is required")

            description = data.get("description")
            restaurant_id = data.get("restaurant_id")
            price = data.get("price")
            images = []

        logger.debug(f"Creating food with name: {name}")

        # Use service layer - it will handle validation
        food_data = FoodService.create_food(
            name=name,
            description=description,
            price=price,
            restaurant_id=restaurant_id,
            images=images,
        )

        logger.info(
            f"Food created successfully: {food_data['name']} (ID: {food_data['id']})"
        )
        return ResponseHelper.success(
            data=food_data, message="Food created successfully", status_code=201
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to create food: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to create food")


@food_blueprint.route("/foods", methods=["GET"])
def get_foods():
    """
    Get all foods with pagination.

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)
        search (str): Search term for food name

    Returns:
        JSON response with paginated food list
    """
    logger.info("GET /foods - Retrieving foods with pagination")

    try:
        # Get query parameters - let service handle validation
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)
        search = request.args.get("search", None, type=str)

        logger.info(f"Pagination params: page={page}, limit={limit}, search={search}")

        # Use service layer
        result = FoodService.get_all_foods_with_details(
            page=page, limit=limit, search=search
        )

        foods = result["items"]
        logger.info(f"Retrieved {len(foods)} foods from total {result['total']}")

        # Return paginated response
        return ResponseHelper.success(
            data={
                "foods": foods,
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
            },
            message="Foods retrieved successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve foods: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve foods")


@food_blueprint.route("/foods/<string:food_id>", methods=["GET"])
@has_login
def get_food_detail(food_id):
    """
    Get detailed information about a specific food item.

    Args:
        food_id (str): Food ID

    Returns:
        JSON response with food details including ratings
    """
    logger.info(f"GET /foods/{food_id} - Retrieving food detail")

    try:
        # Use service layer
        food_detail = FoodService.get_food_detail(food_id)

        if not food_detail:
            logger.warning(f"Food with ID {food_id} not found")
            return ResponseHelper.not_found("Food", food_id)

        logger.info(
            f"Successfully retrieved food detail: {food_detail.get('name', 'Unknown')}"
        )

        # Add user rating if logged in
        user_id = g.user_id if hasattr(g, "user_id") else None
        if user_id:
            user_rating = FoodService.get_user_rating(user_id, food_id)
            # Add user rating to the response structure
            if "ratings" not in food_detail:
                food_detail["ratings"] = {}
            food_detail["ratings"]["user_rating"] = (
                user_rating.get("rating", 0) if user_rating else 0
            )
        else:
            if "ratings" not in food_detail:
                food_detail["ratings"] = {}
            food_detail["ratings"]["user_rating"] = 0

        return ResponseHelper.success(data=food_detail)

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to retrieve food details {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve food details")


@food_blueprint.route("/foods/<string:food_id>", methods=["PUT"])
@admin_required
def update_food(food_id):
    """
    Update food information by ID (admin only).

    Args:
        food_id (str): Food ID

    Expected JSON payload or form data:
    {
        "name": "string (optional)",
        "description": "string (optional)",
        "price": "float (optional)",
        "restaurant_id": "string (optional)",
        "deleted_image_ids": ["id1", "id2"] (optional)
    }

    Also supports multipart/form-data for new image uploads.

    Returns:
        JSON response with updated food data
    """
    logger.info(f"PUT /foods/{food_id} - Updating food")

    try:
        data = {}
        new_images = []
        deleted_image_ids = []

        # Handle form data with images
        if request.content_type and "multipart/form-data" in request.content_type:
            form = request.form
            new_images = request.files.getlist("new_images")

            # Get list of image IDs to delete
            if form.get("deleted_image_ids"):
                try:
                    deleted_image_ids = form.getlist("deleted_image_ids")
                    logger.info(f"Deleting {len(deleted_image_ids)} selected images")
                except Exception:
                    logger.error("Invalid deleted_image_ids format")

            logger.info(
                f"New images: {len(new_images)}, Deleted: {len(deleted_image_ids)}"
            )

            # Prepare data for update with form fields
            for key in form:
                if key not in ["new_images", "deleted_image_ids"]:
                    value = form[key]
                    # Convert price to float if needed
                    if key == "price" and value:
                        try:
                            value = float(value)
                        except ValueError:
                            return ResponseHelper.validation_error(
                                "Invalid price format"
                            )
                    data[key] = value
        else:
            # Handle direct JSON
            json_data = request.get_json()
            if not json_data:
                return ResponseHelper.validation_error("No data provided")

            data = json_data.copy()
            deleted_image_ids = data.pop("deleted_image_ids", [])

        logger.debug(f"Update data: {data}")
        logger.info(
            f"Images - new: {len(new_images)}, deleted: {len(deleted_image_ids)}"
        )

        # Use service layer - it will handle validation
        food_data = FoodService.update_food(
            food_id, data, new_images=new_images, deleted_image_ids=deleted_image_ids
        )

        if not food_data:
            logger.warning(f"Food with ID {food_id} not found")
            return ResponseHelper.not_found("Food", food_id)

        logger.info(
            f"Food {food_id} updated successfully: {food_data.get('name', 'Unknown')}"
        )
        return ResponseHelper.success(
            data=food_data, message="Food updated successfully"
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to update food {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to update food")


@food_blueprint.route("/foods/<string:food_id>", methods=["DELETE"])
@admin_required
def delete_food(food_id):
    """
    Delete food by ID (admin only).

    Args:
        food_id (str): Food ID

    Returns:
        JSON response confirming deletion
    """
    logger.info(f"DELETE /foods/{food_id} - Deleting food")

    try:
        # Use service layer
        result = FoodService.delete_food(food_id)

        if not result:
            logger.warning(f"Food with ID {food_id} not found")
            return ResponseHelper.not_found("Food", food_id)

        logger.info(f"Food {food_id} deleted successfully")
        return ResponseHelper.success(message="Food deleted successfully")

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to delete food {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete food")


@food_blueprint.route("/foods/search", methods=["GET"])
def search_foods():
    """
    Search foods by restaurant and other filters.

    Query Parameters:
        restaurant_id (str): Restaurant ID to filter by
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)

    Returns:
        JSON response with search results
    """
    logger.info("GET /foods/search - Searching foods")

    try:
        # Get query parameters - let service handle validation
        restaurant_id = request.args.get("restaurant_id", type=str)
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", default=10, type=int)

        logger.debug(
            f"Search params: restaurant_id={restaurant_id}, page={page}, limit={limit}"
        )

        # Use service layer
        search_results = FoodService.search_foods(
            restaurant_id=restaurant_id, page=page, limit=limit
        )

        logger.info(f"Search found {len(search_results.get('items', []))} foods")
        return ResponseHelper.success(
            data={"foods": search_results.get("items", [])},
            message="Food search completed successfully",
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to search foods: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to search foods")


# Utility routes
@food_blueprint.route("/static/<path:filename>")
def serve_static(filename):
    """
    Serve static files from the assets directory.
    This is a utility route to serve images or other static files.

    Args:
        filename (str): Name of the file to serve

    Returns:
        Static file response
    """
    food_folder_images = current_app.config.get("FOODS_IMAGES_PATH")
    if not food_folder_images:
        return ResponseHelper.error("Static files path not configured", 500)
    return send_from_directory(food_folder_images, filename)
