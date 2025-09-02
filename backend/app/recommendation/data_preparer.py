"""
Data Preparation Utilities
"""

import pandas as pd
from surprise import Dataset, Reader
from app.modules.rating.models import FoodRating
from app.utils import training_logger as logger
from typing import List, Tuple, Optional


class DataPreparer:
    @staticmethod
    def prepare_rating_data() -> Optional[Dataset]:
        """Prepare rating data for the recommendation algorithms"""
        try:
            # Get all ratings from the database
            ratings = FoodRating.query.all()

            if not ratings:
                logger.warning("Tidak ada data rating yang tersedia")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(
                [(r.user_id, r.food_id, r.rating) for r in ratings],
                columns=["user_id", "food_id", "rating"],
            )

            # Validate data
            if df.empty:
                logger.warning("DataFrame rating kosong")
                return None

            # Remove rows with null values
            df_clean = df.dropna()
            if len(df_clean) != len(df):
                logger.info(f"Removed {len(df) - len(df_clean)} rows with null values")

            # Check if we have enough ratings to make recommendations
            if len(df_clean) < 10:
                logger.warning(
                    f"Tidak cukup data rating untuk membuat rekomendasi (tersedia: {len(df_clean)}, minimum: 10)"
                )
                return None

            # Validate rating scale
            min_rating = df_clean["rating"].min()
            max_rating = df_clean["rating"].max()

            if min_rating < 1 or max_rating > 5:
                logger.warning(
                    f"Rating diluar skala 1-5: min={min_rating}, max={max_rating}"
                )
                # Clip ratings to valid range
                df_clean["rating"] = df_clean["rating"].clip(1, 5)

            # Check for unique users and items
            unique_users = df_clean["user_id"].nunique()
            unique_foods = df_clean["food_id"].nunique()

            logger.info(
                f"Dataset statistics: {len(df_clean)} ratings, {unique_users} users, {unique_foods} foods"
            )

            # Create a Surprise reader and dataset
            reader = Reader(rating_scale=(1, 5))
            dataset = Dataset.load_from_df(
                df_clean[["user_id", "food_id", "rating"]], reader
            )

            logger.debug(f"Dataset berhasil disiapkan dengan {len(df_clean)} rating")
            return dataset

        except Exception as e:
            logger.error(f"Error dalam prepare_rating_data: {str(e)}")
            return None

    @staticmethod
    def prepare_rating_data_from_tuples(
        enhanced_ratings: List[Tuple[str, str, float]],
    ) -> Optional[Dataset]:
        """
        Prepare rating data from enhanced ratings tuples for the recommendation algorithms

        Args:
            enhanced_ratings: List of tuples (user_id, food_id, adjusted_rating)

        Returns:
            Surprise Dataset object ready for training
        """
        try:
            if not enhanced_ratings:
                logger.warning("Enhanced ratings list kosong")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(
                enhanced_ratings,
                columns=["user_id", "food_id", "rating"],
            )

            # Validate data
            if df.empty:
                logger.warning("Enhanced ratings DataFrame kosong")
                return None

            # Remove rows with null values
            df_clean = df.dropna()
            if len(df_clean) != len(df):
                logger.info(
                    f"Removed {len(df) - len(df_clean)} enhanced rating rows with null values"
                )

            # Check if we have enough ratings to make recommendations
            if len(df_clean) < 10:
                logger.warning(
                    f"Tidak cukup enhanced rating untuk membuat rekomendasi (tersedia: {len(df_clean)}, minimum: 10)"
                )
                return None

            # Validate and clip rating scale
            df_clean["rating"] = df_clean["rating"].clip(1.0, 5.0)

            # Check for unique users and items
            unique_users = df_clean["user_id"].nunique()
            unique_foods = df_clean["food_id"].nunique()

            logger.info(
                f"Enhanced dataset statistics: {len(df_clean)} ratings, {unique_users} users, {unique_foods} foods"
            )

            # Create a Surprise reader and dataset
            reader = Reader(rating_scale=(1, 5))
            dataset = Dataset.load_from_df(
                df_clean[["user_id", "food_id", "rating"]], reader
            )

            logger.debug(
                f"Enhanced dataset berhasil disiapkan dengan {len(df_clean)} adjusted rating"
            )
            return dataset

        except Exception as e:
            logger.error(f"Error dalam prepare_rating_data_from_tuples: {str(e)}")
            return None

    @staticmethod
    def validate_rating_data(df: pd.DataFrame) -> bool:
        """
        Validate rating data quality

        Args:
            df: DataFrame with columns user_id, food_id, rating

        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check required columns
            required_columns = ["user_id", "food_id", "rating"]
            if not all(col in df.columns for col in required_columns):
                logger.error(
                    f"Missing required columns. Expected: {required_columns}, Got: {list(df.columns)}"
                )
                return False

            # Check for empty data
            if df.empty:
                logger.error("DataFrame is empty")
                return False

            # Check for null values
            null_counts = df.isnull().sum()
            if null_counts.any():
                logger.warning(f"Null values found: {null_counts.to_dict()}")

            # Check rating range
            ratings = df["rating"]
            if ratings.min() < 1 or ratings.max() > 5:
                logger.warning(
                    f"Ratings outside 1-5 range: min={ratings.min()}, max={ratings.max()}"
                )

            # Check for sufficient data diversity
            unique_users = df["user_id"].nunique()
            unique_items = df["food_id"].nunique()

            if unique_users < 2:
                logger.error(
                    f"Insufficient user diversity: {unique_users} unique users"
                )
                return False

            if unique_items < 2:
                logger.error(
                    f"Insufficient item diversity: {unique_items} unique items"
                )
                return False

            logger.info(
                f"Data validation passed: {len(df)} ratings, {unique_users} users, {unique_items} items"
            )
            return True

        except Exception as e:
            logger.error(f"Error in validate_rating_data: {str(e)}")
            return False
