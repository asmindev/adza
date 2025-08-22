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
            return None

        if "username" in data:
            logger.debug(
                f"Memperbarui username dari '{user.username}' menjadi '{data['username']}'"
            )
            user.username = data["username"]
        if "email" in data:
            logger.debug(
                f"Memperbarui email dari '{user.email}' menjadi '{data['email']}'"
            )
            user.email = data["email"]
        if "password" in data:
            logger.debug(f"Memperbarui password untuk pengguna {user.username}")
            user.password = generate_password_hash(data["password"])

        return UserRepository.update(user)

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
