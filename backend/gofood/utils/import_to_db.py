"""
Import data from GoFood Excel files to database.
Handles restaurants and foods import from scrapped data.
"""

import pandas as pd
import os
import sys
from typing import Optional, List, Dict, Any, Union

# Add backend path to allow imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import create_app
from app.extensions import db
from app.modules.restaurant.models import Restaurant
from app.modules.food.models import Food, FoodImage
from app.modules.category.models import Category


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

    def extract_and_create_categories(self, outlets_df: pd.DataFrame) -> Dict[str, str]:
        """Extract categories from Tags column and create Category entities."""
        print("Extracting and creating categories...")

        # Collect all unique tags
        all_tags = set()
        for _, row in outlets_df.iterrows():
            tags_str = row.get("Tags", "")
            if tags_str and not pd.isna(tags_str):
                # Split by comma and clean each tag
                tags = [tag.strip() for tag in str(tags_str).split(",")]
                all_tags.update(tags)

        # Remove empty tags
        all_tags = {tag for tag in all_tags if tag}

        print(f"Found {len(all_tags)} unique categories: {sorted(list(all_tags))}")

        # Create categories in database
        category_map = {}  # name -> id mapping
        categories_created = 0

        for tag_name in sorted(all_tags):
            # Check if category already exists
            existing = Category.query.filter(Category.name == tag_name).first()

            if existing:
                category_map[tag_name] = existing.id
                print(f"Found existing category: {tag_name}")
            else:
                # Create new category
                category = Category(
                    name=tag_name,
                    description=f"Category for {tag_name} restaurants",
                    is_active=True,
                )
                db.session.add(category)
                db.session.flush()  # Get ID without committing
                category_map[tag_name] = category.id
                categories_created += 1
                print(f"Created new category: {tag_name}")

        print(
            f"✅ Categories processed: {categories_created} new, {len(all_tags) - categories_created} existing"
        )
        return category_map

    def get_primary_category_id(
        self, tags_str: str, category_map: Dict[str, str]
    ) -> Optional[str]:
        """Get primary category ID from tags string."""
        if not tags_str or pd.isna(tags_str):
            return None

        # Split tags and get the first one as primary
        tags = [tag.strip() for tag in str(tags_str).split(",")]
        if tags and tags[0] in category_map:
            return category_map[tags[0]]

        return None

    def get_category_ids_from_tags(
        self, tags_str: str, category_map: Dict[str, str]
    ) -> List[str]:
        """Get list of category IDs from tags string."""
        if not tags_str or pd.isna(tags_str):
            return []

        # Split tags and get all matching category IDs
        tags = [tag.strip() for tag in str(tags_str).split(",")]
        category_ids = []

        for tag in tags:
            if tag in category_map:
                category_ids.append(category_map[tag])

        return category_ids

    def add_categories_to_restaurant(
        self, restaurant: Restaurant, category_ids: List[str]
    ):
        """Add categories to restaurant using many-to-many relationship."""
        if not category_ids:
            return

        for category_id in category_ids:
            category = db.session.get(Category, category_id)
            if category:
                # Check if relationship already exists
                existing = db.session.execute(
                    db.text(
                        "SELECT 1 FROM restaurant_categories WHERE restaurant_id = :rid AND category_id = :cid"
                    ),
                    {"rid": restaurant.id, "cid": category_id},
                ).fetchone()

                if not existing:
                    restaurant.categories.append(category)
                    print(
                        f"Added category '{category.name}' to restaurant '{restaurant.name}'"
                    )

    def clean_restaurant_data(
        self, row: pd.Series, category_map: Optional[Dict[str, str]] = None
    ) -> tuple[Dict[str, Any], List[str]]:
        """Clean and prepare restaurant data for database and return category IDs."""

        # Handle NaN values
        def safe_get(value, default=None):
            if pd.isna(value):
                return default
            return value

        # Create description from tags if available
        tags = safe_get(row.get("Tags"), "")
        description = f"Categories: {tags}" if tags else None

        # Get all category IDs from tags for many-to-many relationship
        category_ids = []
        if category_map and tags:
            category_ids = self.get_category_ids_from_tags(str(tags), category_map)

        restaurant_data = {
            "id": safe_get(row.get("UID")),  # Use Excel UID as database ID
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

        return restaurant_data, category_ids

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
            "id": safe_get(
                row.get("UID")
            ),  # Use Excel UID as database ID for consistency
            "name": safe_get(row.get("Food Name"), "Unknown Food"),
            "description": safe_get(row.get("Description")),
            "price": price,
            "restaurant_id": restaurant_id,
        }

    def get_or_create_restaurant(self, restaurant_data: Dict[str, Any]) -> Restaurant:
        """Get existing restaurant or create new one."""
        # Try to find by Excel UID (now used as ID)
        restaurant_id = restaurant_data.get("id")
        if restaurant_id:
            existing = Restaurant.query.filter(Restaurant.id == restaurant_id).first()
            if existing:
                print(f"Found existing restaurant: {existing.name}")
                # Update existing restaurant data
                for key, value in restaurant_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                return existing

        # Create new restaurant with Excel UID as ID
        restaurant = Restaurant(**restaurant_data)
        db.session.add(restaurant)
        db.session.flush()  # Get ID without committing
        print(f"Created new restaurant: {restaurant.name}")
        return restaurant

    def get_or_create_food(
        self, food_data: Dict[str, Any], image_url: Optional[str] = None
    ) -> Food:
        """Get existing food or create new one."""
        # Try to find by Excel UID (now used as ID)
        food_id = food_data.get("id")
        if food_id:
            existing = Food.query.filter(Food.id == food_id).first()
            if existing:
                print(f"Found existing food: {existing.name}")
                # Update existing food data
                for key, value in food_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                return existing

        # Create new food with Excel UID as ID
        food = Food(**food_data)
        db.session.add(food)
        db.session.flush()  # Get ID without committing

        # Add image if provided
        if image_url and not pd.isna(image_url):
            food_image = FoodImage(
                food_id=food.id, image_url=str(image_url), is_main=True
            )
            db.session.add(food_image)

        print(f"Created food: {food.name}")
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
            categories_new = 0
            restaurants_new = 0
            restaurants_updated = 0
            foods_new = 0
            foods_updated = 0

            # Get outlets and foods sheets
            outlets_df = excel_data.get("Outlets", pd.DataFrame())
            foods_df = excel_data.get("Foods", pd.DataFrame())

            if outlets_df.empty:
                print("No outlets data found")
                return False

            # Step 1: Extract and create categories from Tags
            print(f"\n🏷️  Step 1: Processing categories...")
            category_map = self.extract_and_create_categories(outlets_df)
            print(
                f"✅ Categories processed successfully. Total categories in map: {len(category_map)}"
            )

            # Category count is handled in extract_and_create_categories method

            # Step 2: Create restaurants from outlets sheet
            print(f"\n🏪 Step 2: Processing {len(outlets_df)} restaurants...")
            restaurant_uid_map = {}  # Map UID to restaurant ID

            for _, outlet_row in outlets_df.iterrows():
                restaurant_data, category_ids = self.clean_restaurant_data(
                    outlet_row, category_map
                )

                # Check if restaurant exists before creating
                existing_restaurant = Restaurant.query.filter(
                    Restaurant.id == restaurant_data["id"]
                ).first()

                restaurant = self.get_or_create_restaurant(restaurant_data)

                # Add categories to restaurant (many-to-many)
                self.add_categories_to_restaurant(restaurant, category_ids)

                # Map UID to restaurant ID for foods import
                outlet_uid = outlet_row.get("UID")
                if outlet_uid:
                    restaurant_uid_map[outlet_uid] = restaurant.id

                # Count new vs updated restaurants
                if not existing_restaurant:
                    restaurants_new += 1
                else:
                    restaurants_updated += 1

            # Step 3: Create foods from foods sheet
            if not foods_df.empty:
                print(f"\n🍽️  Step 3: Processing {len(foods_df)} foods...")

                for _, food_row in foods_df.iterrows():
                    restaurant_uid = food_row.get("Restaurant UID")

                    if restaurant_uid not in restaurant_uid_map:
                        print(f"Warning: Restaurant UID {restaurant_uid} not found")
                        continue

                    restaurant_id = restaurant_uid_map[restaurant_uid]
                    food_data = self.clean_food_data(food_row, restaurant_id)

                    # Check if food exists before creating
                    existing_food = Food.query.filter(
                        Food.id == food_data["id"]
                    ).first()

                    # Use get_or_create_food which handles both new and existing foods by ID
                    image_url = food_row.get("Image URL")
                    food = self.get_or_create_food(food_data, image_url)

                    # Count new vs updated foods
                    if not existing_food:
                        foods_new += 1
                    else:
                        foods_updated += 1

            # Commit all changes
            db.session.commit()

            print(f"\n✅ Import completed successfully!")
            print(f"🏷️  Categories: processed {len(category_map)} unique categories")
            print(
                f"🏪 Restaurants: {restaurants_new} new, {restaurants_updated} updated"
            )
            print(f"🍽️  Foods: {foods_new} new, {foods_updated} updated")
            print(
                f"📊 Total processed: {restaurants_new + restaurants_updated} restaurants, {foods_new + foods_updated} foods"
            )

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
