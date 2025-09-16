"""
Utility functions for recommendation module
"""

from typing import List, Dict, Any, Optional
from app.modules.food.models import Food, FoodImage
from app.modules.restaurant.models import Restaurant
from app.modules.rating.models import FoodRating
from app.extensions import db
from sqlalchemy import func
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_food_details_batch(food_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get complete food details for a batch of food IDs

    Args:
        food_ids: List of food IDs to fetch details for

    Returns:
        List of dictionaries containing complete food information
    """
    try:
        if not food_ids:
            return []

        # Query foods with their restaurants in one go
        foods_query = (
            db.session.query(Food, Restaurant)
            .outerjoin(Restaurant, Food.restaurant_id == Restaurant.id)
            .filter(Food.id.in_(food_ids))
        )

        foods_data = foods_query.all()

        if not foods_data:
            return []

        # Get all food ratings for calculating averages
        ratings_query = (
            db.session.query(
                FoodRating.food_id,
                func.avg(FoodRating.rating).label("avg_rating"),
                func.count(FoodRating.id).label("rating_count"),
            )
            .filter(FoodRating.food_id.in_(food_ids))
            .group_by(FoodRating.food_id)
        )

        ratings_data = {
            rating.food_id: {
                "average": float(rating.avg_rating) if rating.avg_rating else 0,
                "count": int(rating.rating_count),
            }
            for rating in ratings_query.all()
        }

        # Get all images for these foods
        images_query = (
            db.session.query(FoodImage)
            .filter(FoodImage.food_id.in_(food_ids))
            .order_by(FoodImage.is_main.desc(), FoodImage.created_at.asc())
        )

        images_data = {}
        for image in images_query.all():
            if image.food_id not in images_data:
                images_data[image.food_id] = []
            images_data[image.food_id].append(image.to_dict())

        # Build complete food data
        result = []
        for food, restaurant in foods_data:
            food_dict = food.to_dict()

            # Add restaurant information
            if restaurant:
                food_dict["restaurant"] = {"id": restaurant.id, "name": restaurant.name}
            else:
                food_dict["restaurant"] = None

            # Add rating information
            food_id = food.id
            food_dict["ratings"] = ratings_data.get(food_id, {"average": 0, "count": 0})

            # Add images information
            food_images = images_data.get(food_id, [])
            food_dict["images"] = food_images

            # Find main image
            main_image = None
            for img in food_images:
                if img.get("is_main"):
                    main_image = img
                    break
            if not main_image and food_images:
                main_image = food_images[0]

            food_dict["main_image"] = main_image

            # Format price as per requirement
            if food_dict["price"] is not None:
                food_dict["price"] = {
                    "source": str(food_dict["price"]),
                    "parsedValue": float(food_dict["price"]),
                }
            else:
                food_dict["price"] = {"source": "0.0", "parsedValue": 0.0}

            result.append(food_dict)

        # Maintain original order
        result_dict = {item["id"]: item for item in result}
        ordered_result = [
            result_dict[food_id] for food_id in food_ids if food_id in result_dict
        ]

        logger.info(f"Retrieved details for {len(ordered_result)} foods")
        return ordered_result

    except Exception as e:
        logger.error(f"Error fetching food details: {e}")
        return []


def format_foods_response(
    foods_data: List[Dict[str, Any]], predictions: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Format foods data for API response

    Args:
        foods_data: List of food dictionaries from get_food_details_batch
        predictions: Optional dictionary of food_id -> predicted_rating for recommendations

    Returns:
        List of formatted food dictionaries (direct array without index wrapping)
    """
    try:
        result = []

        for food in foods_data:
            # Create a copy to avoid modifying original
            formatted_food = food.copy()

            # Add predicted rating if provided (for recommendations)
            if predictions and food["id"] in predictions:
                formatted_food["predicted_rating"] = predictions[food["id"]]

            # Return food directly without index wrapping
            result.append(formatted_food)

        return result

    except Exception as e:
        logger.error(f"Error formatting foods response: {e}")
        return []
