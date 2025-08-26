from flask import Blueprint, request, g
from app.modules.user.service import UserService
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
        "password": "string"
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
            data["username"], data["email"], data["password"]
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
    Get current user's profile information.

    Requires:
        Valid JWT token in Authorization header

    Returns:
        JSON response with current user's data
    """
    logger.info("GET /me - Mengambil informasi pengguna yang sedang login")
    logger.info(f"User ID: {g.user_id}")

    user = UserService.get_user_by_id(g.user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {g.user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", g.user_id)

    logger.info(f"Berhasil mengambil informasi pengguna: {user.username}")
    return ResponseHelper.success(data=user.to_dict())


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
            items=[user.to_dict() for user in users],
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
    Get user details by ID.

    Args:
        user_id (str): User ID

    Returns:
        JSON response with user data
    """
    logger.info(f"GET /users/{user_id} - Mengambil detail pengguna")

    user = UserService.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return ResponseHelper.not_found("User", user_id)

    logger.info(f"Berhasil mengambil detail pengguna {user.username}")
    return ResponseHelper.success(data=user.to_dict())


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

    # Validate new password length (optional but recommended)
    if len(new_password) < 6:
        logger.warning("New password terlalu pendek")
        return ResponseHelper.validation_error(
            "New password must be at least 6 characters long"
        )

    try:
        result = UserService.change_password(user_id, old_password, new_password)
        if not result:
            logger.warning(
                f"Gagal mengubah password - pengguna tidak ditemukan atau password lama salah"
            )
            return ResponseHelper.validation_error(
                "User not found or old password is incorrect"
            )

        logger.info(f"Password pengguna berhasil diubah")
        return ResponseHelper.success(message="Password changed successfully")
    except Exception as e:
        logger.error(f"Gagal mengubah password pengguna: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to change password")
