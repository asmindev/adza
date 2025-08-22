"""
Main GoFood scraper - simplified and clean.
Orchestrates the scraping workflow with minimal code.
"""

import logging
from typing import List, Optional

from core.models import Outlet, OutletDetails, ScrapingResult
from services.api_client import APIClient
from services.parser import DataParser
from utils.cookies import CookieManager
from utils.excel_export import ExcelExporter
from utils.helpers import DelayManager, setup_logging


class GoFoodScraper:
    """Main scraper orchestrator - clean and minimal."""

    def __init__(self, location: str, cookie_file: Optional[str] = None):
        """Initialize scraper with essential components."""
        self.location = location
        self.cookie_manager = CookieManager(cookie_file)
        self.parser = DataParser()
        self.exporter = ExcelExporter()
        self.delay_manager = DelayManager()
        self.logger = logging.getLogger(__name__)
        self.api: Optional[APIClient] = None

    def setup(self) -> bool:
        """Setup scraper (load cookies, initialize API)."""
        setup_logging()

        cookies = self.cookie_manager.load_cookies()
        if not cookies:
            self.logger.error("Failed to load cookies")
            return False

        self.api = APIClient(cookies, self.location)
        self.logger.info("Scraper setup completed")
        return True

    def scrape_outlets(self, max_pages: Optional[int] = None) -> ScrapingResult:
        """Scrape outlets with pagination."""
        if not self.api:
            raise ValueError("Scraper not initialized. Call setup() first.")

        outlets = []
        page_token = None
        page_count = 0

        while True:
            if max_pages and page_count >= max_pages:
                break

            response_data = self.api.get_outlets_page(page_token)
            if not response_data:
                break

            page_outlets = self.parser.parse_outlets(response_data)
            outlets.extend(page_outlets)

            page_token = response_data.get("nextPageToken")
            page_count += 1

            self.logger.info(f"Page {page_count}: Found {len(page_outlets)} outlets")

            if not page_token:
                break

            self.delay_manager.add_delay()

        filename = self.exporter.export_outlets(outlets) if outlets else None

        return ScrapingResult(
            outlets=outlets, total_count=len(outlets), export_filename=filename
        )

    def scrape_outlet_details(self, outlets: List[Outlet]) -> List[OutletDetails]:
        """Scrape detailed information for outlets."""
        if not self.api:
            raise ValueError("Scraper not initialized. Call setup() first.")
        print(f"Scraping details for {len(outlets)} outlets...")

        detailed_outlets = []

        for i, outlet in enumerate(outlets, 1):
            if not outlet.link:
                continue

            self.logger.info(
                f"Fetching details {i}/{len(outlets)}: {outlet.core.displayName}"
            )

            outlet_data = self.api.get_outlet_details(outlet.link)
            if outlet_data:
                details = self.parser.parse_outlet_details(outlet_data)
                if details:
                    detailed_outlets.append(details)

            self.delay_manager.add_delay()

        return detailed_outlets

    def export_detailed_data(self, outlet_details: List[OutletDetails]) -> str:
        """Export detailed outlet data to Excel."""
        return self.exporter.export_outlet_details(outlet_details)
