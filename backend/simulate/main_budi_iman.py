#!/usr/bin/env python3
"""
Simulasi User untuk Sistem Rekomendasi SVD - Versi Sederhana

Output hanya:
1. Table rating user untuk makanan
2. Hasil prediksi collaborative

Scenario: 2 users (Budi dan Iman)
- Iman: rating sempurna 4-5 untuk semua 10 makanan
- Budi: rating sempurna untuk 8 makanan saja
- Target: SVD merekomendasikan 2 makanan yang belum di-rating Budi
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
    """Simulasi SVD sederhana dengan Budi dan Iman"""

    def __init__(self):
        self.app = create_app()
        self.simulation_users = []
        self.sample_foods = []

    def cleanup_previous_simulation(self):
        """Hapus data simulasi sebelumnya"""
        with self.app.app_context():
            print("🧹 Membersihkan data simulasi sebelumnya...")

            # Hapus ratings users simulasi berdasarkan nama dan email
            sim_user_names = ["Budi", "Iman"]
            sim_user_emails = ["budi@example.com", "iman@example.com"]

            # Cari users berdasarkan username atau email
            sim_users = User.query.filter(
                db.or_(
                    User.username.in_(sim_user_names), User.email.in_(sim_user_emails)
                )
            ).all()

            for user in sim_users:
                # Hapus semua ratings user ini
                FoodRating.query.filter_by(user_id=user.id).delete()
                # Hapus user
                db.session.delete(user)

            db.session.commit()
            print("✅ Data simulasi sebelumnya berhasil dibersihkan")

    def create_users(self):
        """Buat 2 users simulasi: Budi dan Iman"""
        with self.app.app_context():
            print("👤 Membuat 2 users simulasi...")

            users_data = [
                {"username": "Iman", "name": "Iman", "email": "iman@example.com"},
                {"username": "Budi", "name": "Budi", "email": "budi@example.com"},
            ]

            for user_data in users_data:
                user = User(
                    username=user_data["username"],
                    name=user_data["name"],
                    email=user_data["email"],
                    password=generate_password_hash("password123"),
                )
                db.session.add(user)
                self.simulation_users.append(user)

            db.session.commit()

            # Refresh users untuk menghindari DetachedInstanceError
            self.simulation_users = []
            for username in ["Iman", "Budi"]:
                user = User.query.filter_by(username=username).first()
                self.simulation_users.append(user)

            print(f"✅ {len(self.simulation_users)} users berhasil dibuat")

    def get_foods(self):
        """Ambil 10 makanan dari database"""
        with self.app.app_context():
            print("🍽️ Mengambil 10 makanan dari database...")

            # Ambil 10 makanan secara random
            self.sample_foods = Food.query.limit(10).all()

            if len(self.sample_foods) < 10:
                print(
                    f"⚠️ Hanya ada {len(self.sample_foods)} makanan di database, butuh minimal 10"
                )
                return

            print(f"✅ {len(self.sample_foods)} makanan berhasil diambil")
            for i, food in enumerate(self.sample_foods, 1):
                print(f"   {i}. {food.name}")

    def create_ratings(self):
        """Buat rating strategis: Iman rating semua (4-5), Budi rating 8 saja (4-5)"""
        with self.app.app_context():
            print("⭐ Membuat rating strategis...")

            iman = self.simulation_users[0]  # Iman
            budi = self.simulation_users[1]  # Budi

            # Iman: rating sempurna untuk SEMUA 10 makanan (4-5)
            print(f"   🌟 {iman.name}: Rating sempurna untuk SEMUA 10 makanan")
            for food in self.sample_foods:
                rating_value = random.choice([4.0, 4.5, 5.0])
                rating = FoodRating(
                    user_id=iman.id, food_id=food.id, rating=rating_value
                )
                db.session.add(rating)

            # Budi: rating sempurna untuk 8 makanan saja (sisakan 2 untuk rekomendasi)
            print(f"   🎯 {budi.name}: Rating sempurna untuk 8 makanan (sisakan 2)")
            sample_foods_copy = self.sample_foods.copy()
            random.shuffle(sample_foods_copy)

            # Rating 8 makanan pertama
            for food in sample_foods_copy[:8]:
                rating_value = random.choice([4.0, 4.5, 5.0])
                rating = FoodRating(
                    user_id=budi.id, food_id=food.id, rating=rating_value
                )
                db.session.add(rating)

            # 2 makanan terakhir tidak di-rating Budi (target rekomendasi)
            unrated_foods = sample_foods_copy[8:]
            print(f"   💡 Makanan yang TIDAK di-rating {budi.name}:")
            for food in unrated_foods:
                print(f"      - {food.name}")

            db.session.commit()
            print("✅ Rating strategis berhasil dibuat")

    def display_rating_table(self):
        """Tampilkan table rating dalam format sederhana"""
        with self.app.app_context():
            print(f"\n📊 TABLE RATING USER")
            print("=" * 60)

            # Header
            print(f"{'Makanan':<25} {'Iman':<8} {'Budi':<8}")
            print("-" * 60)

            # Isi table
            for food in self.sample_foods:
                ratings = {}
                for user in self.simulation_users:
                    rating = FoodRating.query.filter_by(
                        user_id=user.id, food_id=food.id
                    ).first()
                    ratings[user.name] = f"{rating.rating:.1f}" if rating else "-"

                print(f"{food.name[:24]:<25} {ratings['Iman']:<8} {ratings['Budi']:<8}")

        print()

    def analyze_user_similarity(self):
        """Analisis similaritas antara Iman dan Budi"""
        import numpy as np

        with self.app.app_context():
            print(f"\n🔍 ANALISIS SIMILARITAS IMAN vs BUDI")
            print("=" * 50)

            iman = self.simulation_users[0]  # Iman
            budi = self.simulation_users[1]  # Budi

            # Kumpulkan rating untuk makanan yang sama
            common_ratings_iman = []
            common_ratings_budi = []
            common_foods = []

            for food in self.sample_foods:
                iman_rating = FoodRating.query.filter_by(
                    user_id=iman.id, food_id=food.id
                ).first()
                budi_rating = FoodRating.query.filter_by(
                    user_id=budi.id, food_id=food.id
                ).first()

                # Hanya hitung jika KEDUA user memberikan rating
                if iman_rating and budi_rating:
                    common_ratings_iman.append(iman_rating.rating)
                    common_ratings_budi.append(budi_rating.rating)
                    common_foods.append(food.name)

            print(f"📊 Makanan yang di-rating KEDUA user: {len(common_foods)}")

            if len(common_foods) >= 2:
                # Konversi ke numpy arrays
                iman_array = np.array(common_ratings_iman)
                budi_array = np.array(common_ratings_budi)

                # Hitung korelasi Pearson secara manual
                correlation = np.corrcoef(iman_array, budi_array)[0, 1]

                print(f"� Korelasi Pearson: {correlation:.3f}")

                # Interpretasi korelasi
                if correlation > 0.7:
                    interpretation = "SANGAT MIRIP - Selera hampir sama!"
                elif correlation > 0.3:
                    interpretation = "CUKUP MIRIP - Ada kesamaan selera"
                elif correlation > 0:
                    interpretation = "SEDIKIT MIRIP - Beberapa kesamaan"
                elif correlation > -0.3:
                    interpretation = "NETRAL - Selera berbeda tapi tidak bertentangan"
                elif correlation > -0.7:
                    interpretation = "BERBEDA - Selera cukup berlawanan"
                else:
                    interpretation = "SANGAT BERBEDA - Selera berlawanan total!"

                print(f"💡 Interpretasi: {interpretation}")

                # Detail perbandingan rating
                print(f"\n📋 Detail Perbandingan Rating:")
                print(f"{'Makanan':<25} {'Iman':<6} {'Budi':<6} {'Diff':<6}")
                print("-" * 50)

                total_diff = 0
                for i, food_name in enumerate(common_foods):
                    iman_rating = common_ratings_iman[i]
                    budi_rating = common_ratings_budi[i]
                    diff = abs(iman_rating - budi_rating)
                    total_diff += diff

                    print(f"{food_name[:24]:<25} {iman_rating:<6.1f} {budi_rating:<6.1f} {diff:<6.1f}")

                avg_diff = total_diff / len(common_foods)
                print(f"\n📊 Rata-rata perbedaan rating: {avg_diff:.2f}")

                # Rating agreement
                exact_matches = sum(1 for i in range(len(common_foods))
                                  if abs(common_ratings_iman[i] - common_ratings_budi[i]) < 0.1)
                close_matches = sum(1 for i in range(len(common_foods))
                                  if abs(common_ratings_iman[i] - common_ratings_budi[i]) <= 0.5)

                print(f"🎯 Rating yang sama persis: {exact_matches}/{len(common_foods)} ({exact_matches/len(common_foods)*100:.1f}%)")
                print(f"🎯 Rating yang mirip (diff ≤ 0.5): {close_matches}/{len(common_foods)} ({close_matches/len(common_foods)*100:.1f}%)")

            else:
                print("❌ Tidak cukup data untuk analisis similaritas (butuh minimal 2 rating bersama)")

    def predict_collaborative(self):
        """Tampilkan prediksi collaborative untuk Budi berdasarkan Iman"""
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

        # Fokus pada BUDI sebagai target rekomendasi
        budi = self.simulation_users[1]  # Budi adalah user kedua
        iman = self.simulation_users[0]  # Iman adalah user pertama

        print(f"\n👤 Prediksi SVD untuk BUDI (target user):")

        # Get SVD recommendations untuk Budi
        all_recommendations = recommender.get_recommendations(budi.id, n=20)

        # Filter hanya makanan yang ada di sample
        sample_food_names = [f.name for f in self.sample_foods]
        sample_recommendations = [
            rec
            for rec in all_recommendations
            if rec["food"]["name"] in sample_food_names
        ]

        print(
            f"   📊 Found {len(sample_recommendations)} recommendations dalam 10 makanan sample"
        )

        if sample_recommendations:
            # Cari makanan yang belum di-rating Budi
            unrated_recommendations = []
            rated_recommendations = []

            for rec in sample_recommendations:
                food_name = rec["food"]["name"]
                predicted_rating = rec["predicted_rating"]

                # Cek apakah Budi sudah rating makanan ini
                sample_food = next(
                    (f for f in self.sample_foods if f.name == food_name), None
                )
                if sample_food:
                    budi_rating = FoodRating.query.filter_by(
                        user_id=budi.id, food_id=sample_food.id
                    ).first()

                    if not budi_rating:
                        # Belum di-rating Budi - ini target rekomendasi!
                        iman_rating = FoodRating.query.filter_by(
                            user_id=iman.id, food_id=sample_food.id
                        ).first()

                        unrated_recommendations.append(
                            {
                                "food_name": food_name,
                                "svd_prediction": predicted_rating,
                                "iman_rating": (
                                    iman_rating.rating if iman_rating else None
                                ),
                            }
                        )
                    else:
                        # Sudah di-rating Budi
                        rated_recommendations.append(
                            {
                                "food_name": food_name,
                                "svd_prediction": predicted_rating,
                                "budi_actual": budi_rating.rating,
                            }
                        )

            # Tampilkan hasil rekomendasi untuk makanan yang belum di-rating
            if unrated_recommendations:
                print(f"\n   🎯 REKOMENDASI UNTUK MAKANAN YANG BELUM DI-RATING BUDI:")
                for i, rec in enumerate(unrated_recommendations, 1):
                    print(f"   {i}. 💡 Budi mungkin akan SUKA {rec['food_name']}")
                    print(f"      SVD prediksi: ⭐{rec['svd_prediction']:.1f}")
                    if rec["iman_rating"]:
                        print(
                            f"      karena Iman memberikan rating {rec['iman_rating']:.1f}"
                        )
                    print(f"      (Budi belum pernah mencoba)")
                    print()
            else:
                print("   ❌ Tidak ada rekomendasi untuk makanan yang belum di-rating")

            # Tampilkan juga prediksi untuk makanan yang sudah di-rating (untuk validasi)
            if rated_recommendations:
                print(
                    f"   📈 VALIDASI SVD vs ACTUAL (makanan yang sudah di-rating Budi):"
                )
                for i, rec in enumerate(rated_recommendations[:3], 1):
                    print(
                        f"   {i}. {rec['food_name']}: SVD={rec['svd_prediction']:.1f} vs Actual={rec['budi_actual']:.1f}"
                    )
                print()

        else:
            print("   ❌ Tidak ada rekomendasi SVD untuk makanan dalam sample")

    def run_simulation(self):
        """Jalankan simulasi"""
        try:
            with self.app.app_context():
                print("🚀 SIMULASI COLLABORATIVE FILTERING - BUDI & IMAN")
                print("=" * 50)

                self.cleanup_previous_simulation()
                self.create_users()
                self.get_foods()
                self.create_ratings()

                # Output 1: Table rating
                self.display_rating_table()

                # Output 2: Analisis similaritas
                self.analyze_user_similarity()

                # Output 3: Prediksi
                self.predict_collaborative()

                print(f"\n🎉 SIMULASI SELESAI!")

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    print("🚀 SIMULASI SVD SEDERHANA - BUDI & IMAN")
    print("📊 Output: Table Rating + Prediksi Collaborative")
    print("🎯 Scenario: Iman rating sempurna semua, Budi cuma 8 makanan")
    print("")

    simulator = SimpleSVDSimulator()
    simulator.run_simulation()
