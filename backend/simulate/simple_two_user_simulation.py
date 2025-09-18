#!/usr/bin/env python3
"""
Script simulasi dengan 2 user saja - menggunakan fallback mechanism
- Hapus semua data rating
- Buat 2 user (adza dan asriani)
- Ambil 6 makanan
- Asriani rating 6 makanan dengan rating sempurna (4-5)
- Adza rating 4 dari 6 makanan tersebut
- Test fallback recommendation untuk adza
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
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
    """Buat atau ambil user adza dan asriani saja"""
    print("👤 Membuat/mengambil user adza dan asriani...")

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

    try:
        db.session.commit()
        return adza, asriani
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


def simple_similarity_recommendation(adza, asriani, expected_foods):
    """Implementasi rekomendasi sederhana berdasarkan similarity 2 user"""
    print("🤖 Testing rekomendasi sederhana berdasarkan similarity 2 user...")

    # Ambil semua rating dari kedua user
    adza_ratings = FoodRating.query.filter_by(user_id=adza.id).all()
    asriani_ratings = FoodRating.query.filter_by(user_id=asriani.id).all()

    print(f"📊 Rating Adza: {len(adza_ratings)} makanan")
    print(f"📊 Rating Asriani: {len(asriani_ratings)} makanan")

    # Buat mapping rating
    adza_food_ratings = {r.food_id: r.rating for r in adza_ratings}
    asriani_food_ratings = {r.food_id: r.rating for r in asriani_ratings}

    # Cari makanan yang sama-sama di-rating
    common_foods = set(adza_food_ratings.keys()) & set(asriani_food_ratings.keys())
    print(f"📊 Makanan yang sama-sama di-rating: {len(common_foods)}")

    if len(common_foods) > 0:
        # Hitung similarity berdasarkan makanan yang sama-sama di-rating
        adza_common = [adza_food_ratings[fid] for fid in common_foods]
        asriani_common = [asriani_food_ratings[fid] for fid in common_foods]

        # Cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity

        similarity = cosine_similarity([adza_common], [asriani_common])[0][0]

        print(f"🎯 Similarity Score: {similarity:.3f}")

        # Jika similarity tinggi (> 0.7), rekomendasikan makanan yang disukai Asriani tapi belum di-rating Adza
        if similarity > 0.7:
            recommendations = []
            asriani_unrated_by_adza = set(asriani_food_ratings.keys()) - set(
                adza_food_ratings.keys()
            )

            print(f"🎁 Makanan kandidat rekomendasi: {len(asriani_unrated_by_adza)}")

            # Sortir berdasarkan rating Asriani (tertinggi dulu)
            candidates = [
                (fid, asriani_food_ratings[fid]) for fid in asriani_unrated_by_adza
            ]
            candidates.sort(key=lambda x: x[1], reverse=True)

            # Ambil top recommendations
            recommendations = [fid for fid, rating in candidates if rating >= 4.0]

            print("🏆 REKOMENDASI BERDASARKAN SIMILARITY:")
            print()

            expected_food_ids = set(food.id for food in expected_foods)
            found_expected = set()

            for i, food_id in enumerate(recommendations, 1):
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
            if len(expected_food_ids) > 0:
                success_rate = len(found_expected) / len(expected_food_ids) * 100
                print("=" * 60)
                print("📈 HASIL ANALISIS:")
                print(f"   🎯 Makanan yang diharapkan: {len(expected_food_ids)}")
                print(
                    f"   ✅ Makanan yang berhasil direkomendasikan: {len(found_expected)}"
                )
                print(f"   📊 Success Rate: {success_rate:.1f}%")
                print(f"   📊 Similarity Score: {similarity:.3f}")

                if success_rate >= 50:
                    print(
                        "   🔥 SIMULASI BERHASIL! Algoritma similarity sederhana bekerja!"
                    )
                else:
                    print("   ⚠️ Simulasi kurang optimal.")

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
            print(
                f"⚠️ Similarity terlalu rendah ({similarity:.3f}) untuk memberikan rekomendasi"
            )
    else:
        print(
            "❌ Tidak ada makanan yang sama-sama di-rating untuk menghitung similarity"
        )


def run_simulation():
    """Jalankan simulasi lengkap dengan 2 user saja"""
    app = create_app()

    with app.app_context():
        print("=" * 80)
        print("🚀 SIMULASI: SISTEM REKOMENDASI SEDERHANA ADZA & ASRIANI (2 USER)")
        print("=" * 80)
        print()

        # Step 1: Clear all ratings
        clear_all_ratings()
        print()

        # Step 2: Create/get users
        adza, asriani = create_or_get_users()
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

        # Step 6: Test simple similarity recommendation
        simple_similarity_recommendation(adza, asriani, unrated_foods)

        print("=" * 80)
        print("✅ SIMULASI SELESAI!")
        print("=" * 80)


if __name__ == "__main__":
    run_simulation()
