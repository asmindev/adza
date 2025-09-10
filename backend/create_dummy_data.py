#!/usr/bin/env python3
"""
Script to generate dummy data for recommendation system testing
"""

import sys
import os
import random
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from flask import Flask
from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating, RestaurantRating


def generate_dummy_users(count=50):
    """Generate dummy users"""
    users = []
    first_names = [
        "Andi",
        "Budi",
        "Citra",
        "Dewi",
        "Eko",
        "Fitri",
        "Gani",
        "Heni",
        "Indra",
        "Joko",
        "Kartika",
        "Lina",
        "Maya",
        "Nanda",
        "Oni",
        "Putri",
        "Qori",
        "Rizki",
        "Sari",
        "Tono",
        "Udin",
        "Vina",
        "Wati",
        "Yoga",
        "Zahra",
        "Agus",
        "Bella",
        "Candra",
        "Diana",
        "Edo",
    ]

    last_names = [
        "Pratama",
        "Sari",
        "Wijaya",
        "Kusuma",
        "Putri",
        "Santoso",
        "Wulandari",
        "Hidayat",
        "Rahayu",
        "Setiawan",
        "Maharani",
        "Nugroho",
        "Permata",
        "Subagyo",
        "Lestari",
        "Hakim",
        "Sartika",
        "Gunawan",
        "Fitriana",
        "Saputra",
        "Dewanti",
        "Pramono",
    ]

    print(f"Generating {count} dummy users...")

    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        user = User(
            name=f"{first_name} {last_name}",
            username=f"user_{i+1:03d}",
            email=f"user{i+1}@example.com",
            password="$2b$12$dummy_hashed_password",  # Dummy hashed password
            role="user",
            onboarding_completed=True,
        )
        users.append(user)

    return users


def generate_dummy_restaurants(count=20):
    """Generate dummy restaurants"""
    restaurants = []

    restaurant_names = [
        "Warung Bu Sri",
        "RM Padang Sederhana",
        "Bakso Pak Kumis",
        "Nasi Gudeg Yogya",
        "Soto Ayam Lamongan",
        "Pecel Lele Pak Jono",
        "Ayam Geprek Bensu",
        "Mie Ayam Pak Tarno",
        "Gado-Gado Pak Dul",
        "Rendang Minang",
        "Nasi Uduk Bu Tuti",
        "Satay Kambing Madura",
        "Bubur Ayam Barito",
        "Nasi Rawon Surabaya",
        "Bakmi GM",
        "Es Campur Bu Yani",
        "Nasi Liwet Solo",
        "Pempek Palembang",
        "Rujak Cingur Pak Ali",
        "Martabak Manis 77",
    ]

    cities = [
        "Jakarta",
        "Bandung",
        "Surabaya",
        "Yogyakarta",
        "Semarang",
        "Malang",
        "Solo",
        "Denpasar",
    ]

    print(f"Generating {count} dummy restaurants...")

    for i, name in enumerate(restaurant_names[:count]):
        city = random.choice(cities)

        restaurant = Restaurant(
            name=name,
            description=f"Authentic Indonesian restaurant serving delicious {name.split()[0]} and traditional dishes",
            address=f"Jl. Merdeka No. {random.randint(1, 200)}, {city}",
            phone=f"08{random.randint(10000000, 99999999)}",
            email=f"info@{name.lower().replace(' ', '').replace('.', '')}restaurant.com",
            latitude=-6.2 + random.uniform(-1, 1),  # Around Indonesia latitude
            longitude=106.8 + random.uniform(-5, 5),  # Around Indonesia longitude
            rating_average=round(random.uniform(3.0, 5.0), 1),
            is_active=True,
        )
        restaurants.append(restaurant)

    return restaurants


def generate_dummy_foods(restaurants, count_per_restaurant=10):
    """Generate dummy foods for each restaurant"""
    foods = []

    food_items = {
        "main_dishes": [
            "Nasi Gudeg",
            "Rendang Daging",
            "Ayam Bakar",
            "Gado-Gado",
            "Nasi Rawon",
            "Soto Ayam",
            "Bakso Urat",
            "Mie Ayam",
            "Pecel Lele",
            "Ayam Geprek",
            "Nasi Uduk",
            "Sate Kambing",
            "Bubur Ayam",
            "Nasi Liwet",
            "Pempek Kapal Selam",
        ],
        "snacks": [
            "Kerupuk Udang",
            "Tahu Isi",
            "Tempe Mendoan",
            "Bakwan Jagung",
            "Pisang Goreng",
            "Cireng",
            "Siomay",
            "Batagor",
            "Otak-Otak",
            "Lumpia Basah",
        ],
        "drinks": [
            "Es Teh Manis",
            "Es Jeruk",
            "Jus Alpukat",
            "Es Campur",
            "Wedang Jahe",
            "Es Kelapa Muda",
            "Jus Mangga",
            "Es Cendol",
            "Bandrek",
            "Bajigur",
        ],
        "desserts": [
            "Es Krim Vanila",
            "Klepon",
            "Onde-Onde",
            "Martabak Manis",
            "Kue Lapis",
            "Pudding Coklat",
            "Es Doger",
            "Cendol",
            "Dawet",
            "Kolak Pisang",
        ],
    }

    print(f"Generating foods for {len(restaurants)} restaurants...")

    for restaurant in restaurants:
        for i in range(count_per_restaurant):
            category = random.choice(list(food_items.keys()))
            food_name = random.choice(food_items[category])

            # Add variation to food names
            variations = ["", "Special", "Original", "Pedas", "Manis", "Gurih"]
            variation = random.choice(variations)
            if variation:
                food_name = f"{food_name} {variation}"

            # Set price based on category
            price_ranges = {
                "main_dishes": (15000, 45000),
                "snacks": (5000, 15000),
                "drinks": (3000, 12000),
                "desserts": (8000, 20000),
            }

            min_price, max_price = price_ranges[category]
            price = random.randint(min_price, max_price)

            food = Food(
                name=food_name,
                description=f"Delicious {food_name.lower()} made with traditional recipe and fresh ingredients",
                price=float(price),
                restaurant_id=restaurant.id,
            )
            foods.append(food)

    return foods


def generate_dummy_ratings(users, foods, restaurants):
    """Generate dummy food and restaurant ratings"""
    food_ratings = []
    restaurant_ratings = []

    print("Generating food ratings...")

    # Each user rates 30-70% of foods randomly
    for user in users:
        num_food_ratings = random.randint(int(len(foods) * 0.3), int(len(foods) * 0.7))
        rated_foods = random.sample(foods, num_food_ratings)

        for food in rated_foods:
            # Generate realistic rating (skewed towards higher ratings)
            rating = random.choices(
                [1.0, 2.0, 3.0, 4.0, 5.0],
                weights=[5, 10, 20, 35, 30],  # More likely to get 4-5 stars
            )[0]

            food_rating = FoodRating(user_id=user.id, food_id=food.id, rating=rating)
            food_ratings.append(food_rating)

    print("Generating restaurant ratings...")

    # Each user rates 40-80% of restaurants randomly
    for user in users:
        num_restaurant_ratings = random.randint(
            int(len(restaurants) * 0.4), int(len(restaurants) * 0.8)
        )
        rated_restaurants = random.sample(restaurants, num_restaurant_ratings)

        for restaurant in rated_restaurants:
            # Generate realistic rating (skewed towards higher ratings)
            rating = random.choices(
                [1.0, 2.0, 3.0, 4.0, 5.0],
                weights=[
                    3,
                    8,
                    25,
                    40,
                    24,
                ],  # Slightly more conservative than food ratings
            )[0]

            # Generate optional comment
            comments = [
                "Pelayanan cepat dan ramah!",
                "Makanan enak dan porsi besar",
                "Tempat bersih dan nyaman",
                "Harga sesuai dengan kualitas",
                "Recommended!",
                "Akan datang lagi",
                "Suasana bagus",
                None,
                None,
                None,  # Some ratings without comments
            ]

            restaurant_rating = RestaurantRating(
                user_id=user.id,
                restaurant_id=restaurant.id,
                rating=rating,
                comment=random.choice(comments),
            )
            restaurant_ratings.append(restaurant_rating)

    return food_ratings, restaurant_ratings


def create_dummy_data():
    """Main function to create all dummy data"""
    app = create_app()

    with app.app_context():
        print("Creating dummy data for recommendation system...")
        print("=" * 60)

        try:
            # Clear existing data using raw SQL to handle foreign keys
            print("Clearing existing data...")

            # Disable foreign key checks temporarily
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))

            # List all tables that might contain data
            tables_to_clear = [
                "food_ratings",
                "restaurant_ratings",
                "reviews",
                "food_images",
                "foods",
                "restaurants",
                "users",
            ]

            for table in tables_to_clear:
                try:
                    result = db.session.execute(db.text(f"DELETE FROM {table}"))
                    print(f"  ✓ Cleared {table} ({result.rowcount} rows)")
                except Exception as e:
                    print(f"  ⚠ Could not clear {table}: {e}")

            # Re-enable foreign key checks
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
            db.session.commit()
            print("  ✓ All data cleared successfully")

            # Generate users
            users = generate_dummy_users(50)
            db.session.add_all(users)
            db.session.commit()
            print(f"✓ Created {len(users)} users")

            # Generate restaurants
            restaurants = generate_dummy_restaurants(20)
            db.session.add_all(restaurants)
            db.session.commit()
            print(f"✓ Created {len(restaurants)} restaurants")

            # Generate foods
            foods = generate_dummy_foods(restaurants, 8)
            db.session.add_all(foods)
            db.session.commit()
            print(f"✓ Created {len(foods)} foods")

            # Generate ratings
            food_ratings, restaurant_ratings = generate_dummy_ratings(
                users, foods, restaurants
            )
            db.session.add_all(food_ratings)
            db.session.add_all(restaurant_ratings)
            db.session.commit()
            print(f"✓ Created {len(food_ratings)} food ratings")
            print(f"✓ Created {len(restaurant_ratings)} restaurant ratings")

            print("\n" + "=" * 60)
            print("✅ DUMMY DATA CREATION COMPLETED!")
            print(f"Summary:")
            print(f"  - Users: {len(users)}")
            print(f"  - Restaurants: {len(restaurants)}")
            print(f"  - Foods: {len(foods)}")
            print(f"  - Food Ratings: {len(food_ratings)}")
            print(f"  - Restaurant Ratings: {len(restaurant_ratings)}")
            print(f"\nRecommendation system is now ready for testing!")

        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating dummy data: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    create_dummy_data()
