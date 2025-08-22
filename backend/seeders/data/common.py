"""
Common utilities and shared data for seed generation
"""

import uuid

# Generate UUIDs for consistent referencing - expanded dataset
user_uuids = {f"user{i}": str(uuid.uuid4()) for i in range(1, 11)}  # 10 users
restaurant_uuids = {
    f"restaurant{i}": str(uuid.uuid4()) for i in range(1, 8)
}  # 7 restaurants
food_uuids = {f"food{i}": str(uuid.uuid4()) for i in range(1, 21)}  # 20 foods

# Define user price preferences for enhanced rating system (as floats to avoid type errors)
user_price_preferences = {
    user_uuids["user1"]: 25000.0,  # Admin - moderate preference
    user_uuids["user2"]: 12000.0,  # Budget Budi - very budget conscious
    user_uuids["user3"]: 50000.0,  # Premium Sari - high-end preference
    user_uuids["user4"]: 15000.0,  # Student Andi - student budget
    user_uuids["user5"]: 35000.0,  # Foodie Maya - willing to pay for quality
    user_uuids["user6"]: 22000.0,  # Office Worker Rini - moderate budget
    user_uuids["user7"]: 20000.0,  # Family Dad Joko - family budget
    user_uuids["user8"]: 18000.0,  # Health Conscious Lisa - moderate budget
    user_uuids["user9"]: 16000.0,  # Traditional Pak Umar - traditional prices
    user_uuids["user10"]: 40000.0,  # Modern Millenial Alex - willing to spend
}
