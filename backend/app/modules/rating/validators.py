"""
Rating validation utilities
Contains validation logic that can be reused across the application
"""

from typing import Dict, Any, Optional


class RatingValidator:
    """Utility class for rating-related validations"""

    @staticmethod
    def validate_rating_value(rating: Any) -> Dict[str, Any]:
        """
        Validate rating value

        Args:
            rating: Rating value to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if rating is None:
            errors.append("Rating value is required")
            return {"valid": False, "errors": errors}

        # Try to convert to float
        try:
            rating_float = float(rating)
        except (ValueError, TypeError):
            errors.append("Rating must be a valid number")
            return {"valid": False, "errors": errors}

        # Check range
        if not (1.0 <= rating_float <= 5.0):
            errors.append("Rating must be between 1.0 and 5.0")
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": [], "rating": rating_float}

    @staticmethod
    def validate_comment(comment: Optional[str]) -> Dict[str, Any]:
        """
        Validate comment field

        Args:
            comment: Comment text to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        # Comment is optional, so None/empty is valid
        if comment is None or comment == "":
            return {"valid": True, "errors": []}

        if not isinstance(comment, str):
            errors.append("Comment must be a string")
            return {"valid": False, "errors": errors}

        # Check length
        comment = comment.strip()
        if len(comment) > 1000:
            errors.append("Comment is too long (maximum 1000 characters)")
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": [], "comment": comment}

    @staticmethod
    def validate_entity_id(
        entity_id: Any, entity_type: str = "entity"
    ) -> Dict[str, Any]:
        """
        Validate entity ID (food_id, restaurant_id, user_id)

        Args:
            entity_id: ID to validate
            entity_type: Type of entity for error messages

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []

        if not entity_id:
            errors.append(f"{entity_type.title()} ID is required")
            return {"valid": False, "errors": errors}

        if not isinstance(entity_id, str):
            errors.append(f"{entity_type.title()} ID must be a string")
            return {"valid": False, "errors": errors}

        entity_id = entity_id.strip()
        if not entity_id:
            errors.append(f"{entity_type.title()} ID cannot be empty")
            return {"valid": False, "errors": errors}

        # Check UUID format (basic check)
        if len(entity_id) != 36:
            errors.append(f"{entity_type.title()} ID must be a valid UUID")
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": [], "entity_id": entity_id}

    @staticmethod
    def validate_food_rating_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete food rating data

        Args:
            data: Rating data to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []
        validated_data = {}

        # Validate rating value
        rating_validation = RatingValidator.validate_rating_value(data.get("rating"))
        if not rating_validation["valid"]:
            errors.extend(rating_validation["errors"])
        else:
            validated_data["rating"] = rating_validation["rating"]

        # Validate food_id
        food_id_validation = RatingValidator.validate_entity_id(
            data.get("food_id"), "food"
        )
        if not food_id_validation["valid"]:
            errors.extend(food_id_validation["errors"])
        else:
            validated_data["food_id"] = food_id_validation["entity_id"]

        # Validate user_id if provided
        if "user_id" in data:
            user_id_validation = RatingValidator.validate_entity_id(
                data.get("user_id"), "user"
            )
            if not user_id_validation["valid"]:
                errors.extend(user_id_validation["errors"])
            else:
                validated_data["user_id"] = user_id_validation["entity_id"]

        if errors:
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": [], "data": validated_data}

    @staticmethod
    def validate_restaurant_rating_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete restaurant rating data

        Args:
            data: Rating data to validate

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []
        validated_data = {}

        # Validate rating value
        rating_validation = RatingValidator.validate_rating_value(data.get("rating"))
        if not rating_validation["valid"]:
            errors.extend(rating_validation["errors"])
        else:
            validated_data["rating"] = rating_validation["rating"]

        # Validate restaurant_id
        restaurant_id_validation = RatingValidator.validate_entity_id(
            data.get("restaurant_id"), "restaurant"
        )
        if not restaurant_id_validation["valid"]:
            errors.extend(restaurant_id_validation["errors"])
        else:
            validated_data["restaurant_id"] = restaurant_id_validation["entity_id"]

        # Validate comment (optional)
        comment_validation = RatingValidator.validate_comment(data.get("comment"))
        if not comment_validation["valid"]:
            errors.extend(comment_validation["errors"])
        else:
            if "comment" in comment_validation:
                validated_data["comment"] = comment_validation["comment"]

        # Validate user_id if provided
        if "user_id" in data:
            user_id_validation = RatingValidator.validate_entity_id(
                data.get("user_id"), "user"
            )
            if not user_id_validation["valid"]:
                errors.extend(user_id_validation["errors"])
            else:
                validated_data["user_id"] = user_id_validation["entity_id"]

        if errors:
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": [], "data": validated_data}

    @staticmethod
    def validate_pagination_params(page: Any, limit: Any) -> Dict[str, Any]:
        """
        Validate pagination parameters

        Args:
            page: Page number
            limit: Items per page limit

        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        errors = []
        validated_data = {}

        # Validate page
        try:
            page_int = int(page) if page is not None else 1
            if page_int < 1:
                page_int = 1
            validated_data["page"] = page_int
        except (ValueError, TypeError):
            errors.append("Page must be a valid positive integer")

        # Validate limit
        try:
            limit_int = int(limit) if limit is not None else 10
            if limit_int < 1:
                limit_int = 10
            elif limit_int > 100:
                limit_int = 100
            validated_data["limit"] = limit_int
        except (ValueError, TypeError):
            errors.append("Limit must be a valid positive integer")

        if errors:
            return {"valid": False, "errors": errors}

        return {"valid": True, "errors": [], "data": validated_data}
