"""
Simplified Recommendation Service - Collaborative Filtering Only
"""

from app.recommendation.config import RecommendationConfig
from app.recommendation.model_trainer import ModelTrainer
from app.recommendation.collaborative_filtering import CollaborativeFilteringRecommender
from app.recommendation.popular import PopularFoodRecommender
from app.utils import training_logger as logger
from typing import Dict


class RecommendationService:
    @staticmethod
    def initialize():
        """Initialize the recommendation service"""
        RecommendationConfig.initialize()

    @staticmethod
    def train_model(force=False):
        """Train the collaborative filtering model"""
        return ModelTrainer.train_svd_model(force)

    @staticmethod
    def get_recommendations(
        user_id,
        user_price_preferences: Dict[str, float] = None,
        price_filter: Dict[str, float] = None,
        n=None,
        alpha=None,
        beta=None,
        gamma=None,
    ):
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

        logger.info(
            f"Memproses rekomendasi enhanced collaborative filtering untuk user {user_id}"
        )
        if price_filter:
            logger.info(f"Price filter applied: {price_filter}")

        return CollaborativeFilteringRecommender.get_enhanced_recommendations(
            user_id, user_price_preferences, price_filter, n, alpha, beta, gamma
        )

    @staticmethod
    def get_popular_foods(n=None):
        """Get popular foods as fallback"""
        if n is None:
            n = RecommendationConfig.DEFAULT_RECOMMENDATIONS
        return PopularFoodRecommender.get_popular_foods(n)

    @staticmethod
    def schedule_training():
        """Schedule model training"""
        logger.info("Memulai pelatihan terjadwal untuk model rekomendasi")
        ModelTrainer.train_svd_model(force=True)
        logger.info("Pelatihan terjadwal selesai")


# Initialize the recommendation service at module import time
RecommendationService.initialize()
