"""
Recommendation System Orchestrator
Main interface class for the recommendation system
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import time
from app.utils.logger import get_logger
from app.modules.rating.models import FoodRating

logger = get_logger(__name__)
from app.modules.food.models import Food
from app.modules.user.models import User
from app.extensions import db

from .config import RecommendationConfig
from .local_data import LocalDataProcessor
from .local_model import LocalSVDModel
from .similarity import validate_similarity_calculation


class Recommendations:
    """
    Main recommendation system class with hybrid food+restaurant scoring
    Provides the public interface: recommend(user_id, top_n, alpha)
    """

    def __init__(self, alpha: Optional[float] = None):
        """
        Initialize the recommendation system

        Args:
            alpha: Weight for food vs restaurant rating (0-1). If None, uses config default
        """
        self.alpha = (
            alpha
            if alpha is not None
            else RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA
        )
        self.data_processor = LocalDataProcessor(alpha=self.alpha)
        self.svd_model = LocalSVDModel()
        self.is_initialized = False
        self.last_data_load = 0
        self.cache_duration = 3600  # 1 hour cache
        self.use_hybrid_scoring = True

        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "successful_recommendations": 0,
            "avg_processing_time": 0.0,
            "hybrid_coverage": 0.0,  # Average restaurant rating coverage
        }

    def _load_and_validate_data(self) -> bool:
        """
        Load and validate data from database (with hybrid scoring support)

        Returns:
            bool: True if data loaded successfully
        """
        try:
            # Check if we need to reload data
            current_time = time.time()
            if (
                current_time - self.last_data_load
            ) < self.cache_duration and self.is_initialized:
                return True

            logger.info("Loading ratings data from database...")

            # Load ratings data (hybrid or food-only)
            if self.use_hybrid_scoring:
                ratings_df = self.data_processor.load_hybrid_ratings_from_db()

                # Get hybrid coverage statistics
                if "has_restaurant_rating" in ratings_df.columns:
                    self.stats["hybrid_coverage"] = ratings_df[
                        "has_restaurant_rating"
                    ].mean()
                    logger.info(
                        f"Hybrid scoring active: alpha={self.alpha}, coverage={self.stats['hybrid_coverage']*100:.1f}%"
                    )
            else:
                ratings_df = self.data_processor.load_ratings_from_db()
                logger.info("Using food ratings only")

            if len(ratings_df) == 0:
                logger.error("No ratings data found in database")
                return False

            # Validate data quality
            if not self._validate_data_quality(ratings_df):
                logger.error("Data quality validation failed")
                return False

            # Validate similarity calculations on a sample
            if not validate_similarity_calculation(ratings_df, sample_size=3):
                logger.warning(
                    "Similarity calculation validation failed, but continuing..."
                )

            self.last_data_load = current_time
            self.is_initialized = True

            logger.info(f"Data loaded successfully: {len(ratings_df)} ratings")
            return True

        except Exception as e:
            logger.error(f"Error loading and validating data: {e}")
            return False

    def _validate_data_quality(self, ratings_df: pd.DataFrame) -> bool:
        """
        Validate the quality of ratings data

        Args:
            ratings_df: DataFrame with ratings data

        Returns:
            bool: True if data quality is acceptable
        """
        try:
            # Basic data validation
            min_users = 2
            min_foods = 3
            min_ratings = 5

            n_users = ratings_df["user_id"].nunique()
            n_foods = ratings_df["food_id"].nunique()
            n_ratings = len(ratings_df)

            if n_users < min_users:
                logger.warning(f"Too few users: {n_users} < {min_users}")
                return False

            if n_foods < min_foods:
                logger.warning(f"Too few foods: {n_foods} < {min_foods}")
                return False

            if n_ratings < min_ratings:
                logger.warning(f"Too few ratings: {n_ratings} < {min_ratings}")
                return False

            # Check rating value ranges
            invalid_ratings = ratings_df[
                (ratings_df["rating"] < 1) | (ratings_df["rating"] > 5)
            ]
            if len(invalid_ratings) > 0:
                logger.warning(
                    f"Found {len(invalid_ratings)} invalid ratings (outside 1-5 range)"
                )

            # Check for data sparsity
            total_possible = n_users * n_foods
            sparsity = 1 - (n_ratings / total_possible)

            if sparsity > 0.999:
                logger.warning(f"Data is very sparse: {sparsity:.4f}")

            logger.info(
                f"Data quality check passed: {n_users} users, {n_foods} foods, "
                f"{n_ratings} ratings, sparsity: {sparsity:.4f}"
            )

            return True

        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            return False

    def _get_user_context(self, user_id: str) -> Dict[str, any]:
        """
        Get additional context about the user for recommendations

        Args:
            user_id: User ID

        Returns:
            Dict[str, any]: User context information
        """
        try:
            # Get user's rating history
            user_ratings = self.data_processor.get_user_rated_foods(user_id)

            # Get user's rating statistics
            if len(user_ratings) > 0:
                user_ratings_df = self.data_processor.ratings_df[
                    self.data_processor.ratings_df["user_id"] == user_id
                ]
                avg_rating = user_ratings_df["rating"].mean()
                rating_count = len(user_ratings_df)
            else:
                avg_rating = 0.0
                rating_count = 0

            context = {
                "rated_foods": user_ratings,
                "rating_count": rating_count,
                "avg_rating": avg_rating,
            }

            return context

        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {
                "rated_foods": [],
                "rating_count": 0,
                "avg_rating": 0.0,
            }

    def recommend(self, user_id: str, top_n: int = 5) -> List[str]:
        """
        Generate recommendations for a user (returns only food IDs for backward compatibility)

        Args:
            user_id: User ID to generate recommendations for
            top_n: Number of recommendations to return (1-50)

        Returns:
            List[str]: List of recommended food IDs, empty if no recommendations
        """
        # Get detailed recommendations
        detailed_recs = self.recommend_with_scores(user_id, top_n)

        # Extract only food IDs for backward compatibility
        return [rec["food_id"] for rec in detailed_recs]

    def recommend_with_scores(
        self, user_id: str, top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate detailed recommendations for a user with predicted ratings

        Args:
            user_id: User ID to generate recommendations for
            top_n: Number of recommendations to return (1-50)

        Returns:
            List[Dict]: List of recommendation dicts with food_id and predicted_rating
                Example: [{"food_id": "abc", "predicted_rating": 4.5, "rank": 1}, ...]
        """
        start_time = time.time()

        try:
            # Validate input parameters
            if not user_id:
                logger.error("User ID cannot be empty")
                return []

            top_n = max(
                RecommendationConfig.MIN_RECOMMENDATIONS,
                min(top_n, RecommendationConfig.MAX_RECOMMENDATIONS),
            )

            self.stats["total_requests"] += 1

            logger.info(f"Generating recommendations for user {user_id}, top_n={top_n}")

            # Load and validate data
            if not self._load_and_validate_data():
                logger.error("Failed to load or validate data")
                return []

            # Get user context
            user_context = self._get_user_context(user_id)
            exclude_foods = user_context["rated_foods"]

            # Create local dataset with similar users
            try:
                sub_ratings_df, sub_pivot_matrix = (
                    self.data_processor.create_local_dataset(
                        target_user_id=user_id,
                        top_k_users=50,
                        similarity_method="cosine",
                        similarity_threshold=0.2,
                    )
                )

                if sub_pivot_matrix.empty:
                    logger.warning("Empty pivot matrix, no recommendations available")
                    return []

            except Exception as e:
                logger.error(f"Error creating local dataset: {e}")
                return []

            # Train SVD model on local dataset
            try:
                if not self.svd_model.fit(sub_pivot_matrix):
                    logger.warning("SVD training failed, no recommendations available")
                    return []

            except Exception as e:
                logger.error(f"Error training SVD model: {e}")
                return []

            # Get user index in the local dataset
            try:
                user_idx = self.data_processor.user_mapping.get(user_id)
                if user_idx is None:
                    logger.warning(f"User {user_id} not found in local dataset mapping")
                    return []

            except Exception as e:
                logger.error(f"Error getting user index: {e}")
                return []

            # Get item indices to exclude
            exclude_item_indices = []
            for food_id in exclude_foods:
                item_idx = self.data_processor.food_mapping.get(food_id)
                if item_idx is not None:
                    exclude_item_indices.append(item_idx)

            # Generate recommendations using SVD
            try:
                recommendations = self.svd_model.get_top_recommendations(
                    user_idx=user_idx,
                    top_n=top_n,
                    exclude_items=exclude_item_indices,
                    min_rating=RecommendationConfig.MIN_RATING_THRESHOLD,
                )

                if len(recommendations) == 0:
                    logger.warning("No SVD recommendations generated")
                    return []

            except Exception as e:
                logger.error(f"Error generating SVD recommendations: {e}")
                return []

            # Convert item indices to food IDs with predicted ratings
            detailed_recommendations = []
            for rank, (item_idx, predicted_rating) in enumerate(recommendations, 1):
                food_id = self.data_processor.reverse_food_mapping.get(item_idx)
                if food_id and food_id not in exclude_foods:
                    detailed_recommendations.append(
                        {
                            "food_id": food_id,
                            "predicted_rating": round(float(predicted_rating), 3),
                            "rank": rank,
                        }
                    )

            # Update statistics
            processing_time = time.time() - start_time
            self.stats["successful_recommendations"] += 1
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_requests"] - 1)
                + processing_time
            ) / self.stats["total_requests"]

            logger.info(
                f"Generated {len(detailed_recommendations)} recommendations for user {user_id} "
                f"in {processing_time:.3f}s"
            )

            return detailed_recommendations

        except Exception as e:
            logger.error(f"Error in recommend_with_scores method: {e}")
            processing_time = time.time() - start_time
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_requests"] - 1)
                + processing_time
            ) / self.stats["total_requests"]
            return []

    def get_recommendation_explanation(
        self, user_id: str, recommended_food_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Get explanation for why foods were recommended

        Args:
            user_id: User ID
            recommended_food_ids: List of recommended food IDs

        Returns:
            Dict[str, any]: Explanation information
        """
        try:
            user_context = self._get_user_context(user_id)

            explanation = {
                "method": "collaborative_filtering_svd",
                "user_profile": {
                    "total_ratings": user_context["rating_count"],
                    "average_rating": round(user_context["avg_rating"], 2),
                },
                "recommendations": len(recommended_food_ids),
                "model_info": (
                    self.svd_model.get_model_info() if self.svd_model.is_fitted else {}
                ),
            }

            return explanation

        except Exception as e:
            logger.error(f"Error generating recommendation explanation: {e}")
            return {"error": str(e)}

    def get_system_stats(self) -> Dict[str, any]:
        """
        Get system statistics and performance metrics

        Returns:
            Dict[str, any]: System statistics
        """
        try:
            success_rate = (
                self.stats["successful_recommendations"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0
                else 0
            )

            system_stats = {
                "total_requests": self.stats["total_requests"],
                "successful_recommendations": self.stats["successful_recommendations"],
                "success_rate": round(success_rate, 3),
                "avg_processing_time": round(self.stats["avg_processing_time"], 3),
                "is_initialized": self.is_initialized,
                "cache_age": (
                    time.time() - self.last_data_load if self.last_data_load > 0 else 0
                ),
            }

            # Add data statistics if available
            if self.data_processor.ratings_df is not None:
                df = self.data_processor.ratings_df
                system_stats["data_stats"] = {
                    "total_ratings": len(df),
                    "unique_users": df["user_id"].nunique(),
                    "unique_foods": df["food_id"].nunique(),
                    "avg_rating": round(df["rating"].mean(), 2),
                    "rating_distribution": df["rating"].value_counts().to_dict(),
                }

            return system_stats

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
