"""
Review data generation for database seeding
"""

import random
import uuid
from datetime import datetime


def generate_reviews_data(ratings_data, foods_data):
    """Generate sample review data based on ratings"""
    reviews_data = []

    review_templates = {
        "excellent": [
            "Makanan luar biasa enak! Sangat direkomendasikan untuk semua orang.",
            "Kualitas terbaik dengan harga yang sepadan. Pasti akan kembali lagi.",
            "Rasa yang autentik dan pelayanan yang memuaskan. Sempurna!",
            "Hidangan terbaik yang pernah saya coba di kategori ini.",
        ],
        "good": [
            "Makanan enak dengan kualitas baik. Worth it untuk dicoba.",
            "Rasa yang memuaskan dan porsi yang cukup. Recommended!",
            "Cukup bagus, sesuai dengan ekspektasi. Akan pesan lagi.",
            "Kualitas makanan baik dengan harga yang wajar.",
        ],
        "average": [
            "Lumayan enak, tapi masih bisa diperbaiki lagi.",
            "Standar saja, tidak istimewa tapi tidak mengecewakan juga.",
            "Cukup untuk mengisi perut, rasa biasa saja.",
            "Oke lah untuk harga segini, tapi jangan terlalu berharap.",
        ],
        "poor": [
            "Kurang memuaskan, rasa tidak sesuai ekspektasi.",
            "Harga mahal tapi kualitas biasa saja. Tidak worth it.",
            "Pelayanan lambat dan makanan dingin. Kecewa.",
            "Tidak akan pesan lagi, banyak tempat lain yang lebih baik.",
        ],
    }

    # Generate reviews based on ratings
    for rating_data in ratings_data:
        # 70% chance to write a review
        if random.random() < 0.7:
            rating_value = rating_data["rating"]

            if rating_value >= 5:
                review_category = "excellent"
            elif rating_value >= 4:
                review_category = "good"
            elif rating_value >= 3:
                review_category = "average"
            else:
                review_category = "poor"

            review_content = random.choice(review_templates[review_category])

            # Add specific food mentions for better content-based filtering
            food_data = next(f for f in foods_data if f["id"] == rating_data["food_id"])
            food_name = food_data["name"]
            category = food_data["category"]

            if "Ramen" in food_name or category == "Noodles":
                if rating_value >= 4:
                    review_content += f" Mie {food_name.lower()} memiliki tekstur yang sempurna dan kuah yang lezat."
            elif category == "Rice":
                if rating_value >= 4:
                    review_content += (
                        f" Nasi dan lauk-pauknya sangat pas, bumbu meresap dengan baik."
                    )
            elif category in ["Seafood", "Fish"]:
                if rating_value >= 4:
                    review_content += f" Seafood segar dengan cita rasa yang autentik."

            reviews_data.append(
                {
                    "id": str(uuid.uuid4()),
                    "user_id": rating_data["user_id"],
                    "food_id": rating_data["food_id"],
                    "content": review_content,
                    "created_at": rating_data["created_at"],
                }
            )

    return reviews_data
