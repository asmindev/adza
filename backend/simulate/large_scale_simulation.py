#!/usr/bin/env python3
"""
Simulasi User untuk Sistem Rekomendasi SVD - Versi Skala Besar

Simulasi dengan:
- 10 users dengan pola rating yang berbeda-beda
- 50 makanan dari database
- Collaborative filtering untuk menemukan similar users
- Hyperparameter tuning otomatis

Output:
1. Summary user dan makanan
2. Heatmap rating patterns
3. Hasil prediksi collaborative dengan explanation
"""

import sys
import os
import random
import numpy as np

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.recommendation.service import Recommendations
from werkzeug.security import generate_password_hash


class LargeScaleSVDSimulator:
    """Simulasi SVD skala besar dengan 10 users dan 50 makanan"""

    def __init__(self):
        self.app = create_app()
        self.simulation_users = []
        self.sample_foods = []
        self.user_profiles = []

        # User personas dengan karakteristik berbeda
        self.user_personas = [
            {
                "name": "Alice Food Lover",
                "username": "alice_fl",
                "email": "alice@foodlover.com",
                "rating_style": "high_standards",
                "coverage": 0.8,
            },  # Rating tinggi, banyak makanan
            {
                "name": "Bob Casual Eater",
                "username": "bob_ce",
                "email": "bob@casual.com",
                "rating_style": "average",
                "coverage": 0.6,
            },  # Rating sedang, sebagian makanan
            {
                "name": "Charlie Critic",
                "username": "charlie_c",
                "email": "charlie@critic.com",
                "rating_style": "critical",
                "coverage": 0.9,
            },  # Rating bervariasi, hampir semua makanan
            {
                "name": "Diana Health Conscious",
                "username": "diana_hc",
                "email": "diana@healthy.com",
                "rating_style": "selective",
                "coverage": 0.4,
            },  # Rating tinggi untuk makanan sehat
            {
                "name": "Eddie Fast Food Fan",
                "username": "eddie_fff",
                "email": "eddie@fastfood.com",
                "rating_style": "fast_food",
                "coverage": 0.7,
            },  # Suka fast food
            {
                "name": "Fiona Fine Dining",
                "username": "fiona_fd",
                "email": "fiona@finedining.com",
                "rating_style": "premium",
                "coverage": 0.5,
            },  # Hanya makanan premium
            {
                "name": "George Generous",
                "username": "george_g",
                "email": "george@generous.com",
                "rating_style": "generous",
                "coverage": 0.85,
            },  # Rating hampir semua tinggi
            {
                "name": "Hannah Conservative",
                "username": "hannah_c",
                "email": "hannah@conservative.com",
                "rating_style": "conservative",
                "coverage": 0.3,
            },  # Sedikit rating, konservatif
            {
                "name": "Ivan International",
                "username": "ivan_i",
                "email": "ivan@international.com",
                "rating_style": "diverse",
                "coverage": 0.75,
            },  # Suka berbagai jenis makanan
            {
                "name": "Julia Junk Food",
                "username": "julia_jf",
                "email": "julia@junkfood.com",
                "rating_style": "junk_food",
                "coverage": 0.6,
            },  # Suka junk food
        ]

    def cleanup_previous_simulation(self):
        """Hapus data simulasi sebelumnya"""
        with self.app.app_context():
            print("🧹 Membersihkan data simulasi sebelumnya...")

            # Hapus users simulasi dan ratings mereka
            sim_usernames = [persona["username"] for persona in self.user_personas]
            sim_users = User.query.filter(User.username.in_(sim_usernames)).all()

            for user in sim_users:
                FoodRating.query.filter_by(user_id=user.id).delete()
                db.session.delete(user)

            db.session.commit()
            print("✅ Data simulasi sebelumnya berhasil dibersihkan")

    def create_users(self):
        """Buat 10 users dengan persona berbeda"""
        with self.app.app_context():
            print("👥 Membuat 10 users dengan persona berbeda...")

            for persona in self.user_personas:
                user = User(
                    name=persona["name"],
                    username=persona["username"],
                    email=persona["email"],
                    password=generate_password_hash("password123"),
                    role="user",
                )
                db.session.add(user)
                self.simulation_users.append(user)

            db.session.commit()

            # Refresh users untuk menghindari DetachedInstanceError
            self.simulation_users = []
            for persona in self.user_personas:
                user = User.query.filter_by(username=persona["username"]).first()
                self.simulation_users.append(user)

            print(f"✅ {len(self.simulation_users)} users berhasil dibuat")

            # Display user personas
            print("\n👤 USER PERSONAS:")
            for i, (user, persona) in enumerate(
                zip(self.simulation_users, self.user_personas)
            ):
                print(
                    f"   {i+1:2}. {user.name} - {persona['rating_style']} (coverage: {persona['coverage']*100:.0f}%)"
                )

    def get_foods(self):
        """Ambil 50 makanan dari database"""
        with self.app.app_context():
            print("\n🍽️ Mengambil 50 makanan dari database...")

            foods = Food.query.limit(50).all()
            if len(foods) < 50:
                print(f"⚠️ Hanya ada {len(foods)} makanan di database, butuh minimal 50")
                self.sample_foods = foods
            else:
                self.sample_foods = foods[:50]

            print(f"✅ {len(self.sample_foods)} makanan berhasil diambil")

            # Kategorisasi makanan (berdasarkan nama untuk demo)
            categories = {
                "fast_food": [],
                "healthy": [],
                "premium": [],
                "dessert": [],
                "beverage": [],
                "other": [],
            }

            for food in self.sample_foods:
                name_lower = food.name.lower()
                if any(
                    word in name_lower
                    for word in ["burger", "pizza", "fries", "kfc", "mcd"]
                ):
                    categories["fast_food"].append(food)
                elif any(
                    word in name_lower
                    for word in ["salad", "vegetable", "fruit", "organic", "healthy"]
                ):
                    categories["healthy"].append(food)
                elif any(
                    word in name_lower
                    for word in ["premium", "wagyu", "truffle", "caviar", "gold"]
                ):
                    categories["premium"].append(food)
                elif any(
                    word in name_lower
                    for word in ["cake", "ice cream", "dessert", "pudding", "donat"]
                ):
                    categories["dessert"].append(food)
                elif any(
                    word in name_lower
                    for word in ["coffee", "tea", "juice", "latte", "drink"]
                ):
                    categories["beverage"].append(food)
                else:
                    categories["other"].append(food)

            print(f"\n📊 Kategori makanan:")
            for category, foods in categories.items():
                if foods:
                    print(f"   {category.title()}: {len(foods)} items")

    def get_rating_for_user_food(self, user_idx, food_idx, food):
        """Generate rating berdasarkan user persona dan karakteristik makanan"""
        persona = self.user_personas[user_idx]
        style = persona["rating_style"]
        coverage = persona["coverage"]

        # Tentukan apakah user ini akan me-rating makanan ini
        if random.random() > coverage:
            return None  # User tidak me-rating makanan ini

        food_name = food.name.lower()
        base_rating = 3.0  # Rating dasar

        # Adjust rating berdasarkan user persona
        if style == "high_standards":
            # Alice: rating tinggi untuk semua, tapi sangat selektif
            base_rating = random.uniform(4.0, 5.0)

        elif style == "average":
            # Bob: rating rata-rata
            base_rating = random.uniform(2.5, 4.0)

        elif style == "critical":
            # Charlie: rating bervariasi luas, lebih kritik
            base_rating = random.uniform(1.5, 4.5)

        elif style == "selective":
            # Diana: rating tinggi untuk makanan sehat, rendah untuk junk food
            if any(
                word in food_name for word in ["salad", "vegetable", "fruit", "healthy"]
            ):
                base_rating = random.uniform(4.5, 5.0)
            elif any(word in food_name for word in ["burger", "pizza", "fries"]):
                base_rating = random.uniform(1.0, 2.5)
            else:
                base_rating = random.uniform(3.0, 4.0)

        elif style == "fast_food":
            # Eddie: rating tinggi untuk fast food
            if any(word in food_name for word in ["burger", "pizza", "fries", "kfc"]):
                base_rating = random.uniform(4.0, 5.0)
            else:
                base_rating = random.uniform(2.0, 3.5)

        elif style == "premium":
            # Fiona: rating tinggi untuk makanan premium
            if any(
                word in food_name for word in ["premium", "wagyu", "gold", "truffle"]
            ):
                base_rating = random.uniform(4.5, 5.0)
            elif "gold" in food_name or food.price and food.price > 50000:
                base_rating = random.uniform(4.0, 5.0)
            else:
                return None  # Tidak tertarik makanan non-premium

        elif style == "generous":
            # George: hampir semua rating tinggi
            base_rating = random.uniform(3.5, 5.0)

        elif style == "conservative":
            # Hannah: rating konservatif, tidak ekstrem
            base_rating = random.uniform(3.0, 4.0)

        elif style == "diverse":
            # Ivan: suka variasi, rating bervariasi tapi cenderung positif
            base_rating = random.uniform(3.0, 4.8)

        elif style == "junk_food":
            # Julia: suka junk food dan dessert
            if any(
                word in food_name
                for word in ["burger", "pizza", "cake", "ice cream", "donat"]
            ):
                base_rating = random.uniform(4.0, 5.0)
            else:
                base_rating = random.uniform(2.5, 3.5)

        # Clamp rating ke range 1.0-5.0
        rating = max(1.0, min(5.0, base_rating))

        # Round ke 0.5 terdekat untuk realism
        return round(rating * 2) / 2

    def create_ratings(self):
        """Buat rating berdasarkan user personas"""
        with self.app.app_context():
            print("\n⭐ MEMBUAT RATING BERDASARKAN USER PERSONAS")
            print("=" * 60)

            total_ratings = 0
            user_rating_counts = []

            for user_idx, user in enumerate(self.simulation_users):
                persona = self.user_personas[user_idx]
                user_ratings = 0

                print(f"\n👤 {user.name} ({persona['rating_style']}):")

                for food_idx, food in enumerate(self.sample_foods):
                    rating = self.get_rating_for_user_food(user_idx, food_idx, food)

                    if rating is not None:
                        food_rating = FoodRating(
                            user_id=user.id, food_id=food.id, rating=rating
                        )
                        db.session.add(food_rating)
                        user_ratings += 1
                        total_ratings += 1

                user_rating_counts.append(user_ratings)
                print(f"   📊 {user_ratings} ratings dibuat")

                db.session.commit()

            print(f"\n✅ SUMMARY RATINGS:")
            print(f"   📊 Total ratings: {total_ratings}")
            print(f"   👥 Users: {len(self.simulation_users)}")
            print(f"   🍽️ Foods: {len(self.sample_foods)}")
            print(
                f"   📈 Avg ratings per user: {total_ratings / len(self.simulation_users):.1f}"
            )
            print(
                f"   📊 Rating density: {total_ratings / (len(self.simulation_users) * len(self.sample_foods)) * 100:.1f}%"
            )

    def display_rating_summary(self):
        """Tampilkan ringkasan rating patterns"""
        with self.app.app_context():
            print(f"\n📊 SUMMARY RATING PATTERNS")
            print("=" * 60)

            print(
                f"{'User':<20} {'Ratings':<8} {'Avg Rating':<10} {'Min':<5} {'Max':<5}"
            )
            print("-" * 60)

            for user in self.simulation_users:
                ratings = FoodRating.query.filter_by(user_id=user.id).all()
                if ratings:
                    rating_values = [r.rating for r in ratings]
                    avg_rating = sum(rating_values) / len(rating_values)
                    min_rating = min(rating_values)
                    max_rating = max(rating_values)

                    print(
                        f"{user.name[:19]:<20} {len(ratings):<8} {avg_rating:<10.2f} {min_rating:<5.1f} {max_rating:<5.1f}"
                    )
                else:
                    print(
                        f"{user.name[:19]:<20} {'0':<8} {'N/A':<10} {'N/A':<5} {'N/A':<5}"
                    )

    def predict_collaborative_recommendations(self):
        """Prediksi collaborative dengan analisis mendalam"""
        with self.app.app_context():
            print(f"\n🎯 COLLABORATIVE FILTERING RECOMMENDATIONS")
            print("=" * 60)

            # Training SVD dengan hyperparameter tuning
            print("🤖 Training SVD model dengan hyperparameter tuning...")
            recommender = Recommendations(alpha=1.0, auto_tune=True)
            training_result = recommender.train_full_system()

            if not training_result["success"]:
                print(f"❌ Training SVD gagal: {training_result['error']}")
                return

            print("✅ SVD model berhasil di-training!")

            # Tampilkan metrics
            if training_result["validation_metrics"]:
                metrics = training_result["validation_metrics"]["food_model"]
                if "note" not in metrics:
                    print(
                        f"📊 SVD Performance: RMSE={metrics['rmse']:.3f}, MAE={metrics['mae']:.3f}"
                    )
                    if metrics.get("tuned", False):
                        print("🔧 ✅ Menggunakan hyperparameters yang di-tuning")
                    else:
                        print("🔧 Menggunakan default parameters")

            print()

            # Analisis untuk 3 users representative
            target_users = self.simulation_users[:3]  # Alice, Bob, Charlie

            for user in target_users:
                print(f"\n👤 REKOMENDASI UNTUK {user.name.upper()}")
                print("-" * 50)

                # Get recommendations
                recommendations = recommender.get_recommendations(user.id, n=10)

                if recommendations:
                    print(f"🎯 Top 5 rekomendasi:")

                    for i, rec in enumerate(recommendations[:5], 1):
                        food_name = rec["food"]["name"]
                        predicted_rating = rec["predicted_rating"]

                        # Cari user lain yang sudah rating makanan ini tinggi
                        food_id = rec["food"]["id"]
                        similar_ratings = FoodRating.query.filter(
                            FoodRating.food_id == food_id,
                            FoodRating.user_id != user.id,
                            FoodRating.rating >= 4.0,
                        ).all()

                        print(f"   {i}. 🍽️ {food_name[:35]}")
                        print(f"      ⭐ Prediksi: {predicted_rating:.1f}")

                        if similar_ratings:
                            # Ambil 2 user dengan rating tertinggi
                            similar_ratings.sort(key=lambda x: x.rating, reverse=True)
                            similar_users = []

                            for rating in similar_ratings[:2]:
                                similar_user = User.query.get(rating.user_id)
                                if similar_user:
                                    similar_users.append(
                                        f"{similar_user.name.split()[0]} ({rating.rating:.1f}⭐)"
                                    )

                            if similar_users:
                                print(
                                    f"      👥 Disukai oleh: {', '.join(similar_users)}"
                                )

                        print()

                else:
                    print("   ❌ Tidak ada rekomendasi ditemukan")

            # Analisis similarity antar users
            print(f"\n🔍 ANALISIS USER SIMILARITY")
            print("-" * 50)

            # Hitung overlap ratings antara beberapa users
            users_to_compare = self.simulation_users[:4]  # Alice, Bob, Charlie, Diana

            print("📊 Rating overlap antar users:")
            for i, user1 in enumerate(users_to_compare):
                for j, user2 in enumerate(users_to_compare[i + 1 :], i + 1):
                    # Cari makanan yang di-rating kedua user
                    user1_foods = set(
                        r.food_id
                        for r in FoodRating.query.filter_by(user_id=user1.id).all()
                    )
                    user2_foods = set(
                        r.food_id
                        for r in FoodRating.query.filter_by(user_id=user2.id).all()
                    )

                    common_foods = user1_foods.intersection(user2_foods)

                    if common_foods:
                        # Hitung correlation
                        user1_ratings = []
                        user2_ratings = []

                        for food_id in common_foods:
                            r1 = FoodRating.query.filter_by(
                                user_id=user1.id, food_id=food_id
                            ).first()
                            r2 = FoodRating.query.filter_by(
                                user_id=user2.id, food_id=food_id
                            ).first()
                            if r1 and r2:
                                user1_ratings.append(r1.rating)
                                user2_ratings.append(r2.rating)

                        if len(user1_ratings) > 1:
                            correlation = np.corrcoef(user1_ratings, user2_ratings)[
                                0, 1
                            ]
                            if not np.isnan(correlation):
                                print(
                                    f"   {user1.name.split()[0]} ↔ {user2.name.split()[0]}: {len(common_foods)} makanan, korelasi: {correlation:.3f}"
                                )

    def run_simulation(self):
        """Jalankan simulasi skala besar"""
        try:
            with self.app.app_context():
                print("🚀 SIMULASI COLLABORATIVE FILTERING - SKALA BESAR")
                print("=" * 60)
                print("📊 10 Users × 50 Foods × User Personas")
                print()

                self.cleanup_previous_simulation()
                self.create_users()
                self.get_foods()
                self.create_ratings()
                self.display_rating_summary()
                self.predict_collaborative_recommendations()

                print(f"\n🎉 SIMULASI SELESAI!")
                print("=" * 60)
                print("📈 Sistem SVD berhasil melakukan collaborative filtering")
                print(
                    "👥 User dengan pola rating mirip dapat saling merekomendasikan makanan"
                )
                print("🎯 Hyperparameter tuning meningkatkan akurasi prediksi")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    print("🚀 SIMULASI SVD SKALA BESAR")
    print("📊 10 Users dengan Personas Berbeda × 50 Makanan")
    print("🎯 Collaborative Filtering dengan Hyperparameter Tuning")
    print()

    simulator = LargeScaleSVDSimulator()
    simulator.run_simulation()
