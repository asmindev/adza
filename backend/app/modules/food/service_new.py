from app.modules.food.repository import FoodRepository
from app.modules.food.models import Food
from app.modules.food.data_service import FoodDataService
from app.utils import api_logger as logger
import os
import uuid
from typing import List, Dict, Optional, Any, Union, Text
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app


class FoodService:

    @staticmethod
    def get_all_foods() -> List[Food]:
        """Get all foods - returns ORM objects"""
        return FoodRepository.get_all()

    @staticmethod
    def get_all_foods_with_details(
        page: int = 1, limit: int = 10, search: Optional[Text] = None
    ) -> Dict[str, Any]:
        """Get paginated foods with aggregated details"""
        # Basic validation
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        # Get paginated results
        result = FoodRepository.get_all_with_limit(
            page=page, limit=limit, search=search
        )

        # Use basic data for now
        foods_dict = []
        for food in result["items"]:
            base_data = food.to_dict()
            foods_dict.append(base_data)

        return {
            "items": foods_dict,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"],
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
        return result_food if result_food else food.to_dict()

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
        return result_food if result_food else food.to_dict()

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
            # Search by restaurant - use available method
            # Since get_by_restaurant_id doesn't exist, we'll filter differently
            all_foods = FoodRepository.get_all()
            foods = [f for f in all_foods if f.restaurant_id == restaurant_id][:limit]
            # Convert to paginated format for consistency
            result = {
                "items": foods,
                "total": len(foods),
                "page": 1,
                "limit": limit,
                "pages": 1,
            }
        else:
            result = FoodRepository.get_all_with_limit(page=page, limit=limit)

        # Use basic data for now
        foods_dict = []
        for food in result["items"]:
            base_data = food.to_dict()
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
        image_dir = FoodService._get_food_image_directory(food_id)
        os.makedirs(image_dir, exist_ok=True)

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
