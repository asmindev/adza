#!/usr/bin/env python3
"""
Script untuk debug sistem rekomendasi
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.recommendation.service import Recommendations
from app.modules.user.models import User


def debug_recommendation_system():
    """Debug sistem rekomendasi untuk melihat status training"""

    app = create_app()

    with app.app_context():
        adza_id = "0aa296a2-2abb-40b4-b339-c7157e4eaaba"

        print("🔧 DEBUG SISTEM REKOMENDASI")
        print("=" * 50)

        try:
            # Initialize recommendation service
            rec_service = Recommendations()

            print("🔍 Checking system status...")

            # Check if models are trained
            print(
                f"📊 Food SVD Model: {'✅ Trained' if rec_service.food_svd_model is not None else '❌ Not Trained'}"
            )
            print(
                f"📊 Restaurant SVD Model: {'✅ Trained' if rec_service.restaurant_svd_model is not None else '❌ Not Trained'}"
            )

            # Check data availability
            print(
                f"🍕 Food ratings data shape: {rec_service.food_ratings_df.shape if hasattr(rec_service, 'food_ratings_df') and rec_service.food_ratings_df is not None else 'None'}"
            )
            print(
                f"🏪 Restaurant ratings data shape: {rec_service.restaurant_ratings_df.shape if hasattr(rec_service, 'restaurant_ratings_df') and rec_service.restaurant_ratings_df is not None else 'None'}"
            )

            # Try to train if not trained
            if rec_service.food_svd_model is None:
                print("🔄 Trying to train models...")
                try:
                    result = rec_service.train_full_system()
                    print("✅ Training completed!")
                    print(
                        f"📊 Food SVD Model: {'✅ Trained' if rec_service.food_svd_model is not None else '❌ Still Not Trained'}"
                    )
                    print(
                        f"📊 Restaurant SVD Model: {'✅ Trained' if rec_service.restaurant_svd_model is not None else '❌ Still Not Trained'}"
                    )
                    print(f"📈 Training results: {result}")
                except Exception as e:
                    print(f"❌ Training failed: {str(e)}")
                    import traceback

                    traceback.print_exc()

            # Try simple prediction after training
            if rec_service.food_svd_model is not None:
                print("\\n🎯 Testing recommendation generation...")
                try:
                    recommendations = rec_service.get_recommendations(
                        user_id=adza_id, n=5
                    )
                    print(
                        f"✅ Generated {len(recommendations)} recommendations successfully!"
                    )

                    if recommendations:
                        print("\\n🏆 Sample recommendations:")
                        for i, rec in enumerate(recommendations[:3], 1):
                            print(f"   {i}. Food ID: {rec.get('food_id', 'N/A')}")
                            print(f"      Score: {rec.get('score', 'N/A')}")

                except Exception as e:
                    print(f"❌ Recommendation generation failed: {str(e)}")
                    import traceback

                    traceback.print_exc()

        except Exception as e:
            print(f"❌ System initialization failed: {str(e)}")
            import traceback

            traceback.print_exc()

        print("=" * 50)


if __name__ == "__main__":
    debug_recommendation_system()
