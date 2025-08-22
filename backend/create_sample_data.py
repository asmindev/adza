"""
Sample Data Creation Script
Creates initial data for testing the recommendation system
"""

import random
import string
import uuid
import argparse
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.modules.review.models import Review

# Parse command line arguments
parser = argparse.ArgumentParser(description="Create sample data for GoFood API")
parser.add_argument(
    "--reset", action="store_true", help="Reset database (delete existing sample data)"
)
args = parser.parse_args()

# Import database models and recommendation service
from app.extensions import db
from app.modules.user.models import User
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food, FoodImage
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.review.models import Review

from app.recommendation.service import RecommendationService
from app.utils import training_logger as logger

# Initialize database connection (ensure app context is available)
from app import create_app

app = create_app()
app.app_context().push()

logger.info("Starting enhanced sample data creation and insertion into database...")
if args.reset:
    logger.info(
        "Reset flag detected - will clear existing sample data before insertion"
    )

# Generate UUIDs for consistent referencing - expanded dataset
user_uuids = {f"user{i}": str(uuid.uuid4()) for i in range(1, 11)}  # 10 users
restaurant_uuids = {
    f"restaurant{i}": str(uuid.uuid4()) for i in range(1, 8)
}  # 7 restaurants
food_uuids = {f"food{i}": str(uuid.uuid4()) for i in range(1, 21)}  # 20 foods

# Create data structures to hold our sample data
users_data = []
restaurants_data = []
foods_data = []
ratings_data = []
restaurant_ratings_data = []
reviews_data = []

# 1. Create 10 users with varied price preferences
admin = {
    "name": "Admin",
    "id": user_uuids["user1"],
    "username": "admin",
    "email": "admin@example.com",
    "password": generate_password_hash("admin123"),
    "role": "admin",
}
users_data.append(admin)

# Regular users with different personas
user_personas = [
    {"name": "Budget Budi", "username": "budi_budget", "email": "budi@example.com"},
    {"name": "Premium Sari", "username": "sari_premium", "email": "sari@example.com"},
    {"name": "Student Andi", "username": "andi_student", "email": "andi@example.com"},
    {"name": "Foodie Maya", "username": "maya_foodie", "email": "maya@example.com"},
    {
        "name": "Office Worker Rini",
        "username": "rini_office",
        "email": "rini@example.com",
    },
    {"name": "Family Dad Joko", "username": "joko_family", "email": "joko@example.com"},
    {
        "name": "Health Conscious Lisa",
        "username": "lisa_health",
        "email": "lisa@example.com",
    },
    {
        "name": "Traditional Pak Umar",
        "username": "umar_traditional",
        "email": "umar@example.com",
    },
    {
        "name": "Modern Millenial Alex",
        "username": "alex_modern",
        "email": "alex@example.com",
    },
]

for i, persona in enumerate(user_personas, 2):
    users_data.append(
        {
            "name": persona["name"],
            "id": user_uuids[f"user{i}"],
            "username": persona["username"],
            "email": persona["email"],
            "password": generate_password_hash("user123"),
            "role": "regular",
        }
    )

# 2. Create 7 restaurants with varied quality levels and price ranges
restaurants_data = [
    {
        "id": restaurant_uuids["restaurant1"],
        "name": "Warung Nasi Bu Sari",
        "description": "Warung tradisional yang menyajikan nasi kuning dan ayam geprek terbaik di kota",
        "address": "Jl. Malioboro No. 123, Yogyakarta",
        "phone": "+62274123456",
        "email": "warungbusari@gmail.com",
        "latitude": -7.7956,
        "longitude": 110.3695,
        "rating_average": 4.2,  # Good quality traditional place
        "is_active": True,
    },
    {
        "id": restaurant_uuids["restaurant2"],
        "name": "Mie Corner",
        "description": "Spesialis mie dengan berbagai varian - bakso, ayam, dan ramen",
        "address": "Jl. Kaliurang KM 5, Yogyakarta",
        "phone": "+62274234567",
        "email": "miecorner@gmail.com",
        "latitude": -7.7667,
        "longitude": 110.3833,
        "rating_average": 3.8,  # Decent noodle place
        "is_active": True,
    },
    {
        "id": restaurant_uuids["restaurant3"],
        "name": "Premium Ramen House",
        "description": "Authentic Japanese ramen with rich and flavorful broth",
        "address": "Jl. Solo No. 45, Yogyakarta",
        "phone": "+62274345678",
        "email": "ramenhouse@gmail.com",
        "latitude": -7.8014,
        "longitude": 110.3644,
        "rating_average": 4.7,  # High-end ramen place
        "is_active": True,
    },
    {
        "id": restaurant_uuids["restaurant4"],
        "name": "Burger King Local",
        "description": "Fast food burger joint with local Indonesian twist",
        "address": "Jl. Sudirman No. 78, Yogyakarta",
        "phone": "+62274456789",
        "email": "burgerkinglocal@gmail.com",
        "latitude": -7.7834,
        "longitude": 110.3672,
        "rating_average": 3.5,  # Average fast food
        "is_active": True,
    },
    {
        "id": restaurant_uuids["restaurant5"],
        "name": "Seafood Paradise",
        "description": "Fresh seafood restaurant with ocean-to-table concept",
        "address": "Jl. Pantai Parangtritis, Yogyakarta",
        "phone": "+62274567890",
        "email": "seafoodparadise@gmail.com",
        "latitude": -8.0250,
        "longitude": 110.3297,
        "rating_average": 4.5,  # High quality seafood
        "is_active": True,
    },
    {
        "id": restaurant_uuids["restaurant6"],
        "name": "Warung Tegal Pak Jono",
        "description": "Warteg murah meriah dengan menu lengkap",
        "address": "Jl. Gejayan No. 12, Yogyakarta",
        "phone": "+62274678901",
        "email": "wartegpakjono@gmail.com",
        "latitude": -7.7729,
        "longitude": 110.3755,
        "rating_average": 3.2,  # Cheap but basic quality
        "is_active": True,
    },
    {
        "id": restaurant_uuids["restaurant7"],
        "name": "Fine Dining Le Gourmet",
        "description": "Upscale restaurant with international cuisine",
        "address": "Jl. Jenderal Sudirman No. 1, Yogyakarta",
        "phone": "+62274789012",
        "email": "legourmet@gmail.com",
        "latitude": -7.7897,
        "longitude": 110.3678,
        "rating_average": 4.8,  # Premium fine dining
        "is_active": True,
    },
]

# 3. Create 20 foods with varied prices and categories
foods_data = [
    # Budget options (5k-15k)
    {
        "id": food_uuids["food1"],
        "name": "Nasi Putih + Tahu Tempe",
        "description": "Basic rice with tofu and tempeh",
        "price": 8000,
        "category": "Rice",
        "restaurant_id": restaurant_uuids["restaurant6"],
    },
    {
        "id": food_uuids["food2"],
        "name": "Mie Instan Rebus",
        "description": "Simple boiled instant noodles",
        "price": 12000,
        "category": "Noodles",
        "restaurant_id": restaurant_uuids["restaurant6"],
    },
    # Mid-range options (15k-25k)
    {
        "id": food_uuids["food3"],
        "name": "Nasi Kuning",
        "description": "Indonesian yellow rice made with coconut milk and turmeric",
        "price": 15000,
        "category": "Rice",
        "restaurant_id": restaurant_uuids["restaurant1"],
    },
    {
        "id": food_uuids["food4"],
        "name": "Ayam Geprek",
        "description": "Crushed fried chicken with spicy sauce",
        "price": 20000,
        "category": "Chicken",
        "restaurant_id": restaurant_uuids["restaurant1"],
    },
    {
        "id": food_uuids["food5"],
        "name": "Mie Bakso",
        "description": "Noodles with meatballs in savory broth",
        "price": 18000,
        "category": "Noodles",
        "restaurant_id": restaurant_uuids["restaurant2"],
    },
    {
        "id": food_uuids["food6"],
        "name": "Mie Ayam",
        "description": "Chicken noodles with savory chicken broth",
        "price": 18000,
        "category": "Noodles",
        "restaurant_id": restaurant_uuids["restaurant2"],
    },
    {
        "id": food_uuids["food7"],
        "name": "Burger Classic",
        "description": "Classic beef burger with cheese and vegetables",
        "price": 22000,
        "category": "Fast Food",
        "restaurant_id": restaurant_uuids["restaurant4"],
    },
    {
        "id": food_uuids["food8"],
        "name": "Fried Chicken Bucket",
        "description": "Crispy fried chicken with special seasoning",
        "price": 25000,
        "category": "Chicken",
        "restaurant_id": restaurant_uuids["restaurant4"],
    },
    # Higher-end options (25k-40k)
    {
        "id": food_uuids["food9"],
        "name": "Tonkotsu Ramen",
        "description": "Rich pork bone broth ramen with chashu",
        "price": 35000,
        "category": "Noodles",
        "restaurant_id": restaurant_uuids["restaurant3"],
    },
    {
        "id": food_uuids["food10"],
        "name": "Spicy Miso Ramen",
        "description": "Spicy miso-based ramen with bamboo shoots",
        "price": 32000,
        "category": "Noodles",
        "restaurant_id": restaurant_uuids["restaurant3"],
    },
    {
        "id": food_uuids["food11"],
        "name": "Grilled Salmon",
        "description": "Fresh grilled salmon with lemon butter sauce",
        "price": 45000,
        "category": "Seafood",
        "restaurant_id": restaurant_uuids["restaurant5"],
    },
    {
        "id": food_uuids["food12"],
        "name": "Seafood Platter",
        "description": "Mixed seafood platter with prawns, fish, and calamari",
        "price": 38000,
        "category": "Seafood",
        "restaurant_id": restaurant_uuids["restaurant5"],
    },
    # Premium options (40k+)
    {
        "id": food_uuids["food13"],
        "name": "Wagyu Steak",
        "description": "Premium wagyu beef steak with truffle sauce",
        "price": 85000,
        "category": "Steak",
        "restaurant_id": restaurant_uuids["restaurant7"],
    },
    {
        "id": food_uuids["food14"],
        "name": "Lobster Thermidor",
        "description": "Classic French lobster dish with cream sauce",
        "price": 95000,
        "category": "Seafood",
        "restaurant_id": restaurant_uuids["restaurant7"],
    },
    {
        "id": food_uuids["food15"],
        "name": "Duck Confit",
        "description": "Slow-cooked duck leg with garlic and herbs",
        "price": 75000,
        "category": "Duck",
        "restaurant_id": restaurant_uuids["restaurant7"],
    },
    # Additional variety
    {
        "id": food_uuids["food16"],
        "name": "Tom Yum Seafood",
        "description": "Spicy and sour Thai soup with mixed seafood",
        "price": 28000,
        "category": "Soup",
        "restaurant_id": restaurant_uuids["restaurant5"],
    },
    {
        "id": food_uuids["food17"],
        "name": "Nasi Gudeg",
        "description": "Traditional Yogyakarta sweet jackfruit curry with rice",
        "price": 16000,
        "category": "Rice",
        "restaurant_id": restaurant_uuids["restaurant1"],
    },
    {
        "id": food_uuids["food18"],
        "name": "Gado-Gado",
        "description": "Indonesian salad with peanut sauce",
        "price": 14000,
        "category": "Salad",
        "restaurant_id": restaurant_uuids["restaurant6"],
    },
    {
        "id": food_uuids["food19"],
        "name": "Beef Rendang",
        "description": "Slow-cooked spicy beef curry from Padang",
        "price": 30000,
        "category": "Beef",
        "restaurant_id": restaurant_uuids["restaurant1"],
    },
    {
        "id": food_uuids["food20"],
        "name": "Fish and Chips",
        "description": "Crispy battered fish with french fries",
        "price": 26000,
        "category": "Fish",
        "restaurant_id": restaurant_uuids["restaurant4"],
    },
]

# 4. Create realistic ratings based on user personas and price preferences
user_price_preferences = {
    user_uuids["user1"]: 25000,  # Admin - moderate preference
    user_uuids["user2"]: 12000,  # Budget Budi - very budget conscious
    user_uuids["user3"]: 50000,  # Premium Sari - high-end preference
    user_uuids["user4"]: 15000,  # Student Andi - student budget
    user_uuids["user5"]: 35000,  # Foodie Maya - willing to pay for quality
    user_uuids["user6"]: 22000,  # Office Worker Rini - moderate budget
    user_uuids["user7"]: 20000,  # Family Dad Joko - family budget
    user_uuids["user8"]: 18000,  # Health Conscious Lisa - moderate budget
    user_uuids["user9"]: 16000,  # Traditional Pak Umar - traditional prices
    user_uuids["user10"]: 40000,  # Modern Millenial Alex - willing to spend
}

# Create realistic rating patterns
for user_key, user_id in user_uuids.items():
    user_price_pref = user_price_preferences[user_id]

    # Each user rates 60-80% of available foods
    foods_to_rate = random.sample(list(food_uuids.values()), k=random.randint(12, 16))

    for food_id in foods_to_rate:
        # Find the food to get its price and restaurant
        food_data = next(f for f in foods_data if f["id"] == food_id)
        food_price = food_data["price"]
        restaurant_id = food_data["restaurant_id"]
        restaurant_data = next(r for r in restaurants_data if r["id"] == restaurant_id)
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

# 4.5. Create restaurant ratings (tempat/place quality ratings)
# Generate realistic restaurant ratings based on user personas and restaurant quality
for user_key, user_id in user_uuids.items():
    # Each user rates 70-90% of restaurants (place quality evaluation)
    restaurants_to_rate = random.sample(
        list(restaurant_uuids.values()), k=random.randint(5, 7)
    )

    for restaurant_id in restaurants_to_rate:
        # Find the restaurant data
        restaurant_data = next(r for r in restaurants_data if r["id"] == restaurant_id)
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
        elif user_key == "user7":  # Family Dad Joko - focuses on family-friendly places
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

# 5. Create comprehensive reviews with varied content
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

try:
    # Clear existing data if the reset flag is provided
    if args.reset:
        logger.info("Clearing existing sample data...")
        Review.query.delete()
        RestaurantRating.query.delete()
        FoodRating.query.delete()
        FoodImage.query.delete()
        Food.query.delete()
        Restaurant.query.delete()
        # Only delete sample users, not all users
        User.query.filter(
            User.username.in_(
                [
                    "admin",
                    "budi_budget",
                    "sari_premium",
                    "andi_student",
                    "maya_foodie",
                    "rini_office",
                    "joko_family",
                    "lisa_health",
                    "umar_traditional",
                    "alex_modern",
                ]
            )
        ).delete(synchronize_session=False)
        db.session.commit()
        logger.info("Existing sample data cleared successfully")

    # Insert users
    logger.info("Inserting users...")
    users_db = []
    for user_data in users_data:
        user = User(
            id=user_data["id"],
            name=user_data["name"],
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            role=user_data["role"],
        )
        db.session.add(user)
        users_db.append(user)
    db.session.commit()

    # Insert restaurants
    logger.info("Inserting restaurants...")
    restaurants_db = []
    for restaurant_data in restaurants_data:
        restaurant = Restaurant(
            id=restaurant_data["id"],
            name=restaurant_data["name"],
            description=restaurant_data["description"],
            address=restaurant_data["address"],
            phone=restaurant_data["phone"],
            email=restaurant_data["email"],
            latitude=restaurant_data["latitude"],
            longitude=restaurant_data["longitude"],
            is_active=restaurant_data["is_active"],
        )
        db.session.add(restaurant)
        restaurants_db.append(restaurant)
    db.session.commit()

    # Insert foods
    logger.info("Inserting foods...")
    foods_db = []
    for food_data in foods_data:
        food = Food(
            id=food_data["id"],
            name=food_data["name"],
            description=food_data["description"],
            price=food_data["price"],
            category=food_data["category"],
            restaurant_id=food_data["restaurant_id"],
        )
        db.session.add(food)
        foods_db.append(food)
    db.session.commit()

    # Insert ratings
    logger.info("Inserting food ratings...")
    for rating_data in ratings_data:
        rating = FoodRating(
            id=rating_data["id"],
            user_id=rating_data["user_id"],
            food_id=rating_data["food_id"],
            rating=rating_data["rating"],
            created_at=datetime.fromisoformat(rating_data["created_at"]),
        )
        db.session.add(rating)
    db.session.commit()

    # Insert restaurant ratings (place quality ratings)
    logger.info("Inserting restaurant ratings...")
    for restaurant_rating_data in restaurant_ratings_data:
        restaurant_rating = RestaurantRating(
            id=restaurant_rating_data["id"],
            user_id=restaurant_rating_data["user_id"],
            restaurant_id=restaurant_rating_data["restaurant_id"],
            rating=restaurant_rating_data["rating"],
            comment=restaurant_rating_data["comment"],
            created_at=datetime.fromisoformat(restaurant_rating_data["created_at"]),
        )
        db.session.add(restaurant_rating)
    db.session.commit()

    # Insert reviews
    logger.info("Inserting reviews...")
    for review_data in reviews_data:
        review = Review(
            id=review_data["id"],
            user_id=review_data["user_id"],
            food_id=review_data["food_id"],
            review_text=review_data["content"],
        )
        db.session.add(review)
    db.session.commit()

    # Print summary
    logger.info("Enhanced sample data created and inserted into database:")
    logger.info(
        f"- {len(users_data)} users (1 admin, {len(users_data)-1} regular with varied personas)"
    )
    logger.info(f"- {len(restaurants_data)} restaurants (varied quality levels)")
    logger.info(f"- {len(foods_data)} food items (budget to premium pricing)")
    logger.info(
        f"- {len(ratings_data)} food ratings (realistic patterns based on user preferences)"
    )
    logger.info(
        f"- {len(restaurant_ratings_data)} restaurant ratings (place quality assessments)"
    )
    logger.info(f"- {len(reviews_data)} reviews (contextual content)")

    # Print user price preferences for enhanced rating system
    logger.info("\nUser price preferences for enhanced rating system:")
    for user_key, user_id in user_uuids.items():
        user_data = next(u for u in users_data if u["id"] == user_id)
        price_pref = user_price_preferences[user_id]
        logger.info(
            f"- {user_data['name']} ({user_data['username']}): Rp{price_pref:,}"
        )

    # Show restaurant quality distribution
    logger.info("\nRestaurant quality distribution:")
    for restaurant_data in restaurants_data:
        logger.info(
            f"- {restaurant_data['name']}: {restaurant_data['rating_average']}/5.0"
        )

    # Show food price ranges
    logger.info("\nFood price distribution:")
    budget_foods = [f for f in foods_data if f["price"] <= 15000]
    mid_foods = [f for f in foods_data if 15000 < f["price"] <= 30000]
    premium_foods = [f for f in foods_data if f["price"] > 30000]
    logger.info(f"- Budget (≤15k): {len(budget_foods)} items")
    logger.info(f"- Mid-range (15k-30k): {len(mid_foods)} items")
    logger.info(f"- Premium (>30k): {len(premium_foods)} items")

    admin_user_id = user_uuids["user1"]
    admin_ratings = FoodRating.query.filter_by(user_id=admin_user_id).all()
    logger.info(f"\nAdmin rated {len(admin_ratings)} items:")
    for rating in admin_ratings[:5]:  # Show first 5
        food_name = Food.query.get(rating.food_id).name
        logger.info(f"- {food_name}: {rating.rating} stars")

    logger.info("\nTraining standard recommendation models...")
    # Train the SVD model using the RecommendationService
    RecommendationService.train_model(force=True)

    # Test enhanced rating system
    logger.info("\nTesting enhanced rating system...")
    try:
        # Test enhanced recommendations for different user types
        test_users = [
            ("admin", user_uuids["user1"]),
            ("budi_budget", user_uuids["user2"]),
            ("sari_premium", user_uuids["user3"]),
            ("maya_foodie", user_uuids["user5"]),
        ]

        for username, user_id in test_users:
            logger.info(f"\nEnhanced recommendations for {username}:")
            enhanced_recs = RecommendationService.get_recommendations(
                user_id=user_id,
                user_price_preferences=user_price_preferences,
                n=3,
                alpha=0.3,
                beta=0.2,
                gamma=0.2,
            )

            if enhanced_recs:
                for i, rec in enumerate(enhanced_recs[:3], 1):
                    food_name = rec["food"]["name"]
                    price = rec["food"]["price"]
                    predicted_rating = rec["predicted_rating"]
                    logger.info(
                        f"  {i}. {food_name} (Rp{price:,}) - Rating: {predicted_rating:.2f}"
                    )
            else:
                logger.info(f"  No enhanced recommendations available for {username}")

        logger.info("Enhanced rating system test completed successfully!")

    except Exception as e:
        logger.warning(f"Enhanced rating system test failed: {e}")
        logger.info("Standard recommendation system is still available")

    # Get standard recommendations for comparison
    logger.info(f"\nGenerating standard hybrid recommendations for admin...")
    recommendations = RecommendationService.get_hybrid_recommendations(
        admin_user_id, n=5
    )

    if recommendations:
        logger.info("\nStandard hybrid recommendations for admin:")
        for rec in recommendations:
            food_name = rec["food"]["name"]
            price = rec["food"]["price"]
            hybrid_score = rec["hybrid_score"]
            logger.info(f"- {food_name} (Rp{price:,}): Score {hybrid_score:.4f}")
    else:
        logger.info("Could not generate standard recommendations")

    logger.info("\n" + "=" * 60)
    logger.info("ENHANCED SAMPLE DATA CREATION COMPLETE!")
    logger.info("=" * 60)
    logger.info("Features added:")
    logger.info("✓ 10 users with varied price preferences and personas")
    logger.info("✓ 7 restaurants with different quality levels (3.2-4.8 stars)")
    logger.info("✓ 20 foods across budget (8k) to premium (95k) price ranges")
    logger.info("✓ Realistic rating patterns based on user preferences")
    logger.info("✓ Enhanced rating system with place quality, price, and food quality")
    logger.info("✓ Comprehensive reviews for better content-based filtering")
    logger.info("✓ Ready for testing both standard and enhanced recommendation systems")
    logger.info("\nTo reset and regenerate: python create_sample_data.py --reset")

except Exception as e:
    db.session.rollback()
    logger.error(f"Error creating enhanced sample data: {str(e)}")
    raise
