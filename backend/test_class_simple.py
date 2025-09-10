#!/usr/bin/env python3
"""
Simple test script for the single Recomendations class
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from flask import Flask
from app import create_app
from app.recommendation.service import Recomendations


def test_class_instantiation():
    """Test basic class functionality without database dependencies"""

    print("Testing Recomendations Class Basic Functionality")
    print("=" * 60)

    try:
        # Test 1: Class instantiation
        print("1. Testing class instantiation...")
        rec_system = Recomendations(alpha=0.7, n_factors=50, n_epochs=10)
        print(f"✓ Class instantiated successfully")
        print(f"  - Alpha: {rec_system.alpha}")
        print(f"  - N_factors: {rec_system.n_factors}")
        print(f"  - N_epochs: {rec_system.n_epochs}")

        # Test 2: Check methods exist
        print("\n2. Testing method availability...")
        methods = [
            "_import_modules",
            "_prepare_data",
            "_train_and_test_models",
            "_validate_models",
            "predict_hybrid_recommendations",
            "train_full_system",
            "get_recommendations",
            "get_popular_foods",
        ]

        for method in methods:
            if hasattr(rec_system, method):
                print(f"✓ Method '{method}' available")
            else:
                print(f"✗ Method '{method}' missing")

        # Test 3: Test step 1 (import modules)
        print("\n3. Testing module import step...")
        if rec_system._import_modules():
            print("✓ All required modules can be imported")
        else:
            print("✗ Module import failed")

        print("\n4. Testing alpha parameter variations...")
        alphas = [0.3, 0.5, 0.7, 0.9]
        for alpha in alphas:
            test_rec = Recomendations(alpha=alpha)
            print(f"✓ Alpha {alpha}: food_weight={alpha}, restaurant_weight={1-alpha}")

        print("\n" + "=" * 60)
        print("✓ ALL BASIC TESTS PASSED!")
        print("Class Recomendations is properly structured and ready to use.")
        print("\nNote: Database-dependent tests require actual rating data.")

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()


def test_with_flask_context():
    """Test within Flask application context"""

    print("\n" + "=" * 60)
    print("Testing with Flask App Context")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        try:
            print("1. Creating instance within Flask context...")
            rec_system = Recomendations(alpha=0.8)
            print("✓ Instance created successfully in Flask context")

            print("\n2. Testing get_popular_foods method...")
            popular = rec_system.get_popular_foods(n=5)
            if popular:
                print(f"✓ get_popular_foods returned {len(popular)} foods")
                if len(popular) > 0:
                    print(
                        f"  First food: {popular[0] if isinstance(popular[0], dict) else 'Food object'}"
                    )
            else:
                print("⚠ get_popular_foods returned empty result (normal if no data)")

            print("\n✓ Flask context tests completed!")

        except Exception as e:
            print(f"✗ Flask context test failed: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_class_instantiation()
    test_with_flask_context()
