"""
Food data service for handling complex food data operations
This handles data aggregation and business logic related to food data presentation
"""

from .models import Food, FoodImage
from .repository import FoodRepository
from app.extensions import db
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class FoodDataService:
    """Service for handling food data aggregation and complex operations"""

    @staticmethod
    def get_food_with_details(food_id: str) -> Optional[Dict[str, Any]]:
        """
        Get food with detailed information including aggregated data
        This replaces the complex logic that was in the model's to_dict method
        """
        logger.debug(f"Getting detailed information for food: {food_id}")

        try:
            food = FoodRepository.get_by_id(food_id)
            if not food:
                return None

            # Get base food data
            food_data = food.to_dict()

            # Add aggregated ratings data
            ratings_data = FoodDataService._get_food_ratings_aggregated(food)
            food_data["ratings"] = ratings_data

            # Add aggregated reviews data
            reviews_data = FoodDataService._get_food_reviews_aggregated(food)
            food_data["reviews"] = reviews_data

            # Add image data with proper handling
            images_data = FoodDataService._get_food_images_processed(food)
            food_data["images"] = images_data["images"]
            food_data["main_image"] = images_data["main_image"]

            # Add restaurant data if available
            restaurant_data = FoodDataService._get_food_restaurant_info(food)
            if restaurant_data:
                food_data["restaurant"] = restaurant_data["restaurant"]
                food_data["category"] = restaurant_data["category"]

            logger.info(f"Successfully retrieved detailed info for food {food_id}")
            return food_data

        except Exception as e:
            logger.error(f"Error getting food details for {food_id}: {str(e)}")
            return None

    @staticmethod
    def get_foods_with_aggregated_data(foods: List[Food]) -> List[Dict[str, Any]]:
        """
        Get list of foods with aggregated data
        """
        logger.debug(f"Processing {len(foods)} foods with aggregated data")

        result = []
        for food in foods:
            try:
                food_data = food.to_dict()

                # Add basic aggregated data (lighter than full details)
                ratings_summary = FoodDataService._get_food_ratings_summary(food)
                food_data["ratings"] = ratings_summary

                # Add image count and main image
                images_summary = FoodDataService._get_food_images_summary(food)
                food_data.update(images_summary)

                result.append(food_data)

            except Exception as e:
                logger.error(f"Error processing food {food.id}: {str(e)}")
                # Include basic data even if aggregation fails
                result.append(food.to_dict())

        logger.info(f"Successfully processed {len(result)} foods with aggregated data")
        return result

    @staticmethod
    def _get_food_ratings_aggregated(food: Food) -> Dict[str, Any]:
        """Get aggregated ratings data for a food"""
        try:
            # Check if ratings relationship is loaded and has data
            ratings = getattr(food, "ratings", None)
            if not ratings:
                return {"average": 0.0, "count": 0, "data": []}

            ratings_list = []
            try:
                for rating in ratings:
                    try:
                        rating_data = rating.to_dict()
                        ratings_list.append(rating_data)
                    except Exception as e:
                        logger.warning(
                            f"Error processing rating {getattr(rating, 'id', 'unknown')}: {str(e)}"
                        )
            except Exception as e:
                logger.warning(f"Error iterating ratings for food {food.id}: {str(e)}")
                return {"average": 0.0, "count": 0, "data": []}

            # Sort by created_at (most recent first)
            ratings_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            # Calculate average
            if ratings_list:
                total_rating = sum(r.get("rating", 0) for r in ratings_list)
                average = round(total_rating / len(ratings_list), 2)
            else:
                average = 0.0

            return {
                "average": average,
                "count": len(ratings_list),
                "data": ratings_list,
            }

        except Exception as e:
            logger.error(f"Error aggregating ratings for food {food.id}: {str(e)}")
            return {"average": 0.0, "count": 0, "data": []}

    @staticmethod
    def _get_food_ratings_summary(food: Food) -> Dict[str, Any]:
        """Get summary ratings data (lighter version)"""
        try:
            ratings = getattr(food, "ratings", None)
            if not ratings:
                return {"average": 0.0, "count": 0}

            rating_values = []
            try:
                for r in ratings:
                    if hasattr(r, "rating"):
                        rating_values.append(r.rating)
            except Exception as e:
                logger.warning(f"Error iterating ratings for food {food.id}: {str(e)}")
                return {"average": 0.0, "count": 0}

            if rating_values:
                average = round(sum(rating_values) / len(rating_values), 2)
            else:
                average = 0.0

            return {"average": average, "count": len(rating_values)}

        except Exception as e:
            logger.error(f"Error getting ratings summary for food {food.id}: {str(e)}")
            return {"average": 0.0, "count": 0}

    @staticmethod
    def _get_food_reviews_aggregated(food: Food) -> Dict[str, Any]:
        """Get aggregated reviews data for a food"""
        try:
            reviews = getattr(food, "reviews", None)
            if not reviews:
                return {"review_count": 0, "data": []}

            reviews_list = []
            try:
                for review in reviews:
                    try:
                        review_data = review.to_dict()
                        reviews_list.append(review_data)
                    except Exception as e:
                        logger.warning(
                            f"Error processing review {getattr(review, 'id', 'unknown')}: {str(e)}"
                        )
            except Exception as e:
                logger.warning(f"Error iterating reviews for food {food.id}: {str(e)}")
                return {"review_count": 0, "data": []}

            # Sort by created_at (most recent first)
            reviews_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            return {"review_count": len(reviews_list), "data": reviews_list}

        except Exception as e:
            logger.error(f"Error aggregating reviews for food {food.id}: {str(e)}")
            return {"review_count": 0, "data": []}

    @staticmethod
    def _get_food_images_processed(food: Food) -> Dict[str, Any]:
        """Get processed images data with main image logic"""
        try:
            images = getattr(food, "images", None)
            if not images:
                return {"images": [], "main_image": None}

            images_list = []
            main_image = None

            try:
                for image in images:
                    try:
                        image_data = image.to_dict()
                        images_list.append(image_data)

                        # Find main image
                        if image_data.get("is_main", False):
                            main_image = image_data

                    except Exception as e:
                        logger.warning(
                            f"Error processing image {getattr(image, 'id', 'unknown')}: {str(e)}"
                        )
            except Exception as e:
                logger.warning(f"Error iterating images for food {food.id}: {str(e)}")
                return {"images": [], "main_image": None}

            # If no main image is set, use the first one
            if not main_image and images_list:
                main_image = images_list[0].copy()
                main_image["is_main"] = True

            return {"images": images_list, "main_image": main_image}

        except Exception as e:
            logger.error(f"Error processing images for food {food.id}: {str(e)}")
            return {"images": [], "main_image": None}

    @staticmethod
    def _get_food_images_summary(food: Food) -> Dict[str, Any]:
        """Get summary images data (lighter version)"""
        try:
            images = getattr(food, "images", None)
            if not images:
                return {"image_count": 0, "main_image": None}

            # Find main image and count
            main_image = None
            image_count = 0

            try:
                for image in images:
                    image_count += 1
                    try:
                        if hasattr(image, "is_main") and image.is_main:
                            main_image = image.to_dict()
                    except Exception:
                        continue

                # If no main image, use first one
                if not main_image and image_count > 0:
                    try:
                        first_image = next(iter(images))
                        main_image = first_image.to_dict()
                        main_image["is_main"] = True
                    except Exception:
                        pass

            except Exception as e:
                logger.warning(f"Error iterating images for food {food.id}: {str(e)}")
                return {"image_count": 0, "main_image": None}

            return {"image_count": image_count, "main_image": main_image}

        except Exception as e:
            logger.error(f"Error getting images summary for food {food.id}: {str(e)}")
            return {"image_count": 0, "main_image": None}

    @staticmethod
    def _get_food_restaurant_info(food: Food) -> Optional[Dict[str, Any]]:
        """Get restaurant information for a food (avoiding circular imports)"""
        try:
            if not food.restaurant_id:
                return None

            # Import here to avoid circular imports
            from app.modules.restaurant.models import Restaurant

            restaurant = Restaurant.query.get(food.restaurant_id)
            if not restaurant:
                return None

            restaurant_info = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": getattr(restaurant, "address", None),
                "latitude": getattr(restaurant, "latitude", None),
                "longitude": getattr(restaurant, "longitude", None),
            }

            # Get category from restaurant
            category_info = None
            if hasattr(restaurant, "categories") and restaurant.categories:
                try:
                    # Get first category for backward compatibility
                    first_category = restaurant.categories[0]
                    category_info = {
                        "id": first_category.id,
                        "name": first_category.name,
                        "description": getattr(first_category, "description", None),
                    }
                except (IndexError, AttributeError):
                    pass

            return {"restaurant": restaurant_info, "category": category_info}

        except Exception as e:
            logger.error(f"Error getting restaurant info for food {food.id}: {str(e)}")
            return None

    @staticmethod
    def search_foods_with_filters(
        search_term: Optional[str] = None,
        restaurant_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Advanced search for foods with multiple filters
        """
        logger.debug(
            f"Searching foods with filters: search={search_term}, restaurant={restaurant_id}"
        )

        try:
            # Start with all foods query
            query = Food.query

            # Apply search filter
            if search_term:
                search_pattern = f"%{search_term}%"
                query = query.filter(
                    db.or_(
                        Food.name.ilike(search_pattern),
                        Food.description.ilike(search_pattern),
                    )
                )

            # Apply restaurant filter
            if restaurant_id:
                query = query.filter(Food.restaurant_id == restaurant_id)

            # Apply price filters
            if min_price is not None:
                query = query.filter(Food.price >= min_price)

            if max_price is not None:
                query = query.filter(Food.price <= max_price)

            # Execute query
            foods = query.all()

            # Process results with aggregated data
            result = FoodDataService.get_foods_with_aggregated_data(foods)

            # Apply rating filter (after aggregation)
            if min_rating is not None:
                result = [
                    food
                    for food in result
                    if food.get("ratings", {}).get("average", 0) >= min_rating
                ]

            logger.info(f"Found {len(result)} foods matching search criteria")
            return result

        except Exception as e:
            logger.error(f"Error searching foods with filters: {str(e)}")
            return []

    @staticmethod
    def get_food_statistics(food_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive statistics for a food item
        """
        logger.debug(f"Getting statistics for food: {food_id}")

        try:
            food = FoodRepository.get_by_id(food_id)
            if not food:
                return None

            # Basic stats
            ratings_data = FoodDataService._get_food_ratings_aggregated(food)
            reviews_data = FoodDataService._get_food_reviews_aggregated(food)
            images_data = FoodDataService._get_food_images_summary(food)

            stats = {
                "food_id": food.id,
                "food_name": food.name,
                "total_ratings": ratings_data["count"],
                "average_rating": ratings_data["average"],
                "total_reviews": reviews_data["review_count"],
                "total_images": images_data["image_count"],
                "created_at": (
                    food.created_at.isoformat() + "Z" if food.created_at else None
                ),
                "last_updated": (
                    food.updated_at.isoformat() + "Z" if food.updated_at else None
                ),
            }

            # Rating distribution (can be enhanced)
            if ratings_data["data"]:
                rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                for rating in ratings_data["data"]:
                    rating_val = rating.get("rating", 0)
                    if 1 <= rating_val <= 5:
                        rating_counts[int(rating_val)] += 1

                stats["rating_distribution"] = rating_counts

            logger.info(f"Successfully retrieved statistics for food {food_id}")
            return stats

        except Exception as e:
            logger.error(f"Error getting statistics for food {food_id}: {str(e)}")
            return None
