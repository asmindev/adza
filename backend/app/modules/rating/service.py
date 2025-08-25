from app.modules.rating.repository import (
    FoodRatingRepository,
    RestaurantRatingRepository,
)
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.food.repository import FoodRepository
from app.modules.user.repository import UserRepository
from app.modules.restaurant.repository import RestaurantRepository
from app.utils import api_logger as logger


class FoodRatingService:
    @staticmethod
    def get_food_ratings(food_id, page=1, limit=10):
        """Get all ratings for a specific food with pagination"""
        result = FoodRatingRepository.get_by_food_id(food_id, page=page, limit=limit)
        return {
            "items": [rating.to_dict() for rating in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }

    @staticmethod
    def get_user_ratings(user_id):
        """Get all ratings given by a specific user"""
        ratings = FoodRatingRepository.get_by_user_id(user_id)
        return [rating.to_dict() for rating in ratings]

    @staticmethod
    def get_food_average_rating(food_id):
        """Get average rating for a food"""
        return FoodRatingRepository.get_food_average_rating(food_id)

    @staticmethod
    def get_food_rating_count(food_id):
        """Get rating count for a food"""
        return FoodRatingRepository.get_food_rating_count(food_id)

    @staticmethod
    def create_rating(user_id, food_id, rating_value):
        """Create or update rating"""
        logger.info(
            f"Membuat/memperbarui rating makanan {food_id} dari pengguna {user_id}"
        )

        # Verify user and food exist
        user = UserRepository.get_by_id(user_id)
        food = FoodRepository.get_by_id(food_id)

        if not user:
            logger.warning(f"Pengguna {user_id} tidak ditemukan")
            return None

        if not food:
            logger.warning(f"Makanan {food_id} tidak ditemukan")
            return None

        # Validate rating value
        if not (1 <= rating_value <= 5):
            logger.warning(
                f"Rating value tidak valid: {rating_value}. Harus antara 1-5"
            )
            return None

        # Check if rating already exists
        existing_rating = FoodRatingRepository.get_user_rating(user_id, food_id)

        if existing_rating:
            # Update existing rating
            update_data = {"rating": rating_value}
            updated_rating = FoodRatingRepository.update(existing_rating, update_data)
            logger.info(
                f"Rating diperbarui untuk makanan {food_id} oleh user {user_id}"
            )
            return updated_rating.to_dict()
        else:
            # Create new rating
            rating_data = {
                "user_id": user_id,
                "food_id": food_id,
                "rating": rating_value,
            }
            new_rating = FoodRatingRepository.create(rating_data)
            logger.info(
                f"Rating baru dibuat untuk makanan {food_id} oleh user {user_id}"
            )
            return new_rating.to_dict()

    @staticmethod
    def delete_rating(user_id, food_id):
        """Delete a rating"""
        rating = FoodRatingRepository.get_user_rating(user_id, food_id)
        if not rating:
            return False

        success = FoodRatingRepository.delete(rating)
        if success:
            logger.info(f"Rating dihapus untuk makanan {food_id} oleh user {user_id}")
        return success

    @staticmethod
    def get_user_food_rating(user_id, food_id):
        """Get specific rating by user for a food"""
        rating = FoodRatingRepository.get_user_rating(user_id, food_id)
        return rating.to_dict() if rating else 0


# Legacy alias for backward compatibility
RatingService = FoodRatingService


class RestaurantRatingService:
    @staticmethod
    def get_restaurant_ratings(restaurant_id, page=1, limit=10):
        """Get all ratings for a specific restaurant with pagination"""
        result = RestaurantRatingRepository.get_by_restaurant_id(
            restaurant_id, page=page, limit=limit
        )
        return {
            "items": result["items"],
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }

    @staticmethod
    def get_user_restaurant_ratings(user_id):
        return RestaurantRatingRepository.get_by_user_id(user_id)

    @staticmethod
    def get_user_rating(user_id, restaurant_id):
        return RestaurantRatingRepository.get_user_rating(user_id, restaurant_id)

    @staticmethod
    def get_restaurant_average_rating(restaurant_id):
        return RestaurantRatingRepository.get_restaurant_average_rating(restaurant_id)

    @staticmethod
    def get_restaurant_rating_stats(restaurant_id):
        """Get restaurant rating statistics"""
        avg_rating = RestaurantRatingRepository.get_restaurant_average_rating(
            restaurant_id
        )
        rating_count = RestaurantRatingRepository.get_restaurant_rating_count(
            restaurant_id
        )

        return {"average_rating": avg_rating, "total_ratings": rating_count}

    @staticmethod
    def create_or_update_rating(user_id, restaurant_id, rating_value, comment=None):
        logger.info(
            f"Membuat/memperbarui rating restaurant {restaurant_id} dari pengguna {user_id}"
        )

        # Verify user and restaurant exist
        user = UserRepository.get_by_id(user_id)
        restaurant = RestaurantRepository.get_by_id(restaurant_id)

        if not user or not restaurant:
            logger.warning(
                f"Pengguna {user_id} atau restaurant {restaurant_id} tidak ditemukan"
            )
            return None

        # Validate rating value
        if not (1 <= rating_value <= 5):
            logger.warning(
                f"Rating value tidak valid: {rating_value}. Harus antara 1-5"
            )
            return None

        # Check if rating already exists
        existing_rating = RestaurantRatingRepository.get_user_rating(
            user_id, restaurant_id
        )

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating_value
            if comment is not None:
                existing_rating.comment = comment
            updated_rating = RestaurantRatingRepository.update(existing_rating)

            # Update restaurant's average rating
            RestaurantRatingService._update_restaurant_average_rating(restaurant_id)

            return updated_rating
        else:
            # Create new rating
            new_rating = RestaurantRating(
                user_id=user_id,
                restaurant_id=restaurant_id,
                rating=rating_value,
                comment=comment,
            )
            created_rating = RestaurantRatingRepository.create(new_rating)

            # Update restaurant's average rating
            RestaurantRatingService._update_restaurant_average_rating(restaurant_id)

            return created_rating

    @staticmethod
    def delete_rating(user_id, restaurant_id):
        logger.info(
            f"Menghapus rating restaurant {restaurant_id} dari pengguna {user_id}"
        )
        rating = RestaurantRatingRepository.get_user_rating(user_id, restaurant_id)

        if not rating:
            return False

        success = RestaurantRatingRepository.delete(rating)

        if success:
            # Update restaurant's average rating after deletion
            RestaurantRatingService._update_restaurant_average_rating(restaurant_id)

        return success

    @staticmethod
    def _update_restaurant_average_rating(restaurant_id):
        """Update restaurant's rating_average field"""
        try:
            restaurant = RestaurantRepository.get_by_id(restaurant_id)
            if restaurant:
                avg_rating = RestaurantRatingRepository.get_restaurant_average_rating(
                    restaurant_id
                )
                update_data = {"rating_average": avg_rating if avg_rating else 0.0}
                RestaurantRepository.update(restaurant_id, update_data)
                logger.info(
                    f"Restaurant {restaurant_id} rating_average updated to {avg_rating}"
                )
        except Exception as e:
            logger.error(f"Error updating restaurant average rating: {str(e)}")
