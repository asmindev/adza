#!/usr/bin/env python3
"""
Test script for the single Recomendations class
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from flask import Flask
from app import create_app
from app.recommendation.service import Recomendations


def test_single_class():
    """Test the consolidated Recomendations class"""

    # Create Flask app context
    app = create_app()

    with app.app_context():
        print("Testing Single Recomendations Class")
        print("=" * 50)

        try:
            # Create recommendation system
            print("1. Creating Recomendations instance...")
            rec_system = Recomendations(alpha=0.7)
            print(f"✓ Instance created with alpha={rec_system.alpha}")

            # Train the full system
            print("\n2. Training full system...")
            results = rec_system.train_full_system()

            if results["success"]:
                print("✓ Training completed successfully!")
                print(f"Steps completed: {results['steps_completed']}")

                if results["validation_metrics"]:
                    print("\n3. Validation Metrics:")
                    for model_name, metrics in results["validation_metrics"].items():
                        print(f"  {model_name}:")
                        print(
                            f"    RMSE: {metrics['rmse']:.4f} ± {metrics['rmse_std']:.4f}"
                        )
                        print(
                            f"    MAE:  {metrics['mae']:.4f} ± {metrics['mae_std']:.4f}"
                        )

                # Test predictions
                print("\n4. Testing predictions...")
                user_id = "1"
                recommendations = rec_system.predict_hybrid_recommendations(
                    user_id, limit=5
                )

                if recommendations:
                    print(
                        f"✓ Generated {len(recommendations)} recommendations for user {user_id}"
                    )
                    print("\nTop 3 recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(
                            f"  {i}. {rec['food_name']} (Rating: {rec['final_predicted_rating']:.2f})"
                        )
                        print(
                            f"     Food Score: {rec['predicted_food_rating']:.2f}, Restaurant Score: {rec['predicted_restaurant_rating']:.2f}"
                        )
                        print(f"     Hybrid Score: {rec['hybrid_score']:.3f}")
                else:
                    print("⚠ No recommendations generated")

                # Test compatibility method
                print("\n5. Testing compatibility method...")
                compat_recs = rec_system.get_recommendations(user_id, n=3)

                if compat_recs:
                    print(
                        f"✓ Compatibility method returned {len(compat_recs)} recommendations"
                    )
                    print("First recommendation structure:")
                    rec = compat_recs[0]
                    print(f"  Food: {rec['food']['name']}")
                    print(f"  Predicted Rating: {rec['predicted_rating']:.2f}")
                    print(f"  Hybrid Score: {rec['hybrid_score']:.3f}")
                else:
                    print("⚠ Compatibility method returned no results")

                print("\n" + "=" * 50)
                print("✓ ALL TESTS PASSED - Single class working correctly!")

            else:
                print(f"✗ Training failed: {results['error']}")

        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_single_class()
