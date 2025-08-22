from flask import Blueprint, request, jsonify, send_from_directory, current_app, g
import json
from app.modules.food.service import FoodService
from app.utils import api_logger as logger
from app.utils.auth import has_login, token_required, admin_required

food_blueprint = Blueprint("food", __name__)


@food_blueprint.route("/foods", methods=["POST"])
@token_required
def create_food():
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

    if not data or "name" not in data:
        logger.warning(f"Permintaan tidak valid: nama makanan tidak ada")
        return jsonify({"error": True, "message": "Food name is required"}), 400

    try:
        # Use the standard create_food method but pass images as well
        food = FoodService.create_food(
            name=data["name"],
            description=data.get("description"),
            category=data.get("category"),
            price=data.get("price"),
            images=images,
        )

        logger.info(f"Makanan baru berhasil dibuat: {food.name} (ID: {food.id})")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "Food created successfully",
                    "data": food.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Gagal membuat makanan: {str(e)}")
        return jsonify({"error": True, "message": "Failed to create food"}), 500


@food_blueprint.route("/foods", methods=["GET"])
def get_foods():
    logger.info("GET /foods - Mengambil semua makanan")
    limit = request.args.get("limit", default=20, type=int)

    # Get all foods with their images and average ratings
    foods = FoodService.get_all_foods_with_details(limit=limit)

    logger.info(f"Berhasil mengambil {len(foods)} makanan")
    return jsonify({"error": False, "data": {"foods": foods}}), 200


@food_blueprint.route("/foods/<string:food_id>", methods=["GET"])
@has_login
def get_food_detail(food_id):
    logger.info(f"GET /foods/{food_id} - Mengambil detail makanan")

    food_detail = FoodService.get_food_detail(food_id)

    if not food_detail:
        logger.warning(f"Makanan dengan ID {food_id} tidak ditemukan")
        return jsonify({"error": True, "message": "Food not found"}), 404

    logger.info(f"Berhasil mengambil detail makanan: {food_detail['name']}")
    user_id = g.user_id if hasattr(g, "user_id") else None
    if user_id:
        # get the user's rating for the food
        user_rating = FoodService.get_user_rating(user_id, food_id)
        food_detail["ratings"]["user_rating"] = (
            user_rating.to_dict()["rating"] if user_rating else None
        )
    else:
        food_detail["ratings"]["user_rating"] = None

    return jsonify({"error": False, "data": food_detail}), 200


@food_blueprint.route("/foods/<string:food_id>", methods=["PUT"])
@admin_required
def update_food(food_id):
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
        return jsonify({"error": True, "message": "No data provided"}), 400

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
            return jsonify({"error": True, "message": "Food not found"}), 404

        logger.info(f"Makanan dengan ID {food_id} berhasil diperbarui: {food.name}")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "Food updated successfully",
                    "data": food.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Gagal memperbarui makanan dengan ID {food_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to update food"}), 500


@food_blueprint.route("/foods/<string:food_id>", methods=["DELETE"])
@admin_required
def delete_food(food_id):
    logger.info(f"DELETE /foods/{food_id} - Menghapus makanan")
    try:
        result = FoodService.delete_food(food_id)
        if not result:
            logger.warning(f"Makanan dengan ID {food_id} tidak ditemukan")
            return jsonify({"error": True, "message": "Food not found"}), 404

        logger.info(f"Makanan dengan ID {food_id} berhasil dihapus")
        return jsonify({"error": False, "message": "Food deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Gagal menghapus makanan dengan ID {food_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to delete food"}), 500


@food_blueprint.route("/foods/search", methods=["GET"])
def search_foods():
    logger.info("GET /foods/search - Mencari makanan")

    category = request.args.get("category", type=str)
    limit = request.args.get("limit", default=10, type=int)

    logger.debug(f"Parameter pencarian: category={category}, limit={limit}")

    search_results = FoodService.search_foods(category=category, limit=limit)

    logger.info(f"Berhasil menemukan {len(search_results)} makanan")
    return jsonify({"error": False, "data": {"foods": search_results}}), 200


# utils routes
@food_blueprint.route("/static/<path:filename>")
def serve_static(filename):
    """
    Serve static files from the assets directory.
    This is a utility route to serve images or other static files.
    """
    # logger.info(f"GET /static/{filename} - Mengambil file statis")
    food_folder_images = current_app.config.get("FOODS_IMAGES_PATH")
    return send_from_directory(food_folder_images, filename)
