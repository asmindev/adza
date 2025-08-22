"""
Utility helpers.
"""

import time
import random
import logging
from typing import Optional

from config.settings import paths


class DelayManager:
    """Manages request delays to avoid rate limiting."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def add_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add random delay between requests."""
        delay = random.uniform(min_seconds, max_seconds)
        self.logger.debug(f"Adding delay of {delay:.2f} seconds")
        time.sleep(delay)


def setup_logging(log_file: Optional[str] = None):
    """Setup logging configuration."""
    # Use default log path if no file specified
    if log_file:
        log_path = paths.logs_dir / log_file
    else:
        log_path = paths.get_log_path()

    # Create logs directory if it doesn't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )
