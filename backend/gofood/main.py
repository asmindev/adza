"""
Simple main entry point for GoFood scraper.
Clean and minimal usage example.
"""

from scraper import GoFoodScraper


def main():
    """Main entry point - simple and clean."""
    # Configuration
    location = "YOUR_LOCATION_BASE64"  # Replace with actual location

    # Initialize scraper
    scraper = GoFoodScraper(location)

    # Setup (load cookies, initialize API)
    if not scraper.setup():
        print("Failed to setup scraper")
        return

    # Scrape outlets (basic information)
    print("Scraping outlets...")
    result = scraper.scrape_outlets(max_pages=5)  # Limit to 5 pages

    print(f"Found {result.total_count} outlets")
    if result.export_filename:
        print(f"Basic data exported to: {result.export_filename}")

    # Scrape detailed information (optional)
    print("Scraping detailed information...")
    detailed_data = scraper.scrape_outlet_details(
        result.outlets[:10]
    )  # First 10 outlets

    if detailed_data:
        filename = scraper.export_detailed_data(detailed_data)
        print(f"Detailed data exported to: {filename}")


if __name__ == "__main__":
    main()
