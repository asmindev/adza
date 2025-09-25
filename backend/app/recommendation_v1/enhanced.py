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
            "fallback_recommendations": 0,
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
        self.data_processor.set_alpha(alpha)

        # Reset cache to reload data with new alpha
        self.is_initialized = False
        self.last_data_load = 0

        logger.info(f"Alpha parameter updated to {alpha}")

    def enable_hybrid_scoring(self, enable: bool = True) -> None:
        """
        Enable or disable hybrid scoring

        Args:
            enable: True to enable hybrid scoring, False to use food ratings only
        """
        self.use_hybrid_scoring = enable
        self.data_processor.enable_hybrid_scoring(enable)

        # Reset cache to reload data with new settings
        self.is_initialized = False
        self.last_data_load = 0

        mode = "enabled" if enable else "disabled"
        logger.info(f"Hybrid scoring {mode}")

    def get_hybrid_info(self) -> Dict[str, any]:
        """
        Get information about hybrid scoring configuration

        Returns:
            Dict with hybrid scoring information
        """
        return {
            "hybrid_scoring_enabled": self.use_hybrid_scoring,
            "alpha": self.alpha,
            "restaurant_coverage": self.stats.get("hybrid_coverage", 0.0),
            "formula": f"score = ({self.alpha} * food_rating) + ({1-self.alpha} * restaurant_rating)",
        }

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
                "is_new_user": rating_count < 3,
            }

            return context

        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {
                "rated_foods": [],
                "rating_count": 0,
                "avg_rating": 0.0,
                "is_new_user": True,
            }

    def _get_fallback_recommendations(
        self, user_id: str, top_n: int, exclude_foods: List[str] = None
    ) -> List[str]:
        """
        Get fallback recommendations when SVD approach fails

        Args:
            user_id: User ID
            top_n: Number of recommendations to return
            exclude_foods: Foods to exclude

        Returns:
            List[str]: List of recommended food IDs
        """
        try:
            logger.info(f"Using fallback recommendations for user {user_id}")

            # Get popular foods as fallback
            popular_foods = self.data_processor.get_popular_foods(
                top_n=top_n * 2,  # Get more to allow for filtering
                exclude_foods=exclude_foods,
            )

            # Limit to requested number
            fallback_recommendations = popular_foods[:top_n]

            self.stats["fallback_recommendations"] += 1

            logger.info(
                f"Generated {len(fallback_recommendations)} fallback recommendations"
            )
            return fallback_recommendations

        except Exception as e:
            logger.error(f"Error generating fallback recommendations: {e}")
            return []

    def recommend(self, user_id: str, top_n: int = 5) -> List[str]:
        """
        Generate recommendations for a user

        Args:
            user_id: User ID to generate recommendations for
            top_n: Number of recommendations to return (1-50)

        Returns:
            List[str]: List of recommended food IDs
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

            # Handle new users with few ratings
            if user_context["is_new_user"]:
                logger.info(
                    f"New user detected ({user_context['rating_count']} ratings), using fallback"
                )
                return self._get_fallback_recommendations(user_id, top_n, exclude_foods)

            # Create local dataset with similar users - PERBAIKAN: Default ke cosine untuk fokus pola rating
            try:
                sub_ratings_df, sub_pivot_matrix = (
                    self.data_processor.create_local_dataset(
                        target_user_id=user_id,
                        top_k_users=50,
                        similarity_method="cosine",  # PERBAIKAN: Ganti dari jaccard ke cosine
                        similarity_threshold=0.2,  # PERBAIKAN: Threshold lebih ketat untuk cosine
                    )
                )

                if sub_pivot_matrix.empty:
                    logger.warning("Empty pivot matrix, using fallback recommendations")
                    return self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )

            except Exception as e:
                logger.error(f"Error creating local dataset: {e}")
                return self._get_fallback_recommendations(user_id, top_n, exclude_foods)

            # Train SVD model on local dataset
            try:
                if not self.svd_model.fit(sub_pivot_matrix):
                    logger.warning(
                        "SVD training failed, using fallback recommendations"
                    )
                    return self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )

            except Exception as e:
                logger.error(f"Error training SVD model: {e}")
                return self._get_fallback_recommendations(user_id, top_n, exclude_foods)

            # Get user index in the local dataset
            try:
                user_idx = self.data_processor.user_mapping.get(user_id)
                if user_idx is None:
                    logger.warning(f"User {user_id} not found in local dataset mapping")
                    return self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )

            except Exception as e:
                logger.error(f"Error getting user index: {e}")
                return self._get_fallback_recommendations(user_id, top_n, exclude_foods)

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
                    top_n=top_n * 2,  # Get more candidates
                    exclude_items=exclude_item_indices,
                    min_rating=3.0,
                )

                if len(recommendations) == 0:
                    logger.warning("No SVD recommendations generated, using fallback")
                    return self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )

            except Exception as e:
                logger.error(f"Error generating SVD recommendations: {e}")
                return self._get_fallback_recommendations(user_id, top_n, exclude_foods)

            # Convert item indices back to food IDs
            recommended_food_ids = []
            for item_idx, predicted_rating in recommendations:
                food_id = self.data_processor.reverse_food_mapping.get(item_idx)
                if food_id and food_id not in exclude_foods:
                    recommended_food_ids.append(food_id)

                if len(recommended_food_ids) >= top_n:
                    break

            # If we don't have enough recommendations, supplement with popular foods
            if len(recommended_food_ids) < top_n:
                additional_needed = top_n - len(recommended_food_ids)
                exclude_all = exclude_foods + recommended_food_ids

                additional_foods = self.data_processor.get_popular_foods(
                    top_n=additional_needed, exclude_foods=exclude_all
                )

                recommended_food_ids.extend(additional_foods)

            # Final trim to requested number
            final_recommendations = recommended_food_ids[:top_n]

            # Update statistics
            processing_time = time.time() - start_time
            self.stats["successful_recommendations"] += 1
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_requests"] - 1)
                + processing_time
            ) / self.stats["total_requests"]

            logger.info(
                f"Generated {len(final_recommendations)} recommendations for user {user_id} "
                f"in {processing_time:.3f}s"
            )

            return final_recommendations

        except Exception as e:
            logger.error(f"Error in recommend method: {e}")
            processing_time = time.time() - start_time
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_requests"] - 1)
                + processing_time
            ) / self.stats["total_requests"]
            return []

    def recommend_with_scores(
        self, user_id: str, top_n: int = 5
    ) -> Tuple[List[str], Dict[str, float]]:
        """
        Generate recommendations for a user with predicted scores

        Args:
            user_id: User ID to generate recommendations for
            top_n: Number of recommendations to return (1-50)

        Returns:
            Tuple[List[str], Dict[str, float]]: (food_ids, {food_id: predicted_rating})
        """
        start_time = time.time()

        try:
            # Validate input parameters
            if not user_id:
                logger.error("User ID cannot be empty")
                return [], {}

            top_n = max(
                RecommendationConfig.MIN_RECOMMENDATIONS,
                min(top_n, RecommendationConfig.MAX_RECOMMENDATIONS),
            )

            self.stats["total_requests"] += 1

            logger.info(
                f"Generating recommendations with scores for user {user_id}, top_n={top_n}"
            )

            # Load and validate data
            if not self._load_and_validate_data():
                logger.error("Failed to load or validate data")
                return [], {}

            # Get user context
            user_context = self._get_user_context(user_id)
            exclude_foods = user_context["rated_foods"]

            # Handle new users with few ratings (fallback doesn't have predicted scores)
            if user_context["is_new_user"]:
                logger.info(
                    f"New user detected ({user_context['rating_count']} ratings), using fallback"
                )
                fallback_foods = self._get_fallback_recommendations(
                    user_id, top_n, exclude_foods
                )
                # PERBAIKAN: Fallback scores dynamic pakai global_mean
                fallback_scores = {
                    food_id: float(self.svd_model.global_mean)
                    for food_id in fallback_foods
                }
                return fallback_foods, fallback_scores

            # Create local dataset with similar users - PERBAIKAN: Sama seperti recommend, default cosine
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
                    logger.warning("Empty pivot matrix, using fallback recommendations")
                    fallback_foods = self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )
                    fallback_scores = {
                        food_id: float(self.svd_model.global_mean)
                        for food_id in fallback_foods
                    }
                    return fallback_foods, fallback_scores

            except Exception as e:
                logger.error(f"Error creating local dataset: {e}")
                fallback_foods = self._get_fallback_recommendations(
                    user_id, top_n, exclude_foods
                )
                fallback_scores = {
                    food_id: float(self.svd_model.global_mean)
                    for food_id in fallback_foods
                }
                return fallback_foods, fallback_scores

            # Train SVD model on local dataset
            try:
                if not self.svd_model.fit(sub_pivot_matrix):
                    logger.warning(
                        "SVD training failed, using fallback recommendations"
                    )
                    fallback_foods = self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )
                    fallback_scores = {
                        food_id: float(self.svd_model.global_mean)
                        for food_id in fallback_foods
                    }
                    return fallback_foods, fallback_scores

            except Exception as e:
                logger.error(f"Error training SVD model: {e}")
                fallback_foods = self._get_fallback_recommendations(
                    user_id, top_n, exclude_foods
                )
                fallback_scores = {
                    food_id: float(self.svd_model.global_mean)
                    for food_id in fallback_foods
                }
                return fallback_foods, fallback_scores

            # Get user index in the local dataset
            try:
                user_idx = self.data_processor.user_mapping.get(user_id)
                if user_idx is None:
                    logger.warning(f"User {user_id} not found in local dataset mapping")
                    fallback_foods = self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )
                    fallback_scores = {
                        food_id: float(self.svd_model.global_mean)
                        for food_id in fallback_foods
                    }
                    return fallback_foods, fallback_scores

            except Exception as e:
                logger.error(f"Error getting user index: {e}")
                fallback_foods = self._get_fallback_recommendations(
                    user_id, top_n, exclude_foods
                )
                fallback_scores = {
                    food_id: float(self.svd_model.global_mean)
                    for food_id in fallback_foods
                }
                return fallback_foods, fallback_scores

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
                    top_n=top_n * 2,  # Get more candidates
                    exclude_items=exclude_item_indices,
                    min_rating=3.0,
                )

                if len(recommendations) == 0:
                    logger.warning("No SVD recommendations generated, using fallback")
                    fallback_foods = self._get_fallback_recommendations(
                        user_id, top_n, exclude_foods
                    )
                    fallback_scores = {
                        food_id: float(self.svd_model.global_mean)
                        for food_id in fallback_foods
                    }
                    return fallback_foods, fallback_scores

            except Exception as e:
                logger.error(f"Error generating SVD recommendations: {e}")
                fallback_foods = self._get_fallback_recommendations(
                    user_id, top_n, exclude_foods
                )
                fallback_scores = {
                    food_id: float(self.svd_model.global_mean)
                    for food_id in fallback_foods
                }
                return fallback_foods, fallback_scores

            # Convert item indices back to food IDs with scores
            recommended_food_ids = []
            predicted_scores = {}
            for item_idx, predicted_rating in recommendations:
                food_id = self.data_processor.reverse_food_mapping.get(item_idx)
                if food_id and food_id not in exclude_foods:
                    recommended_food_ids.append(food_id)
                    predicted_scores[food_id] = float(predicted_rating)

                if len(recommended_food_ids) >= top_n:
                    break

            # If we don't have enough recommendations, supplement with popular foods
            if len(recommended_food_ids) < top_n:
                additional_needed = top_n - len(recommended_food_ids)
                exclude_all = exclude_foods + recommended_food_ids

                additional_foods = self.data_processor.get_popular_foods(
                    top_n=additional_needed, exclude_foods=exclude_all
                )

                # Add scores for additional foods (use global mean)
                for food_id in additional_foods:
                    recommended_food_ids.append(food_id)
                    predicted_scores[food_id] = float(self.svd_model.global_mean)

            # Final trim to requested number
            final_recommendations = recommended_food_ids[:top_n]
            final_scores = {
                food_id: predicted_scores[food_id]
                for food_id in final_recommendations
                if food_id in predicted_scores
            }

            # Update statistics
            processing_time = time.time() - start_time
            self.stats["successful_recommendations"] += 1
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_requests"] - 1)
                + processing_time
            ) / self.stats["total_requests"]

            logger.info(
                f"Generated {len(final_recommendations)} recommendations with scores for user {user_id} "
                f"in {processing_time:.3f}s"
            )

            return final_recommendations, final_scores

        except Exception as e:
            logger.error(f"Error in recommend_with_scores method: {e}")
            processing_time = time.time() - start_time
            self.stats["avg_processing_time"] = (
                self.stats["avg_processing_time"] * (self.stats["total_requests"] - 1)
                + processing_time
            ) / self.stats["total_requests"]
            return [], {}

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
                    "is_new_user": user_context["is_new_user"],
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

            fallback_rate = (
                self.stats["fallback_recommendations"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0
                else 0
            )

            system_stats = {
                "total_requests": self.stats["total_requests"],
                "successful_recommendations": self.stats["successful_recommendations"],
                "fallback_recommendations": self.stats["fallback_recommendations"],
                "success_rate": round(success_rate, 3),
                "fallback_rate": round(fallback_rate, 3),
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

    def validate_recommendations(
        self, user_id: str, recommended_food_ids: List[str]
    ) -> bool:
        """
        Validate that recommended foods exist and are accessible

        Args:
            user_id: User ID
            recommended_food_ids: List of recommended food IDs

        Returns:
            bool: True if recommendations are valid
        """
        try:
            if not recommended_food_ids:
                return True  # Empty list is valid

            # Check if foods exist in database
            existing_foods = (
                db.session.query(Food.id)
                .filter(Food.id.in_(recommended_food_ids))
                .all()
            )

            existing_food_ids = {food.id for food in existing_foods}

            # Check for missing foods
            missing_foods = set(recommended_food_ids) - existing_food_ids

            if missing_foods:
                logger.warning(
                    f"Recommended foods not found in database: {missing_foods}"
                )
                return False

            # Check if user hasn't already rated these foods
            user_rated_foods = set(self.data_processor.get_user_rated_foods(user_id))
            already_rated = set(recommended_food_ids).intersection(user_rated_foods)

            if already_rated:
                logger.warning(
                    f"Recommended foods already rated by user: {already_rated}"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating recommendations: {e}")
            return False


"""
Recommendation Service
Public API for the recommendation system
"""

from typing import List, Dict, Optional, Any
from app.utils.logger import get_logger
from app.utils.response import success_response, error_response
from app.modules.food.models import Food
from app.modules.user.models import User
from app.extensions import db

from .recommender import Recommendations
from .config import RecommendationConfig

# Setup logger
logger = get_logger(__name__)


class RecommendationService:
    """
    Service layer for recommendation system
    Provides clean API interface for the application
    """

    def __init__(self):
        """Initialize recommendation service"""
        self.recommender = Recommendations()
        RecommendationConfig.initialize()

    def get_recommendations(
        self,
        user_id: str,
        top_n: int = RecommendationConfig.DEFAULT_RECOMMENDATIONS,
        include_details: bool = True,
    ) -> Any:
        """
        Get food recommendations for a user

        Args:
            user_id: User ID to get recommendations for
            top_n: Number of recommendations to return
            include_details: Whether to include food details in response

        Returns:
            Dict[str, any]: Response with recommendations
        """
        try:
            # Validate input
            if not user_id:
                return error_response("User ID is required", 400)

            # Validate user exists
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                return error_response("User not found", 404)

            # Validate top_n parameter
            if top_n < RecommendationConfig.MIN_RECOMMENDATIONS:
                top_n = RecommendationConfig.MIN_RECOMMENDATIONS
            elif top_n > RecommendationConfig.MAX_RECOMMENDATIONS:
                top_n = RecommendationConfig.MAX_RECOMMENDATIONS

            logger.info(f"Getting {top_n} recommendations for user {user_id}")

            # Get recommendations
            recommended_food_ids = self.recommender.recommend(user_id, top_n)

            if not recommended_food_ids:
                return success_response(
                    {
                        "recommendations": [],
                        "count": 0,
                        "message": "No recommendations available at this time",
                    }
                )

            # Validate recommendations
            if not self.recommender.validate_recommendations(
                user_id, recommended_food_ids
            ):
                logger.warning(f"Recommendation validation failed for user {user_id}")
                # Try to get fallback recommendations
                recommended_food_ids = self.recommender._get_fallback_recommendations(
                    user_id,
                    top_n,
                    self.recommender._get_user_context(user_id)["rated_foods"],
                )

            # Prepare response
            response_data = {
                "recommendations": recommended_food_ids,
                "count": len(recommended_food_ids),
                "user_id": user_id,
            }

            # Include food details if requested
            if include_details and recommended_food_ids:
                food_details = self._get_food_details(recommended_food_ids)
                response_data["food_details"] = food_details

            # Include explanation if available
            explanation = self.recommender.get_recommendation_explanation(
                user_id, recommended_food_ids
            )
            if explanation and "error" not in explanation:
                response_data["explanation"] = explanation

            logger.info(
                f"Successfully generated {len(recommended_food_ids)} recommendations for user {user_id}"
            )

            return success_response(response_data)

        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {e}")
            return error_response(f"Failed to get recommendations: {str(e)}", 500)

    def _get_food_details(self, food_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information about foods

        Args:
            food_ids: List of food IDs

        Returns:
            List[Dict[str, any]]: List of food details
        """
        try:
            foods = db.session.query(Food).filter(Food.id.in_(food_ids)).all()

            # Maintain order based on input list
            food_dict = {food.id: food for food in foods}
            ordered_foods = [
                food_dict[food_id] for food_id in food_ids if food_id in food_dict
            ]

            food_details = []
            for food in ordered_foods:
                food_data = (
                    food.to_dict()
                    if hasattr(food, "to_dict")
                    else {
                        "id": food.id,
                        "name": food.name if hasattr(food, "name") else "Unknown",
                        "description": (
                            food.description if hasattr(food, "description") else ""
                        ),
                        "price": food.price if hasattr(food, "price") else 0,
                    }
                )
                food_details.append(food_data)

            return food_details

        except Exception as e:
            logger.error(f"Error getting food details: {e}")
            return []

    def get_popular_foods(
        self, top_n: int = RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
    ) -> Any:
        """
        Get most popular foods (most rated)

        Args:
            top_n: Number of popular foods to return

        Returns:
            Dict[str, any]: Response with popular foods
        """
        try:
            # Validate top_n parameter
            if top_n < 1:
                top_n = RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
            elif top_n > RecommendationConfig.MAX_RECOMMENDATIONS:
                top_n = RecommendationConfig.MAX_RECOMMENDATIONS

            logger.info(f"Getting {top_n} popular foods")

            # Load data if needed
            if not self.recommender._load_and_validate_data():
                return error_response("Unable to load recommendation data", 500)

            # Get popular foods
            popular_food_ids = self.recommender.data_processor.get_popular_foods(top_n)

            if not popular_food_ids:
                return success_response(
                    {
                        "popular_foods": [],
                        "count": 0,
                        "message": "No popular foods available",
                    }
                )

            # Get food details
            food_details = self._get_food_details(popular_food_ids)

            response_data = {
                "popular_foods": popular_food_ids,
                "food_details": food_details,
                "count": len(popular_food_ids),
            }

            logger.info(f"Successfully retrieved {len(popular_food_ids)} popular foods")

            return success_response(response_data)

        except Exception as e:
            logger.error(f"Error getting popular foods: {e}")
            return error_response(f"Failed to get popular foods: {str(e)}", 500)

    def get_user_profile(self, user_id: str) -> Any:
        """
        Get user's rating profile and preferences

        Args:
            user_id: User ID

        Returns:
            Dict[str, any]: User profile information
        """
        try:
            # Validate user exists
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                return error_response("User not found", 404)

            logger.info(f"Getting profile for user {user_id}")

            # Load data if needed
            if not self.recommender._load_and_validate_data():
                return error_response("Unable to load recommendation data", 500)

            # Get user context
            user_context = self.recommender._get_user_context(user_id)

            # Get rated foods details
            rated_food_details = []
            if user_context["rated_foods"]:
                rated_food_details = self._get_food_details(user_context["rated_foods"])

            profile_data = {
                "user_id": user_id,
                "rating_stats": {
                    "total_ratings": user_context["rating_count"],
                    "average_rating": round(user_context["avg_rating"], 2),
                    "is_new_user": user_context["is_new_user"],
                },
                "rated_foods": user_context["rated_foods"],
                "rated_food_details": rated_food_details,
            }

            logger.info(f"Successfully retrieved profile for user {user_id}")

            return success_response(profile_data)

        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            return error_response(f"Failed to get user profile: {str(e)}", 500)

    def get_system_status(self) -> Any:
        """
        Get recommendation system status and statistics

        Returns:
            Dict[str, any]: System status information
        """
        try:
            logger.info("Getting recommendation system status")

            # Get system statistics
            stats = self.recommender.get_system_stats()

            # Add configuration information
            status_data = {
                "system_stats": stats,
                "configuration": {
                    "min_recommendations": RecommendationConfig.MIN_RECOMMENDATIONS,
                    "max_recommendations": RecommendationConfig.MAX_RECOMMENDATIONS,
                    "default_recommendations": RecommendationConfig.DEFAULT_RECOMMENDATIONS,
                    "svd_n_factors": RecommendationConfig.SVD_N_FACTORS,
                    "svd_n_epochs": RecommendationConfig.SVD_N_EPOCHS,
                },
                "health": {
                    "status": (
                        "healthy"
                        if stats.get("is_initialized", False)
                        else "initializing"
                    ),
                    "data_available": stats.get("data_stats", {}).get(
                        "total_ratings", 0
                    )
                    > 0,
                },
            }

            return success_response(status_data)

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return error_response(f"Failed to get system status: {str(e)}", 500)

    def refresh_recommendations(self) -> Any:
        """
        Force refresh of recommendation data and models

        Returns:
            Dict[str, any]: Refresh status
        """
        try:
            logger.info("Refreshing recommendation system")

            # Reset data processor and model
            self.recommender.data_processor = type(self.recommender.data_processor)()
            self.recommender.svd_model = type(self.recommender.svd_model)()
            self.recommender.is_initialized = False
            self.recommender.last_data_load = 0

            # Load fresh data
            success = self.recommender._load_and_validate_data()

            if success:
                logger.info("Recommendation system refreshed successfully")
                return success_response(
                    {
                        "message": "Recommendation system refreshed successfully",
                        "timestamp": self.recommender.last_data_load,
                    }
                )
            else:
                logger.error("Failed to refresh recommendation system")
                return error_response("Failed to refresh recommendation system", 500)

        except Exception as e:
            logger.error(f"Error refreshing recommendations: {e}")
            return error_response(f"Failed to refresh recommendations: {str(e)}", 500)


# Create singleton instance
recommendation_service = RecommendationService()


"""
Local SVD Model Module
Handles SVD training on sub-matrix and prediction of missing ratings
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix
import warnings
from app.utils.logger import get_logger
from .config import RecommendationConfig

logger = get_logger(__name__)


class LocalSVDModel:
    """
    Local SVD model for collaborative filtering on user sub-datasets
    """

    def __init__(self, n_components: int = None, random_state: int = None):
        """
        Initialize SVD model

        Args:
            n_components: Number of latent factors (default from config)
            random_state: Random state for reproducibility (default from config)
        """
        self.n_components = n_components or RecommendationConfig.SVD_N_FACTORS
        self.random_state = random_state or RecommendationConfig.SVD_RANDOM_STATE

        self.svd_model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.user_factors = None
        self.item_factors = None
        self.global_mean = 0.0
        self.user_means = None
        self.item_means = None

        # Metadata
        self.n_users = 0
        self.n_items = 0
        self.sparsity = 0.0

    def _prepare_matrix(
        self, pivot_matrix: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare matrix for SVD training with mean centering

        Args:
            pivot_matrix: User-item pivot matrix

        Returns:
            Tuple[np.ndarray, np.ndarray]: (centered_matrix, original_matrix)
        """
        try:
            # Convert to numpy array
            matrix = pivot_matrix.values.astype(np.float32)

            # Calculate means
            self.global_mean = np.mean(matrix[matrix > 0])

            # Calculate user means (excluding zeros)
            user_means = []
            for i in range(matrix.shape[0]):
                user_ratings = matrix[i][matrix[i] > 0]
                user_mean = (
                    np.mean(user_ratings) if len(user_ratings) > 0 else self.global_mean
                )
                user_means.append(user_mean)
            self.user_means = np.array(user_means)

            # Calculate item means (excluding zeros)
            item_means = []
            for j in range(matrix.shape[1]):
                item_ratings = matrix[:, j][matrix[:, j] > 0]
                item_mean = (
                    np.mean(item_ratings) if len(item_ratings) > 0 else self.global_mean
                )
                item_means.append(item_mean)
            self.item_means = np.array(item_means)

            # Center the matrix (subtract user and item biases)
            centered_matrix = matrix.copy()
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    if matrix[i, j] > 0:
                        # Subtract global mean, user bias, and item bias
                        user_bias = self.user_means[i] - self.global_mean
                        item_bias = self.item_means[j] - self.global_mean
                        centered_matrix[i, j] = (
                            matrix[i, j] - self.global_mean - user_bias - item_bias
                        )

            return centered_matrix, matrix

        except Exception as e:
            logger.error(f"Error preparing matrix for SVD: {e}")
            return matrix, matrix

    def fit(self, pivot_matrix: pd.DataFrame) -> bool:
        """
        Train SVD model on pivot matrix

        Args:
            pivot_matrix: User-item pivot matrix

        Returns:
            bool: True if training successful
        """
        try:
            if pivot_matrix.empty:
                logger.error("Empty pivot matrix provided for SVD training")
                return False

            self.n_users, self.n_items = pivot_matrix.shape

            # Calculate sparsity
            total_possible = self.n_users * self.n_items
            actual_ratings = (pivot_matrix.values > 0).sum()
            self.sparsity = 1 - (actual_ratings / total_possible)

            logger.info(
                f"Training SVD on matrix: {self.n_users} users x {self.n_items} items, "
                f"sparsity: {self.sparsity:.3f}"
            )

            # Prepare matrix
            centered_matrix, original_matrix = self._prepare_matrix(pivot_matrix)

            # PERBAIKAN: Auto-adjust n_components berdasarkan sparsity untuk akurasi lebih baik
            max_components = min(self.n_components, min(self.n_users, self.n_items) - 1)
            if self.sparsity > 0.95:
                max_components = min(
                    50, max_components
                )  # Kurangi factors jika very sparse
            if max_components <= 0:
                logger.error("Invalid number of components for SVD")
                return False

            # Initialize SVD model
            self.svd_model = TruncatedSVD(
                n_components=max_components,
                random_state=self.random_state,
                algorithm="randomized",
                n_iter=5,
            )

            # Handle very sparse matrices
            if self.sparsity > 0.99:
                logger.warning(
                    f"Very sparse matrix (sparsity: {self.sparsity:.3f}), using alternative approach"
                )
                # For very sparse matrices, use original ratings without centering
                training_matrix = original_matrix
            else:
                training_matrix = centered_matrix

            # Fit SVD model
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # Replace NaN and inf values
                training_matrix = np.nan_to_num(
                    training_matrix, nan=0.0, posinf=0.0, neginf=0.0
                )

                # Fit the model
                user_factors = self.svd_model.fit_transform(training_matrix)
                item_factors = self.svd_model.components_.T

                self.user_factors = user_factors
                self.item_factors = item_factors
                self.is_fitted = True

                # PERBAIKAN: Early stopping jika explained variance rendah
                explained_var = self.svd_model.explained_variance_ratio_.sum()
                if explained_var < 0.5:
                    logger.warning(
                        f"Low explained variance: {explained_var:.3f}, model may be inaccurate"
                    )

            logger.info(
                f"SVD training completed: {max_components} factors, "
                f"explained variance ratio: {explained_var:.3f}"
            )

            return True

        except Exception as e:
            logger.error(f"Error training SVD model: {e}")
            self.is_fitted = False
            return False

    def predict_user_item(
        self, user_idx: int, item_idx: int, common_items: int = 0
    ) -> float:
        """
        Predict rating for specific user-item pair - PERBAIKAN: Tambah confidence berdasarkan common_items

        Args:
            user_idx: User index
            item_idx: Item index
            common_items: Number of common items for confidence weighting

        Returns:
            float: Predicted rating
        """
        try:
            if not self.is_fitted:
                logger.error("SVD model not fitted")
                return self.global_mean

            # Check bounds
            if user_idx >= self.n_users or item_idx >= self.n_items:
                logger.warning(f"Index out of bounds: user {user_idx}, item {item_idx}")
                return self.global_mean

            # Calculate prediction using latent factors
            user_vector = self.user_factors[user_idx]
            item_vector = self.item_factors[item_idx]

            # Dot product of latent factors
            prediction = np.dot(user_vector, item_vector)

            # Add biases back
            user_bias = self.user_means[user_idx] - self.global_mean
            item_bias = self.item_means[item_idx] - self.global_mean
            prediction += self.global_mean + user_bias + item_bias

            # PERBAIKAN: Weight by confidence jika common_items diketahui (untuk pola rating akurat)
            if common_items > 0:
                confidence_weight = min(
                    1.0, np.sqrt(common_items / 5.0)
                )  # Normalize ke max 5 common
                prediction = self.global_mean + confidence_weight * (
                    prediction - self.global_mean
                )

            # Clip to valid rating range (1-5)
            prediction = np.clip(prediction, 1.0, 5.0)

            return float(prediction)

        except Exception as e:
            logger.error(f"Error predicting user-item rating: {e}")
            return self.global_mean

    def predict_for_user(
        self, user_idx: int, exclude_items: List[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Predict ratings for all items for a specific user

        Args:
            user_idx: User index
            exclude_items: List of item indices to exclude

        Returns:
            List[Tuple[int, float]]: List of (item_idx, predicted_rating) tuples
        """
        try:
            if not self.is_fitted:
                logger.error("SVD model not fitted")
                return []

            exclude_items = exclude_items or []
            predictions = []

            for item_idx in range(self.n_items):
                if item_idx in exclude_items:
                    continue

                # PERBAIKAN: Asumsi common_items=0 jika tidak diketahui; bisa pass dari external jika ada
                predicted_rating = self.predict_user_item(
                    user_idx, item_idx, common_items=0
                )
                predictions.append((item_idx, predicted_rating))

            # Sort by predicted rating (descending)
            predictions.sort(key=lambda x: x[1], reverse=True)

            return predictions

        except Exception as e:
            logger.error(f"Error predicting for user: {e}")
            return []

    def get_top_recommendations(
        self,
        user_idx: int,
        top_n: int = 10,
        exclude_items: List[int] = None,
        min_rating: float = 3.0,
    ) -> List[Tuple[int, float]]:
        """
        Get top-N recommendations for user

        Args:
            user_idx: User index
            top_n: Number of recommendations to return
            exclude_items: List of item indices to exclude
            min_rating: Minimum predicted rating threshold

        Returns:
            List[Tuple[int, float]]: List of (item_idx, predicted_rating) tuples
        """
        try:
            # Get all predictions for user
            predictions = self.predict_for_user(user_idx, exclude_items)

            # Filter by minimum rating
            filtered_predictions = [
                (item_idx, rating)
                for item_idx, rating in predictions
                if rating >= min_rating
            ]

            # Return top N
            top_recommendations = filtered_predictions[:top_n]

            logger.info(
                f"Generated {len(top_recommendations)} recommendations for user {user_idx}"
            )
            return top_recommendations

        except Exception as e:
            logger.error(f"Error getting top recommendations: {e}")
            return []

    def evaluate_model(self, test_matrix: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance on test data - PERBAIKAN: Fix bug exclude_items undefined

        Args:
            test_matrix: Test user-item matrix

        Returns:
            Dict[str, float]: Evaluation metrics
        """
        try:
            if not self.is_fitted:
                logger.error("SVD model not fitted")
                return {}

            predictions = []
            actuals = []

            # Get predictions for test data
            for i in range(min(test_matrix.shape[0], self.n_users)):
                for j in range(min(test_matrix.shape[1], self.n_items)):
                    actual_rating = test_matrix.iloc[i, j]
                    if actual_rating > 0:  # Only evaluate on known ratings
                        predicted_rating = self.predict_user_item(i, j)
                        predictions.append(predicted_rating)
                        actuals.append(actual_rating)

            if len(predictions) == 0:
                logger.warning("No test predictions to evaluate")
                return {}

            # Calculate metrics
            predictions = np.array(predictions)
            actuals = np.array(actuals)

            mae = np.mean(np.abs(predictions - actuals))
            mse = np.mean((predictions - actuals) ** 2)
            rmse = np.sqrt(mse)

            # PERBAIKAN: Coverage berdasarkan actual recommended items / total
            n_recommendable = len([p for p in predictions if p >= 3.0])
            coverage = n_recommendable / self.n_items if self.n_items > 0 else 0.0

            metrics = {
                "mae": float(mae),
                "mse": float(mse),
                "rmse": float(rmse),
                "coverage": float(coverage),
                "n_predictions": len(predictions),
            }

            logger.info(
                f"Model evaluation: MAE={mae:.3f}, RMSE={rmse:.3f}, Coverage={coverage:.3f}"
            )
            return metrics

        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {}

    def get_model_info(self) -> Dict[str, any]:
        """
        Get information about the trained model

        Returns:
            Dict[str, any]: Model information
        """
        try:
            if not self.is_fitted:
                return {"fitted": False}

            info = {
                "fitted": True,
                "n_components": self.svd_model.n_components,
                "n_users": self.n_users,
                "n_items": self.n_items,
                "sparsity": self.sparsity,
                "global_mean": self.global_mean,
                "explained_variance_ratio": self.svd_model.explained_variance_ratio_.sum(),
                "total_explained_variance": float(
                    self.svd_model.explained_variance_ratio_.sum()
                ),
            }

            return info

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {"fitted": False, "error": str(e)}


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

            if len(df) == 0:
                logger.warning("No ratings found in database")
                return pd.DataFrame(columns=["user_id", "food_id", "rating"])

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
        similarity_threshold: float = 0.2,
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

    def get_popular_foods(
        self, top_n: int = 20, exclude_foods: List[str] = None
    ) -> List[str]:
        """
        Get most popular foods (most rated) as fallback recommendations

        Args:
            top_n: Number of popular foods to return
            exclude_foods: Foods to exclude from results

        Returns:
            List[str]: List of popular food IDs
        """
        try:
            # Load data if not already loaded
            if self.ratings_df is None:
                if self.use_hybrid_scoring:
                    self.ratings_df = self.load_hybrid_ratings_from_db()
                else:
                    self.ratings_df = self.load_ratings_from_db()

                if self.ratings_df is None or len(self.ratings_df) == 0:
                    logger.warning("No ratings data available for popular foods")
                    return []

            exclude_foods = exclude_foods or []

            # Count ratings per food
            food_counts = self.ratings_df["food_id"].value_counts()

            # Filter out excluded foods
            if exclude_foods:
                food_counts = food_counts.drop(exclude_foods, errors="ignore")

            # Get top N popular foods
            popular_foods = []
            for i, (food_id, count) in enumerate(food_counts.items()):
                if i >= top_n:
                    break
                popular_foods.append(str(food_id))

            logger.info(f"Retrieved {len(popular_foods)} popular foods")
            return popular_foods

        except Exception as e:
            logger.error(f"Error getting popular foods: {e}")
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


"""
Recommendation System Configuration
"""

import os
import time
from app.utils import training_logger as logger


# Configuration class to hold all constants and paths
class RecommendationConfig:
    # Path to save trained models
    MODEL_PATH = "app/models/saved_models"
    SVD_MODEL_FILE = os.path.join(MODEL_PATH, "svd_model.pkl")
    LAST_TRAINING_FILE = os.path.join(MODEL_PATH, "last_training.txt")

    # Training interval (24 hours in seconds)
    TRAINING_INTERVAL = 24 * 60 * 60

    # PERBAIKAN: Hapus DEFAULT_ALPHA duplikat, gunakan ini saja
    DEFAULT_FOOD_RESTAURANT_ALPHA = 0.7  # Weight for food rating vs restaurant rating
    # score = (alpha * food_rating) + ((1 - alpha) * restaurant_rating)
    # alpha = 0.7 means 70% food, 30% restaurant
    # alpha = 0.0 means 100% restaurant
    # alpha = 1.0 means 100% food

    # API limits
    MIN_RECOMMENDATIONS = 1
    MAX_RECOMMENDATIONS = 50
    DEFAULT_RECOMMENDATIONS = 10
    DEFAULT_TOP_RATED_LIMIT = 10

    # SVD Model parameters
    SVD_N_FACTORS = 100
    SVD_N_EPOCHS = 20
    SVD_RANDOM_STATE = 42

    # Create model directory if it doesn't exist
    @staticmethod
    def initialize():
        os.makedirs(RecommendationConfig.MODEL_PATH, exist_ok=True)


from flask import Blueprint, request, g
from app.recommendation.recommender import Recommendations
from app.recommendation.config import RecommendationConfig
from app.utils import api_logger as logger
from app.utils.auth import token_required
from app.utils.response import ResponseHelper

recommendation_blueprint = Blueprint("recommendation", __name__)


@recommendation_blueprint.route("/recommendation", methods=["GET"])
@token_required
def get_recommendations():
    """Get personalized food recommendations using hybrid collaborative filtering"""
    # Get user_id from the request context from jwt token
    user_id = g.user_id

    logger.info(
        f"GET /recommendations - Permintaan rekomendasi makanan untuk user {user_id}"
    )

    # Get query parameters with config defaults
    limit = request.args.get(
        "limit", default=RecommendationConfig.DEFAULT_RECOMMENDATIONS, type=int
    )
    alpha = request.args.get(
        "alpha", default=RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA, type=float
    )
    enable_hybrid = (
        request.args.get("hybrid", default="true", type=str).lower() == "true"
    )

    logger.debug(f"Parameter: limit={limit}, alpha={alpha}, hybrid={enable_hybrid}")

    # Validate limit using config values
    if (
        limit < RecommendationConfig.MIN_RECOMMENDATIONS
        or limit > RecommendationConfig.MAX_RECOMMENDATIONS
    ):
        return ResponseHelper.validation_error(
            f"Limit must be between {RecommendationConfig.MIN_RECOMMENDATIONS} and {RecommendationConfig.MAX_RECOMMENDATIONS}"
        )

    # Validate alpha parameter (0.0 to 1.0)
    if not (0.0 <= alpha <= 1.0):
        return ResponseHelper.validation_error(
            "Alpha parameter must be between 0.0 and 1.0"
        )

    try:
        # PERBAIKAN: Gunakan singleton recommendation_service untuk efisiensi
        rec_system = recommendation_service.recommender

        # Set alpha dan hybrid config
        rec_system.set_alpha(alpha)
        rec_system.enable_hybrid_scoring(enable_hybrid)

        logger.info(
            f"Hybrid scoring: {'enabled' if enable_hybrid else 'disabled'}, alpha={alpha}"
        )

        # Generate recommendations using the new API with scores
        recommendations, predicted_scores = rec_system.recommend_with_scores(
            user_id=user_id, top_n=limit
        )

        if recommendations is None or len(recommendations) == 0:
            logger.warning(f"User {user_id} tidak ditemukan atau tidak ada rekomendasi")
            # Fallback to popular foods using the data processor
            popular_food_ids = rec_system.data_processor.get_popular_foods(top_n=limit)
            logger.info(f"Generated {len(popular_food_ids)} popular foods as fallback")

            if popular_food_ids:
                # Import utility functions
                from .utils import get_food_details_batch, format_foods_response

                # Get complete food details for fallback
                foods_data = get_food_details_batch(popular_food_ids)
                fallback_scores = {
                    food_id: float(rec_system.svd_model.global_mean)
                    for food_id in popular_food_ids
                }
                formatted_foods = format_foods_response(foods_data, fallback_scores)

                return ResponseHelper.success(
                    data={
                        "recommendations": formatted_foods,
                        "fallback": True,
                        "hybrid_info": rec_system.get_hybrid_info(),
                        "system_stats": rec_system.get_system_stats(),
                        "message": "Menggunakan makanan populer karena tidak ada rekomendasi personal",
                    }
                )
            else:
                return ResponseHelper.not_found("No recommendations available")

        # Import utility functions
        from .utils import get_food_details_batch, format_foods_response

        # Get complete food details for recommendations
        foods_data = get_food_details_batch(recommendations)
        if not foods_data:
            logger.warning("Failed to get food details for recommendations")
            return ResponseHelper.not_found("No food details found")

        # Format response with predicted ratings
        formatted_foods = format_foods_response(foods_data, predicted_scores)

        # Get additional information about the recommendation process
        hybrid_info = rec_system.get_hybrid_info()
        system_stats = rec_system.get_system_stats()

        logger.info(
            f"Mengembalikan {len(recommendations)} rekomendasi untuk user {user_id}"
        )
        logger.info(f"Hybrid info: {hybrid_info}")
        logger.info(
            f"Restaurant coverage: {system_stats.get('hybrid_coverage', 0)*100:.1f}%"
        )

        return ResponseHelper.success(
            data={
                "recommendations": formatted_foods,
                "fallback": False,
                "hybrid_info": hybrid_info,
                "system_stats": system_stats,
            }
        )

    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get recommendations")


# before : top-rated
@recommendation_blueprint.route("/popular", methods=["GET"])
def get_popular():
    """Get popular foods based on user ratings"""
    logger.info("GET /popular - Mengambil makanan populer berdasarkan rating pengguna")
    try:
        # Import utility function
        from .utils import get_food_details_batch, format_foods_response

        # PERBAIKAN: Gunakan singleton
        rec_system_top = recommendation_service.recommender
        top_rated_food_ids = rec_system_top.data_processor.get_popular_foods(
            top_n=RecommendationConfig.DEFAULT_TOP_RATED_LIMIT
        )
        if not top_rated_food_ids:
            logger.info("Tidak ada makanan teratas ditemukan")
            return ResponseHelper.not_found("No top-rated foods found")

        # Get complete food details
        foods_data = get_food_details_batch(top_rated_food_ids)
        if not foods_data:
            logger.warning("Failed to get food details for popular foods")
            return ResponseHelper.not_found("No food details found")

        # Format response as required
        formatted_foods = format_foods_response(foods_data)

        return ResponseHelper.success(data=formatted_foods)

    except Exception as e:
        logger.error(f"Error getting top-rated foods: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get top-rated foods")


@recommendation_blueprint.route("/hybrid-info", methods=["GET"])
def get_hybrid_info():
    """Get information about the hybrid scoring system"""
    logger.info("GET /hybrid-info - Mengambil informasi hybrid scoring system")
    try:
        # Get alpha parameter from query (optional)
        alpha = request.args.get(
            "alpha",
            default=RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA,
            type=float,
        )

        # Validate alpha parameter
        if not (0.0 <= alpha <= 1.0):
            return ResponseHelper.validation_error(
                "Alpha parameter must be between 0.0 and 1.0"
            )

        # PERBAIKAN: Gunakan singleton
        rec_system = recommendation_service.recommender
        rec_system.set_alpha(alpha)

        # Get hybrid info and system stats
        hybrid_info = rec_system.get_hybrid_info()
        system_stats = rec_system.get_system_stats()

        # Get rating statistics from data processor
        rating_stats = rec_system.data_processor.get_rating_statistics()

        return ResponseHelper.success(
            data={
                "hybrid_info": hybrid_info,
                "system_stats": system_stats,
                "rating_statistics": rating_stats,
                "config": {
                    "default_alpha": RecommendationConfig.DEFAULT_FOOD_RESTAURANT_ALPHA,
                    "min_recommendations": RecommendationConfig.MIN_RECOMMENDATIONS,
                    "max_recommendations": RecommendationConfig.MAX_RECOMMENDATIONS,
                    "default_recommendations": RecommendationConfig.DEFAULT_RECOMMENDATIONS,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting hybrid info: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to get hybrid info")


"""
User Similarity Calculation Module
Contains functions for calculating user similarity using Jaccard and Cosine metrics
"""

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine
from typing import Tuple, List, Dict
from app.utils.logger import get_logger

logger = get_logger(__name__)


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Calculate Jaccard similarity between two sets

    Args:
        set1: First set of items
        set2: Second set of items

    Returns:
        float: Jaccard similarity score (0-1)
    """
    if len(set1) == 0 and len(set2) == 0:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union > 0 else 0.0


def cosine_similarity_sparse(
    user_matrix: csr_matrix,
    target_user_idx: int,
    other_user_idx: int,
    common_items_mask: np.ndarray = None,
) -> float:
    """
    Calculate cosine similarity between two users in sparse matrix - PERBAIKAN: Subset ke common items

    Args:
        user_matrix: Sparse user-item matrix
        target_user_idx: Index of target user
        other_user_idx: Index of other user
        common_items_mask: Mask untuk common items (optional, untuk subset)

    Returns:
        float: Cosine similarity score (0-1)
    """
    try:
        user1_vector = user_matrix[target_user_idx].toarray().flatten()
        user2_vector = user_matrix[other_user_idx].toarray().flatten()

        # PERBAIKAN: Subset ke common items jika mask diberikan (fokus pola rating pada overlap)
        if common_items_mask is not None:
            user1_vector = user1_vector[common_items_mask]
            user2_vector = user2_vector[common_items_mask]
            logger.debug(
                f"Cosine calculated on {np.sum(common_items_mask)} common items"
            )

        # Handle zero vectors
        if np.all(user1_vector == 0) or np.all(user2_vector == 0):
            return 0.0

        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(user1_vector, user2_vector)

        # Handle NaN results
        return similarity if not np.isnan(similarity) else 0.0

    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


def calculate_user_similarities(
    ratings_df: pd.DataFrame,
    target_user_id: str,
    method: str = "cosine",  # PERBAIKAN: Default ke cosine
    min_common_items: int = 2,
) -> Dict[str, float]:
    """
    Calculate similarities between target user and all other users - PERBAIKAN: Enhance cosine dengan common mask

    Args:
        ratings_df: DataFrame with columns [user_id, food_id, rating]
        target_user_id: ID of the target user
        method: Similarity method ('jaccard' or 'cosine')
        min_common_items: Minimum number of common items required

    Returns:
        Dict[str, float]: Dictionary mapping user_id to similarity score
    """
    try:
        # Check if target user exists
        if target_user_id not in ratings_df["user_id"].values:
            logger.warning(f"Target user {target_user_id} not found in ratings data")
            return {}

        similarities = {}

        if method == "jaccard":
            # Get target user's rated foods
            target_foods = set(
                ratings_df[ratings_df["user_id"] == target_user_id]["food_id"]
            )

            # Calculate Jaccard similarity with each other user
            for user_id in ratings_df["user_id"].unique():
                if user_id == target_user_id:
                    continue

                user_foods = set(
                    ratings_df[ratings_df["user_id"] == user_id]["food_id"]
                )

                # Check minimum common items
                common_items = len(target_foods.intersection(user_foods))
                if common_items < min_common_items:
                    continue

                similarity = jaccard_similarity(target_foods, user_foods)
                if similarity > 0:
                    similarities[user_id] = similarity

        elif method == "cosine":
            # Create user-item matrix
            user_item_matrix = ratings_df.pivot(
                index="user_id", columns="food_id", values="rating"
            ).fillna(0)

            # Convert to sparse matrix
            sparse_matrix = csr_matrix(user_item_matrix.values)

            # Get target user index
            try:
                target_idx = user_item_matrix.index.get_loc(target_user_id)
            except KeyError:
                logger.warning(
                    f"Target user {target_user_id} not found in pivot matrix"
                )
                return {}

            # Calculate cosine similarity with each other user
            for idx, user_id in enumerate(user_item_matrix.index):
                if user_id == target_user_id:
                    continue

                # Check if users have enough common ratings
                target_ratings = user_item_matrix.iloc[target_idx]
                user_ratings = user_item_matrix.iloc[idx]
                common_mask = ((target_ratings > 0) & (user_ratings > 0)).values
                common_items = np.sum(common_mask)

                if common_items < min_common_items:
                    continue

                # PERBAIKAN: Pass common_mask ke cosine untuk subset calculation
                similarity = cosine_similarity_sparse(
                    sparse_matrix, target_idx, idx, common_mask
                )
                if similarity > 0:
                    similarities[user_id] = similarity

        else:
            raise ValueError(f"Unknown similarity method: {method}")

        logger.info(
            f"Calculated {method} similarities for {len(similarities)} users with target user {target_user_id}"
        )
        return similarities

    except Exception as e:
        logger.error(f"Error calculating user similarities: {e}")
        return {}


def get_similar_users(
    ratings_df: pd.DataFrame,
    target_user_id: str,
    top_k: int = 50,
    similarity_threshold: float = 0.1,
    method: str = "cosine",  # PERBAIKAN: Default ke cosine
    min_common_items: int = 2,
) -> List[Tuple[str, float]]:
    """
    Get top-K most similar users to target user

    Args:
        ratings_df: DataFrame with columns [user_id, food_id, rating]
        target_user_id: ID of the target user
        top_k: Number of top similar users to return
        similarity_threshold: Minimum similarity score threshold
        method: Similarity method ('jaccard' or 'cosine')
        min_common_items: Minimum number of common items required

    Returns:
        List[Tuple[str, float]]: List of (user_id, similarity_score) tuples
    """
    try:
        # Calculate similarities
        similarities = calculate_user_similarities(
            ratings_df, target_user_id, method=method, min_common_items=min_common_items
        )

        # Filter by threshold and sort
        filtered_similarities = [
            (user_id, score)
            for user_id, score in similarities.items()
            if score >= similarity_threshold
        ]

        # Sort by similarity score (descending) and take top-K
        similar_users = sorted(filtered_similarities, key=lambda x: x[1], reverse=True)[
            :top_k
        ]

        logger.info(
            f"Found {len(similar_users)} similar users for {target_user_id} (threshold: {similarity_threshold}, method: {method})"
        )
        return similar_users

    except Exception as e:
        logger.error(f"Error getting similar users: {e}")
        return []


def validate_similarity_calculation(
    ratings_df: pd.DataFrame, sample_size: int = 5
) -> bool:
    """
    Validate similarity calculation with a small sample - PERBAIKAN: Tambah test cosine + SVD

    Args:
        ratings_df: DataFrame with columns [user_id, food_id, rating]
        sample_size: Number of users to test

    Returns:
        bool: True if validation passes
    """
    try:
        if len(ratings_df) == 0:
            logger.warning("Empty ratings dataframe for validation")
            return False

        # Get sample users
        sample_users = ratings_df["user_id"].unique()[:sample_size]

        for user_id in sample_users:
            # Test Cosine similarity (fokus utama)
            cosine_similarities = get_similar_users(
                ratings_df, user_id, top_k=5, method="cosine"
            )

            # Test Jaccard sebagai backup
            jaccard_similarities = get_similar_users(
                ratings_df, user_id, top_k=5, method="jaccard"
            )

            logger.info(
                f"User {user_id}: {len(cosine_similarities)} Cosine, {len(jaccard_similarities)} Jaccard similarities"
            )

            # PERBAIKAN: Simple SVD test pada sample sub-dataset
            if len(cosine_similarities) > 0:
                sub_df = ratings_df[
                    ratings_df["user_id"].isin(
                        [user_id] + [u[0] for u in cosine_similarities[:3]]
                    )
                ]
                if len(sub_df) > 5:
                    from .local_model import LocalSVDModel

                    svd = LocalSVDModel()
                    pivot = pd.pivot_table(
                        sub_df,
                        index="user_id",
                        columns="food_id",
                        values="rating",
                        fill_value=0,
                    )
                    svd.fit(pivot)
                    logger.debug(
                        f"SVD test on sample for {user_id}: fitted={svd.is_fitted}"
                    )

        logger.info("Similarity calculation validation completed successfully")
        return True

    except Exception as e:
        logger.error(f"Similarity validation failed: {e}")
        return False
