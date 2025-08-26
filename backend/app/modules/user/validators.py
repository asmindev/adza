"""
User validation utilities
Contains validation logic that can be reused across the application
"""

import re
from typing import Dict, List, Optional, Any


class UserValidator:
    """Utility class for user-related validations"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format using regex

        Args:
            email (str): Email to validate

        Returns:
            bool: True if email format is valid, False otherwise
        """
        if not email:
            return False

        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength

        Args:
            password (str): Password to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not password:
            errors.append("Password is required")
            return {"valid": False, "errors": errors}

        if len(password) < 6:
            errors.append("Password must be at least 6 characters long")

        if len(password) > 128:
            errors.append("Password must not exceed 128 characters")

        # Additional strength checks can be added here
        # if not re.search(r"[A-Z]", password):
        #     errors.append("Password must contain at least one uppercase letter")

        # if not re.search(r"[a-z]", password):
        #     errors.append("Password must contain at least one lowercase letter")

        # if not re.search(r"\d", password):
        #     errors.append("Password must contain at least one digit")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_username(username: str) -> Dict[str, Any]:
        """
        Validate username format

        Args:
            username (str): Username to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not username:
            errors.append("Username is required")
            return {"valid": False, "errors": errors}

        if len(username) < 3:
            errors.append("Username must be at least 3 characters long")

        if len(username) > 50:
            errors.append("Username must not exceed 50 characters")

        # Check for valid characters (alphanumeric and underscore only)
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            errors.append("Username can only contain letters, numbers, and underscores")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_name(name: str) -> Dict[str, Any]:
        """
        Validate user name

        Args:
            name (str): Name to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not name:
            errors.append("Name is required")
            return {"valid": False, "errors": errors}

        if len(name.strip()) < 1:
            errors.append("Name cannot be empty")

        if len(name) > 50:
            errors.append("Name must not exceed 50 characters")

        return {"valid": len(errors) == 0, "errors": errors}


class UserBusinessRules:
    """Business rules related to users"""

    @staticmethod
    def is_admin(user) -> bool:
        """Check if user has admin role"""
        return user.role == "admin" if user and user.role else False

    @staticmethod
    def has_completed_onboarding(user) -> bool:
        """Check if user has completed onboarding"""
        return bool(user.onboarding_completed) if user else False

    @staticmethod
    def can_modify_user(current_user, target_user_id: str) -> bool:
        """
        Check if current user can modify target user
        Admin can modify anyone, users can only modify themselves
        """
        if not current_user:
            return False

        # Admin can modify anyone
        if UserBusinessRules.is_admin(current_user):
            return True

        # Users can only modify themselves
        return current_user.id == target_user_id
