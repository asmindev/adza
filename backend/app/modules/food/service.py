from app.modules.food.repository import FoodRepository
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant
from app.modules.rating.models import FoodRating
from app.modules.rating.repository import FoodRatingRepository
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
        return FoodRepository.get_all()

    @staticmethod
    def get_all_foods_with_details(limit: int = 10) -> List[Dict[str, Any]]:
        foods = FoodRepository.get_all_with_limit(limit)
        return [food.to_dict() for food in foods]

    @staticmethod
    def get_food_detail(food_id: int) -> Optional[Dict[str, Any]]:
        food = FoodRepository.get_by_id(food_id)
        if not food:
            return None
        return food.to_dict()

    @staticmethod
    def get_user_rating(user_id: int, food_id: int) -> Optional[FoodRating]:
        return FoodRatingRepository.get_user_rating(user_id, food_id)

    @staticmethod
    def create_food(
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        price: Optional[float] = None,
        images: Optional[List[FileStorage]] = None,
    ) -> Food:
        logger.info(f"Membuat makanan baru dengan nama: {name}")

        # Create food record
        food = Food(name=name, description=description, category=category, price=price)
        food = FoodRepository.create(food)

        # Handle image uploads if any
        if images and len(images) > 0:
            logger.info(f"Memproses {len(images)} gambar untuk makanan ID: {food.id}")

            # Make sure directory exists
            try:
                # Try to get path from app config
                image_dir = current_app.config.get("FOODS_IMAGES_PATH")
                if not image_dir:
                    # Fallback to default path
                    image_dir = os.path.join(
                        "app", "assets", "images", "foods", str(food.id)
                    )
                    logger.warning(
                        "FOODS_IMAGES_PATH not found in config, using default path"
                    )
            except RuntimeError:
                # Not in application context
                image_dir = os.path.join(
                    "app", "assets", "images", "foods", str(food.id)
                )
                logger.warning("Not in application context, using default path")

            os.makedirs(image_dir, exist_ok=True)

            for image in images:
                if image and image.filename:
                    # Generate a secure filename with unique identifier
                    filename = secure_filename(image.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"

                    # Create full path
                    file_path = os.path.join(image_dir, unique_filename)

                    # Save the file
                    image.save(file_path)
                    logger.info(f"Gambar disimpan di {file_path}")

                    # Associate image with food in database
                    FoodRepository.add_food_image(food.id, unique_filename)

        return food

    @staticmethod
    def update_food(
        food_id: int,
        data: Dict[str, Any],
        new_images: Optional[List[FileStorage]] = None,
        deleted_image_ids: Optional[List[Text]] = None,
    ) -> Optional[Food]:
        logger.info(f"Memperbarui makanan dengan ID: {food_id}")
        food = FoodRepository.get_by_id(food_id)
        if not food:
            return None

        # Update food properties
        for key, value in data.items():
            if hasattr(food, key):
                setattr(food, key, value)

        # Save the updated food information
        food = FoodRepository.update(food)

        # Handle image management if we received image-related parameters
        if new_images is not None or deleted_image_ids is not None:
            # Process deleted images
            if deleted_image_ids:
                # Convert to integers to ensure proper comparison

                for image_id in deleted_image_ids:
                    try:
                        # Get the image record
                        image = FoodRepository.get_food_image(image_id)
                        if image and image.food_id == food_id:  # Security check
                            # Delete the file from filesystem
                            image_path = os.path.join(
                                current_app.config.get(
                                    "FOODS_IMAGES_PATH",
                                    os.path.join("app", "assets", "images", "foods"),
                                ),
                                image.filename,
                            )
                            if os.path.exists(image_path):
                                os.remove(image_path)
                                logger.info(f"File gambar dihapus: {image_path}")

                            # Delete the database record
                            FoodRepository.delete_food_image(image_id)
                            logger.info(f"Record gambar dihapus: ID {image_id}")
                    except Exception as e:
                        logger.error(f"Gagal menghapus gambar ID {image_id}: {str(e)}")

            # Add new images if any
            if new_images and len(new_images) > 0:
                logger.info(f"Menambahkan {len(new_images)} gambar baru")

                # Ensure directory exists
                image_dir = current_app.config.get(
                    "FOODS_IMAGES_PATH",
                    os.path.join("app", "assets", "images", "foods"),
                )
                os.makedirs(image_dir, exist_ok=True)

                # Process each new image
                for image in new_images:
                    if image and image.filename:
                        # Generate unique filename
                        filename = secure_filename(image.filename)
                        unique_filename = f"{uuid.uuid4().hex}_{filename}"

                        # Save file
                        file_path = os.path.join(image_dir, unique_filename)
                        image.save(file_path)
                        logger.info(f"Gambar baru disimpan: {file_path}")

                        # Add to database
                        FoodRepository.add_food_image(food.id, unique_filename)

        return food

    @staticmethod
    def delete_food(food_id: int) -> bool:
        logger.info(f"Menghapus makanan dengan ID: {food_id}")
        food = FoodRepository.get_by_id(food_id)
        # hapus gambar di filesystem
        if food.images:
            for img in food.images:
                try:
                    # Delete the file if it exists
                    if os.path.exists(img.file_path):
                        os.remove(img.file_path)
                        logger.info(f"Menghapus file: {img.file_path}")
                except Exception as e:
                    logger.error(f"Gagal menghapus file gambar: {str(e)}")
        if not food:
            return False

        return FoodRepository.delete(food)

    @staticmethod
    def search_foods(
        category: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        if category:
            return [
                food.to_dict()
                for food in FoodRepository.get_by_category(category, limit)
            ]
        else:
            return [food.to_dict() for food in FoodRepository.get_all_with_limit(limit)]
