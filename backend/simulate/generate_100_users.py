"""
Script to generate 100 users with realistic rating patterns
This will help test recommendation system scalability
"""

import random
import string
from datetime import datetime, timezone
from app import create_app
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.extensions import db
from werkzeug.security import generate_password_hash
import uuid

# Configuration
NUM_USERS = 100
MIN_RATINGS_PER_USER = 5
MAX_RATINGS_PER_USER = 50
BATCH_SIZE = 20  # Process in batches to avoid memory issues

# Realistic rating distribution (more 4s and 5s, fewer 1s)
RATING_WEIGHTS = {
    1: 0.05,  # 5% - Very bad
    2: 0.10,  # 10% - Bad
    3: 0.20,  # 20% - Average
    4: 0.35,  # 35% - Good
    5: 0.30,  # 30% - Excellent
}

# Indonesian-style names for realistic users
FIRST_NAMES = [
    "Adi",
    "Budi",
    "Citra",
    "Dewi",
    "Eko",
    "Fitri",
    "Galih",
    "Hesti",
    "Indra",
    "Joko",
    "Kartika",
    "Lina",
    "Maya",
    "Nurul",
    "Omar",
    "Putri",
    "Rina",
    "Sari",
    "Tono",
    "Udin",
    "Vita",
    "Wawan",
    "Yanti",
    "Zahra",
    "Ayu",
    "Bambang",
    "Cahyo",
    "Diah",
    "Erik",
    "Farah",
    "Gilang",
    "Hendra",
    "Ika",
    "Johan",
    "Kemal",
    "Laras",
    "Mega",
    "Nanda",
    "Okta",
    "Prita",
    "Qori",
    "Reza",
    "Sinta",
    "Teguh",
    "Ulfa",
    "Vina",
    "Wahyu",
    "Xenia",
    "Yoga",
    "Zaky",
    "Agus",
    "Bella",
    "Chandra",
    "Dian",
    "Edo",
    "Fika",
    "Gita",
    "Hani",
    "Ivan",
    "Jihan",
    "Krisna",
    "Lisa",
    "Mira",
    "Noval",
    "Okky",
    "Ratna",
    "Sigit",
    "Tari",
    "Umi",
    "Vero",
    "Winda",
    "Yoga",
    "Zainal",
    "Alif",
    "Bela",
    "Citra",
    "Dani",
    "Elsa",
    "Fauzi",
    "Gina",
]

LAST_NAMES = [
    "Pratama",
    "Sari",
    "Putra",
    "Wati",
    "Santoso",
    "Maharani",
    "Wijaya",
    "Lestari",
    "Kusuma",
    "Dewi",
    "Permana",
    "Anggraeni",
    "Nugroho",
    "Safitri",
    "Setiawan",
    "Rahayu",
    "Firmansyah",
    "Handayani",
    "Kurniawan",
    "Utami",
    "Suryanto",
    "Fitriani",
    "Hidayat",
    "Nuraini",
    "Prasetyo",
    "Indriati",
    "Rahman",
    "Kartika",
    "Gunawan",
    "Wulandari",
]


def generate_username(first_name, last_name, existing_usernames):
    """Generate unique username"""
    base_username = f"{first_name.lower()}.{last_name.lower()}"

    # Add numbers if base username exists
    counter = 1
    username = base_username
    while username in existing_usernames:
        username = f"{base_username}{counter}"
        counter += 1

    existing_usernames.add(username)
    return username


def generate_email(first_name, last_name, existing_emails):
    """Generate unique email"""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "email.com"]

    base_email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

    # Add numbers if base email exists
    counter = 1
    email = base_email
    while email in existing_emails:
        domain = random.choice(domains)
        email = f"{first_name.lower()}.{last_name.lower()}{counter}@{domain}"
        counter += 1

    existing_emails.add(email)
    return email


def weighted_rating_choice():
    """Generate rating based on realistic distribution"""
    ratings = list(RATING_WEIGHTS.keys())
    weights = list(RATING_WEIGHTS.values())
    return random.choices(ratings, weights=weights)[0]


def create_users_batch(batch_num, batch_size, existing_usernames, existing_emails):
    """Create a batch of users"""
    users = []

    for i in range(batch_size):
        user_num = (batch_num * batch_size) + i + 1

        # Generate name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"

        # Generate unique username and email
        username = generate_username(first_name, last_name, existing_usernames)
        email = generate_email(first_name, last_name, existing_emails)

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            name=full_name,
            username=username,
            email=email,
            password=generate_password_hash("password123"),  # Default password
            role="user",
            onboarding_completed=True,
        )

        users.append(user)
        print(f"Generated user {user_num}/100: {username} ({email})")

    return users


def create_ratings_for_user(user, all_foods):
    """Create realistic ratings for a user"""
    # Determine how many ratings this user will have
    num_ratings = random.randint(MIN_RATINGS_PER_USER, MAX_RATINGS_PER_USER)

    # Randomly select foods to rate (without replacement)
    foods_to_rate = random.sample(all_foods, min(num_ratings, len(all_foods)))

    ratings = []
    for food in foods_to_rate:
        rating = FoodRating(
            id=str(uuid.uuid4()),
            user_id=user.id,
            food_id=food.id,
            rating=weighted_rating_choice(),
        )
        ratings.append(rating)

    return ratings


def main():
    """Main function to generate users and ratings"""
    app = create_app()

    with app.app_context():
        print("Starting 100 user generation...")
        print(
            f"Target: {NUM_USERS} users with {MIN_RATINGS_PER_USER}-{MAX_RATINGS_PER_USER} ratings each"
        )

        # Get all foods
        print("Loading all foods...")
        all_foods = db.session.query(Food).all()
        print(f"Found {len(all_foods)} foods available for rating")

        if len(all_foods) == 0:
            print("ERROR: No foods found in database!")
            return

        # Get existing usernames and emails to avoid conflicts
        existing_users = db.session.query(User.username, User.email).all()
        existing_usernames = {user.username for user in existing_users}
        existing_emails = {user.email for user in existing_users}
        print(f"Found {len(existing_usernames)} existing users")

        # Calculate batches
        num_batches = (NUM_USERS + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Processing in {num_batches} batches of {BATCH_SIZE} users each")

        total_users_created = 0
        total_ratings_created = 0

        try:
            for batch_num in range(num_batches):
                print(f"\n--- Batch {batch_num + 1}/{num_batches} ---")

                # Calculate batch size (last batch might be smaller)
                current_batch_size = min(
                    BATCH_SIZE, NUM_USERS - (batch_num * BATCH_SIZE)
                )

                # Create users for this batch
                batch_users = create_users_batch(
                    batch_num, current_batch_size, existing_usernames, existing_emails
                )

                # Add users to database
                for user in batch_users:
                    db.session.add(user)

                # Commit users first
                db.session.commit()
                print(f"Committed {len(batch_users)} users to database")

                # Create ratings for each user in this batch
                batch_ratings = []
                for user in batch_users:
                    user_ratings = create_ratings_for_user(user, all_foods)
                    batch_ratings.extend(user_ratings)
                    print(f"Generated {len(user_ratings)} ratings for {user.username}")

                # Add ratings to database
                for rating in batch_ratings:
                    db.session.add(rating)

                # Commit ratings
                db.session.commit()
                print(f"Committed {len(batch_ratings)} ratings to database")

                total_users_created += len(batch_users)
                total_ratings_created += len(batch_ratings)

                print(
                    f"Batch complete: {len(batch_users)} users, {len(batch_ratings)} ratings"
                )

            print(f"\n🎉 SUCCESS!")
            print(f"Created {total_users_created} users")
            print(f"Created {total_ratings_created} ratings")

            # Final verification
            final_user_count = db.session.query(User).count()
            final_rating_count = db.session.query(FoodRating).count()
            print(f"\nFinal database state:")
            print(f"Total users: {final_user_count}")
            print(f"Total ratings: {final_rating_count}")

            # Show some statistics
            avg_ratings_per_user = (
                total_ratings_created / total_users_created
                if total_users_created > 0
                else 0
            )
            print(f"Average ratings per new user: {avg_ratings_per_user:.1f}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()
