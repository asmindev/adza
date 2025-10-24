from app.modules.rating.repository import (
    FoodRatingRepository,
    RestaurantRatingRepository,
)
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.rating.validators import RatingValidator
from app.modules.rating.data_service import RatingDataService
from app.utils import get_logger
logger = get_logger(__name__)
from typing import Dict, Any, List, Optional


class FoodRatingService:
    """Service for food rating business logic"""

    @staticmethod
    def get_food_ratings(
        food_id: str, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """Get all ratings for a specific food with pagination and statistics"""
        # Validate inputs
        entity_validation = RatingValidator.validate_entity_id(food_id, "food")
        if not entity_validation["valid"]:
            raise ValueError(entity_validation["errors"][0])

        pagination_validation = RatingValidator.validate_pagination_params(page, limit)
        if not pagination_validation["valid"]:
            raise ValueError(pagination_validation["errors"][0])

        page = pagination_validation["data"]["page"]
        limit = pagination_validation["data"]["limit"]

        # Use data service for aggregated data
        return RatingDataService.get_food_ratings_with_aggregation(food_id, page, limit)

    @staticmethod
    def get_user_ratings(user_id: str) -> List[Dict[str, Any]]:
        """Get all ratings given by a specific user"""
        # Validate user ID
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        ratings = FoodRatingRepository.get_by_user_id(user_id)
        return [rating.to_dict() for rating in ratings]

    @staticmethod
    def get_food_rating_statistics(food_id: str) -> Dict[str, Any]:
        """Get rating statistics for a food"""
        # Validate food ID
        entity_validation = RatingValidator.validate_entity_id(food_id, "food")
        if not entity_validation["valid"]:
            raise ValueError(entity_validation["errors"][0])

        return RatingDataService.get_food_rating_statistics(food_id)

    @staticmethod
    def create_or_update_rating(
        user_id: str,
        food_id: str,
        rating_details: Dict[str, float] = None,
        rating_value: float = None,
    ) -> Dict[str, Any]:
        """Create or update rating with proper validation - supports both detailed and simple rating"""
        logger.info(f"Creating/updating food rating {food_id} from user {user_id}")

        # Prepare rating data - prioritize rating_details over rating_value
        if rating_details:
            rating_data = {
                "user_id": user_id,
                "food_id": food_id,
                "rating_details": rating_details,
            }
        elif rating_value is not None:
            rating_data = {
                "user_id": user_id,
                "food_id": food_id,
                "rating": rating_value,
            }
        else:
            raise ValueError("Either rating_details or rating_value must be provided")

        validation_result = RatingValidator.validate_food_rating_data(rating_data)
        if not validation_result["valid"]:
            raise ValueError("; ".join(validation_result["errors"]))

        validated_data = validation_result["data"]

        # Check if rating already exists
        existing_rating = FoodRatingRepository.get_user_rating(
            validated_data["user_id"], validated_data["food_id"]
        )

        if existing_rating:
            # Update existing rating using model method
            existing_rating.update_rating_details(validated_data["rating_details"])
            updated_rating = FoodRatingRepository.update(existing_rating, {})
            logger.info(f"Rating updated for food {food_id} by user {user_id}")
            return updated_rating.to_dict()
        else:
            # Create new rating
            new_rating = FoodRating(
                user_id=validated_data["user_id"],
                food_id=validated_data["food_id"],
                rating_details=validated_data["rating_details"],
            )
            created_rating = FoodRatingRepository.create_instance(new_rating)
            logger.info(f"New rating created for food {food_id} by user {user_id}")
            return created_rating.to_dict()

    @staticmethod
    def delete_rating(user_id: str, food_id: str) -> bool:
        """Delete a rating with validation"""
        # Validate IDs
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        food_validation = RatingValidator.validate_entity_id(food_id, "food")
        if not food_validation["valid"]:
            raise ValueError(food_validation["errors"][0])

        rating = FoodRatingRepository.get_user_rating(user_id, food_id)
        if not rating:
            return False

        success = FoodRatingRepository.delete(rating)
        if success:
            logger.info(f"Rating deleted for food {food_id} by user {user_id}")
        return success

    @staticmethod
    def get_user_food_rating(user_id: str, food_id: str) -> Optional[Dict[str, Any]]:
        """Get specific rating by user for a food"""
        # Validate IDs
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        food_validation = RatingValidator.validate_entity_id(food_id, "food")
        if not food_validation["valid"]:
            raise ValueError(food_validation["errors"][0])

        rating = FoodRatingRepository.get_user_rating(user_id, food_id)
        return rating.to_dict() if rating else None

    @staticmethod
    def get_user_rating_summary(user_id: str) -> Dict[str, Any]:
        """Get comprehensive rating summary for a user"""
        # Validate user ID
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        return RatingDataService.get_user_rating_summary(user_id)


# Legacy alias for backward compatibility
RatingService = FoodRatingService


class RestaurantRatingService:
    """Service for restaurant rating business logic"""

    @staticmethod
    def get_restaurant_ratings(
        restaurant_id: str, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """Get all ratings for a specific restaurant with pagination and statistics"""
        # Validate inputs
        entity_validation = RatingValidator.validate_entity_id(
            restaurant_id, "restaurant"
        )
        if not entity_validation["valid"]:
            raise ValueError(entity_validation["errors"][0])

        pagination_validation = RatingValidator.validate_pagination_params(page, limit)
        if not pagination_validation["valid"]:
            raise ValueError(pagination_validation["errors"][0])

        page = pagination_validation["data"]["page"]
        limit = pagination_validation["data"]["limit"]

        # Use data service for aggregated data
        return RatingDataService.get_restaurant_ratings_with_aggregation(
            restaurant_id, page, limit
        )

    @staticmethod
    def get_user_restaurant_ratings(user_id: str) -> List[Dict[str, Any]]:
        """Get all restaurant ratings given by a specific user"""
        # Validate user ID
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        ratings = RestaurantRatingRepository.get_by_user_id(user_id)
        return [rating.to_dict() for rating in ratings]

    @staticmethod
    def get_user_rating(user_id: str, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """Get specific rating by user for a restaurant"""
        # Validate IDs
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        restaurant_validation = RatingValidator.validate_entity_id(
            restaurant_id, "restaurant"
        )
        if not restaurant_validation["valid"]:
            raise ValueError(restaurant_validation["errors"][0])

        rating = RestaurantRatingRepository.get_user_rating(user_id, restaurant_id)
        return rating.to_dict() if rating else None

    @staticmethod
    def get_restaurant_rating_statistics(restaurant_id: str) -> Dict[str, Any]:
        """Get restaurant rating statistics"""
        # Validate restaurant ID
        entity_validation = RatingValidator.validate_entity_id(
            restaurant_id, "restaurant"
        )
        if not entity_validation["valid"]:
            raise ValueError(entity_validation["errors"][0])

        return RatingDataService.get_restaurant_rating_statistics(restaurant_id)

    @staticmethod
    def create_or_update_rating(
        user_id: str,
        restaurant_id: str,
        rating_value: float,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or update restaurant rating with validation"""
        logger.info(
            f"Creating/updating restaurant rating {restaurant_id} from user {user_id}"
        )

        # Validate input data
        rating_data = {
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "rating": rating_value,
            "comment": comment,
        }

        validation_result = RatingValidator.validate_restaurant_rating_data(rating_data)
        if not validation_result["valid"]:
            raise ValueError("; ".join(validation_result["errors"]))

        validated_data = validation_result["data"]

        # Check if rating already exists
        existing_rating = RestaurantRatingRepository.get_user_rating(
            validated_data["user_id"], validated_data["restaurant_id"]
        )

        if existing_rating:
            # Update existing rating
            existing_rating.rating = validated_data["rating"]
            if "comment" in validated_data:
                existing_rating.comment = validated_data["comment"]
            updated_rating = RestaurantRatingRepository.update(existing_rating)
            logger.info(
                f"Restaurant rating updated for {restaurant_id} by user {user_id}"
            )
            return updated_rating.to_dict()
        else:
            # Create new rating
            new_rating = RestaurantRating(
                user_id=validated_data["user_id"],
                restaurant_id=validated_data["restaurant_id"],
                rating=validated_data["rating"],
                comment=validated_data.get("comment"),
            )
            created_rating = RestaurantRatingRepository.create(new_rating)
            logger.info(
                f"New restaurant rating created for {restaurant_id} by user {user_id}"
            )
            return created_rating.to_dict()

    @staticmethod
    def delete_rating(user_id: str, restaurant_id: str) -> bool:
        """Delete a restaurant rating with validation"""
        # Validate IDs
        user_validation = RatingValidator.validate_entity_id(user_id, "user")
        if not user_validation["valid"]:
            raise ValueError(user_validation["errors"][0])

        restaurant_validation = RatingValidator.validate_entity_id(
            restaurant_id, "restaurant"
        )
        if not restaurant_validation["valid"]:
            raise ValueError(restaurant_validation["errors"][0])

        logger.info(f"Deleting restaurant rating {restaurant_id} from user {user_id}")
        rating = RestaurantRatingRepository.get_user_rating(user_id, restaurant_id)

        if not rating:
            return False

        success = RestaurantRatingRepository.delete(rating)
        if success:
            logger.info(
                f"Restaurant rating deleted for {restaurant_id} by user {user_id}"
            )

        return success
