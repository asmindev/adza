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

    # Enhanced recommendation parameters
    DEFAULT_ALPHA = 0.3  # Weight for place quality adjustment
    DEFAULT_BETA = 0.2  # Weight for price preference adjustment
    DEFAULT_GAMMA = 0.2  # Weight for food quality adjustment

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

    # Helper method to check if retraining is needed
    @staticmethod
    def needs_retraining():
        if not os.path.exists(RecommendationConfig.SVD_MODEL_FILE):
            logger.info("Model SVD belum ada, akan dilatih")
            return True

        if os.path.exists(RecommendationConfig.LAST_TRAINING_FILE):
            try:
                with open(RecommendationConfig.LAST_TRAINING_FILE, "r") as f:
                    last_training_time = float(f.read().strip())
                    current_time = time.time()
                    time_diff = current_time - last_training_time

                    if time_diff > RecommendationConfig.TRAINING_INTERVAL:
                        logger.info(
                            f"Model sudah {time_diff/3600:.1f} jam sejak pelatihan terakhir, akan dilatih ulang"
                        )
                        return True
                    else:
                        logger.debug(
                            f"Model masih baru ({time_diff/3600:.1f} jam sejak pelatihan terakhir)"
                        )
                        return False
            except Exception as e:
                logger.error(f"Error saat membaca waktu training terakhir: {str(e)}")
                return True
        else:
            logger.info(
                "File timestamp training tidak ditemukan, akan melatih model baru"
            )
            return True

    # Update the last training timestamp
    @staticmethod
    def update_training_timestamp():
        with open(RecommendationConfig.LAST_TRAINING_FILE, "w") as f:
            timestamp = str(time.time())
            f.write(timestamp)
            logger.debug(f"Timestamp training ({timestamp}) disimpan")
            logger.info("Timestamp training diperbarui")

    # Validate enhancement parameters
    @staticmethod
    def validate_enhancement_params(alpha, beta, gamma):
        """Validate alpha, beta, gamma parameters"""
        if not (0 <= alpha <= 1 and 0 <= beta <= 1 and 0 <= gamma <= 1):
            return False, "Alpha, beta, and gamma must be between 0 and 1"

        if alpha + beta + gamma > 1:
            return False, "Sum of alpha, beta, and gamma must not exceed 1"

        return True, "Valid parameters"
