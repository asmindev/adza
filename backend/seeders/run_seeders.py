"""
Main Seeder File
Runs all seeders in the correct order
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from category_seeder import seed_restaurant_categories


def run_all_seeders():
    """Run all seeders in the correct order"""

    print("🌱 Starting database seeding process...")
    print("=" * 60)

    try:
        # 1. Seed restaurant categories
        print("\n1️⃣ Seeding restaurant categories...")
        seed_restaurant_categories()

        print("\n" + "=" * 60)
        print("✅ All seeders completed successfully!")
        print("🎉 Database is now ready with categories")
        print("\n💡 Next step: Run migration script from backend folder")
        print("   cd /home/labubu/Projects/adza/backend")
        print("   python migrate_restaurant_categories.py")

    except Exception as e:
        print(f"\n❌ Seeding process failed: {str(e)}")
        print("💡 Please check the error above and try again")
        raise e


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        run_all_seeders()
