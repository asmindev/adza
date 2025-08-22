"""
Minimized GoFood API client.
Clean and focused on essential functionality.
"""

import requests
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import json

from config.settings import config, Headers


class APIClient:
    """Handles HTTP requests to GoFood API."""

    def __init__(self, cookies: Dict[str, str], location: str):
        """Initialize API client."""
        self.cookies = cookies
        self.location = location
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def get_outlets_page(
        self, page_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch outlets page from API."""
        data = {
            "code": "MOST_LOVED",
            "location": config.default_location,
            "pageSize": config.page_size,
            "pageToken": page_token,
            "language": config.language,
            "timezone": config.timezone,
            "country_code": config.country_code,
        }

        try:
            self.logger.info(f"Fetching outlets page with token: {page_token}")
            response = self.session.post(
                f"{config.base_url}/outlets",
                json=data,
                cookies=self.cookies,
                headers=Headers.get_api_headers(),
                timeout=config.timeout,
            )

            if response.status_code == 200:
                self.logger.info(f"Successfully fetched page")
                return response.json()
            else:
                self.logger.error(f"Failed to fetch page: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching outlets page: {e}")
            return None

    def get_outlet_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch outlet details from URL."""
        try:
            response = self.session.get(
                url,
                cookies=self.cookies,
                headers=Headers.get_html_headers(),
                timeout=config.timeout,
            )

            if response.status_code == 200:
                self.logger.info("Successfully fetched outlet details")
                return self._parse_outlet_html(response.text)
            else:
                self.logger.error(
                    f"Failed to fetch outlet details: {response.status_code}"
                )
                return None
        except Exception as e:
            self.logger.error(f"Error fetching outlet details: {e}")
            return None

    def _parse_outlet_html(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content to extract outlet data."""
        soup = BeautifulSoup(html_content, "html.parser")
        script = soup.find("script", {"id": "__NEXT_DATA__"})

        if not script:
            raise Exception("No __NEXT_DATA__ script found")

        data_json = json.loads(script.text)
        props = data_json.get("props", {}).get("pageProps", {})
        return props.get("outlet", {})
