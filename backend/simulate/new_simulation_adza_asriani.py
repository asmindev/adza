#!/usr/bin/env python3
"""
Script simulasi baru untuk sistem rekomendasi
- Hapus semua data rating
- Buat 2 user (adza dan asriani)
- Ambil 6 makanan
- Asriani rating 6 makanan dengan rating sempurna (4-5)
- Adza rating 4 dari 6 makanan tersebut
- Test apakah 2 makanan yang belum di-rating akan menjadi rekomendasi untuk adza
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.recommendation.service import Recommendations
from app.modules.user.models import User
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant
from app.extensions import db


def clear_all_ratings():
    """Hapus semua data rating dari database"""
    print("🗑️ Menghapus semua data rating...")

    try:
        # Hapus semua food ratings
        food_ratings_count = db.session.query(FoodRating).count()
        db.session.query(FoodRating).delete()

        # Hapus semua restaurant ratings
        restaurant_ratings_count = db.session.query(RestaurantRating).count()
        db.session.query(RestaurantRating).delete()

        db.session.commit()

        print(f"✅ Berhasil menghapus {food_ratings_count} food ratings")
        print(f"✅ Berhasil menghapus {restaurant_ratings_count} restaurant ratings")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error saat menghapus rating: {str(e)}")
        raise


def create_or_get_users():
    """Buat atau ambil user adza dan asriani, plus beberapa user dummy"""
    print("👤 Membuat/mengambil user adza, asriani, dan beberapa user dummy...")

    # User Adza
    adza = User.query.filter_by(username="adza").first()
    if not adza:
        adza = User(
            name="Adza",
            username="adza",
            email="adza@example.com",
            password=generate_password_hash("password123"),
            role="user",
            onboarding_completed=True,
        )
        db.session.add(adza)
        print("✅ User Adza dibuat")
    else:
        print(f"✅ User Adza sudah ada (ID: {adza.id})")

    # User Asriani
    asriani = User.query.filter_by(username="asriani").first()
    if not asriani:
        asriani = User(
            name="Asriani",
            username="asriani",
            email="asriani@example.com",
            password=generate_password_hash("password123"),
            role="user",
            onboarding_completed=True,
        )
        db.session.add(asriani)
        print("✅ User Asriani dibuat")
    else:
        print(f"✅ User Asriani sudah ada (ID: {asriani.id})")

    # Buat beberapa user dummy untuk memenuhi minimal 3 user
    dummy_users = []
    for i in range(1, 4):  # Buat 3 user dummy
        username = f"dummy{i}"
        dummy_user = User.query.filter_by(username=username).first()
        if not dummy_user:
            dummy_user = User(
                name=f"Dummy User {i}",
                username=username,
                email=f"dummy{i}@example.com",
                password=generate_password_hash("password123"),
                role="user",
                onboarding_completed=True,
            )
            db.session.add(dummy_user)
            print(f"✅ User Dummy {i} dibuat")
        else:
            print(f"✅ User Dummy {i} sudah ada (ID: {dummy_user.id})")
        dummy_users.append(dummy_user)

    try:
        db.session.commit()
        return adza, asriani, dummy_users
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error saat membuat user: {str(e)}")
        raise


def get_random_foods(count=6):
    """Ambil makanan acak dari database"""
    print(f"🍕 Mengambil {count} makanan acak...")

    foods = Food.query.limit(count).all()

    if len(foods) < count:
        print(f"⚠️ Hanya tersedia {len(foods)} makanan di database")

    print("📋 Makanan yang dipilih:")
    for i, food in enumerate(foods, 1):
        restaurant = Restaurant.query.filter_by(id=food.restaurant_id).first()
        restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"
        print(f"   {i}. {food.name} - {restaurant_name} (Rp {food.price:,})")

    return foods


def create_asriani_ratings(asriani, foods):
    """Buat rating sempurna untuk Asriani pada semua 6 makanan"""
    print("⭐ Membuat rating sempurna untuk Asriani...")

    perfect_ratings = [4.0, 5.0, 4.5, 5.0, 4.0, 4.5]  # Rating sempurna antara 4-5

    for i, food in enumerate(foods):
        rating_value = perfect_ratings[i % len(perfect_ratings)]

        rating = FoodRating(user_id=asriani.id, food_id=food.id, rating=rating_value)

        db.session.add(rating)

        restaurant = Restaurant.query.filter_by(id=food.restaurant_id).first()
        restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"
        print(f"   ✅ {food.name} ({restaurant_name}): {rating_value}⭐")

    try:
        db.session.commit()
        print(f"✅ Berhasil membuat {len(foods)} rating untuk Asriani")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error saat membuat rating Asriani: {str(e)}")
        raise


def create_adza_ratings(adza, foods):
    """Buat rating tinggi untuk Adza pada 4 dari 6 makanan"""
    print("⭐ Membuat rating tinggi untuk Adza pada 4 makanan...")

    # Ambil 4 makanan pertama untuk diberi rating
    foods_to_rate = foods[:4]
    high_ratings = [4.0, 5.0, 4.5, 4.0]  # Rating tinggi

    print("📋 Makanan yang akan di-rating Adza:")
    for i, food in enumerate(foods_to_rate):
        rating_value = high_ratings[i % len(high_ratings)]

        rating = FoodRating(user_id=adza.id, food_id=food.id, rating=rating_value)

        db.session.add(rating)

        restaurant = Restaurant.query.filter_by(id=food.restaurant_id).first()
        restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"
        print(f"   ✅ {food.name} ({restaurant_name}): {rating_value}⭐")

    print("📋 Makanan yang BELUM di-rating Adza (harapan rekomendasi):")
    unrated_foods = foods[4:]
    for i, food in enumerate(unrated_foods, 1):
        restaurant = Restaurant.query.filter_by(id=food.restaurant_id).first()
        restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"
        print(
            f"   🎯 {food.name} ({restaurant_name}) - Rating Asriani: {get_asriani_rating(food.id)}⭐"
        )

    try:
        db.session.commit()
        print(f"✅ Berhasil membuat {len(foods_to_rate)} rating untuk Adza")
        return unrated_foods
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error saat membuat rating Adza: {str(e)}")
        raise


def get_asriani_rating(food_id):
    """Ambil rating Asriani untuk makanan tertentu"""
    asriani = User.query.filter_by(username="asriani").first()
    if asriani:
        rating = FoodRating.query.filter_by(user_id=asriani.id, food_id=food_id).first()
        return rating.rating if rating else "N/A"
    return "N/A"


def test_recommendations(adza, expected_foods):
    """Test apakah makanan yang belum di-rating muncul dalam rekomendasi"""
    print("🤖 Testing sistem rekomendasi untuk Adza...")

    try:
        # Initialize recommendation service
        rec_service = Recommendations()

        # Ensure data is loaded
        print("🔄 Loading recommendation data...")
        success = rec_service._load_and_validate_data()
        if not success:
            print("❌ Failed to load recommendation data")
            return

        print("🔄 Memproses rekomendasi untuk Adza...")

        # Get recommendations for Adza (returns list of food IDs)
        recommended_food_ids = rec_service.recommend(user_id=adza.id, top_n=10)

        print(f"✅ Sistem menghasilkan {len(recommended_food_ids)} rekomendasi")
        print()

        if recommended_food_ids:
            print("🏆 TOP REKOMENDASI UNTUK ADZA:")
            print()

            expected_food_ids = set(food.id for food in expected_foods)
            found_expected = set()

            for i, food_id in enumerate(recommended_food_ids, 1):
                # Get food details
                food = Food.query.filter_by(id=food_id).first()
                if not food:
                    continue

                restaurant = Restaurant.query.filter_by(id=food.restaurant_id).first()
                restaurant_name = (
                    restaurant.name if restaurant else "Unknown Restaurant"
                )

                # Check if this is one of our expected foods
                is_expected = "🎯" if food_id in expected_food_ids else "   "
                if food_id in expected_food_ids:
                    found_expected.add(food_id)

                asriani_rating = get_asriani_rating(food_id)

                print(f"{is_expected} {i:2d}. 🍕 {food.name}")
                print(f"       🏪 {restaurant_name}")
                print(f"       💰 Rp {food.price:,.0f}")
                print(f"       ⭐ Rating Asriani: {asriani_rating}")
                print()

            # Analysis
            success_rate = len(found_expected) / len(expected_food_ids) * 100
            print("=" * 60)
            print("📈 HASIL ANALISIS:")
            print(f"   🎯 Makanan yang diharapkan: {len(expected_food_ids)}")
            print(
                f"   ✅ Makanan yang berhasil direkomendasikan: {len(found_expected)}"
            )
            print(f"   📊 Success Rate: {success_rate:.1f}%")

            if success_rate >= 50:
                print(
                    "   🔥 SIMULASI BERHASIL! Sistem rekomendasi bekerja dengan baik!"
                )
            else:
                print("   ⚠️ Simulasi kurang optimal. Perlu penyesuaian algoritma.")

            print()
            if found_expected:
                print("   ✅ Makanan yang berhasil direkomendasikan:")
                for food_id in found_expected:
                    food = Food.query.filter_by(id=food_id).first()
                    if food:
                        asriani_rating = get_asriani_rating(food_id)
                        print(
                            f"      • {food.name} (Rating Asriani: {asriani_rating}⭐)"
                        )

            missing_foods = expected_food_ids - found_expected
            if missing_foods:
                print("   ❌ Makanan yang tidak direkomendasikan:")
                for food_id in missing_foods:
                    food = Food.query.filter_by(id=food_id).first()
                    if food:
                        asriani_rating = get_asriani_rating(food_id)
                        print(
                            f"      • {food.name} (Rating Asriani: {asriani_rating}⭐)"
                        )

        else:
            print("📭 Sistem tidak menghasilkan rekomendasi")

    except Exception as e:
        print(f"❌ Error dalam sistem rekomendasi: {str(e)}")
        import traceback

        traceback.print_exc()


def create_dummy_ratings(dummy_users, foods):
    """Buat rating acak untuk user dummy agar sistem rekomendasi bisa bekerja"""
    print("⭐ Membuat rating acak untuk user dummy...")

    import random

    for dummy_user in dummy_users:
        # Setiap dummy user rating 2-3 makanan secara acak
        num_ratings = random.randint(2, 3)
        selected_foods = random.sample(foods, num_ratings)

        for food in selected_foods:
            # Rating acak antara 2.5 - 4.5
            rating_value = round(random.uniform(2.5, 4.5), 1)

            rating = FoodRating(
                user_id=dummy_user.id, food_id=food.id, rating=rating_value
            )

            db.session.add(rating)
            print(f"   ✅ {dummy_user.name} -> {food.name}: {rating_value}⭐")

    try:
        db.session.commit()
        print(f"✅ Berhasil membuat rating untuk {len(dummy_users)} user dummy")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error saat membuat rating dummy: {str(e)}")
        raise


def run_simulation():
    """Jalankan simulasi lengkap"""
    app = create_app()

    with app.app_context():
        print("=" * 80)
        print("🚀 SIMULASI BARU: SISTEM REKOMENDASI ADZA & ASRIANI")
        print("=" * 80)
        print()

        # Step 1: Clear all ratings
        clear_all_ratings()
        print()

        # Step 2: Create/get users
        adza, asriani, dummy_users = create_or_get_users()
        print()

        # Step 3: Get 6 random foods
        foods = get_random_foods(6)
        print()

        # Step 4: Create perfect ratings for Asriani
        create_asriani_ratings(asriani, foods)
        print()

        # Step 5: Create ratings for Adza (4 out of 6 foods)
        unrated_foods = create_adza_ratings(adza, foods)
        print()

        # Step 6: Create dummy ratings to satisfy minimum user requirement
        create_dummy_ratings(dummy_users, foods)
        print()

        # Step 7: Test recommendations
        test_recommendations(adza, unrated_foods)

        print("=" * 80)
        print("✅ SIMULASI SELESAI!")
        print("=" * 80)


if __name__ == "__main__":
    run_simulation()
