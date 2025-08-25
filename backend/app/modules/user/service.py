from app.modules.user.repository import UserRepository
from app.modules.user.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import db_logger as logger
from app.utils.jwt_utils import generate_token


class UserService:
    @staticmethod
    def get_all_users(page=1, limit=10, search=None):
        return UserRepository.get_all(page=page, limit=limit, search=search)

    @staticmethod
    def get_user_by_id(user_id):
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def get_user_by_username(username):
        return UserRepository.get_by_username(username)

    @staticmethod
    def create_user(username, email, password):
        logger.info(
            f"Membuat pengguna baru dengan username: {username}, email: {email}"
        )
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        return UserRepository.create(user)

    @staticmethod
    def update_user(user_id, data):
        logger.info(f"Memperbarui pengguna dengan ID: {user_id}")
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
            return None

        # Validate email format if email is being updated
        if "email" in data and data["email"]:
            import re

            email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
            if not re.match(email_pattern, data["email"]):
                logger.warning(f"Format email tidak valid: {data['email']}")
                raise ValueError("Format email tidak valid")

            # Check if email already exists for other users
            from app.modules.user.models import User

            existing_user = User.query.filter_by(email=data["email"]).first()
            if existing_user and existing_user.id != user_id:
                logger.warning(
                    f"Email {data['email']} sudah digunakan oleh pengguna lain"
                )
                raise ValueError("Email sudah digunakan")

        # Validate username if username is being updated
        if "username" in data and data["username"]:
            # Check if username already exists for other users
            existing_user = UserRepository.get_by_username(data["username"])
            if existing_user and existing_user.id != user_id:
                logger.warning(
                    f"Username {data['username']} sudah digunakan oleh pengguna lain"
                )
                raise ValueError("Username sudah digunakan")

        # Update fields
        if "name" in data and data["name"]:
            logger.debug(
                f"Memperbarui name dari '{getattr(user, 'name', 'N/A')}' menjadi '{data['name']}'"
            )
            user.name = data["name"]

        if "username" in data and data["username"]:
            logger.debug(
                f"Memperbarui username dari '{user.username}' menjadi '{data['username']}'"
            )
            user.username = data["username"]

        if "email" in data and data["email"]:
            logger.debug(
                f"Memperbarui email dari '{user.email}' menjadi '{data['email']}'"
            )
            user.email = data["email"]

        if "password" in data and data["password"]:
            logger.debug(f"Memperbarui password untuk pengguna {user.username}")
            user.password = generate_password_hash(data["password"])

        try:
            updated_user = UserRepository.update(user)
            logger.info(f"Berhasil memperbarui pengguna dengan ID: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Gagal memperbarui pengguna dengan ID {user_id}: {str(e)}")
            raise e

    @staticmethod
    def delete_user(user_id):
        logger.info(f"Menghapus pengguna dengan ID: {user_id}")
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False

        return UserRepository.delete(user)

    @staticmethod
    def verify_password(user, password):
        logger.info(f"User {user.password} found, verifying password {password}...")

        return check_password_hash(user.password, password)

    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user and return a JWT token if successful"""
        logger.info(f"Attempting authentication for user: {username}")
        user = UserRepository.get_by_username(username)

        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return None

        if not UserService.verify_password(user, password):
            logger.warning(f"Authentication failed: invalid password for {username}")
            return None

        # Generate JWT token
        # Determine if user is admin (you may need to modify this based on your app's admin logic)
        is_admin = user.role == "admin" if user.role else False
        token = generate_token(user.id, is_admin, user.username)
        if not token:
            logger.error(f"Failed to generate token for user {username}")
            return None

        logger.info(f"Authentication successful for user {username}")
        return {"user": user, "token": token}

    @staticmethod
    def change_password(user_id, old_password, new_password):
        logger.info(f"Changing password for user ID: {user_id}")
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            return False

        if not UserService.verify_password(user, old_password):
            logger.warning(f"Old password does not match for user ID {user_id}")
            return False

        user.password = generate_password_hash(new_password)
        try:
            UserRepository.update(user)
            logger.info(f"Password changed successfully for user ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to change password for user ID {user_id}: {str(e)}")
            return False
