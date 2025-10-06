"""
Test Recommendation System - Pattern Based (Similarity Based on Food Rating Patterns)

Skenario:
- 20 makanan berbeda
- 30 user dengan pola rating yang berbeda-beda
- Sistem mencari user dengan pola rating makanan yang serupa
- Merekomendasikan makanan yang belum dicoba berdasarkan user serupa

Contoh:
- User A: suka makanan [1,2,3,4,5] dengan rating tinggi
- User B: suka makanan [1,2,3,6,7] dengan rating tinggi
- User C: tidak suka [1,2,3,4,5,6] dengan rating rendah

Maka:
- User A akan direkomendasikan [6,7] (karena mirip dengan User B)
- User B akan direkomendasikan [4,5] (karena mirip dengan User A)
- User C tidak mendapat rekomendasi (tidak ada user serupa)

Output: CSV dengan metrik evaluasi
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import json
from werkzeug.security import generate_password_hash

# Adjust path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.recommendation.recommender import Recommendations
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings

warnings.filterwarnings("ignore")


class PatternBasedTester:
    """Test sistem rekomendasi berbasis pola rating makanan serupa"""

    def __init__(self):
        self.app = create_app()
        self.users = []
        self.foods = []
        self.user_patterns = []  # Pola rating setiap user
        self.test_data = []  # Data untuk testing
        self.results = []

    def setup_foods(self):
        """Setup 20 makanan dari database"""
        with self.app.app_context():
            self.foods = Food.query.limit(20).all()
            if len(self.foods) < 20:
                print(f"⚠️  Hanya ada {len(self.foods)} makanan di database")
                return False
            print(f"✓ Menggunakan {len(self.foods)} makanan")
            return True

    def create_user_patterns(self):
        """
        Buat 30 user dengan pola rating berbeda:

        Pattern 1 (5 user): Suka makanan A=[0,1,2,3,4] rating 4-5
        Pattern 2 (5 user): Suka makanan B=[0,1,2,5,6] rating 4-5 (overlap dengan Pattern 1 di makanan 0,1,2)
        Pattern 3 (5 user): Suka makanan C=[3,4,5,6,7] rating 4-5 (overlap dengan Pattern 1 dan 2)
        Pattern 4 (5 user): Suka makanan D=[8,9,10,11,12] rating 4-5 (berbeda total)
        Pattern 5 (5 user): Suka makanan E=[10,11,12,13,14] rating 4-5 (overlap dengan Pattern 4)
        Pattern 6 (5 user): Tidak suka apapun, rating rendah 1-2 untuk berbagai makanan
        """
        # Daftar nama user yang akan digunakan
        user_names = [
            "Asmin",
            "Laode Muhammad Firza Fahrezi",
            "Emma",
            "Muhammad gibran fitrah hidayahtullah",
            "Keysa",
            "Hikma",
            "Zahra vebryan maharani",
            "SAFARAZ AUFA AZALIA",
            "JUNIATIN",
            "adell",
            "Ade Sultra Ningrum",
            "Dini",
            "Desna",
            "Elvi",
            "Hashimatul Zaria",
            "ais",
            "Afifa Zahra'",
            "Siti Husnul Khotimah Muliono",
            "anggun zahrani",
            "Gianni",
            "Nur harisa",
            "Wilda Aryani",
            "Windy",
            "puspita",
            "Gilang Bargamoreno",
            "mawar",
            "Muhammad Adi Saputra",
            "Muhammad Azriel Saktiawan",
            "ASRIANI",
            "DWI AYU RAHMAWATI",
            "Ricky",
            "Musdalipa",
        ]

        patterns = [
            {
                "name": "Pattern_A",
                "likes": [0, 1, 2, 3, 4],
                "test_foods": [5, 6],  # Makanan untuk testing
                "count": 5,
            },
            {
                "name": "Pattern_B",
                "likes": [0, 1, 2, 5, 6],
                "test_foods": [3, 4],
                "count": 5,
            },
            {
                "name": "Pattern_C",
                "likes": [3, 4, 5, 6, 7],
                "test_foods": [0, 1, 2],
                "count": 5,
            },
            {
                "name": "Pattern_D",
                "likes": [8, 9, 10, 11, 12],
                "test_foods": [13, 14],
                "count": 5,
            },
            {
                "name": "Pattern_E",
                "likes": [10, 11, 12, 13, 14],
                "test_foods": [8, 9],
                "count": 5,
            },
            {
                "name": "Pattern_Negative",
                "likes": [],  # Tidak suka apapun
                "dislikes": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # Rating rendah
                "test_foods": [],
                "count": 5,
            },
        ]

        with self.app.app_context():
            # Hapus test users sebelumnya
            User.query.filter(User.username.like("pattern_user_%")).delete()
            db.session.commit()

            user_idx = 0
            for pattern in patterns:
                for i in range(pattern["count"]):
                    # Gunakan nama dari daftar, fallback ke pattern name jika habis
                    if user_idx < len(user_names):
                        name = user_names[user_idx]
                        # Buat username dari nama (lowercase, replace space dengan underscore)
                        username = f"pattern_user_{name.lower().replace(' ', '_')}"
                    else:
                        name = f"User {pattern['name']} #{i}"
                        username = f"pattern_user_{pattern['name']}_{i}"

                    user = User(
                        username=username,
                        email=f"{username}@test.com",
                        name=name,
                        role="user",
                        password=generate_password_hash("test123"),
                    )
                    db.session.add(user)
                    db.session.flush()

                    self.user_patterns.append(
                        {
                            "user_id": user.id,
                            "username": username,
                            "pattern": pattern["name"],
                            "likes": pattern["likes"],
                            "dislikes": pattern.get("dislikes", []),
                            "test_foods": pattern["test_foods"],
                        }
                    )

                    user_idx += 1

            db.session.commit()
            self.users = User.query.filter(User.username.like("pattern_user_%")).all()
            print(
                f"✓ Berhasil membuat {len(self.users)} user dengan {len(patterns)} pola berbeda"
            )

    def create_ratings(self):
        """Buat rating berdasarkan pola user, sisihkan beberapa untuk testing"""
        with self.app.app_context():
            # Reload users untuk memastikan dalam session
            pattern_user_ids = [up["user_id"] for up in self.user_patterns]
            users_in_session = User.query.filter(User.id.in_(pattern_user_ids)).all()

            # Create mapping from id to user
            user_map = {u.id: u for u in users_in_session}

            # Hapus rating lama
            FoodRating.query.filter(FoodRating.user_id.in_(pattern_user_ids)).delete()
            db.session.commit()

            train_count = 0
            test_count = 0

            for user_pattern in self.user_patterns:
                user_id = user_pattern["user_id"]
                user = user_map[user_id]  # Get user from session
                likes = user_pattern["likes"]
                dislikes = user_pattern["dislikes"]
                test_foods = user_pattern["test_foods"]

                # Rating untuk makanan yang disukai (training)
                for food_idx in likes:
                    if food_idx < len(self.foods):
                        food = self.foods[food_idx]
                        rating_value = np.random.uniform(4.0, 5.0)

                        rating = FoodRating(
                            user_id=user.id,
                            food_id=food.id,
                            rating_details={
                                "flavor": rating_value,
                                "serving": rating_value,
                                "price": rating_value,
                                "place": rating_value,
                            },
                        )
                        db.session.add(rating)
                        train_count += 1

                # Rating untuk makanan yang tidak disukai (training)
                for food_idx in dislikes:
                    if food_idx < len(self.foods):
                        food = self.foods[food_idx]
                        rating_value = np.random.uniform(1.0, 2.5)

                        rating = FoodRating(
                            user_id=user.id,
                            food_id=food.id,
                            rating_details={
                                "flavor": rating_value,
                                "serving": rating_value,
                                "price": rating_value,
                                "place": rating_value,
                            },
                        )
                        db.session.add(rating)
                        train_count += 1

                # Simpan test foods (tidak dimasukkan ke database, untuk evaluasi)
                for food_idx in test_foods:
                    if food_idx < len(self.foods):
                        food = self.foods[food_idx]
                        # Expected rating berdasarkan pola
                        expected_rating = (
                            4.5  # Karena seharusnya disukai berdasarkan similar users
                        )

                        self.test_data.append(
                            {
                                "user_id": user.id,
                                "username": user.username,
                                "pattern": user_pattern["pattern"],
                                "food_id": food.id,
                                "food_name": food.name,
                                "expected_rating": expected_rating,
                            }
                        )
                        test_count += 1

            db.session.commit()
            print(f"✓ Training ratings: {train_count}")
            print(f"✓ Test items: {test_count}")

    def analyze_patterns(self):
        """Analisis pola rating untuk melihat similarity"""
        with self.app.app_context():
            print("\n" + "=" * 80)
            print("PATTERN ANALYSIS")
            print("=" * 80)

            pattern_summary = defaultdict(lambda: {"users": [], "foods": set()})

            for user_pattern in self.user_patterns:
                pattern = user_pattern["pattern"]
                username = user_pattern["username"]
                likes = user_pattern["likes"]

                pattern_summary[pattern]["users"].append(username)
                pattern_summary[pattern]["foods"].update(likes)

            for pattern, data in sorted(pattern_summary.items()):
                print(f"\n{pattern}:")
                print(f"  Users: {len(data['users'])}")
                print(f"  Liked foods (indices): {sorted(data['foods'])}")
                if data["users"]:
                    print(f"  Example users: {', '.join(data['users'][:3])}")

            print()

    def evaluate_recommendations(self):
        """Evaluasi sistem rekomendasi"""
        with self.app.app_context():
            print("=" * 80)
            print("EVALUATING RECOMMENDATIONS")
            print("=" * 80)

            recommender = Recommendations()

            # Group test data by user
            test_by_user = defaultdict(list)
            for test_item in self.test_data:
                test_by_user[test_item["user_id"]].append(test_item)

            print(f"Evaluating {len(test_by_user)} users...\n")

            all_metrics = {"mae": [], "rmse": [], "precision": [], "recall": []}

            for idx, (user_id, user_tests) in enumerate(test_by_user.items(), 1):
                try:
                    # Get user info
                    user_pattern = next(
                        up for up in self.user_patterns if up["user_id"] == user_id
                    )
                    username = user_pattern["username"]
                    pattern = user_pattern["pattern"]

                    # Get recommendations
                    recommendations = recommender.recommend_with_scores(
                        user_id=user_id, top_n=10
                    )

                    if not recommendations:
                        print(f"  [{idx:2d}] {username:30s} | No recommendations")
                        continue

                    # Get recommended food IDs
                    recommended_ids = [r["food_id"] for r in recommendations]

                    # Calculate metrics
                    actual_ratings = []
                    predicted_ratings = []
                    relevant_items = []  # Items that should be recommended
                    recommended_relevant = 0  # How many relevant items were recommended

                    for test_item in user_tests:
                        food_id = test_item["food_id"]
                        relevant_items.append(food_id)

                        # Find prediction
                        pred = next(
                            (r for r in recommendations if r["food_id"] == food_id),
                            None,
                        )

                        if pred:
                            actual_ratings.append(test_item["expected_rating"])
                            predicted_ratings.append(pred["predicted_rating"])
                            recommended_relevant += 1

                    # MAE & RMSE
                    mae = (
                        mean_absolute_error(actual_ratings, predicted_ratings)
                        if len(actual_ratings) > 0
                        else None
                    )
                    rmse = (
                        np.sqrt(mean_squared_error(actual_ratings, predicted_ratings))
                        if len(actual_ratings) > 0
                        else None
                    )

                    # Precision & Recall
                    precision = (
                        recommended_relevant / len(recommended_ids)
                        if len(recommended_ids) > 0
                        else 0
                    )
                    recall = (
                        recommended_relevant / len(relevant_items)
                        if len(relevant_items) > 0
                        else 0
                    )

                    # Save result
                    result = {
                        "user_id": user_id,
                        "username": username,
                        "pattern": pattern,
                        "n_train_ratings": FoodRating.query.filter_by(
                            user_id=user_id
                        ).count(),
                        "n_test_items": len(user_tests),
                        "n_recommendations": len(recommendations),
                        "n_relevant_recommended": recommended_relevant,
                        "mae": mae,
                        "rmse": rmse,
                        "precision": precision,
                        "recall": recall,
                        "top_5_recommendations": json.dumps(
                            [
                                {
                                    "food_id": r["food_id"],
                                    "predicted_rating": r["predicted_rating"],
                                }
                                for r in recommendations[:5]
                            ]
                        ),
                    }

                    self.results.append(result)

                    # Add to metrics
                    if mae is not None:
                        all_metrics["mae"].append(mae)
                    if rmse is not None:
                        all_metrics["rmse"].append(rmse)
                    all_metrics["precision"].append(precision)
                    all_metrics["recall"].append(recall)

                    # Print progress
                    mae_str = f"{mae:.3f}" if mae else "N/A"
                    rmse_str = f"{rmse:.3f}" if rmse else "N/A"
                    print(
                        f"  [{idx:2d}] {username:30s} | "
                        f"MAE: {mae_str:6s} | RMSE: {rmse_str:6s} | "
                        f"P: {precision:.2f} | R: {recall:.2f} | "
                        f"Recs: {len(recommendations)}"
                    )

                except Exception as e:
                    print(f"  [{idx:2d}] Error: {str(e)}")
                    continue

            # Print summary
            print("\n" + "=" * 80)
            print("EVALUATION SUMMARY")
            print("=" * 80)

            if all_metrics["mae"]:
                print(
                    f"Avg MAE:       {np.mean(all_metrics['mae']):.4f} ± {np.std(all_metrics['mae']):.4f}"
                )
            if all_metrics["rmse"]:
                print(
                    f"Avg RMSE:      {np.mean(all_metrics['rmse']):.4f} ± {np.std(all_metrics['rmse']):.4f}"
                )
            if all_metrics["precision"]:
                print(
                    f"Avg Precision: {np.mean(all_metrics['precision']):.4f} ± {np.std(all_metrics['precision']):.4f}"
                )
            if all_metrics["recall"]:
                print(
                    f"Avg Recall:    {np.mean(all_metrics['recall']):.4f} ± {np.std(all_metrics['recall']):.4f}"
                )

            print()

    def save_results_to_csv(self, filename=None):
        """Simpan hasil ke CSV"""
        if not self.results:
            print("⚠️  No results to save")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recommendation_pattern_test_{timestamp}.csv"

        # Create results directory
        results_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "results"
        )
        os.makedirs(results_dir, exist_ok=True)

        filepath = os.path.join(results_dir, filename)

        # Convert to DataFrame
        df = pd.DataFrame(self.results)

        # Reorder columns
        columns = [
            "user_id",
            "username",
            "pattern",
            "n_train_ratings",
            "n_test_items",
            "n_recommendations",
            "n_relevant_recommended",
            "mae",
            "rmse",
            "precision",
            "recall",
            "top_5_recommendations",
        ]
        df = df[columns]

        # Save
        df.to_csv(filepath, index=False)

        print("=" * 80)
        print("RESULTS SAVED")
        print("=" * 80)
        print(f"✓ File: {filepath}")
        print(f"✓ Rows: {len(df)}")
        print()

        # Print by pattern
        print("Results by Pattern:")
        print("-" * 80)
        for pattern in sorted(df["pattern"].unique()):
            pattern_df = df[df["pattern"] == pattern]
            mae_mean = pattern_df["mae"].mean()
            rmse_mean = pattern_df["rmse"].mean()
            precision_mean = pattern_df["precision"].mean()
            recall_mean = pattern_df["recall"].mean()

            print(
                f"{pattern:20s}: MAE={mae_mean:.3f}, RMSE={rmse_mean:.3f}, "
                f"P={precision_mean:.3f}, R={recall_mean:.3f}"
            )

        print()

    def run_full_test(self):
        """Jalankan test lengkap"""
        print("\n")
        print("*" * 80)
        print("PATTERN-BASED RECOMMENDATION SYSTEM TEST")
        print("*" * 80)
        print()

        # Setup
        print("=" * 80)
        print("SETUP")
        print("=" * 80)

        if not self.setup_foods():
            return

        self.create_user_patterns()
        self.create_ratings()

        # Analyze
        self.analyze_patterns()

        # Evaluate
        self.evaluate_recommendations()

        # Save
        self.save_results_to_csv()

        print("*" * 80)
        print("TEST COMPLETED")
        print("*" * 80)
        print()


if __name__ == "__main__":
    tester = PatternBasedTester()
    tester.run_full_test()
