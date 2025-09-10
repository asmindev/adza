"""
Main Seeder File
Runs all seeders in the correct order for recommendation system testing
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.review.models import Review

# Import data generators
from data.users import generate_users_data
from data.restaurants import generate_restaurants_data
from data.foods import generate_foods_data
from data.food_ratings import generate_food_ratings_data
from data.restaurant_ratings import generate_restaurant_ratings_data
from data.reviews import generate_reviews_data


def clear_database():
    """Clear all existing data"""
    print("🧹 Clearing existing data...")

    try:
        # Disable foreign key checks temporarily
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))

        # Delete in any order since foreign keys are disabled
        Review.query.delete()
        FoodRating.query.delete()
        RestaurantRating.query.delete()
        Food.query.delete()
        Restaurant.query.delete()
        User.query.delete()

        # Delete restaurant_categories if exists
        try:
            db.session.execute(db.text("DELETE FROM restaurant_categories"))
        except Exception:
            # Table might not exist, ignore
            pass

        # Re-enable foreign key checks
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))

        db.session.commit()
        print("✅ Database cleared successfully")

    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        db.session.rollback()
        # Re-enable foreign key checks in case of error
        try:
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
            db.session.commit()
        except:
            pass
        raise e
def seed_users():
    """Seed users data"""
    print("👥 Seeding users...")

    try:
        users_data = generate_users_data()

        for user_data in users_data:
            user = User(
                id=user_data["id"],
                name=user_data["name"],
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"]
            )
            db.session.add(user)

        db.session.commit()
        print(f"✅ Successfully seeded {len(users_data)} users")

    except Exception as e:
        print(f"❌ Error seeding users: {str(e)}")
        db.session.rollback()
        raise e


def seed_restaurants():
    """Seed restaurants data"""
    print("� Seeding restaurants...")

    try:
        restaurants_data = generate_restaurants_data()

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
                is_active=restaurant_data["is_active"]
            )
            db.session.add(restaurant)

        db.session.commit()
        print(f"✅ Successfully seeded {len(restaurants_data)} restaurants")
        return restaurants_data

    except Exception as e:
        print(f"❌ Error seeding restaurants: {str(e)}")
        db.session.rollback()
        raise e


def seed_foods():
    """Seed foods data"""
    print("🍽️ Seeding foods...")

    try:
        foods_data = generate_foods_data()

        for food_data in foods_data:
            food = Food(
                id=food_data["id"],
                name=food_data["name"],
                description=food_data["description"],
                price=food_data["price"],
                restaurant_id=food_data["restaurant_id"]
                # Note: image_url will be handled separately via FoodImage if needed
            )
            db.session.add(food)

        db.session.commit()
        print(f"✅ Successfully seeded {len(foods_data)} foods")
        return foods_data

    except Exception as e:
        print(f"❌ Error seeding foods: {str(e)}")
        db.session.rollback()
        raise e
def seed_food_ratings(foods_data, restaurants_data):
    """Seed food ratings data"""
    print("⭐ Seeding food ratings...")

    try:
        ratings_data = generate_food_ratings_data(foods_data, restaurants_data)

        for rating_data in ratings_data:
            rating = FoodRating(
                id=rating_data["id"],
                user_id=rating_data["user_id"],
                food_id=rating_data["food_id"],
                rating=rating_data["rating"]
            )
            db.session.add(rating)

        db.session.commit()
        print(f"✅ Successfully seeded {len(ratings_data)} food ratings")

    except Exception as e:
        print(f"❌ Error seeding food ratings: {str(e)}")
        db.session.rollback()
        raise e


def seed_restaurant_ratings(restaurants_data):
    """Seed restaurant ratings data"""
    print("🏪⭐ Seeding restaurant ratings...")

    try:
        ratings_data = generate_restaurant_ratings_data(restaurants_data)

        for rating_data in ratings_data:
            rating = RestaurantRating(
                id=rating_data["id"],
                user_id=rating_data["user_id"],
                restaurant_id=rating_data["restaurant_id"],
                rating=rating_data["rating"],
                comment=rating_data.get("comment")
            )
            db.session.add(rating)

        db.session.commit()
        print(f"✅ Successfully seeded {len(ratings_data)} restaurant ratings")

    except Exception as e:
        print(f"❌ Error seeding restaurant ratings: {str(e)}")
        db.session.rollback()
        raise e


def seed_reviews(foods_data, restaurants_data):
    """Seed reviews data"""
    print("📝 Seeding reviews...")

    try:
        # Get food ratings data to base reviews on
        food_ratings = FoodRating.query.all()
        ratings_data = []
        for rating in food_ratings:
            ratings_data.append({
                "id": rating.id,
                "user_id": rating.user_id,
                "food_id": rating.food_id,
                "rating": rating.rating,
                "created_at": rating.created_at.isoformat() if rating.created_at else datetime.now().isoformat()
            })

        reviews_data = generate_reviews_data(ratings_data, foods_data)

        for review_data in reviews_data:
            review = Review(
                id=review_data["id"],
                user_id=review_data["user_id"],
                food_id=review_data["food_id"],
                content=review_data["content"]  # Review model uses 'content' field
            )
            db.session.add(review)

        db.session.commit()
        print(f"✅ Successfully seeded {len(reviews_data)} reviews")

    except Exception as e:
        print(f"❌ Error seeding reviews: {str(e)}")
        db.session.rollback()
        raise e
def run_all_seeders():
    """Run all seeders in the correct order"""

    print("🌱 Starting comprehensive database seeding process...")
    print("=" * 70)

    try:
        # Step 1: Clear existing data
        clear_database()

        # Step 2: Seed users
        seed_users()

        # Step 3: Seed restaurants
        restaurants_data = seed_restaurants()

        # Step 4: Seed foods
        foods_data = seed_foods()

        # Step 5: Seed food ratings
        seed_food_ratings(foods_data, restaurants_data)

        # Step 6: Seed restaurant ratings
        seed_restaurant_ratings(restaurants_data)

        # Step 7: Seed reviews
        seed_reviews(foods_data, restaurants_data)

        print("\n" + "=" * 70)
        print("✅ ALL SEEDERS COMPLETED SUCCESSFULLY!")
        print("🎉 Database is now ready for recommendation system testing!")

        # Print summary
        print("\n📊 Data Summary:")
        print(f"   👥 Users: {User.query.count()}")
        print(f"   🏪 Restaurants: {Restaurant.query.count()}")
        print(f"   🍽️ Foods: {Food.query.count()}")
        print(f"   ⭐ Food Ratings: {FoodRating.query.count()}")
        print(f"   🏪⭐ Restaurant Ratings: {RestaurantRating.query.count()}")
        print(f"   📝 Reviews: {Review.query.count()}")

        print("\n💡 Next step: Test the recommendation system!")
        print("   cd /home/labubu/Projects/adza/backend")
        print("   python test_single_class.py")

    except Exception as e:
        print(f"\n❌ Seeding process failed: {str(e)}")
        print("💡 Please check the error above and try again")
        raise e


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_all_seeders()
