from app.modules.food.repository import FoodRepository
from app.modules.food.models import Food
from app.modules.food.data_service import FoodDataService
from app.utils import get_logger
logger = get_logger(__name__)
import os
import uuid
from typing import List, Dict, Optional, Any, Union, Text
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app


class FoodService:

    @staticmethod
    def get_main_image(food):
        """Business logic to find main image for a food"""
        if not hasattr(food, "images") or not food.images:
            return None

        main_image = next((img for img in food.images if img.is_main), None)
        return main_image.to_dict() if main_image else None

    @staticmethod
    def to_dict_with_main_image(food):
        """Convert food to dict with main image logic and restaurant name"""
        base_data = food.to_dict()
        base_data["main_image"] = FoodService.get_main_image(food)

        # Add restaurant name if available
        if hasattr(food, "restaurant") and food.restaurant:
            base_data["restaurant"] = {
                "id": food.restaurant.id,
                "name": food.restaurant.name,
            }

        else:
            base_data["restaurant"] = {}

        # ratings - calculate from the ratings list
        if hasattr(food, "ratings") and food.ratings:
            # Calculate average rating from the list of ratings
            ratings_list = food.ratings
            if ratings_list:
                total_rating = sum(rating.rating for rating in ratings_list)
                average_rating = total_rating / len(ratings_list)
                base_data["ratings"] = {
                    "average": round(average_rating, 1),
                    "count": len(ratings_list),
                }
            else:
                base_data["ratings"] = {"average": 0, "count": 0}
        else:
            base_data["ratings"] = {"average": 0, "count": 0}

        return base_data

    @staticmethod
    def get_all_foods() -> List[Food]:
        """Get all foods - returns ORM objects"""
        return FoodRepository.get_all()

    @staticmethod
    def get_all_foods_with_details(
        page: int = 1,
        limit: int = 10,
        search: Optional[Text] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get paginated foods with aggregated details

        Args:
            page: Page number
            limit: Items per page
            search: Search term (if provided, ignores user preferences)
            user_id: User ID for filtering by favorite categories (ignored if search is provided)
        """
        # Basic validation
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        # Get paginated results with user preferences filtering
        result = FoodRepository.get_all_with_limit(
            page=page, limit=limit, search=search, user_id=user_id
        )
        logger.info(f"result: {result['total_foods']} foods found")

        # Use service method that includes main image
        foods_dict = []
        for food in result["items"]:
            base_data = FoodService.to_dict_with_main_image(food)
            foods_dict.append(base_data)

        return {
            "items": foods_dict,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
            "count": result["total_foods"],
        }

    @staticmethod
    def get_food_detail(food_id: str) -> Optional[Dict[str, Any]]:
        """Get single food with full details"""
        if not food_id or not food_id.strip():
            return None

        food = FoodRepository.get_by_id(food_id)
        if not food:
            return None

        # Use data service to get full details
        return FoodDataService.get_food_with_details(food_id)

    @staticmethod
    def get_user_rating(user_id: str, food_id: str) -> Optional[Dict[str, Any]]:
        """Get user's rating for a food"""
        # Note: This should ideally use rating service, not direct repository
        # For now, keeping compatible with existing code
        from app.modules.rating.repository import FoodRatingRepository

        rating = FoodRatingRepository.get_user_rating(user_id, food_id)
        return rating.to_dict() if rating else None

    @staticmethod
    def create_food(
        name: str,
        description: Optional[str] = None,
        price: Optional[float] = None,
        restaurant_id: Optional[str] = None,
        images: Optional[List[FileStorage]] = None,
    ) -> Dict[str, Any]:
        """Create new food with business validation"""
        logger.info(f"Creating new food: {name}")

        # Basic validation
        if not name or not name.strip():
            raise ValueError("Food name is required")

        name = name.strip()
        if len(name) > 100:
            raise ValueError("Food name too long (max 100 characters)")

        # Create food record
        food = Food(
            name=name, description=description, price=price, restaurant_id=restaurant_id
        )
        food = FoodRepository.create(food)

        # Handle image uploads if any
        if images and len(images) > 0:
            try:
                FoodService._handle_image_uploads(food.id, images)
            except Exception as e:
                logger.error(f"Error uploading images for food {food.id}: {str(e)}")

        # Return full details
        result_food = FoodDataService.get_food_with_details(food.id)
        if not result_food:
            # Fallback to service method if data service fails
            result_food = FoodService.to_dict_with_main_image(food)
        return result_food

    @staticmethod
    def update_food(
        food_id: str,
        data: Dict[str, Any],
        new_images: Optional[List[FileStorage]] = None,
        deleted_image_ids: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update food with validation"""
        logger.info(f"Updating food: {food_id}")

        if not food_id or not food_id.strip():
            return None

        food = FoodRepository.get_by_id(food_id)
        if not food:
            return None

        # Basic validation
        if "name" in data:
            if not data["name"] or not data["name"].strip():
                raise ValueError("Food name cannot be empty")
            data["name"] = data["name"].strip()
            if len(data["name"]) > 100:
                raise ValueError("Food name too long (max 100 characters)")

        # Update food properties
        for key, value in data.items():
            if hasattr(food, key) and key not in ["id", "created_at", "updated_at"]:
                setattr(food, key, value)

        # Save the updated food
        food = FoodRepository.update(food)

        # Handle image management
        if deleted_image_ids:
            FoodService._handle_image_deletions(food_id, deleted_image_ids)

        if new_images:
            FoodService._handle_image_uploads(food_id, new_images)

        # Return updated food with full details
        result_food = FoodDataService.get_food_with_details(food.id)
        if not result_food:
            # Fallback to service method if data service fails
            result_food = FoodService.to_dict_with_main_image(food)
        return result_food

    @staticmethod
    def delete_food(food_id: str) -> bool:
        """Delete food and cleanup associated files"""
        logger.info(f"Deleting food: {food_id}")

        if not food_id or not food_id.strip():
            return False

        food = FoodRepository.get_by_id(food_id)
        if not food:
            return False

        # Clean up image files before deletion
        try:
            FoodService._cleanup_food_images(food)
        except Exception as e:
            logger.error(f"Error cleaning up images for food {food_id}: {str(e)}")

        return FoodRepository.delete(food)

    @staticmethod
    def search_foods(
        restaurant_id: Optional[str] = None, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """Search foods with filters"""
        # Basic validation
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        if restaurant_id:
            # Search by restaurant - use proper query
            from app.extensions import db
            from app.modules.food.models import Food

            # Use proper query without complex joinedload for now
            foods_query = (
                Food.query.filter(Food.restaurant_id == restaurant_id)
                .order_by(Food.created_at.desc())
                .limit(limit)
                .all()
            )

            # Convert to paginated format for consistency
            result = {
                "items": foods_query,
                "total": len(foods_query),
                "page": 1,
                "limit": limit,
                "pages": 1,
            }
        else:
            result = FoodRepository.get_all_with_limit(page=page, limit=limit)

        # Use service method that includes main image and restaurant name
        foods_dict = []
        for food in result["items"]:
            base_data = FoodService.to_dict_with_main_image(food)
            foods_dict.append(base_data)

        return {
            "items": foods_dict,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
        }

    # Private helper methods
    @staticmethod
    def _handle_image_uploads(food_id: str, images: List[FileStorage]) -> None:
        """Handle uploading multiple images for a food"""
        logger.info(f"Processing {len(images)} images for food {food_id}")

        # Get or create image directory
        image_dir = current_app.config.get("FOODS_IMAGES_PATH") or os.path.join(
            "app", "assets", "images", "foods"
        )

        for image in images:
            if image and image.filename:
                try:
                    # Generate secure filename
                    filename = secure_filename(image.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"

                    # Save file
                    file_path = os.path.join(image_dir, unique_filename)
                    image.save(file_path)
                    logger.info(f"Image saved: {file_path}")

                    # Add to database
                    FoodRepository.add_food_image(food_id, unique_filename)

                except Exception as e:
                    logger.error(f"Error saving image {image.filename}: {str(e)}")
                    # Continue with other images

    @staticmethod
    def _handle_image_deletions(food_id: str, deleted_image_ids: List[str]) -> None:
        """Handle deletion of specified images"""
        for image_id in deleted_image_ids:
            try:
                # Get the image record
                image = FoodRepository.get_food_image(image_id)
                if image and image.food_id == food_id:  # Security check
                    # Delete file from filesystem
                    image_path = os.path.join(
                        FoodService._get_food_image_directory(food_id), image.filename
                    )
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.info(f"Image file deleted: {image_path}")

                    # Delete database record
                    FoodRepository.delete_food_image(image_id)
                    logger.info(f"Image record deleted: {image_id}")

            except Exception as e:
                logger.error(f"Error deleting image {image_id}: {str(e)}")

    @staticmethod
    def _cleanup_food_images(food: Food) -> None:
        """Clean up all image files for a food"""
        try:
            images = getattr(food, "images", None)
            if images:
                for image in images:
                    try:
                        image_path = os.path.join(
                            FoodService._get_food_image_directory(food.id),
                            image.filename,
                        )
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            logger.info(f"Cleaned up image: {image_path}")
                    except Exception as e:
                        logger.error(
                            f"Error cleaning up image {image.filename}: {str(e)}"
                        )
        except Exception as e:
            logger.error(f"Error accessing images for food {food.id}: {str(e)}")

    @staticmethod
    def _get_food_image_directory(food_id: str) -> str:
        """Get the directory path for food images"""
        try:
            base_path = current_app.config.get("FOODS_IMAGES_PATH")
            if not base_path:
                base_path = os.path.join("app", "assets", "images", "foods")
                logger.warning("FOODS_IMAGES_PATH not in config, using default")
        except RuntimeError:
            # Not in application context
            base_path = os.path.join("app", "assets", "images", "foods")
            logger.warning("Not in application context, using default path")

        return os.path.join(base_path, str(food_id))
