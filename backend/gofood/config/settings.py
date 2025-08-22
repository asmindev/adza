"""
GoFood API configuration.
Centralized configuration values.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path


@dataclass
class Paths:
    """File and folder paths configuration."""

    # Base project directory
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    # Logs directory
    logs_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "logs"
    )

    # Output directory for exports
    output_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "output"
    )

    # Config directory (for cookies and other config files)
    config_dir: Path = field(default_factory=lambda: Path(__file__).parent)

    # Default log file
    default_log_file: str = "gofood_scraper.log"

    # Default cookies file
    default_cookies_file: str = "cookies.json"

    def get_log_path(self, log_filename: Optional[str] = None) -> Path:
        """Get full path for log file."""
        filename = log_filename or self.default_log_file
        return self.logs_dir / filename

    def get_cookies_path(self, cookies_filename: Optional[str] = None) -> Path:
        """Get full path for cookies file."""
        filename = cookies_filename or self.default_cookies_file
        return self.config_dir / filename

    def get_output_path(self, output_filename: Optional[str] = None) -> Path:
        """Get full path for output file."""
        if output_filename:
            return self.output_dir / output_filename
        return self.output_dir


@dataclass
class APIConfig:
    """API configuration settings."""

    base_url: str = "https://gofood.co.id/api"
    timeout: int = 30
    page_size: str = "12"
    language: str = "en"
    timezone: str = "Asia/Makassar"
    country_code: str = "ID"

    # Default location (Makassar)
    default_location: Dict[str, float] = field(
        default_factory=lambda: {"latitude": -3.9984597, "longitude": 122.5129742}
    )


@dataclass
class Headers:
    """HTTP headers configuration."""

    @staticmethod
    def get_api_headers() -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    @staticmethod
    def get_html_headers() -> Dict[str, str]:
        """Get headers for HTML requests."""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }


# Global config instances
paths = Paths()
config = APIConfig()
