"""
Restaurant rating data generation for database seeding
"""

import random
import uuid
from datetime import datetime, timedelta
from .common import user_uuids, restaurant_uuids


def generate_restaurant_ratings_data(restaurants_data):
    """Generate sample restaurant rating data"""
    restaurant_ratings_data = []

    # Generate realistic restaurant ratings based on user personas and restaurant quality
    for user_key, user_id in user_uuids.items():
        # Each user rates 70-90% of restaurants (place quality evaluation)
        restaurants_to_rate = random.sample(
            list(restaurant_uuids.values()), k=random.randint(5, 7)
        )

        for restaurant_id in restaurants_to_rate:
            # Find the restaurant data
            restaurant_data = next(
                r for r in restaurants_data if r["id"] == restaurant_id
            )
            restaurant_quality = restaurant_data["rating_average"]

            # Base rating around restaurant's inherent quality with some variation
            base_rating = restaurant_quality + random.gauss(0, 0.6)

            # User-specific preferences for place quality
            if user_key == "user2":  # Budget Budi - lower standards for cheaper places
                if restaurant_quality <= 3.5:  # For lower-end places
                    base_rating += random.uniform(0.2, 0.5)  # More forgiving
            elif user_key == "user3":  # Premium Sari - high standards
                if restaurant_quality < 4.0:  # Critical of lower quality places
                    base_rating -= random.uniform(0.3, 0.8)
                else:  # Appreciates high quality
                    base_rating += random.uniform(0.1, 0.4)
            elif user_key == "user5":  # Foodie Maya - very critical about place quality
                if restaurant_quality >= 4.5:  # Loves premium places
                    base_rating += random.uniform(0.2, 0.5)
                elif restaurant_quality < 3.5:  # Dislikes poor quality places
                    base_rating -= random.uniform(0.5, 0.9)
            elif (
                user_key == "user7"
            ):  # Family Dad Joko - focuses on family-friendly places
                # Prefers mid-range, family-friendly places
                if 3.5 <= restaurant_quality <= 4.2:
                    base_rating += random.uniform(0.2, 0.4)

            # Ensure rating is within 1-5 range
            final_rating = max(1.0, min(5.0, base_rating))

            # Add some comments for higher/lower ratings
            comment = None
            if final_rating >= 4.5:
                comments = [
                    "Tempat yang sangat nyaman dan bersih",
                    "Pelayanan excellent dan suasana bagus",
                    "Kualitas tempat sangat memuaskan",
                    "Ambience bagus, cocok untuk berbagai acara",
                ]
                comment = random.choice(comments)
            elif final_rating <= 2.5:
                comments = [
                    "Tempat kurang bersih dan kurang nyaman",
                    "Pelayanan perlu diperbaiki",
                    "Suasana kurang mendukung",
                    "Kebersihan dan kenyamanan masih kurang",
                ]
                comment = random.choice(comments)
            elif random.random() < 0.3:  # 30% chance for mid-range ratings
                comments = [
                    "Tempat cukup nyaman untuk makan",
                    "Standar untuk tempat makan",
                    "Lokasi strategis tapi bisa lebih baik",
                    "Suasana oke, pelayanan standar",
                ]
                comment = random.choice(comments)

            restaurant_ratings_data.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "restaurant_id": restaurant_id,
                    "rating": round(final_rating, 1),
                    "comment": comment,
                    "created_at": (
                        datetime.now() - timedelta(days=random.randint(1, 60))
                    ).isoformat(),
                }
            )

    return restaurant_ratings_data
