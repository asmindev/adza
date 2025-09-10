from app.modules.user.repository import UserRepository
from app.modules.user.models import User
from app.modules.user.validators import UserValidator, UserBusinessRules
from app.modules.user.data_service import UserDataService
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import db_logger as logger
from app.utils.jwt_utils import generate_token
from typing import Dict, Any, Optional


class UserService:
    @staticmethod
    def get_all_users(page=1, limit=10, search=None):
        """Get all users with basic data (no relations)"""
        return UserDataService.get_users_with_basic_data(
            page=page, limit=limit, search=search
        )

    @staticmethod
    def get_user_by_id(user_id: str):
        """Get user by ID (basic data only)"""
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def get_user_with_details(user_id: str):
        """Get user with full details including relations"""
        return UserDataService.get_user_with_aggregated_data(user_id)

    @staticmethod
    def get_user_by_username(username: str):
        """Get user by username"""
        return UserRepository.get_by_username(username)

    @staticmethod
    def create_user(
        username: str, email: str, password: str, name: Optional[str] = None
    ) -> User:
        """
        Create a new user with validation

        Args:
            username (str): Username
            email (str): Email address
            password (str): Plain password
            name (str, optional): User's display name

        Returns:
            User: Created user object

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Creating new user with username: {username}, email: {email}")

        # Validate input data
        email_valid = UserValidator.validate_email(email)
        if not email_valid:
            logger.warning(f"Invalid email format: {email}")
            raise ValueError("Invalid email format")

        username_validation = UserValidator.validate_username(username)
        if not username_validation["valid"]:
            logger.warning(f"Invalid username: {username_validation['errors']}")
            raise ValueError("; ".join(username_validation["errors"]))

        password_validation = UserValidator.validate_password_strength(password)
        if not password_validation["valid"]:
            logger.warning(f"Invalid password: {password_validation['errors']}")
            raise ValueError("; ".join(password_validation["errors"]))

        if name:
            name_validation = UserValidator.validate_name(name)
            if not name_validation["valid"]:
                logger.warning(f"Invalid name: {name_validation['errors']}")
                raise ValueError("; ".join(name_validation["errors"]))

        # Check for existing username
        if UserRepository.get_by_username(username):
            logger.warning(f"Username {username} already exists")
            raise ValueError("Username already exists")

        # Check for existing email
        if UserRepository.get_by_email(email):
            logger.warning(f"Email {email} already exists")
            raise ValueError("Email already exists")

        # Create user
        hashed_password = generate_password_hash(password)
        user_data = {"username": username, "email": email, "password": hashed_password}

        if name:
            user_data["name"] = name

        user = User(**user_data)
        return UserRepository.create(user)

    @staticmethod
    def update_user(user_id: str, data: Dict[str, Any]) -> Optional[User]:
        """
        Update user with validation

        Args:
            user_id (str): User ID
            data (dict): Data to update

        Returns:
            User: Updated user object or None if not found

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Updating user with ID: {user_id}")
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            return None

        # Validate email if provided
        if "email" in data and data["email"]:
            if not UserValidator.validate_email(data["email"]):
                logger.warning(f"Invalid email format: {data['email']}")
                raise ValueError("Invalid email format")

            # Check if email already exists for other users
            existing_user = UserRepository.get_by_email(data["email"])
            if existing_user and existing_user.id != user_id:
                logger.warning(f"Email {data['email']} already in use")
                raise ValueError("Email already in use")

        # Validate username if provided
        if "username" in data and data["username"]:
            username_validation = UserValidator.validate_username(data["username"])
            if not username_validation["valid"]:
                logger.warning(f"Invalid username: {username_validation['errors']}")
                raise ValueError("; ".join(username_validation["errors"]))

            # Check if username already exists for other users
            existing_user = UserRepository.get_by_username(data["username"])
            if existing_user and existing_user.id != user_id:
                logger.warning(f"Username {data['username']} already in use")
                raise ValueError("Username already in use")

        # Validate name if provided
        if "name" in data and data["name"]:
            name_validation = UserValidator.validate_name(data["name"])
            if not name_validation["valid"]:
                logger.warning(f"Invalid name: {name_validation['errors']}")
                raise ValueError("; ".join(name_validation["errors"]))

        # Validate password if provided
        if "password" in data and data["password"]:
            password_validation = UserValidator.validate_password_strength(
                data["password"]
            )
            if not password_validation["valid"]:
                logger.warning(f"Invalid password: {password_validation['errors']}")
                raise ValueError("; ".join(password_validation["errors"]))

        # Update fields
        if "name" in data and data["name"]:
            logger.debug(
                f"Updating name from '{getattr(user, 'name', 'N/A')}' to '{data['name']}'"
            )
            user.name = data["name"]

        if "username" in data and data["username"]:
            logger.debug(
                f"Updating username from '{user.username}' to '{data['username']}'"
            )
            user.username = data["username"]

        if "email" in data and data["email"]:
            logger.debug(f"Updating email from '{user.email}' to '{data['email']}'")
            user.email = data["email"]

        if "password" in data and data["password"]:
            logger.debug(f"Updating password for user {user.username}")
            user.password = generate_password_hash(data["password"])

        try:
            updated_user = UserRepository.update(user)
            logger.info(f"Successfully updated user with ID: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Failed to update user with ID {user_id}: {str(e)}")
            raise e

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user by ID"""
        logger.info(f"Deleting user with ID: {user_id}")
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False

        return UserRepository.delete(user)

    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Verify user password"""
        logger.debug(f"Verifying password for user {user.username}")
        return check_password_hash(user.password, password)

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user and return user data with JWT token if successful

        Args:
            username (str): Username
            password (str): Password

        Returns:
            dict: Contains user object and token, or None if authentication fails
        """
        logger.info(f"Attempting authentication for user: {username}")
        user = UserRepository.get_by_username(username)

        if not user:
            logger.warning(f"Authentication failed: user {username} not found")
            return None

        if not UserService.verify_password(user, password):
            logger.warning(f"Authentication failed: invalid password for {username}")
            return None

        # Generate JWT token
        is_admin = UserBusinessRules.is_admin(user)
        token = generate_token(user.id, is_admin, user.username)
        if not token:
            logger.error(f"Failed to generate token for user {username}")
            return None

        logger.info(f"Authentication successful for user {username}")
        return {"user": user, "token": token}

    @staticmethod
    def change_password(user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password with validation

        Args:
            user_id (str): User ID
            old_password (str): Current password
            new_password (str): New password

        Returns:
            bool: True if password changed successfully, False otherwise

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Changing password for user ID: {user_id}")

        # Validate new password
        password_validation = UserValidator.validate_password_strength(new_password)
        if not password_validation["valid"]:
            logger.warning(f"Invalid new password: {password_validation['errors']}")
            raise ValueError("; ".join(password_validation["errors"]))

        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            return False

        if not UserService.verify_password(user, old_password):
            logger.warning(f"Old password does not match for user ID {user_id}")
            raise ValueError("Current password is incorrect")

        user.password = generate_password_hash(new_password)
        try:
            UserRepository.update(user)
            logger.info(f"Password changed successfully for user ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to change password for user ID {user_id}: {str(e)}")
            raise e

    @staticmethod
    def get_user_statistics(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        return UserDataService.get_user_statistics(user_id)

    # complete_onboarding
    @staticmethod
    def complete_onboarding(user_id: str) -> bool:
        """Mark user's onboarding as completed"""
        logger.info(f"Completing onboarding for user ID: {user_id}")
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            return False

        if user.onboarding_completed:
            logger.info(f"User ID {user_id} has already completed onboarding")
            return True

        user.onboarding_completed = True
        try:
            UserRepository.update(user)
            logger.info(f"Onboarding marked as completed for user ID: {user_id}")
            return True
        except Exception as e:
            logger.error(
                f"Failed to complete onboarding for user ID {user_id}: {str(e)}"
            )
            return False
