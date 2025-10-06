"""
Local Data Preparation Module
Handles pivot matrix creation, user filtering, and sub-dataset preparation for SVD
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from app.utils.logger import get_logger
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.food.models import Food
from app.extensions import db
from .similarity import get_similar_users
from .config import RecommendationConfig

logger = get_logger(__name__)


class LocalDataProcessor:
    """
    Handles data preprocessing and sub-dataset creation for local SVD training
    with support for hybrid food+restaurant scoring
    """

    def __init__(
        self,
        min_user_ratings: int = 3,
        min_food_ratings: int = 1,
        alpha: Optional[float] = None,
    ):
        """
        Initialize data processor

        Args:
            min_user_ratings: Minimum number of ratings per user
            min_food_ratings: Minimum number of ratings per food item
            alpha: Weight for food vs restaurant rating (0-1). If None, uses config default
        """
        self.min_user_ratings = min_user_ratings
        self.min_food_ratings = min_food_ratings
        self.alpha = (
            alpha
            if alpha is not None
            else RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA
        )
        self.ratings_df = None
        self.user_item_matrix = None
        self.user_mapping = {}
        self.food_mapping = {}
        self.reverse_user_mapping = {}
        self.reverse_food_mapping = {}
        self.use_hybrid_scoring = True  # Flag to enable/disable hybrid scoring

    def load_ratings_from_db(self) -> pd.DataFrame:
        """
        Load ratings data from database into DataFrame

        Returns:
            pd.DataFrame: DataFrame with columns [user_id, food_id, rating]
        """
        try:
            # Query FoodRating table
            ratings_query = db.session.query(
                FoodRating.user_id, FoodRating.food_id, FoodRating.rating
            ).all()

            # Convert to DataFrame
            ratings_data = [
                {
                    "user_id": rating.user_id,
                    "food_id": rating.food_id,
                    "rating": rating.rating,
                }
                for rating in ratings_query
            ]

            df = pd.DataFrame(ratings_data)

            if len(df) > 0:
                logger.info(f"Raw ratings data sample:\n{df.head()}")
                df = df.groupby(["user_id", "food_id"])["rating"].mean().reset_index()

            logger.info(f"Loaded {len(df)} ratings from database")
            self.ratings_df = df
            return df

        except Exception as e:
            logger.error(f"Error loading ratings from database: {e}")
            return pd.DataFrame(columns=["user_id", "food_id", "rating"])

    def filter_sparse_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out users and foods with too few ratings

        Args:
            df: DataFrame with ratings data

        Returns:
            pd.DataFrame: Filtered DataFrame
        """
        try:
            initial_size = len(df)

            # Count ratings per user and food
            user_counts = df["user_id"].value_counts()
            food_counts = df["food_id"].value_counts()

            # Filter users with enough ratings
            valid_users = user_counts[user_counts >= self.min_user_ratings].index
            df_filtered = df[df["user_id"].isin(valid_users)]

            # Filter foods with enough ratings
            valid_foods = food_counts[food_counts >= self.min_food_ratings].index
            df_filtered = df_filtered[df_filtered["food_id"].isin(valid_foods)]

            # Iteratively filter until stable (users/foods might drop below threshold after filtering)
            prev_size = len(df_filtered)
            max_iterations = 5
            iteration = 0

            while iteration < max_iterations:
                user_counts = df_filtered["user_id"].value_counts()
                food_counts = df_filtered["food_id"].value_counts()

                valid_users = user_counts[user_counts >= self.min_user_ratings].index
                valid_foods = food_counts[food_counts >= self.min_food_ratings].index

                df_filtered = df_filtered[
                    df_filtered["user_id"].isin(valid_users)
                    & df_filtered["food_id"].isin(valid_foods)
                ]

                current_size = len(df_filtered)
                if current_size == prev_size:
                    break

                prev_size = current_size
                iteration += 1

            logger.info(f"Filtered data: {initial_size} -> {len(df_filtered)} ratings")
            logger.info(
                f"Users: {df['user_id'].nunique()} -> {df_filtered['user_id'].nunique()}"
            )
            logger.info(
                f"Foods: {df['food_id'].nunique()} -> {df_filtered['food_id'].nunique()}"
            )

            return df_filtered

        except Exception as e:
            logger.error(f"Error filtering sparse data: {e}")
            return df

    def create_pivot_matrix(
        self, df: pd.DataFrame, binary: bool = False
    ) -> pd.DataFrame:
        """
        Create user-item pivot matrix

        Args:
            df: DataFrame with ratings data
            binary: If True, convert ratings to binary (0/1)

        Returns:
            pd.DataFrame: Pivot matrix with users as rows and foods as columns
        """
        try:
            if binary:
                # Convert to binary (rated/not rated)
                df_binary = df.copy()
                df_binary["rating"] = 1
                pivot_matrix = df_binary.pivot_table(
                    index="user_id", columns="food_id", values="rating", fill_value=0
                )
            else:
                # Use actual ratings
                pivot_matrix = df.pivot_table(
                    index="user_id", columns="food_id", values="rating", fill_value=0
                )

            logger.info(f"Created pivot matrix: {pivot_matrix.shape}")
            self.user_item_matrix = pivot_matrix
            return pivot_matrix

        except Exception as e:
            logger.error(f"Error creating pivot matrix: {e}")
            return pd.DataFrame()

    def create_id_mappings(self, user_ids: List[str], food_ids: List[str]) -> None:
        """
        Create mappings between string IDs and integer indices

        Args:
            user_ids: List of user IDs
            food_ids: List of food IDs
        """
        # Create user mappings
        self.user_mapping = {user_id: idx for idx, user_id in enumerate(user_ids)}
        self.reverse_user_mapping = {
            idx: user_id for user_id, idx in self.user_mapping.items()
        }

        # Create food mappings
        self.food_mapping = {food_id: idx for idx, food_id in enumerate(food_ids)}
        self.reverse_food_mapping = {
            idx: food_id for food_id, idx in self.food_mapping.items()
        }

        logger.info(f"Created mappings: {len(user_ids)} users, {len(food_ids)} foods")

    def get_similar_users_subset(
        self,
        target_user_id: str,
        top_k: int = 50,
        similarity_method: str = "cosine",  # PERBAIKAN: Default ke cosine
        similarity_threshold: float = 0.2,  # PERBAIKAN: Threshold default lebih ketat
    ) -> List[str]:
        """
        Get subset of similar users for the target user

        Args:
            target_user_id: ID of target user
            top_k: Number of similar users to return
            similarity_method: Method for similarity calculation
            similarity_threshold: Minimum similarity threshold

        Returns:
            List[str]: List of similar user IDs
        """
        try:
            if self.ratings_df is None:
                logger.error("Ratings data not loaded")
                return []

            # Get similar users
            similar_users = get_similar_users(
                self.ratings_df,
                target_user_id,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                method=similarity_method,
            )

            # Extract user IDs
            similar_user_ids = [user_id for user_id, _ in similar_users]

            # Always include target user
            if target_user_id not in similar_user_ids:
                similar_user_ids.append(target_user_id)

            logger.info(
                f"Selected {len(similar_user_ids)} similar users for {target_user_id} using {similarity_method}"
            )
            return similar_user_ids

        except Exception as e:
            logger.error(f"Error getting similar users subset: {e}")
            return [target_user_id] if target_user_id else []

    def create_local_dataset(
        self,
        target_user_id: str,
        top_k_users: int = 50,
        similarity_method: str = "cosine",  # PERBAIKAN: Default ke cosine
        similarity_threshold: float = 0.3,  # PERBAIKAN: Threshold default lebih ketat
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create local sub-dataset for SVD training

        Args:
            target_user_id: ID of target user
            top_k_users: Number of similar users to include
            similarity_method: Method for similarity calculation
            similarity_threshold: Minimum similarity threshold

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (sub_ratings_df, sub_pivot_matrix)
        """
        try:
            # Load and filter data if not already done
            if self.ratings_df is None:
                self.load_ratings_from_db()

            if len(self.ratings_df) == 0:
                logger.error("No ratings data available")
                return pd.DataFrame(), pd.DataFrame()

            # Filter sparse data
            filtered_df = self.filter_sparse_data(self.ratings_df)

            if len(filtered_df) == 0:
                logger.error("No data remaining after filtering")
                return pd.DataFrame(), pd.DataFrame()

            # Check if target user exists in filtered data
            if target_user_id not in filtered_df["user_id"].values:
                logger.warning(
                    f"Target user {target_user_id} not found in filtered data"
                )
                # Return popular items as fallback data
                return self._get_fallback_data(filtered_df)

            # Get similar users
            similar_user_ids = self.get_similar_users_subset(
                target_user_id,
                top_k=top_k_users,
                similarity_method=similarity_method,
                similarity_threshold=similarity_threshold,
            )

            if len(similar_user_ids) < 2:
                logger.warning(f"Too few similar users found for {target_user_id}")
                return self._get_fallback_data(filtered_df)

            # Create sub-dataset with similar users
            sub_ratings_df = filtered_df[
                filtered_df["user_id"].isin(similar_user_ids)
            ].copy()

            if len(sub_ratings_df) == 0:
                logger.error("Empty sub-dataset after filtering similar users")
                return self._get_fallback_data(filtered_df)

            # Create pivot matrix for sub-dataset
            sub_pivot_matrix = self.create_pivot_matrix(sub_ratings_df)

            # Create ID mappings
            self.create_id_mappings(
                list(sub_pivot_matrix.index), list(sub_pivot_matrix.columns)
            )

            logger.info(
                f"Created local dataset: {len(sub_ratings_df)} ratings, "
                f"{sub_pivot_matrix.shape[0]} users, {sub_pivot_matrix.shape[1]} foods "
                f"(method: {similarity_method})"
            )

            return sub_ratings_df, sub_pivot_matrix

        except Exception as e:
            logger.error(f"Error creating local dataset: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def _get_fallback_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get fallback data when similar users cannot be found

        Args:
            df: Filtered ratings DataFrame

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (fallback_ratings_df, fallback_pivot_matrix)
        """
        try:
            # Take most active users as fallback
            user_activity = df["user_id"].value_counts().head(50)
            fallback_users = user_activity.index.tolist()

            fallback_df = df[df["user_id"].isin(fallback_users)].copy()
            fallback_pivot = self.create_pivot_matrix(fallback_df)

            logger.info(
                f"Created fallback dataset: {len(fallback_df)} ratings, "
                f"{fallback_pivot.shape[0]} users, {fallback_pivot.shape[1]} foods"
            )

            return fallback_df, fallback_pivot

        except Exception as e:
            logger.error(f"Error creating fallback data: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def get_user_rated_foods(self, user_id: str) -> List[str]:
        """
        Get list of foods already rated by user

        Args:
            user_id: User ID

        Returns:
            List[str]: List of food IDs rated by user
        """
        try:
            if self.ratings_df is None:
                return []

            user_ratings = self.ratings_df[self.ratings_df["user_id"] == user_id]
            return user_ratings["food_id"].tolist()

        except Exception as e:
            logger.error(f"Error getting user rated foods: {e}")
            return []

    def load_hybrid_ratings_from_db(self) -> pd.DataFrame:
        """
        Load hybrid ratings data combining food and restaurant ratings
        Formula: score = (alpha * food_rating) + ((1 - alpha) * restaurant_rating)
        Fallback to food ratings only if restaurant ratings are missing

        Returns:
            pd.DataFrame: DataFrame with columns [user_id, food_id, rating, has_restaurant_rating]
        """
        try:
            # Load food ratings
            food_ratings_query = (
                db.session.query(
                    FoodRating.user_id,
                    FoodRating.food_id,
                    FoodRating.rating,
                    Food.restaurant_id,
                )
                .join(Food, FoodRating.food_id == Food.id)
                .all()
            )

            if not food_ratings_query:
                logger.warning("No food ratings found in database")
                return pd.DataFrame(
                    columns=["user_id", "food_id", "rating", "has_restaurant_rating"]
                )

            # Load restaurant ratings
            restaurant_ratings_query = db.session.query(
                RestaurantRating.user_id,
                RestaurantRating.restaurant_id,
                RestaurantRating.rating,
            ).all()

            # Create restaurant ratings lookup
            restaurant_ratings_dict = {}
            for rating in restaurant_ratings_query:
                key = (rating.user_id, rating.restaurant_id)
                restaurant_ratings_dict[key] = rating.rating

            # Process hybrid ratings
            hybrid_ratings_data = []
            restaurant_coverage_count = 0

            for food_rating in food_ratings_query:
                user_id = food_rating.user_id
                food_id = food_rating.food_id
                food_rating_value = food_rating.rating
                restaurant_id = food_rating.restaurant_id

                # Look for corresponding restaurant rating
                restaurant_key = (user_id, restaurant_id)
                restaurant_rating_value = restaurant_ratings_dict.get(restaurant_key)

                if restaurant_rating_value is not None and self.use_hybrid_scoring:
                    # Calculate hybrid score
                    hybrid_score = (self.alpha * food_rating_value) + (
                        (1 - self.alpha) * restaurant_rating_value
                    )
                    has_restaurant_rating = True
                    restaurant_coverage_count += 1
                else:
                    # Fallback to food rating only
                    hybrid_score = food_rating_value
                    has_restaurant_rating = False

                hybrid_ratings_data.append(
                    {
                        "user_id": user_id,
                        "food_id": food_id,
                        "rating": hybrid_score,
                        "has_restaurant_rating": has_restaurant_rating,
                    }
                )

            df = pd.DataFrame(hybrid_ratings_data)

            restaurant_coverage = (
                (restaurant_coverage_count / len(hybrid_ratings_data)) * 100
                if hybrid_ratings_data
                else 0
            )

            if self.use_hybrid_scoring:
                logger.info(
                    f"Loaded {len(df)} hybrid ratings from database "
                    f"(Restaurant coverage: {restaurant_coverage:.1f}%, alpha: {self.alpha})"
                )
            else:
                logger.info(
                    f"Loaded {len(df)} food ratings from database (hybrid scoring disabled)"
                )

            self.ratings_df = df
            return df

        except Exception as e:
            logger.error(f"Error loading hybrid ratings from database: {e}")
            return pd.DataFrame(
                columns=["user_id", "food_id", "rating", "has_restaurant_rating"]
            )

    def set_alpha(self, alpha: float) -> None:
        """
        Set alpha parameter for hybrid scoring

        Args:
            alpha: Weight for food vs restaurant rating (0-1)
                  0 = 100% restaurant rating
                  1 = 100% food rating
        """
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")

        self.alpha = alpha
        logger.info(f"Alpha parameter set to {alpha}")

    def enable_hybrid_scoring(self, enable: bool = True) -> None:
        """
        Enable or disable hybrid scoring

        Args:
            enable: True to enable hybrid scoring, False to use food ratings only
        """
        self.use_hybrid_scoring = enable
        mode = "enabled" if enable else "disabled"
        logger.info(f"Hybrid scoring {mode}")

    def get_rating_statistics(self) -> Dict[str, float]:
        """
        Get statistics about the loaded ratings

        Returns:
            Dict with rating statistics
        """
        if self.ratings_df is None or len(self.ratings_df) == 0:
            return {}

        stats = {
            "total_ratings": len(self.ratings_df),
            "avg_rating": self.ratings_df["rating"].mean(),
            "min_rating": self.ratings_df["rating"].min(),
            "max_rating": self.ratings_df["rating"].max(),
            "std_rating": self.ratings_df["rating"].std(),
            "unique_users": self.ratings_df["user_id"].nunique(),
            "unique_foods": self.ratings_df["food_id"].nunique(),
        }

        if "has_restaurant_rating" in self.ratings_df.columns:
            restaurant_coverage = self.ratings_df["has_restaurant_rating"].mean() * 100
            stats["restaurant_coverage_percent"] = restaurant_coverage

        return stats
