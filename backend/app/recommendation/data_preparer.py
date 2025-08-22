"""
Data Preparation Utilities
"""

import pandas as pd
from surprise import Dataset, Reader
from app.modules.rating.models import FoodRating
from app.utils import training_logger as logger
from typing import List, Tuple


class DataPreparer:
    @staticmethod
    def prepare_rating_data():
        """Prepare rating data for the recommendation algorithms"""
        # Get all ratings from the database
        ratings = FoodRating.query.all()

        # Convert to DataFrame
        df = pd.DataFrame(
            [(r.user_id, r.food_id, r.rating) for r in ratings],
            columns=["user_id", "food_id", "rating"],
        )

        # Check if we have enough ratings to make recommendations
        if len(df) < 10:
            logger.warning(
                "Tidak cukup data rating untuk membuat rekomendasi (minimum 10)"
            )
            return None

        # Create a Surprise reader and dataset
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(df[["user_id", "food_id", "rating"]], reader)

        logger.debug(f"Dataset berhasil disiapkan dengan {len(df)} rating")
        return dataset

    @staticmethod
    def prepare_rating_data_from_tuples(enhanced_ratings: List[Tuple[str, str, float]]):
        """
        Prepare rating data from enhanced ratings tuples for the recommendation algorithms

        Args:
            enhanced_ratings: List of tuples (user_id, food_id, adjusted_rating)

        Returns:
            Surprise Dataset object ready for training
        """
        if not enhanced_ratings:
            logger.warning("Enhanced ratings list kosong")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(
            enhanced_ratings,
            columns=["user_id", "food_id", "rating"],
        )

        # Check if we have enough ratings to make recommendations
        if len(df) < 10:
            logger.warning(
                "Tidak cukup enhanced rating untuk membuat rekomendasi (minimum 10)"
            )
            return None

        # Create a Surprise reader and dataset
        reader = Reader(rating_scale=(1, 5))
        dataset = Dataset.load_from_df(df[["user_id", "food_id", "rating"]], reader)

        logger.debug(
            f"Enhanced dataset berhasil disiapkan dengan {len(df)} adjusted rating"
        )
        return dataset
