#!/usr/bin/env python3
"""
Simulasi User untuk Sistem Rekomendasi SVD - Versi Sederhana

Output hanya:
1. Table rating user untuk makanan
2. Hasil prediksi collaborative
"""

import sys
import os
import random

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.rating.models import FoodRating
from app.recommendation.service import Recommendations
from werkzeug.security import generate_password_hash


class SimpleSVDSimulator:
    """Simulasi SVD sederhana"""

    def __init__(self):
        self.app = create_app()
        self.simulation_users = []
        self.sample_foods = []
        self.created_ratings = []

    def cleanup_previous_simulation(self):
        """Bersihkan data simulasi sebelumnya"""
        print("🧹 Membersihkan data simulasi sebelumnya...")

        svd_usernames = ["svd_budi", "svd_iman"]
        for username in svd_usernames:
            user = User.query.filter_by(username=username).first()
            if user:
                FoodRating.query.filter_by(user_id=user.id).delete()
                db.session.delete(user)

        db.session.commit()
        print("✅ Data simulasi berhasil dibersihkan")

    def create_users(self):
        """Buat 2 user: Budi (target) dan Iman (referensi)"""
        print("👥 Membuat 2 user...")

        users_data = [
            {"name": "Budi SVD", "username": "svd_budi", "email": "budi@example.com"},
            {"name": "Iman SVD", "username": "svd_iman", "email": "iman@example.com"},
        ]

        for user_data in users_data:
            user = User(
                name=user_data["name"],
                username=user_data["username"],
                email=user_data["email"],
                password=generate_password_hash("password123"),
                role="user",
            )

            db.session.add(user)
            db.session.flush()

            self.simulation_users.append(user)

        db.session.commit()
        print(f"✅ Berhasil membuat {len(self.simulation_users)} user")

    def get_foods(self):
        """Ambil tepat 10 makanan dari database"""
        print("🍽️ Mengambil 10 makanan...")

        foods = Food.query.limit(10).all()  # Ambil tepat 10 makanan
        if foods:
            self.sample_foods = foods
            print(f"✅ Berhasil mengambil {len(self.sample_foods)} makanan")
        else:
            print("❌ Tidak ada makanan di database")

    def create_ratings(self):
        """Buat rating dengan strategi Budi vs Iman"""
        print("\n⭐ MEMBUAT RATING STRATEGIS")
        print("=" * 50)

        print("📋 Strategi Rating:")
        print("   • IMAN: Rating 10 makanan semua (4.0-5.0)")
        print("   • BUDI: Rating 8 makanan saja (4.0-5.0)")
        print("   • Target: SVD rekomendasikan 2 makanan yang belum di-rating Budi")
        print()

        # Iman (user 0): Rating semua 10 makanan dengan sempurna
        iman_ratings = [4.8, 5.0, 4.5, 4.7, 4.9, 4.6, 4.4, 5.0, 4.3, 4.8]

        # Budi (user 1): Rating 8 makanan saja (skip makanan index 7 dan 9)
        budi_ratings = [4.5, 4.9, 4.3, 4.6, 4.7, 4.2, 4.8, None, 4.4, None]  # None = tidak di-rating

        rating_data = [iman_ratings, budi_ratings]

        for user_idx, user in enumerate(self.simulation_users):
            user_ratings = rating_data[user_idx]
            print(f"👤 Rating untuk {user.name}:")

            for food_idx, food in enumerate(self.sample_foods):
                rating = user_ratings[food_idx]

                if rating is not None:
                    print(f"   ⭐ {food.name[:25]:25} → {rating}")

                    food_rating = FoodRating(
                        user_id=user.id, food_id=food.id, rating=rating
                    )
                    db.session.add(food_rating)
                    self.created_ratings.append(food_rating)
                else:
                    print(f"   ➖ {food.name[:25]:25} → (tidak di-rating)")

            db.session.commit()
            print()

        print(f"✅ Total {len(self.created_ratings)} rating dibuat")
        print(f"📊 Iman: 10 ratings | Budi: 8 ratings")
        print(f"🎯 Target: SVD harus rekomendasikan 2 makanan yang belum di-rating Budi")

    def display_rating_table(self):
        """Tampilkan table rating"""
        print(f"\n📊 TABLE RATING USER-MAKANAN")
        print("=" * 100)

        # Header
        header = f"{'User':<12}"
        for i, food in enumerate(self.sample_foods):  # Tampilkan semua 10 makanan
            header += f"{food.name[:12]:<14}"
        print(header)
        print("-" * len(header))

        # Data
        for user in self.simulation_users:
            row = f"{user.name:<12}"

            for food in self.sample_foods:
                rating_record = FoodRating.query.filter_by(
                    user_id=user.id, food_id=food.id
                ).first()

                if rating_record:
                    row += f"{rating_record.rating:<14.1f}"
                else:
                    row += f"{'---':<14}"  # Tidak di-rating

            print(row)
        print()

        # Info tambahan
        print("📝 Keterangan:")
        print("   ⭐ = Di-rating | --- = Belum di-rating")
        budi_unrated = [food.name for food in self.sample_foods
                       if not FoodRating.query.filter_by(user_id=self.simulation_users[1].id, food_id=food.id).first()]
        print(f"   🎯 Budi belum rating: {', '.join(budi_unrated)}")
        print()

    def predict_collaborative(self):
        """Tampilkan prediksi collaborative menggunakan SVD"""
        print(f"\n🎯 HASIL PREDIKSI COLLABORATIVE (SVD)")
        print("=" * 50)

        # Inisialisasi SVD
        print("🤖 Training SVD model...")
        recommender = Recommendations(alpha=1.0)  # Hanya food ratings
        training_result = recommender.train_full_system()

        if not training_result["success"]:
            print(f"❌ Training SVD gagal: {training_result['error']}")
            return

        print("✅ SVD model berhasil di-training!")

        # Tampilkan metrics jika ada
        if training_result["validation_metrics"]:
            metrics = training_result["validation_metrics"]["food_model"]
            if "note" not in metrics:
                print(
                    f"📊 SVD Performance: RMSE={metrics['rmse']:.3f}, MAE={metrics['mae']:.3f}"
                )

        print()

        # Prediksi untuk setiap user menggunakan SVD
        for user in self.simulation_users:
            print(f"\n👤 Prediksi SVD untuk {user.name}:")

            # Get SVD recommendations dari SEMUA makanan
            all_recommendations = recommender.get_recommendations(user.id, n=20)

            # Filter hanya makanan yang ada di sample
            sample_food_names = [f.name for f in self.sample_foods]
            sample_recommendations = [
                rec for rec in all_recommendations
                if rec["food"]["name"] in sample_food_names
            ]

            if sample_recommendations:
                found_high_prediction = False

                # Cek prediksi tinggi dalam sample foods
                for rec in sample_recommendations:
                    food_name = rec["food"]["name"]
                    predicted_rating = rec["predicted_rating"]

                    # Cari makanan ini di sample foods
                    sample_food = next(
                        (f for f in self.sample_foods if f.name == food_name), None
                    )
                    if sample_food:
                        # Cek rating actual user ini
                        actual_rating = FoodRating.query.filter_by(
                            user_id=user.id, food_id=sample_food.id
                        ).first()

                        # Jika SVD prediksi tinggi (≥3.8) dan actual rating rendah
                        if predicted_rating >= 3.8:
                            if actual_rating and actual_rating.rating < 4.0:
                                # Cari user lain yang suka makanan ini
                                other_user_rating = FoodRating.query.filter(
                                    FoodRating.food_id == sample_food.id,
                                    FoodRating.user_id != user.id,
                                    FoodRating.rating >= 4.0,
                                ).first()

                                if other_user_rating:
                                    other_user = User.query.get(
                                        other_user_rating.user_id
                                    )
                                    if other_user:
                                        print(
                                            f"   💡 {user.name} mungkin akan SUKA {food_name}"
                                        )
                                        print(
                                            f"      SVD prediksi: ⭐{predicted_rating:.1f}"
                                        )
                                        print(
                                            f"      karena {other_user.name} memberikan rating {other_user_rating.rating:.1f}"
                                        )
                                        print(
                                            f"      (saat ini {user.name} rating {actual_rating.rating:.1f})"
                                        )
                                        found_high_prediction = True
                            elif not actual_rating:
                                # Makanan belum dicoba, tapi SVD prediksi tinggi
                                print(
                                    f"   💡 {user.name} mungkin akan SUKA {food_name}"
                                )
                                print(f"      SVD prediksi: ⭐{predicted_rating:.1f}")
                                print(f"      (makanan belum pernah dicoba)")
                                found_high_prediction = True

                if not found_high_prediction:
                    # Tampilkan top 3 sample recommendations
                    print(f"   � Top SVD recommendations dalam sample:")
                    for i, rec in enumerate(sample_recommendations[:3], 1):
                        print(f"   {i}. {rec['food']['name']} (⭐{rec['predicted_rating']:.1f})")
            else:
                print("   ❌ Tidak ada rekomendasi SVD untuk makanan dalam sample")
                # Tampilkan top recommendation dari seluruh database
                if all_recommendations:
                    top_rec = all_recommendations[0]
                    print(
                        f"   🔍 Top SVD recommendation (database): {top_rec['food']['name']} (⭐{top_rec['predicted_rating']:.1f})"
                    )

    def run_simulation(self):
        """Jalankan simulasi"""
        try:
            with self.app.app_context():
                print("🚀 SIMULASI COLLABORATIVE FILTERING")
                print("=" * 50)

                self.cleanup_previous_simulation()
                self.create_users()
                self.get_foods()
                self.create_ratings()

                # Output 1: Table rating
                self.display_rating_table()

                # Output 2: Prediksi
                self.predict_collaborative()

                print(f"\n🎉 SIMULASI SELESAI!")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    print("🚀 SIMULASI SVD SEDERHANA")
    print("📊 Output: Table Rating + Prediksi Collaborative")
    print("")

    simulator = SimpleSVDSimulator()
    simulator.run_simulation()
