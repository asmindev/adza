"""
Restaurant Validators

This module provides validation utilities for restaurant-related operations.
All validation logic is centralized here to maintain clean separation of concerns.
"""


class RestaurantValidator:
    """Centralized validation logic for restaurant operations"""

    @staticmethod
    def validate_coordinates(latitude, longitude):
        """
        Validate latitude and longitude coordinates.

        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate

        Raises:
            ValueError: If coordinates are invalid
        """
        try:
            lat = float(latitude)
            lng = float(longitude)
        except (TypeError, ValueError):
            raise ValueError("Latitude and longitude must be valid numbers")

        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lng <= 180):
            raise ValueError("Longitude must be between -180 and 180")

        return lat, lng

    @staticmethod
    def validate_radius(radius):
        """
        Validate radius for location-based searches.

        Args:
            radius (float): Search radius in kilometers

        Returns:
            float: Validated radius

        Raises:
            ValueError: If radius is invalid
        """
        try:
            r = float(radius)
        except (TypeError, ValueError):
            raise ValueError("Radius must be a valid number")

        if r <= 0:
            raise ValueError("Radius must be greater than 0")
        if r > 100:  # Reasonable limit for radius
            raise ValueError("Radius cannot exceed 100 kilometers")

        return r

    @staticmethod
    def validate_pagination(page, limit):
        """
        Validate pagination parameters.

        Args:
            page (int): Page number
            limit (int): Items per page

        Returns:
            tuple: (validated_page, validated_limit)

        Raises:
            ValueError: If pagination parameters are invalid
        """
        try:
            p = int(page) if page is not None else 1
            l = int(limit) if limit is not None else 20
        except (TypeError, ValueError):
            raise ValueError("Page and limit must be valid integers")

        if p < 1:
            p = 1
        if l < 1:
            l = 1
        if l > 100:
            l = 100

        return p, l

    @staticmethod
    def validate_search_term(search_term):
        """
        Validate search term for restaurant search.

        Args:
            search_term (str): Search term

        Returns:
            str: Cleaned search term

        Raises:
            ValueError: If search term is invalid
        """
        if search_term is None:
            return None

        if not isinstance(search_term, str):
            raise ValueError("Search term must be a string")

        cleaned_term = search_term.strip()
        if len(cleaned_term) == 0:
            return None

        if len(cleaned_term) > 100:
            raise ValueError("Search term cannot exceed 100 characters")

        return cleaned_term

    @staticmethod
    def validate_restaurant_creation_data(data):
        """
        Validate data for restaurant creation.

        Args:
            data (dict): Restaurant creation data

        Returns:
            dict: Validated and cleaned data

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not data or not isinstance(data, dict):
            raise ValueError("Restaurant data is required")

        # Required fields
        required_fields = ["name", "address", "latitude", "longitude"]
        missing_fields = [
            field for field in required_fields if field not in data or not data[field]
        ]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate and clean data
        validated_data = {}

        # Name validation
        name = data.get("name", "").strip()
        if not name:
            raise ValueError("Restaurant name is required")
        if len(name) > 100:
            raise ValueError("Restaurant name cannot exceed 100 characters")
        validated_data["name"] = name

        # Address validation
        address = data.get("address", "").strip()
        if not address:
            raise ValueError("Restaurant address is required")
        if len(address) > 255:
            raise ValueError("Restaurant address cannot exceed 255 characters")
        validated_data["address"] = address

        # Coordinates validation
        lat, lng = RestaurantValidator.validate_coordinates(
            data.get("latitude"), data.get("longitude")
        )
        validated_data["latitude"] = lat
        validated_data["longitude"] = lng

        # Optional fields validation
        description = data.get("description")
        if description is not None:
            description = description.strip()
            if len(description) > 1000:
                raise ValueError("Description cannot exceed 1000 characters")
            validated_data["description"] = description if description else None

        phone = data.get("phone")
        if phone is not None:
            phone = phone.strip()
            if len(phone) > 20:
                raise ValueError("Phone number cannot exceed 20 characters")
            validated_data["phone"] = phone if phone else None

        email = data.get("email")
        if email is not None:
            email = email.strip()
            if email and len(email) > 100:
                raise ValueError("Email cannot exceed 100 characters")
            # Basic email format validation
            if email and "@" not in email:
                raise ValueError("Invalid email format")
            validated_data["email"] = email if email else None

        # Category IDs validation (optional)
        category_ids = data.get("category_ids")
        if category_ids is not None:
            if not isinstance(category_ids, list):
                raise ValueError("category_ids must be a list")

            # Validate each category ID
            validated_category_ids = []
            for cat_id in category_ids:
                if not isinstance(cat_id, str) or not cat_id.strip():
                    raise ValueError("Each category ID must be a non-empty string")
                validated_category_ids.append(cat_id.strip())

            validated_data["category_ids"] = validated_category_ids

        return validated_data

    @staticmethod
    def validate_restaurant_update_data(data):
        """
        Validate data for restaurant update.

        Args:
            data (dict): Restaurant update data

        Returns:
            dict: Validated and cleaned data

        Raises:
            ValueError: If update data is invalid
        """
        if not data or not isinstance(data, dict):
            raise ValueError("Update data is required")

        validated_data = {}

        # Optional field validations (same as creation but all optional)
        if "name" in data:
            name = data["name"].strip() if data["name"] else ""
            if not name:
                raise ValueError("Restaurant name cannot be empty")
            if len(name) > 100:
                raise ValueError("Restaurant name cannot exceed 100 characters")
            validated_data["name"] = name

        if "address" in data:
            address = data["address"].strip() if data["address"] else ""
            if not address:
                raise ValueError("Restaurant address cannot be empty")
            if len(address) > 255:
                raise ValueError("Restaurant address cannot exceed 255 characters")
            validated_data["address"] = address

        if "latitude" in data and "longitude" in data:
            lat, lng = RestaurantValidator.validate_coordinates(
                data["latitude"], data["longitude"]
            )
            validated_data["latitude"] = lat
            validated_data["longitude"] = lng
        elif "latitude" in data or "longitude" in data:
            raise ValueError("Both latitude and longitude must be provided together")

        if "description" in data:
            description = data["description"]
            if description is not None:
                description = description.strip()
                if len(description) > 1000:
                    raise ValueError("Description cannot exceed 1000 characters")
            validated_data["description"] = description

        if "phone" in data:
            phone = data["phone"]
            if phone is not None:
                phone = phone.strip()
                if len(phone) > 20:
                    raise ValueError("Phone number cannot exceed 20 characters")
            validated_data["phone"] = phone

        if "email" in data:
            email = data["email"]
            if email is not None:
                email = email.strip()
                if email and len(email) > 100:
                    raise ValueError("Email cannot exceed 100 characters")
                if email and "@" not in email:
                    raise ValueError("Invalid email format")
            validated_data["email"] = email

        if "is_active" in data:
            is_active = data["is_active"]
            if not isinstance(is_active, bool):
                raise ValueError("is_active must be a boolean value")
            validated_data["is_active"] = is_active

        if "category_ids" in data:
            category_ids = data["category_ids"]
            if category_ids is not None:
                if not isinstance(category_ids, list):
                    raise ValueError("category_ids must be a list")

                # Validate each category ID
                validated_category_ids = []
                for cat_id in category_ids:
                    if not isinstance(cat_id, str) or not cat_id.strip():
                        raise ValueError("Each category ID must be a non-empty string")
                    validated_category_ids.append(cat_id.strip())

                validated_data["category_ids"] = validated_category_ids
            else:
                validated_data["category_ids"] = []

        return validated_data

    @staticmethod
    def validate_restaurant_id(restaurant_id):
        """
        Validate restaurant ID format.

        Args:
            restaurant_id (str): Restaurant ID

        Returns:
            str: Validated restaurant ID

        Raises:
            ValueError: If restaurant ID is invalid
        """
        if not restaurant_id:
            raise ValueError("Restaurant ID is required")

        if not isinstance(restaurant_id, str):
            raise ValueError("Restaurant ID must be a string")

        # Basic UUID format validation (36 characters with hyphens)
        restaurant_id = restaurant_id.strip()
        if len(restaurant_id) != 36:
            raise ValueError("Invalid restaurant ID format")

        return restaurant_id

    @staticmethod
    def validate_route_data(data):
        """
        Validate data for route calculation.

        Args:
            data (dict): Route calculation data

        Returns:
            dict: Validated route data

        Raises:
            ValueError: If route data is invalid
        """
        if not data or not isinstance(data, dict):
            raise ValueError("Route data is required")

        coordinates = data.get("coordinates")
        restaurant_id = data.get("restaurant_id")

        if not coordinates:
            raise ValueError("Coordinates are required")
        if not restaurant_id:
            raise ValueError("Restaurant ID is required")

        # Validate coordinates format
        if not isinstance(coordinates, list) or len(coordinates) != 2:
            raise ValueError("Coordinates must be an array of [longitude, latitude]")

        try:
            lng, lat = float(coordinates[0]), float(coordinates[1])
        except (TypeError, ValueError):
            raise ValueError("Invalid coordinate values")

        # Validate coordinates ranges (note: longitude first in coordinates array)
        if not (-180 <= lng <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")

        # Validate restaurant ID
        validated_restaurant_id = RestaurantValidator.validate_restaurant_id(
            restaurant_id
        )

        return {"coordinates": [lng, lat], "restaurant_id": validated_restaurant_id}
