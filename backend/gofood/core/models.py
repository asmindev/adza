"""
Data models for GoFood scraper using dataclasses.
Minimal and clean structure.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class Location:
    """Geographical location."""

    latitude: float
    longitude: float


@dataclass
class Tag:
    """Outlet tag/category."""

    displayName: str
    id: Optional[str] = None


@dataclass
class Rating:
    """Rating information."""

    average: float


@dataclass
class Price:
    """Price information."""

    units: int
    currency: str = "IDR"


@dataclass
class OutletCore:
    """Core outlet information."""

    uid: str
    displayName: str
    rating: float = 0.0
    location: Optional[Location] = None
    tags: List[Tag] = field(default_factory=list)


@dataclass
class Outlet:
    """Complete outlet information."""

    core: OutletCore
    ratings: Optional[Rating] = None
    link: Optional[str] = None


@dataclass
class FoodItem:
    """Food item from catalog."""

    displayName: str
    price: Price
    description: Optional[str] = None
    imageUrl: Optional[str] = None


@dataclass
class OutletCatalog:
    """Outlet catalog."""

    sections: List[FoodItem] = field(default_factory=list)


@dataclass
class OutletDetails:
    """Complete outlet details."""

    core: OutletCore
    catalog: OutletCatalog
    ratings: Optional[Rating] = None


@dataclass
class APIResponse:
    """API response structure."""

    outlets: List[Outlet] = field(default_factory=list)
    nextPageToken: Optional[str] = None
    totalResults: Optional[int] = None


@dataclass
class ScrapingResult:
    """Scraping operation result."""

    outlets: List[Outlet]
    total_count: int
    export_filename: Optional[str] = None
