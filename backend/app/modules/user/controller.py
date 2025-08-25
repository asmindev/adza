from flask import Blueprint, request, jsonify, g
from app.modules.user.service import UserService
from app.utils import api_logger as logger
from app.utils.auth import (
    token_required,
    admin_required,
    user_matches_or_admin,
    has_login,
)

user_blueprint = Blueprint("user", __name__)


# Authentication routes
@user_blueprint.route("/auth/register", methods=["POST"])
def register_user():
    logger.info("POST /auth/register - Registrasi pengguna baru")
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "email", "password")):
        logger.warning(f"Permintaan tidak valid: data tidak lengkap")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        user = UserService.create_user(
            data["username"], data["email"], data["password"]
        )
        logger.info(f"Pengguna baru berhasil dibuat: {user.username}")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "User registered successfully",
                    "data": user.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Gagal membuat pengguna: {str(e)}")
        return jsonify({"error": True, "message": "Failed to create user"}), 500


@user_blueprint.route("/auth/login", methods=["POST"])
def login_user():
    logger.info("POST /auth/login - Login pengguna")
    data = request.get_json()

    if not data or not all(k in data for k in ("username", "password")):
        logger.warning(f"Permintaan login tidak valid: data tidak lengkap")
        return jsonify({"error": True, "message": "Missing username or password"}), 400

    # Authenticate user and get token
    auth_result = UserService.authenticate_user(data["username"], data["password"])

    if not auth_result:
        logger.warning(f"Login gagal: kredensial tidak valid")
        return jsonify({"error": True, "message": "Invalid username or password"}), 401

    user = auth_result["user"]
    token = auth_result["token"]

    logger.info(f"Login berhasil untuk pengguna: {user.username}")
    return (
        jsonify(
            {
                "error": False,
                "message": "Login successful",
                "data": {
                    "user": user.to_dict(),
                    "token": token,
                },
            }
        ),
        200,
    )


# me routes
@user_blueprint.route("/me", methods=["GET"])
@token_required
def get_me():
    logger.info("GET /me - Mengambil informasi pengguna yang sedang login")
    logger.info(f"User ID: {g.user_id}")
    user = UserService.get_user_by_id(g.user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {g.user_id} tidak ditemukan")
        return jsonify({"error": True, "message": "User not found"}), 404
    logger.info(f"Berhasil mengambil informasi pengguna: {user.username}")
    return jsonify({"error": False, "data": user.to_dict()}), 200


# User management routes
@user_blueprint.route("/users", methods=["GET"])
@admin_required
def get_users():
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

    # Get users with pagination
    result = UserService.get_all_users(page=page, limit=limit, search=search)

    users = result["items"]
    logger.info(
        f"Berhasil mengambil {len(users)} pengguna dari total {result['total']}"
    )

    # Return paginated response
    return (
        jsonify(
            {
                "error": False,
                "data": {
                    "users": [user.to_dict() for user in users],
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


@user_blueprint.route("/users/<string:user_id>", methods=["GET"])
@user_matches_or_admin
def get_user(user_id):
    logger.info(f"GET /users/{user_id} - Mengambil detail pengguna")
    user = UserService.get_user_by_id(user_id)
    if not user:
        logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return jsonify({"error": True, "message": "User not found"}), 404
    logger.info(f"Berhasil mengambil detail pengguna {user.username}")
    return jsonify({"error": False, "data": user.to_dict()}), 200


@user_blueprint.route("/users/<string:user_id>", methods=["PUT"])
@user_matches_or_admin
def update_user(user_id):
    logger.info(f"PUT /users/{user_id} - Memperbarui data pengguna")
    data = request.get_json()

    if not data:
        logger.warning("Tidak ada data yang diberikan untuk pembaruan")
        return jsonify({"error": True, "message": "No data provided"}), 400

    try:
        user = UserService.update_user(user_id, data)
        if not user:
            logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
            return jsonify({"error": True, "message": "User not found"}), 404

        logger.info(f"Pengguna dengan ID {user_id} berhasil diperbarui")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "User updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Gagal memperbarui pengguna dengan ID {user_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to update user"}), 500


@user_blueprint.route("/users/<string:user_id>", methods=["DELETE"])
@user_matches_or_admin
def delete_user(user_id):
    logger.info(f"DELETE /users/{user_id} - Menghapus pengguna")
    try:
        result = UserService.delete_user(user_id)
        if not result:
            logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
            return jsonify({"error": True, "message": "User not found"}), 404

        logger.info(f"Pengguna dengan ID {user_id} berhasil dihapus")
        return jsonify({"error": False, "message": "User deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Gagal menghapus pengguna dengan ID {user_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to delete user"}), 500


# auth/change-password


@user_blueprint.route("/auth/change-password", methods=["PUT"])
@has_login
def change_password():
    logger.info(f"PUT /auth/change-password - Mengubah password pengguna")
    data = request.get_json()
    logger.info(f"Data yang diterima untuk perubahan password: {data}")
    user_id = g.user_id

    if not data:
        logger.warning("Tidak ada data yang diberikan untuk perubahan password")
        return jsonify({"error": True, "message": "No data provided"}), 400

    old_password = data.get("old_password")
    new_password = data.get("new_password")

    # Validate required fields
    if not old_password or not new_password:
        logger.warning("Old password atau new password tidak diberikan")
        return (
            jsonify(
                {"error": True, "message": "Old password and new password are required"}
            ),
            400,
        )

    # Validate new password length (optional but recommended)
    if len(new_password) < 6:
        logger.warning("New password terlalu pendek")
        return (
            jsonify(
                {
                    "error": True,
                    "message": "New password must be at least 6 characters long",
                }
            ),
            400,
        )

    try:
        result = UserService.change_password(user_id, old_password, new_password)
        if not result:
            logger.warning(
                f"Gagal mengubah password - pengguna tidak ditemukan atau password lama salah"
            )
            return (
                jsonify(
                    {
                        "error": True,
                        "message": "User not found or old password is incorrect",
                    }
                ),
                400,
            )

        logger.info(f"Password pengguna berhasil diubah")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "Password changed successfully",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Gagal mengubah password pengguna: {str(e)}")
        return jsonify({"error": True, "message": "Failed to change password"}), 500
