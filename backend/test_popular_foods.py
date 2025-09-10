#!/usr/bin/env python3

"""
Test script to verify the get_popular_foods method returns the correct format
"""

import sys
import os

# Add the current directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.recommendation.service import Recomendations
import json


def test_popular_foods():
    """Test the get_popular_foods method"""

    # Create Flask app context
    app = create_app()

    with app.app_context():
        try:
            # Create recommendation system instance
            rec_system = Recomendations()

            # Get popular foods
            result = rec_system.get_popular_foods(n=5)

            print("Result type:", type(result))
            print("Number of foods:", len(result))

            # Print formatted result
            print("\nFormatted result:")
            print(json.dumps(result, indent=2, default=str))

            # Check if result matches expected format
            if isinstance(result, dict):
                for key, food in result.items():
                    print(f"\nFood {key}:")
                    print(f"  - ID: {food.get('id', 'N/A')}")
                    print(f"  - Name: {food.get('name', 'N/A')}")
                    print(f"  - Price: {food.get('price', 'N/A')}")
                    print(f"  - Ratings: {food.get('ratings', 'N/A')}")
                    print(f"  - Restaurant: {food.get('restaurant', 'N/A')}")

                    # Verify required fields exist
                    required_fields = ["id", "name", "price", "ratings", "restaurant"]
                    for field in required_fields:
                        if field not in food:
                            print(f"  ⚠️  Missing field: {field}")
                        else:
                            print(f"  ✅ Has field: {field}")
            else:
                print("❌ Result is not a dictionary")

        except Exception as e:
            print(f"❌ Error testing popular foods: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_popular_foods()
