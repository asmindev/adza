"""
GoFood Scraper - Clean and Minimal
Main exports for easy usage.
"""

from scraper import GoFoodScraper
from core.models import Outlet, OutletDetails, ScrapingResult
from utils.helpers import setup_logging

__version__ = "2.0.0"
__author__ = "GoFood Scraper Team"

__all__ = [
    "GoFoodScraper",
    "Outlet",
    "OutletDetails",
    "ScrapingResult",
    "setup_logging",
]
