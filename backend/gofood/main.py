"""
Simple main entry point for GoFood scraper.
Clean and minimal usage example.
"""

import argparse
import sys
from scraper import GoFoodScraper
from import_to_db import GoFoodDBImporter


def scrape_data(location: str, max_pages: int = 5, max_details: int = 10):
    """Scrape data from GoFood API."""
    # Initialize scraper
    scraper = GoFoodScraper(location)

    # Setup (load cookies, initialize API)
    if not scraper.setup():
        print("Failed to setup scraper")
        return None

    # Scrape outlets (basic information)
    print("Scraping outlets...")
    result = scraper.scrape_outlets(max_pages=max_pages)

    print(f"Found {result.total_count} outlets")
    if result.export_filename:
        print(f"Basic data exported to: {result.export_filename}")

    # Scrape detailed information (optional)
    print("Scraping detailed information...")
    detailed_data = scraper.scrape_outlet_details(result.outlets[:max_details])

    if detailed_data:
        filename = scraper.export_detailed_data(detailed_data)
        print(f"Detailed data exported to: {filename}")
        return filename

    return None


def import_to_database(file_path: str | None = None, preview_only: bool = False):
    """Import Excel data to database."""
    importer = GoFoodDBImporter()

    if preview_only:
        importer.preview_data(file_path)
        return True
    else:
        return importer.import_data(file_path)


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description="GoFood Scraper and Database Importer")
    parser.add_argument(
        "--db",
        action="store_true",
        help="Import Excel data to database (from latest gofood_detailed file)",
    )
    parser.add_argument(
        "--file", "-f", help="Specific Excel file to import to database"
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Preview Excel data without importing",
    )
    parser.add_argument(
        "--location",
        "-l",
        default="YOUR_LOCATION_BASE64",
        help="Location in base64 format for scraping",
    )
    parser.add_argument(
        "--max-pages", type=int, default=5, help="Maximum pages to scrape (default: 5)"
    )
    parser.add_argument(
        "--max-details",
        type=int,
        default=10,
        help="Maximum outlets to get detailed info (default: 10)",
    )

    args = parser.parse_args()

    # Check if user wants to import to database
    if args.db or args.preview or args.file:
        print("🗄️  Database import mode")

        file_path = args.file
        preview_only = args.preview

        success = import_to_database(file_path, preview_only)

        if preview_only:
            return
        elif success:
            print("✅ Import to database completed successfully!")
        else:
            print("❌ Import to database failed!")
            sys.exit(1)
    else:
        # Default scraping mode
        print("🕸️  Scraping mode")

        if args.location == "YOUR_LOCATION_BASE64":
            print(
                "⚠️  Warning: Using default location. Please provide --location parameter"
            )
            print("   You can get location from GoFood app network requests")

        filename = scrape_data(args.location, args.max_pages, args.max_details)

        if filename:
            print(f"\n💡 To import this data to database, run:")
            print(f"   python main.py --db --file {filename}")
            print(f"   or just: python main.py --db  (to use latest file)")


if __name__ == "__main__":
    main()
