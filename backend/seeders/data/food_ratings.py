"""
Food rating data generation for database seeding
"""

import random
import uuid
from datetime import datetime, timedelta
from .common import user_uuids, food_uuids, user_price_preferences


def generate_food_ratings_data(foods_data, restaurants_data):
    """Generate sample food rating data"""
    ratings_data = []

    # Create realistic rating patterns
    for user_key, user_id in user_uuids.items():
        user_price_pref = user_price_preferences[user_id]

        # Each user rates 60-80% of available foods
        foods_to_rate = random.sample(
            list(food_uuids.values()), k=random.randint(12, 16)
        )

        for food_id in foods_to_rate:
            # Find the food to get its price and restaurant
            food_data = next(f for f in foods_data if f["id"] == food_id)
            food_price = food_data["price"]
            restaurant_id = food_data["restaurant_id"]
            restaurant_data = next(
                r for r in restaurants_data if r["id"] == restaurant_id
            )
            restaurant_rating = restaurant_data["rating_average"]

            # Base rating influenced by restaurant quality
            base_rating = min(5.0, max(1.0, restaurant_rating + random.gauss(0, 0.5)))

            # Price preference influence
            price_diff_ratio = abs(food_price - user_price_pref) / user_price_pref
            if price_diff_ratio > 0.5:  # If price is very different from preference
                base_rating -= random.uniform(0.3, 0.8)
            elif price_diff_ratio < 0.2:  # If price matches preference well
                base_rating += random.uniform(0.2, 0.5)

            # Special preferences for certain users
            if (
                user_key == "user2" and food_price > 20000
            ):  # Budget Budi dislikes expensive food
                base_rating -= random.uniform(0.5, 1.0)
            elif (
                user_key == "user3" and food_price < 30000
            ):  # Premium Sari dislikes cheap food
                base_rating -= random.uniform(0.3, 0.7)
            elif (
                user_key == "user5" and restaurant_rating > 4.0
            ):  # Foodie Maya loves high-quality places
                base_rating += random.uniform(0.3, 0.6)

            # Ensure rating is within 1-5 range and round to integer
            final_rating = max(1, min(5, round(base_rating)))

            ratings_data.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "food_id": food_id,
                    "rating": final_rating,
                    "created_at": (
                        datetime.now() - timedelta(days=random.randint(1, 60))
                    ).isoformat(),
                }
            )

    return ratings_data

    # Return the generated ratings data
    return ratings_data
