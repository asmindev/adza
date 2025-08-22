"""
Excel export utility.
Clean Excel file generation.
"""

import pandas as pd
import logging
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from core.models import Outlet, OutletDetails
from config.settings import paths


class ExcelExporter:
    """Exports data to Excel files."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def export_outlets(
        self, outlets: List[Outlet], filename: Optional[str] = None
    ) -> str:
        """Export outlets to Excel file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gofood_outlets_{timestamp}.xlsx"

        # Get full output path
        output_path = paths.get_output_path(filename)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = []
        for outlet in outlets:
            data.append(
                {
                    "UID": outlet.core.uid,
                    "Name": outlet.core.displayName,
                    "Average Rating": outlet.ratings.average if outlet.ratings else 0,
                    "Latitude": (
                        outlet.core.location.latitude if outlet.core.location else None
                    ),
                    "Longitude": (
                        outlet.core.location.longitude if outlet.core.location else None
                    ),
                    "Tags": ", ".join([tag.displayName for tag in outlet.core.tags]),
                    "Link": outlet.link,
                }
            )

        df = pd.DataFrame(data)

        try:
            df.to_excel(output_path, index=False)
            self.logger.info(f"Exported {len(outlets)} outlets to {output_path}")
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            raise

    def export_outlet_details(
        self, outlet_details: List[OutletDetails], filename: Optional[str] = None
    ) -> str:
        """Export detailed outlet information to Excel."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gofood_detailed_{timestamp}.xlsx"

        # Get full output path
        output_path = paths.get_output_path(filename)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        outlet_data = []
        food_data = []

        for detail in outlet_details:
            # Outlet data
            outlet_data.append(
                {
                    "UID": detail.core.uid,
                    "Name": detail.core.displayName,
                    "Rating": detail.core.rating,
                    "Average Rating": detail.ratings.average if detail.ratings else 0,
                    "Latitude": (
                        detail.core.location.latitude if detail.core.location else None
                    ),
                    "Longitude": (
                        detail.core.location.longitude if detail.core.location else None
                    ),
                    "Tags": ", ".join([tag.displayName for tag in detail.core.tags]),
                }
            )

            # Food data
            for item in detail.catalog.sections:
                food_data.append(
                    {
                        "Restaurant UID": detail.core.uid,
                        "Restaurant Name": detail.core.displayName,
                        "Food Name": item.displayName,
                        "Price": item.price.units,
                        "Currency": item.price.currency,
                        "Description": item.description,
                        "Image URL": item.imageUrl,
                    }
                )

        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                pd.DataFrame(outlet_data).to_excel(
                    writer, sheet_name="Outlets", index=False
                )
                pd.DataFrame(food_data).to_excel(
                    writer, sheet_name="Foods", index=False
                )

            self.logger.info(f"Exported detailed data to {output_path}")
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Error exporting detailed data to Excel: {e}")
            raise
