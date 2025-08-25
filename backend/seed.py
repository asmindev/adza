#!/usr/bin/env python
"""
Runner script for sample data generation
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add parent directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food
from app.modules.rating.models import RestaurantRating, FoodRating
from app.modules.review.models import Review

# Import data generators
from data.users import generate_users_data
from data.restaurants import generate_restaurants_data
from data.foods import generate_foods_data
from data.restaurant_ratings import generate_restaurant_ratings_data
from data.food_ratings import generate_food_ratings_data
from data.reviews import generate_reviews_data


def setup_logging():
    """Configure logging for the seeder"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("seeders")


def reset_database(logger):
    """Clear all data from the tables"""
    logger.info("Resetting database...")
    try:
        # Clear all data from tables without dropping them
        logger.info("Deleting reviews...")
        Review.query.delete()

        logger.info("Deleting food ratings...")
        FoodRating.query.delete()

        logger.info("Deleting restaurant ratings...")
        RestaurantRating.query.delete()

        logger.info("Deleting foods...")
        Food.query.delete()

        logger.info("Deleting restaurants...")
        Restaurant.query.delete()

        logger.info("Deleting users...")
        User.query.delete()

        # Commit the deletions
        db.session.commit()
        logger.info("Database reset complete")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        db.session.rollback()
        sys.exit(1)


def seed_database(logger):
    """Seed the database with sample data"""
    logger.info("Starting database seeding...")

    try:
        # Generate and insert data in order
        logger.info("Creating users...")
        users = generate_users_data()
        for user_data in users:
            user = User(**user_data)
            db.session.add(user)
        db.session.commit()

        logger.info("Creating restaurants...")
        restaurants = generate_restaurants_data()
        for restaurant_data in restaurants:
            restaurant = Restaurant(**restaurant_data)
            db.session.add(restaurant)
        db.session.commit()

        logger.info("Creating foods...")
        foods = generate_foods_data()
        for food_data in foods:
            food = Food(**food_data)
            db.session.add(food)
        db.session.commit()

        logger.info("Creating restaurant ratings...")
        restaurant_ratings = generate_restaurant_ratings_data(restaurants)
        for rating_data in restaurant_ratings:
            rating = RestaurantRating(**rating_data)
            db.session.add(rating)
        db.session.commit()

        logger.info("Creating food ratings...")
        food_ratings = generate_food_ratings_data(foods, restaurants)
        for rating_data in food_ratings:
            rating = FoodRating(**rating_data)
            db.session.add(rating)
        db.session.commit()

        logger.info("Creating reviews...")
        reviews = generate_reviews_data(food_ratings, foods)
        for review_data in reviews:
            review = Review(**review_data)
            db.session.add(review)
        db.session.commit()

        logger.info("Database seeding complete!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.session.rollback()
        sys.exit(1)


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create sample data for GoFood API")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (delete existing sample data)",
    )
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging()
    logger.info("Starting seed script")

    # Create app context
    app = create_app()

    with app.app_context():
        if args.reset:
            reset_database(logger)

        seed_database(logger)
