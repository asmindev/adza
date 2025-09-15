#!/usr/bin/env python3
"""
🔬 ISOLATED SIMULATION FRAMEWORK
=======================================================
Sistem simulasi yang tidak mempengaruhi database utama
untuk testing rekomendasi tanpa kontaminasi data.

Author: Adza Development Team
Date: September 15, 2025
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import GridSearchCV
from sqlalchemy import create_engine, text
from datetime import datetime
import tempfile
import sqlite3


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"🔬 {title}")
    print(f"{'='*80}")


def print_section(title):
    """Print formatted section"""
    print(f"\n🎯 {title}")
    print("-" * 60)


class IsolatedSimulator:
    """Simulator yang bekerja dengan data terpisah"""

    def __init__(self, scenario_name="isolated_test"):
        self.scenario_name = scenario_name
        self.temp_db = None
        self.engine = None
        self.setup_temp_database()

    def setup_temp_database(self):
        """Setup temporary database untuk simulasi"""
        print(f"🔧 Setting up isolated environment: {self.scenario_name}")

        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

        # Create engine
        self.engine = create_engine(f"sqlite:///{self.temp_db_path}")
        print(f"✅ Temporary database created: {self.temp_db_path}")

    def load_base_data(self, original_db_url):
        """Load base data dari database asli (tanpa data simulasi)"""
        print("📥 Loading base data from original database...")

        # Connect to original database
        original_engine = create_engine(original_db_url)

        # Load food data
        foods_query = """
        SELECT id, name, restaurant_id, price, average_rating
        FROM foods
        LIMIT 50
        """
        foods_df = pd.read_sql(foods_query, original_engine)

        # Load restaurant data
        restaurants_query = """
        SELECT id, name, location
        FROM restaurants
        """
        restaurants_df = pd.read_sql(restaurants_query, original_engine)

        # Load original user ratings (filter out simulation users)
        ratings_query = """
        SELECT r.user_id, r.food_id, r.rating
        FROM food_ratings r
        JOIN users u ON r.user_id = u.id
        WHERE u.username NOT IN ('Budi', 'Iman', 'TestUser1', 'TestUser2')
        """
        ratings_df = pd.read_sql(ratings_query, original_engine)

        # Load users (real users only)
        users_query = """
        SELECT id, username, email
        FROM users
        WHERE username NOT IN ('Budi', 'Iman', 'TestUser1', 'TestUser2')
        """
        users_df = pd.read_sql(users_query, original_engine)

        # Save to temporary database
        foods_df.to_sql("foods", self.engine, if_exists="replace", index=False)
        restaurants_df.to_sql(
            "restaurants", self.engine, if_exists="replace", index=False
        )
        ratings_df.to_sql("food_ratings", self.engine, if_exists="replace", index=False)
        users_df.to_sql("users", self.engine, if_exists="replace", index=False)

        print(f"✅ Base data loaded:")
        print(f"   - Foods: {len(foods_df)}")
        print(f"   - Restaurants: {len(restaurants_df)}")
        print(f"   - Users: {len(users_df)}")
        print(f"   - Food Ratings: {len(ratings_df)}")

        return {
            "foods": foods_df,
            "restaurants": restaurants_df,
            "users": users_df,
            "ratings": ratings_df,
        }

    def add_simulation_users(self, user_configs):
        """Add simulation users dengan rating patterns"""
        print("👥 Adding simulation users...")

        # Get foods for rating
        foods_df = pd.read_sql("SELECT id, name FROM foods LIMIT 10", self.engine)

        simulation_data = []
        user_data = []

        for i, config in enumerate(user_configs):
            user_id = f"sim_user_{i+1}"
            username = config["username"]

            # Add user
            user_data.append(
                {
                    "id": user_id,
                    "username": username,
                    "email": f"{username.lower()}@simulation.test",
                }
            )

            # Add ratings based on config
            ratings = config["ratings"]
            for food_idx, rating in enumerate(ratings):
                if rating is not None:  # Skip None ratings
                    food_id = foods_df.iloc[food_idx]["id"]
                    simulation_data.append(
                        {"user_id": user_id, "food_id": food_id, "rating": rating}
                    )

            print(
                f"   ✅ {username}: {len([r for r in ratings if r is not None])}/10 ratings"
            )

        # Insert to temporary database
        if user_data:
            users_sim_df = pd.DataFrame(user_data)
            users_sim_df.to_sql("users", self.engine, if_exists="append", index=False)

        if simulation_data:
            ratings_sim_df = pd.DataFrame(simulation_data)
            ratings_sim_df.to_sql(
                "food_ratings", self.engine, if_exists="append", index=False
            )

        return foods_df, simulation_data

    def train_svd_model(self):
        """Train SVD model dengan data isolated"""
        print("🤖 Training SVD model with isolated data...")

        # Load ratings
        ratings_df = pd.read_sql(
            "SELECT user_id, food_id, rating FROM food_ratings", self.engine
        )

        if len(ratings_df) == 0:
            print("❌ No ratings data found!")
            return None

        print(f"📊 Training with {len(ratings_df)} ratings")

        # Prepare Surprise dataset
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            ratings_df[["user_id", "food_id", "rating"]], reader
        )

        # Use simplified parameters for small dataset
        param_grid = {
            "n_factors": [50],
            "n_epochs": [20],
            "lr_all": [0.01],
            "reg_all": [0.05],
        }

        gs = GridSearchCV(SVD, param_grid, measures=["rmse"], cv=3, n_jobs=-1)
        gs.fit(data)

        print(f"✅ SVD trained - Best RMSE: {gs.best_score['rmse']:.4f}")
        print(f"✅ Best params: {gs.best_params['rmse']}")

        return gs.best_estimator["rmse"]

    def predict_for_user(self, model, target_user_id):
        """Generate predictions untuk target user"""
        print(f"🎯 Generating predictions for user: {target_user_id}")

        # Get foods not rated by target user
        query = """
        SELECT f.id, f.name, f.price, f.average_rating
        FROM foods f
        WHERE f.id NOT IN (
            SELECT food_id FROM food_ratings
            WHERE user_id = ?
        )
        LIMIT 10
        """

        unrated_foods = pd.read_sql(query, self.engine, params=[target_user_id])

        predictions = []
        for _, food in unrated_foods.iterrows():
            pred = model.predict(target_user_id, food["id"])
            predictions.append(
                {
                    "food_id": food["id"],
                    "food_name": food["name"],
                    "predicted_rating": pred.est,
                    "price": food["price"],
                    "avg_rating": food["average_rating"],
                }
            )

        # Sort by predicted rating
        predictions.sort(key=lambda x: x["predicted_rating"], reverse=True)

        return predictions

    def cleanup(self):
        """Cleanup temporary database"""
        if self.temp_db_path and os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
            print(f"🧹 Cleaned up temporary database")


def run_asriani_adza_isolated():
    """Run Asriani-Adza simulation in isolated environment"""
    print_header("ISOLATED SIMULATION: ASRIANI vs ADZA")

    simulator = IsolatedSimulator("asriani_adza_test")

    try:
        # Load base data (without simulation contamination)
        original_db = "mysql://root:zett@localhost/food_recommendation"
        base_data = simulator.load_base_data(original_db)

        # Define simulation users (simplified pattern)
        user_configs = [
            {
                "username": "Asriani",
                "ratings": [
                    5.0,
                    4.0,
                    5.0,
                    5.0,
                    5.0,
                    5.0,
                    4.0,
                    2.0,
                    5.0,
                    5.0,
                ],  # 10 ratings
            },
            {
                "username": "Adza",
                "ratings": [
                    5.0,
                    5.0,
                    5.0,
                    4.0,
                    None,
                    5.0,
                    None,
                    None,
                    4.0,
                    4.0,
                ],  # 7 ratings, 3 missing
            },
        ]

        # Add simulation users
        foods_df, sim_ratings = simulator.add_simulation_users(user_configs)

        print_section("RATING COMPARISON")
        # Show rating table
        ratings_pivot = pd.read_sql(
            """
        SELECT
            f.name as food_name,
            MAX(CASE WHEN u.username = 'Asriani' THEN fr.rating END) as Asriani,
            MAX(CASE WHEN u.username = 'Adza' THEN fr.rating END) as Adza
        FROM food_ratings fr
        JOIN users u ON fr.user_id = u.id
        JOIN foods f ON fr.food_id = f.id
        WHERE u.username IN ('Asriani', 'Adza')
        GROUP BY f.name, f.id
        ORDER BY f.name
        """,
            simulator.engine,
        )

        print(ratings_pivot.to_string(index=False))

        # Train SVD model
        print_section("SVD TRAINING")
        model = simulator.train_svd_model()

        if model:
            # Get predictions for Adza
            print_section("PREDICTIONS FOR ADZA")
            adza_user_id = "sim_user_2"  # Adza is second user
            predictions = simulator.predict_for_user(model, adza_user_id)

            print("🏆 TOP RECOMMENDATIONS FOR ADZA:")
            for i, pred in enumerate(predictions[:5], 1):
                print(f"{i:2d}. {pred['food_name']}")
                print(f"    🎯 Predicted Rating: {pred['predicted_rating']:.2f}")
                print(f"    💰 Price: Rp {pred['price']:,.0f}")
                print(f"    📊 Avg Rating: {pred['avg_rating']:.1f}")

                # Check if this was rated by Asriani
                asriani_rating = pd.read_sql(
                    """
                SELECT fr.rating
                FROM food_ratings fr
                JOIN users u ON fr.user_id = u.id
                WHERE u.username = 'Asriani' AND fr.food_id = ?
                """,
                    simulator.engine,
                    params=[pred["food_id"]],
                )

                if len(asriani_rating) > 0:
                    print(
                        f"    ⭐ Asriani's Rating: {asriani_rating.iloc[0]['rating']}"
                    )
                print()

    finally:
        simulator.cleanup()


def run_budi_iman_isolated():
    """Run Budi-Iman simulation in isolated environment"""
    print_header("ISOLATED SIMULATION: BUDI vs IMAN")

    simulator = IsolatedSimulator("budi_iman_test")

    try:
        # Load base data
        original_db = "mysql://root:zett@localhost/food_recommendation"
        base_data = simulator.load_base_data(original_db)

        # Define simulation users (opposing preferences)
        user_configs = [
            {
                "username": "Iman",
                "ratings": [
                    4.0,
                    4.0,
                    4.0,
                    4.0,
                    4.0,
                    5.0,
                    5.0,
                    4.0,
                    4.5,
                    4.5,
                ],  # 10 ratings
            },
            {
                "username": "Budi",
                "ratings": [
                    5.0,
                    5.0,
                    4.0,
                    5.0,
                    4.0,
                    4.0,
                    4.5,
                    None,
                    None,
                    4.0,
                ],  # 8 ratings, 2 missing
            },
        ]

        # Add simulation users
        foods_df, sim_ratings = simulator.add_simulation_users(user_configs)

        print_section("RATING COMPARISON")
        # Show rating table
        ratings_pivot = pd.read_sql(
            """
        SELECT
            f.name as food_name,
            MAX(CASE WHEN u.username = 'Iman' THEN fr.rating END) as Iman,
            MAX(CASE WHEN u.username = 'Budi' THEN fr.rating END) as Budi
        FROM food_ratings fr
        JOIN users u ON fr.user_id = u.id
        JOIN foods f ON fr.food_id = f.id
        WHERE u.username IN ('Iman', 'Budi')
        GROUP BY f.name, f.id
        ORDER BY f.name
        """,
            simulator.engine,
        )

        print(ratings_pivot.to_string(index=False))

        # Calculate correlation
        common_ratings = ratings_pivot.dropna()
        if len(common_ratings) > 1:
            correlation = common_ratings["Iman"].corr(common_ratings["Budi"])
            print(f"\n🔗 Correlation: {correlation:.3f}")

        # Train SVD model
        print_section("SVD TRAINING")
        model = simulator.train_svd_model()

        if model:
            # Get predictions for Budi
            print_section("PREDICTIONS FOR BUDI")
            budi_user_id = "sim_user_2"  # Budi is second user
            predictions = simulator.predict_for_user(model, budi_user_id)

            print("🏆 TOP RECOMMENDATIONS FOR BUDI:")
            for i, pred in enumerate(predictions[:5], 1):
                print(f"{i:2d}. {pred['food_name']}")
                print(f"    🎯 Predicted Rating: {pred['predicted_rating']:.2f}")
                print(f"    💰 Price: Rp {pred['price']:,.0f}")
                print(f"    📊 Avg Rating: {pred['avg_rating']:.1f}")

                # Check if this was rated by Iman
                iman_rating = pd.read_sql(
                    """
                SELECT fr.rating
                FROM food_ratings fr
                JOIN users u ON fr.user_id = u.id
                WHERE u.username = 'Iman' AND fr.food_id = ?
                """,
                    simulator.engine,
                    params=[pred["food_id"]],
                )

                if len(iman_rating) > 0:
                    print(f"    ⭐ Iman's Rating: {iman_rating.iloc[0]['rating']}")
                print()

    finally:
        simulator.cleanup()


if __name__ == "__main__":
    print_header("ISOLATED SIMULATION FRAMEWORK")
    print("🔬 Testing recommendation system without data contamination")
    print("📊 Each simulation runs in isolated environment")

    # Run both simulations independently
    run_asriani_adza_isolated()
    print("\n" + "=" * 80)
    run_budi_iman_isolated()

    print_header("SIMULATION COMPLETE")
    print("✅ All simulations completed without cross-contamination")
