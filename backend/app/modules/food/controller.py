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
        "category": "string (optional)",
        "price": "float (optional)"
    }

    Also supports multipart/form-data for image upload.

    Returns:
        JSON response with created food data
    """
    logger.info("POST /foods - Membuat makanan baru")

    # Handle form data with images
    if request.content_type and "multipart/form-data" in request.content_type:
        logger.info("Menggunakan multipart/form-data untuk mengunggah gambar")
        form = request.form
        images = request.files.getlist("images")
        name = form.get("name")
        description = form.get("description")
        category = form.get("category")
        price = form.get("price")
        data = {
            "name": name,
            "description": description,
            "category": category,
            "price": price,
        }

    else:
        # Handle direct JSON
        data = request.get_json()
        images = []

    logger.debug(f"Data yang diterima: {data}")
    logger.info(f"Jumlah gambar yang diterima: {len(images)}")

    if not data or "name" not in data or not data["name"]:
        logger.warning(f"Permintaan tidak valid: nama makanan tidak ada")
        return ResponseHelper.validation_error("Food name is required")

    try:
        # Convert price to float if it's a string
        price = data.get("price")
        if price is not None and isinstance(price, str):
            try:
                price = float(price)
            except ValueError:
                price = None

        # Use the standard create_food method but pass images as well
        food = FoodService.create_food(
            name=str(data["name"]),  # Ensure name is a string
            description=data.get("description"),
            category=data.get("category"),
            price=price,
            images=images,
        )

        logger.info(f"Makanan baru berhasil dibuat: {food.name} (ID: {food.id})")
        return ResponseHelper.success(
            data=food.to_dict(), message="Food created successfully", status_code=201
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Gagal membuat makanan: {str(e)}")
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
    logger.info("GET /foods - Mengambil semua makanan dengan pagination")

    # Get query parameters with defaults
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    search = request.args.get("search", None, type=str)

    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    # Log the pagination parameters
    logger.info(f"Pagination parameters: page={page}, limit={limit}, search={search}")

    try:
        # Get foods with pagination
        result = FoodService.get_all_foods_with_details(
            page=page, limit=limit, search=search
        )

        foods = result["items"]
        logger.info(
            f"Berhasil mengambil {len(foods)} makanan dari total {result['total']}"
        )

        # Return paginated response with custom data structure
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
    except Exception as e:
        logger.error(f"Gagal mengambil daftar makanan: {str(e)}")
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
    logger.info(f"GET /foods/{food_id} - Mengambil detail makanan")

    try:
        food_detail = FoodService.get_food_detail(food_id) or {}
        logger.info(f"Detail makanan yang diambil: {food_detail.get('ratings', {})}")

        if not food_detail:
            logger.warning(f"Makanan dengan ID {food_id} tidak ditemukan")
            return ResponseHelper.not_found("Food", food_id)

        logger.info(f"Berhasil mengambil detail makanan: {food_detail['name']}")
        user_id = g.user_id if hasattr(g, "user_id") else None
        if user_id:
            # get the user's rating for the food
            user_rating = FoodService.get_user_rating(user_id, food_id)
            food_detail["ratings"]["user_rating"] = (
                user_rating.to_dict()["rating"] if user_rating else 0
            )
        else:
            food_detail["ratings"]["user_rating"] = 0

        return ResponseHelper.success(data=food_detail)
    except Exception as e:
        logger.error(f"Gagal mengambil detail makanan {food_id}: {str(e)}")
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
        "category": "string (optional)",
        "price": "float (optional)",
        "deleted_image_ids": ["id1", "id2"] (optional)
    }

    Also supports multipart/form-data for new image uploads.

    Returns:
        JSON response with updated food data
    """
    logger.info(f"PUT /foods/{food_id} - Memperbarui data makanan")
    data = {}
    new_images = []
    deleted_image_ids = []

    # Handle form data with images
    if request.content_type and "multipart/form-data" in request.content_type:
        form = request.form
        # Get new images being uploaded
        new_images = request.files.getlist("new_images")

        # Get list of image IDs to delete
        deleted_image_ids = []
        if form.get("deleted_image_ids"):
            try:
                deleted_image_ids = form.getlist("deleted_image_ids")
                logger.info("Deleted image IDss: %s", deleted_image_ids)
                logger.info(f"Menghapus {len(deleted_image_ids)} gambar yang dipilih")
            except json.JSONDecodeError:
                logger.error("Format deleted_image_ids tidak valid")
        logger.info(f"Jumlah gambar baru: {len(new_images)}")
        logger.info(f"Jumlah gambar yang dihapus: {len(deleted_image_ids)}")
        # Prepare data for update with form fields
        for key in form:
            if key not in ["new_images", "deleted_image_ids"]:
                data[key] = form[key]

    else:
        # Handle direct JSON
        data = request.get_json()
        new_images = []
        deleted_image_ids = data.pop("deleted_image_ids", []) if data else []

    if not data:
        logger.warning("Tidak ada data yang diberikan untuk pembaruan")
        return ResponseHelper.validation_error("No data provided")

    logger.debug(f"Data yang diterima: {data}")
    logger.info(
        f"Jumlah gambar baru: {len(new_images)}, Jumlah ID gambar dihapus: {len(deleted_image_ids)}"
    )

    try:
        logger.info(
            f"Data: data={data}, new_images={len(new_images)}, deleted_image_ids={deleted_image_ids}"
        )
        # Use the standard update_food method with new_images and deleted_image_ids
        food = FoodService.update_food(
            food_id, data, new_images=new_images, deleted_image_ids=deleted_image_ids
        )
        if not food:
            logger.warning(f"Makanan dengan ID {food_id} tidak ditemukan")
            return ResponseHelper.not_found("Food", food_id)

        logger.info(f"Makanan dengan ID {food_id} berhasil diperbarui: {food.name}")
        return ResponseHelper.success(
            data=food.to_dict(), message="Food updated successfully"
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Gagal memperbarui makanan dengan ID {food_id}: {str(e)}")
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
    logger.info(f"DELETE /foods/{food_id} - Menghapus makanan")
    try:
        result = FoodService.delete_food(food_id)
        if not result:
            logger.warning(f"Makanan dengan ID {food_id} tidak ditemukan")
            return ResponseHelper.not_found("Food", food_id)

        logger.info(f"Makanan dengan ID {food_id} berhasil dihapus")
        return ResponseHelper.success(message="Food deleted successfully")
    except Exception as e:
        logger.error(f"Gagal menghapus makanan dengan ID {food_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete food")


@food_blueprint.route("/foods/search", methods=["GET"])
def search_foods():
    """
    Search foods by category and other filters.

    Query Parameters:
        category (str): Food category to filter by
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)

    Returns:
        JSON response with search results
    """
    logger.info("GET /foods/search - Mencari makanan")

    # Get query parameters
    category = request.args.get("category", type=str)
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    logger.debug(
        f"Parameter pencarian: category={category}, page={page}, limit={limit}"
    )

    try:
        search_results = FoodService.search_foods(
            category=category, page=page, limit=limit
        )

        logger.info(f"Berhasil menemukan {len(search_results)} makanan")
        return ResponseHelper.success(
            data={"foods": search_results}, message="Food search completed successfully"
        )
    except Exception as e:
        logger.error(f"Gagal mencari makanan: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to search foods")


# utils routes
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
    # logger.info(f"GET /static/{filename} - Mengambil file statis")
    food_folder_images = current_app.config.get("FOODS_IMAGES_PATH")
    if not food_folder_images:
        return ResponseHelper.error("Static files path not configured", 500)
    return send_from_directory(food_folder_images, filename)
