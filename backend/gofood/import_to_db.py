"""
Import data from GoFood Excel files to database.
Handles restaurants and foods import from scrapped data.
"""

import pandas as pd
import os
import sys
from typing import Optional, List, Dict, Any, Union

# Add backend path to allow imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import create_app
from app.extensions import db
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food, FoodImage


class GoFoodDBImporter:
    """Import GoFood scraped data to database."""

    def __init__(self):
        """Initialize importer with Flask app context."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def __del__(self):
        """Clean up app context."""
        if hasattr(self, "app_context"):
            self.app_context.pop()

    def find_latest_excel_file(self, output_dir: str = "output") -> Optional[str]:
        """Find the latest detailed Excel file."""
        if not os.path.exists(output_dir):
            print(f"Output directory '{output_dir}' not found")
            return None

        # Look for gofood_detailed files
        files = [
            f
            for f in os.listdir(output_dir)
            if f.startswith("gofood_detailed_") and f.endswith(".xlsx")
        ]

        if not files:
            print("No detailed Excel files found")
            return None

        # Sort by filename (which includes timestamp) to get latest
        latest_file = sorted(files)[-1]
        return os.path.join(output_dir, latest_file)

    def load_excel_data(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """Load data from Excel file."""
        try:
            # Read all sheets from Excel file
            excel_data = pd.read_excel(file_path, sheet_name=None)
            print(f"Loaded Excel file: {file_path}")
            print(f"Available sheets: {list(excel_data.keys())}")
            return excel_data
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return {}

    def clean_restaurant_data(self, row: pd.Series) -> Dict[str, Any]:
        """Clean and prepare restaurant data for database."""

        # Handle NaN values
        def safe_get(value, default=None):
            if pd.isna(value):
                return default
            return value

        # Create description from tags if available
        tags = safe_get(row.get("Tags"), "")
        description = f"Categories: {tags}" if tags else None

        return {
            "name": safe_get(
                row.get("Name", row.get("Restaurant Name")), "Unknown Restaurant"
            ),
            "description": description,
            "address": "Kendari, Sulawesi Tenggara",  # Default address since not in data
            "phone": None,  # Not available in Excel
            "email": None,  # Not available in Excel
            "latitude": safe_get(row.get("Latitude"), 0.0),
            "longitude": safe_get(row.get("Longitude"), 0.0),
            "rating_average": safe_get(
                row.get("Average Rating", row.get("Rating")), 0.0
            ),
            "is_active": True,
        }

    def clean_food_data(self, row: pd.Series, restaurant_id: str) -> Dict[str, Any]:
        """Clean and prepare food data for database."""

        def safe_get(value, default=None):
            if pd.isna(value):
                return default
            return value

        # Extract price from integer value
        price_raw = safe_get(row.get("Price"))
        price = 0.0
        if price_raw is not None:
            try:
                if isinstance(price_raw, (int, float)):
                    price = float(price_raw)
                elif isinstance(price_raw, str):
                    # Remove Rp, spaces, dots and convert to float
                    price_str = (
                        price_raw.replace("Rp", "")
                        .replace(".", "")
                        .replace(",", "")
                        .strip()
                    )
                    price = float(price_str)
            except (ValueError, TypeError):
                price = 0.0

        return {
            "name": safe_get(row.get("Food Name"), "Unknown Food"),
            "description": safe_get(row.get("Description")),
            "category": "Food",  # Default category
            "price": price,
            "restaurant_id": restaurant_id,
        }

    def get_or_create_restaurant(self, restaurant_data: Dict[str, Any]) -> Restaurant:
        """Get existing restaurant or create new one."""
        # Try to find existing restaurant by name and location
        existing = Restaurant.query.filter(
            Restaurant.name == restaurant_data["name"],
            Restaurant.latitude == restaurant_data["latitude"],
            Restaurant.longitude == restaurant_data["longitude"],
        ).first()

        if existing:
            print(f"Found existing restaurant: {existing.name}")
            return existing

        # Create new restaurant
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
        db.session.flush()  # Get ID without committing
        print(f"Created new restaurant: {restaurant.name}")
        return restaurant

    def create_food(
        self, food_data: Dict[str, Any], image_url: Optional[str] = None
    ) -> Food:
        """Create new food item."""
        food = Food(**food_data)
        db.session.add(food)
        db.session.flush()  # Get ID without committing

        # Add image if provided
        if image_url and not pd.isna(image_url):
            food_image = FoodImage(
                food_id=food.id, image_url=str(image_url), is_main=True
            )
            db.session.add(food_image)

        print(f"Created food: {food.name} - {food.price}")
        return food

    def import_data(self, file_path: Optional[str] = None) -> bool:
        """Import data from Excel file to database."""
        if not file_path:
            file_path = self.find_latest_excel_file()
            if not file_path:
                return False

        print(f"Starting import from: {file_path}")

        # Load Excel data
        excel_data = self.load_excel_data(file_path)
        if not excel_data:
            return False

        try:
            restaurants_created = 0
            foods_created = 0

            # Get outlets and foods sheets
            outlets_df = excel_data.get("Outlets", pd.DataFrame())
            foods_df = excel_data.get("Foods", pd.DataFrame())

            if outlets_df.empty:
                print("No outlets data found")
                return False

            # Create restaurants from outlets sheet
            print(f"\nProcessing {len(outlets_df)} restaurants...")
            restaurant_uid_map = {}  # Map UID to restaurant ID

            for _, outlet_row in outlets_df.iterrows():
                restaurant_data = self.clean_restaurant_data(outlet_row)
                restaurant = self.get_or_create_restaurant(restaurant_data)

                # Map UID to restaurant ID for foods import
                outlet_uid = outlet_row.get("UID")
                if outlet_uid:
                    restaurant_uid_map[outlet_uid] = restaurant.id

                # Check if this is a new restaurant
                if restaurant.id not in [
                    r.id for r in db.session.new if hasattr(r, "id")
                ]:
                    # Restaurant existed
                    pass
                else:
                    restaurants_created += 1

            # Create foods from foods sheet
            if not foods_df.empty:
                print(f"\nProcessing {len(foods_df)} foods...")

                for _, food_row in foods_df.iterrows():
                    restaurant_uid = food_row.get("Restaurant UID")

                    if restaurant_uid not in restaurant_uid_map:
                        print(f"Warning: Restaurant UID {restaurant_uid} not found")
                        continue

                    restaurant_id = restaurant_uid_map[restaurant_uid]
                    food_data = self.clean_food_data(food_row, restaurant_id)

                    # Check if food already exists for this restaurant
                    existing_food = Food.query.filter(
                        Food.name == food_data["name"],
                        Food.restaurant_id == restaurant_id,
                    ).first()

                    if not existing_food:
                        image_url = food_row.get("Image URL")
                        self.create_food(food_data, image_url)
                        foods_created += 1
                    else:
                        print(f"Food already exists: {existing_food.name}")

            # Commit all changes
            db.session.commit()

            print(f"\n✅ Import completed successfully!")
            print(f"📍 Restaurants created: {restaurants_created}")
            print(f"🍽️  Foods created: {foods_created}")

            return True

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during import: {e}")
            import traceback

            traceback.print_exc()
            return False

    def preview_data(self, file_path: Optional[str] = None, max_rows: int = 5):
        """Preview Excel data before import."""
        if not file_path:
            file_path = self.find_latest_excel_file()
            if not file_path:
                return

        excel_data = self.load_excel_data(file_path)
        if not excel_data:
            return

        print(f"\n📊 Preview of data from: {file_path}")

        for sheet_name, df in excel_data.items():
            print(f"\n--- Sheet: {sheet_name} ---")
            print(f"Columns: {list(df.columns)}")
            print(f"Total rows: {len(df)}")

            if not df.empty:
                print(f"\nFirst {max_rows} rows:")
                print(df.head(max_rows).to_string())

                # Show unique restaurants
                if "Restaurant Name" in df.columns:
                    unique_restaurants = df["Restaurant Name"].nunique()
                    print(f"\nUnique restaurants: {unique_restaurants}")


def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Import GoFood data to database")
    parser.add_argument("--file", "-f", help="Excel file path to import")
    parser.add_argument(
        "--preview", "-p", action="store_true", help="Preview data only"
    )

    args = parser.parse_args()

    importer = GoFoodDBImporter()

    if args.preview:
        importer.preview_data(args.file)
    else:
        success = importer.import_data(args.file)
        if success:
            print("✅ Import completed successfully!")
        else:
            print("❌ Import failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
