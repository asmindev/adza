"""
Category validation utilities
Contains validation logic that can be reused across the application
"""

import re
from typing import Dict, List, Optional, Any


class CategoryValidator:
    """Utility class for category-related validations"""

    @staticmethod
    def validate_name(name: str) -> Dict[str, Any]:
        """
        Validate category name

        Args:
            name (str): Category name to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not name:
            errors.append("Category name is required")
            return {"valid": False, "errors": errors}

        # Remove extra whitespace
        name = name.strip()

        if len(name) < 2:
            errors.append("Category name must be at least 2 characters long")

        if len(name) > 100:
            errors.append("Category name must not exceed 100 characters")

        # Check for valid characters (letters, numbers, spaces, and common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s\-_&'.,()]+$", name):
            errors.append("Category name contains invalid characters")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_description(description: Optional[str]) -> Dict[str, Any]:
        """
        Validate category description

        Args:
            description (str, optional): Category description to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Description is optional
        if description is None or description == "":
            return {"valid": True, "errors": errors}

        if len(description) > 500:
            errors.append("Category description must not exceed 500 characters")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_icon(icon: Optional[str]) -> Dict[str, Any]:
        """
        Validate category icon URL

        Args:
            icon (str, optional): Icon URL to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Icon is optional
        if icon is None or icon == "":
            return {"valid": True, "errors": errors}

        if len(icon) > 255:
            errors.append("Icon URL must not exceed 255 characters")

        # Basic URL validation (optional, can be more strict)
        if icon and not re.match(r"^https?://", icon):
            errors.append("Icon must be a valid HTTP/HTTPS URL")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_category_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete category data

        Args:
            data (dict): Category data to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        all_errors = []

        # Validate name (required)
        if "name" in data:
            name_validation = CategoryValidator.validate_name(data["name"])
            if not name_validation["valid"]:
                all_errors.extend(name_validation["errors"])
        else:
            all_errors.append("Category name is required")

        # Validate description (optional)
        if "description" in data:
            desc_validation = CategoryValidator.validate_description(
                data["description"]
            )
            if not desc_validation["valid"]:
                all_errors.extend(desc_validation["errors"])

        # Validate icon (optional)
        if "icon" in data:
            icon_validation = CategoryValidator.validate_icon(data["icon"])
            if not icon_validation["valid"]:
                all_errors.extend(icon_validation["errors"])

        return {"valid": len(all_errors) == 0, "errors": all_errors}


class CategoryBusinessRules:
    """Business rules related to categories"""

    @staticmethod
    def can_delete_category(category, user) -> Dict[str, Any]:
        """
        Check if category can be deleted

        Args:
            category: Category object
            user: User object

        Returns:
            dict: Result with 'can_delete' boolean and 'reason' string
        """
        if not user:
            return {"can_delete": False, "reason": "User not authenticated"}

        # Only admin can delete categories
        if user.role != "admin":
            return {"can_delete": False, "reason": "Only admin can delete categories"}

        if not category:
            return {"can_delete": False, "reason": "Category not found"}

        if not category.is_active:
            return {"can_delete": False, "reason": "Category is already inactive"}

        # Additional business rules can be added here
        # For example: check if category has associated restaurants

        return {"can_delete": True, "reason": "Category can be deleted"}

    @staticmethod
    def can_modify_category(category, user) -> Dict[str, Any]:
        """
        Check if category can be modified

        Args:
            category: Category object
            user: User object

        Returns:
            dict: Result with 'can_modify' boolean and 'reason' string
        """
        if not user:
            return {"can_modify": False, "reason": "User not authenticated"}

        # Only admin can modify categories
        if user.role != "admin":
            return {"can_modify": False, "reason": "Only admin can modify categories"}

        if not category:
            return {"can_modify": False, "reason": "Category not found"}

        return {"can_modify": True, "reason": "Category can be modified"}

    @staticmethod
    def is_category_active(category) -> bool:
        """Check if category is active"""
        return bool(category and category.is_active)

    @staticmethod
    def can_add_to_favorites(category, user) -> Dict[str, Any]:
        """
        Check if category can be added to user favorites

        Args:
            category: Category object
            user: User object

        Returns:
            dict: Result with 'can_add' boolean and 'reason' string
        """
        if not user:
            return {"can_add": False, "reason": "User not authenticated"}

        if not category:
            return {"can_add": False, "reason": "Category not found"}

        if not CategoryBusinessRules.is_category_active(category):
            return {"can_add": False, "reason": "Category is not active"}

        return {"can_add": True, "reason": "Category can be added to favorites"}
