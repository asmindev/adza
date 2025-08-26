"""
Food validation utilities
Contains validation logic that can be reused across the application
"""

import re
from typing import Dict, List, Optional, Any
from werkzeug.datastructures import FileStorage


class FoodValidator:
    """Utility class for food-related validations"""

    @staticmethod
    def validate_name(name: str) -> Dict[str, Any]:
        """
        Validate food name

        Args:
            name (str): Food name to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not name:
            errors.append("Food name is required")
            return {"valid": False, "errors": errors}

        # Remove extra whitespace
        name = name.strip()

        if len(name) < 2:
            errors.append("Food name must be at least 2 characters long")

        if len(name) > 100:
            errors.append("Food name must not exceed 100 characters")

        # Check for valid characters (letters, numbers, spaces, and common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s\-_&'.,()]+$", name):
            errors.append("Food name contains invalid characters")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_description(description: Optional[str]) -> Dict[str, Any]:
        """
        Validate food description

        Args:
            description (str, optional): Food description to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Description is optional
        if description is None or description == "":
            return {"valid": True, "errors": errors}

        if len(description) > 1000:
            errors.append("Food description must not exceed 1000 characters")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_price(price: Optional[float]) -> Dict[str, Any]:
        """
        Validate food price

        Args:
            price (float, optional): Price to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Price is optional
        if price is None:
            return {"valid": True, "errors": errors}

        try:
            price_val = float(price)

            if price_val < 0:
                errors.append("Price cannot be negative")

            if price_val > 1000000:  # 1 million limit
                errors.append("Price exceeds maximum limit")

            # Check for reasonable decimal places (max 2)
            if len(str(price_val).split(".")[-1]) > 2:
                errors.append("Price cannot have more than 2 decimal places")

        except (ValueError, TypeError):
            errors.append("Price must be a valid number")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_restaurant_id(restaurant_id: Optional[str]) -> Dict[str, Any]:
        """
        Validate restaurant ID format

        Args:
            restaurant_id (str, optional): Restaurant ID to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Restaurant ID is optional
        if restaurant_id is None or restaurant_id == "":
            return {"valid": True, "errors": errors}

        # Basic UUID format validation (36 characters with hyphens)
        if not re.match(
            r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
            restaurant_id,
        ):
            errors.append("Restaurant ID must be a valid UUID format")

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_food_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete food data

        Args:
            data (dict): Food data to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        all_errors = []

        # Validate name (required)
        if "name" in data:
            name_validation = FoodValidator.validate_name(data["name"])
            if not name_validation["valid"]:
                all_errors.extend(name_validation["errors"])
        else:
            all_errors.append("Food name is required")

        # Validate description (optional)
        if "description" in data:
            desc_validation = FoodValidator.validate_description(data["description"])
            if not desc_validation["valid"]:
                all_errors.extend(desc_validation["errors"])

        # Validate price (optional)
        if "price" in data:
            price_validation = FoodValidator.validate_price(data["price"])
            if not price_validation["valid"]:
                all_errors.extend(price_validation["errors"])

        # Validate restaurant_id (optional)
        if "restaurant_id" in data:
            restaurant_validation = FoodValidator.validate_restaurant_id(
                data["restaurant_id"]
            )
            if not restaurant_validation["valid"]:
                all_errors.extend(restaurant_validation["errors"])

        return {"valid": len(all_errors) == 0, "errors": all_errors}

    @staticmethod
    def validate_image_file(file: FileStorage) -> Dict[str, Any]:
        """
        Validate uploaded image file

        Args:
            file (FileStorage): Uploaded file to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not file or not file.filename:
            errors.append("No file provided")
            return {"valid": False, "errors": errors}

        # Check file size (max 5MB)
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            errors.append("File size exceeds 5MB limit")

        # Check file extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_ext = (
            "." + file.filename.rsplit(".", 1)[1].lower()
            if "." in file.filename
            else ""
        )

        if file_ext not in allowed_extensions:
            errors.append(
                "File type not allowed. Allowed types: JPG, JPEG, PNG, GIF, WEBP"
            )

        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_image_files(files: List[FileStorage]) -> Dict[str, Any]:
        """
        Validate multiple uploaded image files

        Args:
            files (List[FileStorage]): List of uploaded files to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        all_errors = []

        if not files:
            return {"valid": True, "errors": all_errors}  # No files is okay

        # Limit number of files
        max_files = 10
        if len(files) > max_files:
            all_errors.append(f"Maximum {max_files} images allowed")

        # Validate each file
        for i, file in enumerate(files):
            file_validation = FoodValidator.validate_image_file(file)
            if not file_validation["valid"]:
                for error in file_validation["errors"]:
                    all_errors.append(f"File {i + 1}: {error}")

        return {"valid": len(all_errors) == 0, "errors": all_errors}


class FoodBusinessRules:
    """Business rules related to foods"""

    @staticmethod
    def can_delete_food(food, user) -> Dict[str, Any]:
        """
        Check if food can be deleted

        Args:
            food: Food object
            user: User object

        Returns:
            dict: Result with 'can_delete' boolean and 'reason' string
        """
        if not user:
            return {"can_delete": False, "reason": "User not authenticated"}

        # Only admin can delete foods
        if user.role != "admin":
            return {"can_delete": False, "reason": "Only admin can delete foods"}

        if not food:
            return {"can_delete": False, "reason": "Food not found"}

        # Additional business rules can be added here
        # For example: check if food has active orders

        return {"can_delete": True, "reason": "Food can be deleted"}

    @staticmethod
    def can_modify_food(food, user) -> Dict[str, Any]:
        """
        Check if food can be modified

        Args:
            food: Food object
            user: User object

        Returns:
            dict: Result with 'can_modify' boolean and 'reason' string
        """
        if not user:
            return {"can_modify": False, "reason": "User not authenticated"}

        # Only admin can modify foods
        if user.role != "admin":
            return {"can_modify": False, "reason": "Only admin can modify foods"}

        if not food:
            return {"can_modify": False, "reason": "Food not found"}

        return {"can_modify": True, "reason": "Food can be modified"}

    @staticmethod
    def can_rate_food(food, user) -> Dict[str, Any]:
        """
        Check if user can rate this food

        Args:
            food: Food object
            user: User object

        Returns:
            dict: Result with 'can_rate' boolean and 'reason' string
        """
        if not user:
            return {"can_rate": False, "reason": "User not authenticated"}

        if not food:
            return {"can_rate": False, "reason": "Food not found"}

        # Users can rate foods (business rule can be enhanced)
        return {"can_rate": True, "reason": "User can rate this food"}

    @staticmethod
    def can_upload_images(food, user) -> Dict[str, Any]:
        """
        Check if user can upload images for this food

        Args:
            food: Food object
            user: User object

        Returns:
            dict: Result with 'can_upload' boolean and 'reason' string
        """
        if not user:
            return {"can_upload": False, "reason": "User not authenticated"}

        # Only admin can upload food images
        if user.role != "admin":
            return {"can_upload": False, "reason": "Only admin can upload food images"}

        if not food:
            return {"can_upload": False, "reason": "Food not found"}

        return {"can_upload": True, "reason": "User can upload images for this food"}
