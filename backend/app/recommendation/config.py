"""
Recommendation System Configuration
"""

import os
import time
from app.utils import get_logger
logger = get_logger(__name__)


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
    SVD_N_FACTORS = 12
    SVD_N_EPOCHS = 20
    SVD_RANDOM_STATE = 42

    # Recommendation threshold
    MIN_RATING_THRESHOLD = 3.0  # Minimum predicted rating threshold

    # Create model directory if it doesn't exist

    @staticmethod
    def initialize():
        os.makedirs(RecommendationConfig.MODEL_PATH, exist_ok=True)
