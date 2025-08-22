"""
Cookie management utility.
Simple and clean cookie handling.
"""

import json
import logging
from typing import Dict, Optional
from pathlib import Path

from config.settings import paths


class CookieManager:
    """Manages cookie storage and retrieval."""

    def __init__(self, cookie_file: Optional[str] = None):
        if cookie_file:
            self.cookie_file = Path(cookie_file)
        else:
            self.cookie_file = paths.get_cookies_path()

        # Create settings directory if it doesn't exist
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def load_cookies(self) -> Optional[Dict[str, str]]:
        """Load cookies from file."""
        if not self.cookie_file.exists():
            self.logger.error(f"Cookie file {self.cookie_file} not found")
            return None

        try:
            with open(self.cookie_file, "r") as f:
                cookies = json.load(f)
            self.logger.info("Cookies loaded successfully")
            return cookies
        except Exception as e:
            self.logger.error(f"Error loading cookies: {e}")
            return None

    def save_cookies(self, cookies: Dict[str, str]) -> bool:
        """Save cookies to file."""
        try:
            with open(self.cookie_file, "w") as f:
                json.dump(cookies, f, indent=2)
            self.logger.info("Cookies saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving cookies: {e}")
            return False
