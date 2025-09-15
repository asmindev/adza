#!/usr/bin/env python3
"""
Script untuk analisis similarity dan rekomendasi antara Asriani dan Adza
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.recommendation.service import Recommendations
from app.modules.user.models import User
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant
from app.extensions import db


def get_food_average_rating(food_id):
    """Calculate average rating for a food"""
    result = (
        db.session.query(func.avg(FoodRating.rating))
        .filter_by(food_id=food_id)
        .scalar()
    )
    return result if result else 0.0


def analyze_similarity_and_recommendations():
    """Analisis similarity dan rekomendasi antara Asriani dan Adza"""

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # ID users
        asriani_id = "4b9e10f9-2cc7-43f6-9502-d8e2f007c0d1"
        adza_id = "0aa296a2-2abb-40b4-b339-c7157e4eaaba"

        print("=" * 80)
        print("🔍 ANALISIS SIMILARITY & REKOMENDASI: ASRIANI vs ADZA")
        print("=" * 80)

        # Get users info
        asriani = User.query.filter_by(id=asriani_id).first()
        adza = User.query.filter_by(id=adza_id).first()

        if not asriani or not adza:
            print("❌ User tidak ditemukan!")
            return

        print(f"👤 User 1: {asriani.name} (@{asriani.username})")
        print(f"👤 User 2: {adza.name} (@{adza.username})")
        print()

        # === 1. TAMPILKAN TABLE RATINGS ===
        print("📊 1. TABLE FOOD RATINGS")
        print("-" * 50)

        # Get all food ratings for both users
        asriani_ratings = FoodRating.query.filter_by(user_id=asriani_id).all()
        adza_ratings = FoodRating.query.filter_by(user_id=adza_id).all()

        print(f"🍕 {asriani.name} ratings ({len(asriani_ratings)} foods):")
        asriani_food_ratings = {}
        for rating in asriani_ratings:
            food = Food.query.filter_by(id=rating.food_id).first()
            if food:
                print(f"   • {food.name}: {rating.rating}⭐ (ID: {food.id})")
                asriani_food_ratings[food.id] = rating.rating

        print()
        print(f"🍕 {adza.name} ratings ({len(adza_ratings)} foods):")
        adza_food_ratings = {}
        for rating in adza_ratings:
            food = Food.query.filter_by(id=rating.food_id).first()
            if food:
                print(f"   • {food.name}: {rating.rating}⭐ (ID: {food.id})")
                adza_food_ratings[food.id] = rating.rating

        print()

        # === 2. ANALISIS SIMILARITY ===
        print("🎯 2. ANALISIS SIMILARITY")
        print("-" * 50)

        # Get all unique food IDs
        all_food_ids = set(asriani_food_ratings.keys()) | set(adza_food_ratings.keys())
        common_food_ids = set(asriani_food_ratings.keys()) & set(
            adza_food_ratings.keys()
        )

        print(f"📈 Total makanan berbeda yang dinilai: {len(all_food_ids)}")
        print(f"📈 Makanan yang sama-sama dinilai: {len(common_food_ids)}")
        print(
            f"📈 Makanan hanya dinilai {asriani.name}: {len(set(asriani_food_ratings.keys()) - set(adza_food_ratings.keys()))}"
        )
        print(
            f"📈 Makanan hanya dinilai {adza.name}: {len(set(adza_food_ratings.keys()) - set(asriani_food_ratings.keys()))}"
        )

        if common_food_ids:
            print("\\n🔗 Makanan yang sama-sama dinilai:")
            for food_id in common_food_ids:
                food = Food.query.filter_by(id=food_id).first()
                if food:
                    asriani_rating = asriani_food_ratings[food_id]
                    adza_rating = adza_food_ratings[food_id]
                    print(
                        f"   • {food.name}: {asriani.name}={asriani_rating}⭐, {adza.name}={adza_rating}⭐"
                    )

            # Calculate similarity on common items
            asriani_common = [asriani_food_ratings[fid] for fid in common_food_ids]
            adza_common = [adza_food_ratings[fid] for fid in common_food_ids]

            # Cosine similarity
            cosine_sim = cosine_similarity([asriani_common], [adza_common])[0][0]

            # Pearson correlation
            correlation = np.corrcoef(asriani_common, adza_common)[0][1]

            # Mean Absolute Error (lower is better)
            mae = np.mean(np.abs(np.array(asriani_common) - np.array(adza_common)))

            print(f"\\n📊 SIMILARITY METRICS:")
            print(
                f"   🎯 Cosine Similarity: {cosine_sim:.3f} (range: -1 to 1, closer to 1 = more similar)"
            )
            print(
                f"   🎯 Pearson Correlation: {correlation:.3f} (range: -1 to 1, closer to 1 = more similar)"
            )
            print(f"   🎯 Mean Absolute Error: {mae:.3f} (lower = more similar)")

            # Interpretation
            if cosine_sim > 0.8:
                similarity_level = "Sangat Mirip 🔥"
            elif cosine_sim > 0.6:
                similarity_level = "Mirip 👍"
            elif cosine_sim > 0.4:
                similarity_level = "Cukup Mirip 👌"
            elif cosine_sim > 0.2:
                similarity_level = "Sedikit Mirip 🤏"
            else:
                similarity_level = "Tidak Mirip 👎"

            print(f"   📈 Tingkat Similarity: {similarity_level}")
        else:
            print("\\n⚠️  Tidak ada makanan yang sama-sama dinilai!")

        print()

        # === 3. POTENSI REKOMENDASI ===
        print("🎁 3. POTENSI REKOMENDASI")
        print("-" * 50)

        # Foods rated by Asriani but not by Adza (potential recommendations)
        potential_recommendations = set(asriani_food_ratings.keys()) - set(
            adza_food_ratings.keys()
        )

        print(f"🎯 Makanan yang dinilai {asriani.name} tapi belum dinilai {adza.name}:")
        print(
            f"    (Total: {len(potential_recommendations)} makanan - ini yang berpotensi direkomendasikan)"
        )
        print()

        if potential_recommendations:
            for food_id in potential_recommendations:
                food = Food.query.filter_by(id=food_id).first()
                if food:
                    asriani_rating = asriani_food_ratings[food_id]
                    restaurant = Restaurant.query.filter_by(
                        id=food.restaurant_id
                    ).first()

                    print(f"   • {food.name}")
                    print(
                        f"     🏪 {restaurant.name if restaurant else 'Unknown Restaurant'}"
                    )
                    print(f"     ⭐ Rating {asriani.name}: {asriani_rating}")
                    print(f"     💰 Harga: Rp {food.price:,}")
                    avg_rating = get_food_average_rating(food.id)
                    print(f"     📊 Avg Rating: {avg_rating:.1f}")
                    print()

        # === 4. TEST SISTEM REKOMENDASI ===
        print("🤖 4. TEST SISTEM REKOMENDASI")
        print("-" * 50)

        try:
            # Initialize recommendation service
            rec_service = Recommendations()

            # Ensure models are trained
            if rec_service.food_svd_model is None:
                print("🔄 Training models first...")
                train_result = rec_service.train_full_system()
                print(f"✅ Training completed: {train_result['success']}")

            print("🔄 Memproses rekomendasi untuk Adza...")

            # Get recommendations for Adza
            recommendations = rec_service.get_recommendations(user_id=adza_id, n=10)

            print(f"✅ Sistem menghasilkan {len(recommendations)} rekomendasi")
            print()

            if recommendations:
                print("🏆 TOP REKOMENDASI UNTUK ADZA:")
                print()

                # Check if any recommendations match potential ones
                recommended_food_ids = set()
                for i, rec in enumerate(recommendations, 1):
                    food_data = rec.get("food")
                    if food_data:
                        food_id = food_data.get("id")
                        if food_id:
                            recommended_food_ids.add(food_id)

                            # Check if this food was rated by Asriani
                            from_asriani = (
                                "✅" if food_id in asriani_food_ratings else "❌"
                            )
                            asriani_rating_text = (
                                f" (Asriani: {asriani_food_ratings[food_id]}⭐)"
                                if food_id in asriani_food_ratings
                                else ""
                            )

                            food_name = food_data.get("name", "Unknown Food")
                            food_price = food_data.get("price", 0)
                            restaurant_data = food_data.get("restaurant", {})
                            restaurant_name = restaurant_data.get(
                                "name", "Unknown Restaurant"
                            )
                            predicted_rating = rec.get("predicted_rating", "N/A")
                            final_score = rec.get("final_score", "N/A")

                            print(f"{i:2d}. 🍕 {food_name} {from_asriani}")
                            print(f"    🏪 {restaurant_name}")
                            print(f"    💰 Rp {food_price:,.0f}")
                            avg_rating = get_food_average_rating(food_id)
                            print(f"    ⭐ Avg Rating: {avg_rating:.1f}")
                            print(f"    🎯 Predicted Rating: {predicted_rating}")
                            print(f"    📊 Final Score: {final_score:.3f}")
                            print(f"    📝 Dari rating Asriani{asriani_rating_text}")
                            print()

                # Analysis
                matched_recommendations = (
                    recommended_food_ids & potential_recommendations
                )
                print("📈 ANALISIS HASIL:")
                print(
                    f"   🎯 Rekomendasi yang cocok dengan pola Asriani: {len(matched_recommendations)}/{len(potential_recommendations)}"
                )

                if matched_recommendations:
                    print(
                        "   ✅ Makanan yang berhasil direkomendasikan berdasarkan similarity:"
                    )
                    for food_id in matched_recommendations:
                        food = Food.query.filter_by(id=food_id).first()
                        if food:
                            print(
                                f"      • {food.name} (Rating Asriani: {asriani_food_ratings[food_id]}⭐)"
                            )
                else:
                    print(
                        "   ⚠️  Tidak ada rekomendasi yang sesuai dengan pola rating Asriani"
                    )

            else:
                print("📭 Sistem tidak menghasilkan rekomendasi")

        except Exception as e:
            print(f"❌ Error dalam sistem rekomendasi: {str(e)}")
            import traceback

            traceback.print_exc()

        print("=" * 80)


if __name__ == "__main__":
    analyze_similarity_and_recommendations()
