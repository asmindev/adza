"""
Data parsing service.
Clean parser for outlet and food data.
"""

import logging
from typing import List, Dict, Any, Optional

from core.models import (
    Outlet,
    OutletCore,
    OutletDetails,
    OutletCatalog,
    FoodItem,
    Price,
    Location,
    Tag,
    Rating,
)


class DataParser:
    """Parses raw API data into structured models."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_outlets(self, api_response: Dict[str, Any]) -> List[Outlet]:
        """Parse outlets from API response."""
        outlets = []
        outlet_data = api_response.get("outlets", [])

        for outlet in outlet_data:
            try:
                parsed_outlet = self._parse_single_outlet(outlet)
                if parsed_outlet:
                    outlets.append(parsed_outlet)
            except Exception as e:
                self.logger.error(f"Error parsing outlet: {e}")
                continue

        return outlets

    def parse_outlet_details(
        self, outlet_data: Dict[str, Any]
    ) -> Optional[OutletDetails]:
        """Parse detailed outlet information."""
        try:
            core = self._extract_outlet_core(outlet_data["core"])
            catalog = self._extract_catalog(outlet_data)
            ratings = self._extract_ratings(outlet_data)

            return OutletDetails(core=core, catalog=catalog, ratings=ratings)
        except Exception as e:
            self.logger.error(f"Error parsing outlet details: {e}")
            return None

    def _parse_single_outlet(self, outlet_data: Dict[str, Any]) -> Optional[Outlet]:
        """Parse single outlet from API data."""
        core = self._extract_outlet_core(outlet_data["core"])
        ratings = self._extract_ratings(outlet_data)

        uid = core.uid if core else None
        name = core.displayName if core else None
        link = None
        if uid and name:
            # ganti semua karakter selain huruf, angka, spasi menjadi hyphen
            import re

            # https://gofood.co.id/en/kendari/restaurant/mixue-ahmad-yani-kendari-kec-wua-wua-d39c7812-c11e-424f-aada-b0af4e8759f8
            name = re.sub(r"[^\w\s]", "-", name.lower()).strip().replace(" ", "-")
            link = f"https://gofood.co.id/en/kendari/restaurant/{name}-{uid}"

        return Outlet(core=core, ratings=ratings, link=link)

    def _extract_outlet_core(self, outlet_data: Dict[str, Any]) -> OutletCore:
        """Extract core outlet information."""
        uid = outlet_data.get("uid", "")
        display_name = outlet_data.get("displayName", "")
        rating = outlet_data.get("rating", {}).get("average", 0.0)

        location = self._extract_location(outlet_data.get("location", {}))
        tags = self._extract_tags(outlet_data.get("tags", []))

        return OutletCore(
            uid=uid,
            displayName=display_name,
            rating=rating,
            location=location,
            tags=tags,
        )

    def _extract_location(self, location_data: Dict[str, Any]) -> Optional[Location]:
        """Extract location data."""
        if not location_data:
            return None

        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")

        if latitude is not None and longitude is not None:
            return Location(latitude=latitude, longitude=longitude)
        return None

    def _extract_tags(self, tags_data: List[Dict[str, Any]]) -> List[Tag]:
        """Extract tags data."""
        tags = []
        for tag_data in tags_data:
            display_name = tag_data.get("displayName")
            if display_name:
                tags.append(Tag(displayName=display_name, id=tag_data.get("id")))
        return tags

    def _extract_ratings(self, outlet_data: Dict[str, Any]) -> Optional[Rating]:
        """Extract rating data."""
        rating_data = outlet_data.get("ratings", {})
        average = rating_data.get("average")

        if average is not None:
            return Rating(average=average)
        return None

    def _extract_catalog(self, outlet_data: Dict[str, Any]) -> OutletCatalog:
        """Extract catalog data."""
        catalog_data = outlet_data.get("catalog", {})
        sections_data = catalog_data.get("sections", [])

        sections = []
        for section_data in sections_data:
            section = self._extract_catalog_section(section_data)
            if section:
                sections.extend(section)
        # remove duplicate food items with the same display name
        self.logger.info(f"Before deduplication: {len(sections)} items")
        sections = list({item.displayName: item for item in sections}.values())
        self.logger.info(f"After deduplication: {len(sections)} items")

        return OutletCatalog(sections=sections)

    def _extract_catalog_section(self, section_data: Dict[str, Any]) -> List[FoodItem]:
        """Extract catalog section."""

        items_data = section_data.get("items", [])
        items = []

        for item_data in items_data:
            item = self._extract_food_item(item_data)
            if item:
                items.append(item)
        return items

    def _extract_food_item(self, item_data: Dict[str, Any]) -> Optional[FoodItem]:
        """Extract food item."""
        print("\n\nExtracting food item:", item_data)
        display_name = item_data.get("displayName")
        price_data = item_data.get("price", {})

        if not display_name or not price_data:
            return None

        price = Price(
            units=price_data.get("units", 0), currency=price_data.get("currency", "IDR")
        )

        return FoodItem(
            id=item_data.get("uid"),
            displayName=display_name,
            price=price,
            description=item_data.get("description"),
            imageUrl=item_data.get("imageUrl"),
        )
