from flask import Blueprint, request, g
from app.modules.user.service import UserService
from app.modules.category.service import UserFavoriteCategoryService
from app.utils import api_logger as logger
from app.utils.response import ResponseHelper
from app.utils.auth import (
    token_required,
    admin_required,
    user_matches_or_admin,
    has_login,
)

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/auth/register", methods=["POST"])
def register_user():
    """
    Register a new user account.

    Expected JSON payload:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "name": "string (optional)"
    }

    Returns:
        JSON response with user data and success/error status
    """
    logger.info("POST /auth/register - Registrasi pengguna baru")
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "email", "password")):
        logger.warning("Permintaan tidak valid: data tidak lengkap")
        return ResponseHelper.validation_error(
            "Missing required fields: username, email, password"
        )

    try:
        user = UserService.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            name=data.get("name"),  # Optional field
        )
        logger.info(f"Pengguna baru berhasil dibuat: {user.username}")
        return ResponseHelper.success(
            data=user.to_dict(), message="User registered successfully", status_code=201
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Gagal membuat pengguna: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to create user")


@user_blueprint.route("/auth/login", methods=["POST"])
def login_user():
    """
    Authenticate user and return JWT token.

    Expected JSON payload:
    {
        "username": "string",
        "password": "string"
    }

    Returns:
        JSON response with user data and JWT token on success
    """
    logger.info("POST /auth/login - Login pengguna")
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "password")):
        logger.warning("Permintaan login tidak valid: data tidak lengkap")
        return ResponseHelper.validation_error("Missing username or password")

    # Authenticate user and get token
    auth_result = UserService.authenticate_user(data["username"], data["password"])

    if not auth_result:
        logger.warning("Login gagal: kredensial tidak valid")
        return ResponseHelper.unauthorized("Invalid username or password")

    user = auth_result["user"]
    token = auth_result["token"]

    logger.info(f"Login berhasil untuk pengguna: {user.username}")
    return ResponseHelper.success(
        data={
            "user": user.to_dict(),
            "token": token,
        },
        message="Login successful",
    )


# me routes
@user_blueprint.route("/me", methods=["GET"])
@token_required
def get_me():
    """
    Get current user's profile information with full details.

    Requires:
        Valid JWT token in Authorization header

    Returns:
        JSON response with current user's data including relations
    """
    logger.info("GET /me - Mengambil informasi pengguna yang sedang login")
    logger.info(f"User ID: {g.user_id}")

    user_data = UserService.get_user_with_details(g.user_id)
    if not user_data:
        logger.warning(f"Pengguna dengan ID {g.user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", g.user_id)

    logger.info(f"Berhasil mengambil informasi pengguna: {user_data.get('username')}")
    return ResponseHelper.success(data=user_data)


# User management routes
@user_blueprint.route("/users", methods=["GET"])
@admin_required
def get_users():
    """
    Get all users with pagination (admin only).

    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 10, max: 100)
        search (str): Search term for username/email

    Returns:
        JSON response with paginated user list
    """
    logger.info("GET /users - Mengambil semua pengguna dengan pagination (admin only)")

    # Get query parameters with defaults
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", None, type=str)

    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10

    # Log the pagination parameters
    logger.info(f"Pagination parameters: page={page}, limit={limit}, search={search}")

    try:
        # Get users with pagination
        result = UserService.get_all_users(page=page, limit=limit, search=search)
        users = result["items"]

        logger.info(
            f"Berhasil mengambil {len(users)} pengguna dari total {result['total']}"
        )

        # Return paginated response
        return ResponseHelper.paginated(
            items=result["items"],  # Already converted to dict in service
            page=result["page"],
            limit=result["limit"],
            total=result["total"],
            message="Users retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Gagal mengambil daftar pengguna: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve users")


@user_blueprint.route("/users/<string:user_id>", methods=["GET"])
@user_matches_or_admin
def get_user(user_id):
    """
    Get user details by ID with full information.

    Args:
        user_id (str): User ID

    Returns:
        JSON response with user data including relations
    """
    logger.info(f"GET /users/{user_id} - Mengambil detail pengguna")

    user_data = UserService.get_user_with_details(user_id)
    if not user_data:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", user_id)

    logger.info(f"Berhasil mengambil detail pengguna {user_data.get('username')}")
    return ResponseHelper.success(data=user_data)


@user_blueprint.route("/users/<string:user_id>", methods=["PUT"])
@user_matches_or_admin
def update_user(user_id):
    """
    Update user information by ID.

    Args:
        user_id (str): User ID

    Expected JSON payload:
    {
        "username": "string (optional)",
        "email": "string (optional)"
    }

    Returns:
        JSON response with updated user data
    """
    logger.info(f"PUT /users/{user_id} - Memperbarui data pengguna")
    data = request.get_json()

    if not data:
        logger.warning("Tidak ada data yang diberikan untuk pembaruan")
        return ResponseHelper.validation_error("No data provided")

    try:
        user = UserService.update_user(user_id, data)
        if not user:
            logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
            return ResponseHelper.not_found("User", user_id)

        logger.info(f"Pengguna dengan ID {user_id} berhasil diperbarui")
        return ResponseHelper.success(
            data=user.to_dict(), message="User updated successfully"
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Gagal memperbarui pengguna dengan ID {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to update user")


@user_blueprint.route("/users/<string:user_id>", methods=["DELETE"])
@user_matches_or_admin
def delete_user(user_id):
    """
    Delete user by ID.

    Args:
        user_id (str): User ID

    Returns:
        JSON response confirming deletion
    """
    logger.info(f"DELETE /users/{user_id} - Menghapus pengguna")
    try:
        result = UserService.delete_user(user_id)
        if not result:
            logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
            return ResponseHelper.not_found("User", user_id)

        logger.info(f"Pengguna dengan ID {user_id} berhasil dihapus")
        return ResponseHelper.success(message="User deleted successfully")
    except Exception as e:
        logger.error(f"Gagal menghapus pengguna dengan ID {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete user")


@user_blueprint.route("/auth/change-password", methods=["PUT"])
@has_login
def change_password():
    """
    Change user password.

    Expected JSON payload:
    {
        "old_password": "string",
        "new_password": "string"
    }

    Returns:
        JSON response confirming password change
    """
    logger.info(f"PUT /auth/change-password - Mengubah password pengguna")
    data = request.get_json()
    logger.info(f"Data yang diterima untuk perubahan password: {data}")
    user_id = g.user_id

    if not data:
        logger.warning("Tidak ada data yang diberikan untuk perubahan password")
        return ResponseHelper.validation_error("No data provided")

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    # Validate required fields
    if not old_password or not new_password:
        logger.warning("Old password atau new password tidak diberikan")
        return ResponseHelper.validation_error(
            "Old password and new password are required"
        )

    try:
        result = UserService.change_password(user_id, old_password, new_password)
        if result:
            logger.info(f"Password pengguna berhasil diubah")
            return ResponseHelper.success(message="Password changed successfully")
        else:
            logger.warning(f"Gagal mengubah password - pengguna tidak ditemukan")
            return ResponseHelper.not_found("User", user_id)
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Gagal mengubah password pengguna: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to change password")


# User Favorite Categories endpoints
@user_blueprint.route("/users/<string:user_id>/favorite-categories", methods=["GET"])
@user_matches_or_admin
def get_user_favorite_categories(user_id):
    """
    Get user's favorite categories.

    Args:
        user_id (str): User ID

    Returns:
        JSON response with user's favorite categories
    """
    logger.info(
        f"GET /users/{user_id}/favorite-categories - Mengambil kategori favorit pengguna"
    )

    # Check if user exists
    user = UserService.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", user_id)

    try:
        result = UserFavoriteCategoryService.get_user_favorite_categories(user_id)

        if result["success"]:
            logger.info(
                f"Berhasil mengambil {len(result['data'])} kategori favorit untuk pengguna {user_id}"
            )
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(f"Gagal mengambil kategori favorit pengguna {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to get user favorite categories"
        )


@user_blueprint.route(
    "/users/<string:user_id>/favorite-categories/<string:category_id>", methods=["POST"]
)
@user_matches_or_admin
def add_user_favorite_category(user_id, category_id):
    """
    Add category to user's favorites.

    Args:
        user_id (str): User ID
        category_id (str): Category ID

    Returns:
        JSON response confirming addition to favorites
    """
    logger.info(
        f"POST /users/{user_id}/favorite-categories/{category_id} - Menambahkan kategori ke favorit pengguna"
    )

    # Check if user exists
    user = UserService.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", user_id)

    try:
        result = UserFavoriteCategoryService.add_favorite_category(user_id, category_id)

        if result["success"]:
            logger.info(
                f"Berhasil menambahkan kategori {category_id} ke favorit pengguna {user_id}"
            )
            return ResponseHelper.success(
                data=result["data"], message=result["message"], status_code=201
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal menambahkan kategori {category_id} ke favorit pengguna {user_id}: {str(e)}"
        )
        return ResponseHelper.internal_server_error("Failed to add favorite category")


@user_blueprint.route(
    "/users/<string:user_id>/favorite-categories/<string:category_id>",
    methods=["DELETE"],
)
@user_matches_or_admin
def remove_user_favorite_category(user_id, category_id):
    """
    Remove category from user's favorites.

    Args:
        user_id (str): User ID
        category_id (str): Category ID

    Returns:
        JSON response confirming removal from favorites
    """
    logger.info(
        f"DELETE /users/{user_id}/favorite-categories/{category_id} - Menghapus kategori dari favorit pengguna"
    )

    # Check if user exists
    user = UserService.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", user_id)

    try:
        result = UserFavoriteCategoryService.remove_favorite_category(
            user_id, category_id
        )

        if result["success"]:
            logger.info(
                f"Berhasil menghapus kategori {category_id} dari favorit pengguna {user_id}"
            )
            return ResponseHelper.success(message=result["message"])
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal menghapus kategori {category_id} dari favorit pengguna {user_id}: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            "Failed to remove favorite category"
        )


@user_blueprint.route(
    "/users/<string:user_id>/favorite-categories/<string:category_id>/check",
    methods=["GET"],
)
@user_matches_or_admin
def check_user_favorite_category(user_id, category_id):
    """
    Check if category is in user's favorites.

    Args:
        user_id (str): User ID
        category_id (str): Category ID

    Returns:
        JSON response with favorite status
    """
    logger.info(
        f"GET /users/{user_id}/favorite-categories/{category_id}/check - Mengecek status favorit kategori"
    )

    # Check if user exists
    user = UserService.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", user_id)

    try:
        result = UserFavoriteCategoryService.check_is_favorite(user_id, category_id)

        if result["success"]:
            is_favorite = result["data"]["is_favorite"]
            logger.info(
                f"Status favorit kategori {category_id} untuk pengguna {user_id}: {is_favorite}"
            )
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal mengecek status favorit kategori {category_id} untuk pengguna {user_id}: {str(e)}"
        )
        return ResponseHelper.internal_server_error("Failed to check favorite status")


# Convenience endpoints for current user (me)
@user_blueprint.route("/me/favorite-categories", methods=["GET"])
@token_required
def get_my_favorite_categories():
    """
    Get current user's favorite categories.

    Returns:
        JSON response with current user's favorite categories
    """
    logger.info(
        "GET /me/favorite-categories - Mengambil kategori favorit pengguna yang sedang login"
    )

    try:
        result = UserFavoriteCategoryService.get_user_favorite_categories(g.user_id)

        if result["success"]:
            logger.info(
                f"Berhasil mengambil {len(result['data'])} kategori favorit untuk pengguna yang sedang login"
            )
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal mengambil kategori favorit pengguna yang sedang login: {str(e)}"
        )
        return ResponseHelper.internal_server_error("Failed to get favorite categories")


@user_blueprint.route("/me/favorite-categories/<string:category_id>", methods=["POST"])
@token_required
def add_my_favorite_category(category_id):
    """
    Add category to current user's favorites.

    Args:
        category_id (str): Category ID

    Returns:
        JSON response confirming addition to favorites
    """
    logger.info(
        f"POST /me/favorite-categories/{category_id} - Menambahkan kategori ke favorit pengguna yang sedang login"
    )

    try:
        result = UserFavoriteCategoryService.add_favorite_category(
            g.user_id, category_id
        )

        if result["success"]:
            logger.info(
                f"Berhasil menambahkan kategori {category_id} ke favorit pengguna yang sedang login"
            )
            return ResponseHelper.success(
                data=result["data"], message=result["message"], status_code=201
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal menambahkan kategori {category_id} ke favorit pengguna yang sedang login: {str(e)}"
        )
        return ResponseHelper.internal_server_error("Failed to add favorite category")


@user_blueprint.route(
    "/me/favorite-categories/<string:category_id>", methods=["DELETE"]
)
@token_required
def remove_my_favorite_category(category_id):
    """
    Remove category from current user's favorites.

    Args:
        category_id (str): Category ID

    Returns:
        JSON response confirming removal from favorites
    """
    logger.info(
        f"DELETE /me/favorite-categories/{category_id} - Menghapus kategori dari favorit pengguna yang sedang login"
    )

    try:
        result = UserFavoriteCategoryService.remove_favorite_category(
            g.user_id, category_id
        )

        if result["success"]:
            logger.info(
                f"Berhasil menghapus kategori {category_id} dari favorit pengguna yang sedang login"
            )
            return ResponseHelper.success(message=result["message"])
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal menghapus kategori {category_id} dari favorit pengguna yang sedang login: {str(e)}"
        )
        return ResponseHelper.internal_server_error(
            "Failed to remove favorite category"
        )


@user_blueprint.route(
    "/me/favorite-categories/<string:category_id>/check", methods=["GET"]
)
@token_required
def check_my_favorite_category(category_id):
    """
    Check if category is in current user's favorites.

    Args:
        category_id (str): Category ID

    Returns:
        JSON response with favorite status
    """
    logger.info(
        f"GET /me/favorite-categories/{category_id}/check - Mengecek status favorit kategori untuk pengguna yang sedang login"
    )

    try:
        result = UserFavoriteCategoryService.check_is_favorite(g.user_id, category_id)

        if result["success"]:
            is_favorite = result["data"]["is_favorite"]
            logger.info(
                f"Status favorit kategori {category_id} untuk pengguna yang sedang login: {is_favorite}"
            )
            return ResponseHelper.success(
                data=result["data"], message=result["message"]
            )
        else:
            return ResponseHelper.error(message=result["message"], status_code=400)
    except Exception as e:
        logger.error(
            f"Gagal mengecek status favorit kategori {category_id} untuk pengguna yang sedang login: {str(e)}"
        )
        return ResponseHelper.internal_server_error("Failed to check favorite status")
