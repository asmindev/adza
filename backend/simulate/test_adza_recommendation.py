#!/usr/bin/env python3
"""
Script sederhana untuk test rekomendasi user Adza
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.recommendation.service import Recommendations
from app.modules.user.models import User
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant


def test_adza_recommendation():
    """Test rekomendasi untuk user Adza"""

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # ID user Adza dari data yang diberikan
        adza_user_id = "0aa296a2-2abb-40b4-b339-c7157e4eaaba"

        print("=" * 60)
        print("🍽️  TEST REKOMENDASI UNTUK USER ADZA")
        print("=" * 60)

        # Get user info
        user = User.query.filter_by(id=adza_user_id).first()
        if not user:
            print("❌ User Adza tidak ditemukan!")
            return

        print(f"👤 User: {user.name} (@{user.username})")
        print(f"📧 Email: {user.email}")
        print(f"🆔 ID: {user.id}")
        print()

        # Initialize recommendation service
        rec_service = Recommendations()

        try:
            print("🔄 Memproses rekomendasi...")

            # Get recommendations
            recommendations = rec_service.get_recommendations(
                user_id=adza_user_id, n=10
            )

            print(f"✅ Berhasil mendapatkan {len(recommendations)} rekomendasi")
            print()

            if not recommendations:
                print("📭 Tidak ada rekomendasi yang ditemukan")
                return

            print("🏆 TOP REKOMENDASI UNTUK ADZA:")
            print("-" * 50)

            for i, rec in enumerate(recommendations, 1):
                food = Food.query.filter_by(id=rec["food_id"]).first()
                restaurant = Restaurant.query.filter_by(id=rec["restaurant_id"]).first()

                if food and restaurant:
                    print(f"{i:2d}. 🍕 {food.name}")
                    print(f"    🏪 {restaurant.name}")
                    print(f"    💰 Rp {food.price:,}")
                    print(f"    ⭐ Rating: {food.average_rating:.1f}")
                    print(f"    🎯 Score: {rec['score']:.3f}")
                    print()

        except Exception as e:
            print(f"❌ Error saat mendapatkan rekomendasi: {str(e)}")
            import traceback

            traceback.print_exc()

        print("=" * 60)


if __name__ == "__main__":
    test_adza_recommendation()
