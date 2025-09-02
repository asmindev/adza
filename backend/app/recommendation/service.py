"""
Simplified Recommendation Service - Collaborative Filtering Only
"""

from app.recommendation.config import RecommendationConfig
from app.recommendation.model_trainer import ModelTrainer
from app.recommendation.collaborative_filtering import CollaborativeFilteringRecommender
from app.recommendation.popular import PopularFoodRecommender
from app.utils import training_logger as logger
from typing import Dict, List, Optional, Any


class RecommendationService:
    @staticmethod
    def initialize():
        """Initialize the recommendation service"""
        try:
            RecommendationConfig.initialize()
            logger.info("Recommendation service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing recommendation service: {str(e)}")

    @staticmethod
    def train_model(force=False) -> bool:
        """
        Train the collaborative filtering model

        Args:
            force: Force retraining even if model is up-to-date

        Returns:
            bool: True if training successful, False otherwise
        """
        try:
            result = ModelTrainer.train_svd_model(force)
            if result is not None:
                logger.info("Model training completed successfully")
                return True
            else:
                logger.error("Model training failed")
                return False
        except Exception as e:
            logger.error(f"Error in train_model: {str(e)}")
            return False

    @staticmethod
    def get_recommendations(
        user_id,
        user_price_preferences: Optional[Dict[str, float]] = None,
        price_filter: Optional[Dict[str, float]] = None,
        n: Optional[int] = None,
        alpha: Optional[float] = None,
        beta: Optional[float] = None,
        gamma: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get enhanced collaborative filtering recommendations

        Args:
            user_id: ID of the user
            user_price_preferences: Dictionary mapping user_id to preferred price
            price_filter: Dictionary containing min_price and/or max_price for filtering
            n: Number of recommendations to return
            alpha: Weight for place quality adjustment
            beta: Weight for price preference adjustment
            gamma: Weight for food quality adjustment

        Returns:
            List of food dictionaries with enhanced predicted ratings
        """
        try:
            # Use default values from config if not provided
            if n is None:
                n = RecommendationConfig.DEFAULT_RECOMMENDATIONS
            if alpha is None:
                alpha = RecommendationConfig.DEFAULT_ALPHA
            if beta is None:
                beta = RecommendationConfig.DEFAULT_BETA
            if gamma is None:
                gamma = RecommendationConfig.DEFAULT_GAMMA
            if user_price_preferences is None:
                user_price_preferences = {}
            if price_filter is None:
                price_filter = {}

            # Validate parameters
            if n < RecommendationConfig.MIN_RECOMMENDATIONS:
                n = RecommendationConfig.MIN_RECOMMENDATIONS
                logger.warning(f"Recommendation count adjusted to minimum: {n}")
            elif n > RecommendationConfig.MAX_RECOMMENDATIONS:
                n = RecommendationConfig.MAX_RECOMMENDATIONS
                logger.warning(f"Recommendation count adjusted to maximum: {n}")

            # Validate enhancement parameters
            valid, message = RecommendationConfig.validate_enhancement_params(
                alpha, beta, gamma
            )
            if not valid:
                logger.warning(
                    f"Invalid enhancement parameters: {message}, using defaults"
                )
                alpha = RecommendationConfig.DEFAULT_ALPHA
                beta = RecommendationConfig.DEFAULT_BETA
                gamma = RecommendationConfig.DEFAULT_GAMMA

            logger.info(
                f"Memproses rekomendasi enhanced collaborative filtering untuk user {user_id}"
            )
            if price_filter:
                logger.info(f"Price filter applied: {price_filter}")

            # Try to get enhanced recommendations
            recommendations = (
                CollaborativeFilteringRecommender.get_enhanced_recommendations(
                    user_id, user_price_preferences, price_filter, n, alpha, beta, gamma
                )
            )

            # If enhanced recommendations fail or return empty, fallback to standard CF
            if not recommendations:
                logger.warning("Enhanced recommendations failed, trying standard CF")
                recommendations = CollaborativeFilteringRecommender.get_recommendations(
                    user_id, n
                )

            # If still no recommendations, return popular foods
            if not recommendations:
                logger.warning("CF recommendations failed, returning popular foods")
                popular_foods = RecommendationService.get_popular_foods(n)
                # Convert popular foods format to recommendation format
                recommendations = []
                for food in popular_foods:
                    recommendations.append(
                        {
                            "food": food,
                            "predicted_rating": food.get("average_rating", 3.0),
                            "normalized_rating_score": round(
                                food.get("average_rating", 3.0) / 5, 2
                            ),
                            "normalized_review_similarity": 0,
                            "hybrid_score": round(food.get("popularity_score", 0.5), 2),
                            "fallback_method": "popular",
                        }
                    )

            logger.info(
                f"Returning {len(recommendations)} recommendations for user {user_id}"
            )
            return recommendations

        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            # Final fallback to popular foods
            try:
                popular_foods = RecommendationService.get_popular_foods(
                    n or RecommendationConfig.DEFAULT_RECOMMENDATIONS
                )
                return [
                    {
                        "food": food,
                        "predicted_rating": food.get("average_rating", 3.0),
                        "normalized_rating_score": round(
                            food.get("average_rating", 3.0) / 5, 2
                        ),
                        "normalized_review_similarity": 0,
                        "hybrid_score": round(food.get("popularity_score", 0.5), 2),
                        "fallback_method": "popular_emergency",
                    }
                    for food in popular_foods
                ]
            except Exception as fallback_error:
                logger.error(f"Emergency fallback also failed: {str(fallback_error)}")
                return []

    @staticmethod
    def get_popular_foods(n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get popular foods as fallback

        Args:
            n: Number of foods to return

        Returns:
            List of popular food dictionaries
        """
        try:
            if n is None:
                n = RecommendationConfig.DEFAULT_RECOMMENDATIONS

            # Validate n parameter
            if n < RecommendationConfig.MIN_RECOMMENDATIONS:
                n = RecommendationConfig.MIN_RECOMMENDATIONS
            elif n > RecommendationConfig.MAX_RECOMMENDATIONS:
                n = RecommendationConfig.MAX_RECOMMENDATIONS

            return PopularFoodRecommender.get_popular_foods(n)

        except Exception as e:
            logger.error(f"Error in get_popular_foods: {str(e)}")
            return []

    @staticmethod
    def get_trending_foods(
        n: Optional[int] = None, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get trending foods

        Args:
            n: Number of foods to return
            days: Number of recent days to consider

        Returns:
            List of trending food dictionaries
        """
        try:
            if n is None:
                n = RecommendationConfig.DEFAULT_RECOMMENDATIONS

            # Validate parameters
            if n < RecommendationConfig.MIN_RECOMMENDATIONS:
                n = RecommendationConfig.MIN_RECOMMENDATIONS
            elif n > RecommendationConfig.MAX_RECOMMENDATIONS:
                n = RecommendationConfig.MAX_RECOMMENDATIONS

            if days < 1:
                days = 7
                logger.warning("Days parameter adjusted to minimum: 7")

            return PopularFoodRecommender.get_trending_foods(n, days)

        except Exception as e:
            logger.error(f"Error in get_trending_foods: {str(e)}")
            return []

    @staticmethod
    def schedule_training():
        """Schedule model training"""
        try:
            logger.info("Memulai pelatihan terjadwal untuk model rekomendasi")
            success = RecommendationService.train_model(force=True)
            if success:
                logger.info("Pelatihan terjadwal selesai dengan sukses")
            else:
                logger.error("Pelatihan terjadwal gagal")
        except Exception as e:
            logger.error(f"Error in schedule_training: {str(e)}")

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """
        Check the health of the recommendation system

        Returns:
            Dictionary with health status information
        """
        try:
            import os

            health_status = {
                "service_status": "healthy",
                "model_exists": os.path.exists(RecommendationConfig.SVD_MODEL_FILE),
                "needs_retraining": RecommendationConfig.needs_retraining(),
                "model_path": RecommendationConfig.SVD_MODEL_FILE,
                "config": {
                    "default_recommendations": RecommendationConfig.DEFAULT_RECOMMENDATIONS,
                    "svd_factors": RecommendationConfig.SVD_N_FACTORS,
                    "svd_epochs": RecommendationConfig.SVD_N_EPOCHS,
                    "training_interval_hours": RecommendationConfig.TRAINING_INTERVAL
                    / 3600,
                },
            }

            # Check if we can load a model
            try:
                model = ModelTrainer.train_svd_model()
                health_status["model_loadable"] = model is not None
                health_status["model_valid"] = (
                    ModelTrainer.validate_model(model) if model else False
                )
            except Exception as e:
                health_status["model_loadable"] = False
                health_status["model_valid"] = False
                health_status["model_error"] = str(e)

            return health_status

        except Exception as e:
            logger.error(f"Error in health_check: {str(e)}")
            return {"service_status": "unhealthy", "error": str(e)}


# Initialize the recommendation service at module import time
try:
    RecommendationService.initialize()
except Exception as e:
    logger.error(f"Failed to initialize recommendation service: {str(e)}")
