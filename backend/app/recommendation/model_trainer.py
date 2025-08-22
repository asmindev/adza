"""
Model Training Utilities - Collaborative Filtering Only
"""

import os
from surprise import SVD, dump
from app.recommendation.config import RecommendationConfig
from app.recommendation.data_preparer import DataPreparer
from app.recommendation.enhanced_rating import get_enhanced_ratings_for_svd
from app.utils import training_logger as logger
from typing import Dict, Optional


class ModelTrainer:
    @staticmethod
    def train_svd_model(
        force=False,
        use_enhanced_ratings=False,
        user_price_preferences: Optional[Dict[str, float]] = None,
        alpha=None,
        beta=None,
        gamma=None,
    ):
        """
        Train the SVD model if it doesn't exist or is outdated

        Args:
            force (bool): Force retraining even if the model is up-to-date
            use_enhanced_ratings (bool): Whether to use enhanced ratings with additional parameters
            user_price_preferences (dict): Dictionary mapping user_id to preferred price
            alpha (float): Weight for place quality adjustment
            beta (float): Weight for price preference adjustment
            gamma (float): Weight for food quality adjustment

        Returns:
            SVD model trained on the full dataset
        """
        # Use default values from config if not provided
        if alpha is None:
            alpha = RecommendationConfig.DEFAULT_ALPHA
        if beta is None:
            beta = RecommendationConfig.DEFAULT_BETA
        if gamma is None:
            gamma = RecommendationConfig.DEFAULT_GAMMA

        # Check if retraining is needed
        should_train = force or RecommendationConfig.needs_retraining()

        # If no retraining needed, load existing model
        if not should_train and not use_enhanced_ratings:
            try:
                logger.debug("Memuat model SVD dari file")
                _, algo = dump.load(RecommendationConfig.SVD_MODEL_FILE)
                return algo
            except Exception as e:
                logger.error(f"Gagal memuat model SVD: {str(e)}")
                logger.info("Melatih model baru sebagai fallback")
                should_train = True

        # Train new model
        if should_train or use_enhanced_ratings:
            if use_enhanced_ratings:
                logger.info("Memulai pelatihan model SVD dengan enhanced ratings")
                if not user_price_preferences:
                    logger.warning(
                        "Enhanced ratings diminta tapi user price preferences tidak disediakan"
                    )
                    use_enhanced_ratings = False
            else:
                logger.info("Memulai pelatihan model SVD dengan rating standar")

            if use_enhanced_ratings and user_price_preferences:
                # Prepare enhanced dataset
                enhanced_ratings = get_enhanced_ratings_for_svd(
                    user_price_preferences, alpha=alpha, beta=beta, gamma=gamma
                )
                dataset = DataPreparer.prepare_rating_data_from_tuples(enhanced_ratings)
            else:
                # Use standard ratings
                dataset = DataPreparer.prepare_rating_data()

            if dataset is None:
                logger.error(
                    "Tidak dapat memulai pelatihan: dataset kosong atau tidak valid"
                )
                return None

            # Train on the entire dataset
            trainset = dataset.build_full_trainset()
            logger.debug(
                f"Melatih model dengan {trainset.n_users} pengguna dan {trainset.n_items} item"
            )

            # Use SVD algorithm with config parameters
            algo = SVD(
                n_factors=RecommendationConfig.SVD_N_FACTORS,
                n_epochs=RecommendationConfig.SVD_N_EPOCHS,
                random_state=RecommendationConfig.SVD_RANDOM_STATE,
            )
            algo.fit(trainset)

            # Save the trained model only if not using enhanced ratings (to preserve standard model)
            if not use_enhanced_ratings:
                dump.dump(RecommendationConfig.SVD_MODEL_FILE, algo=algo)
                logger.info(
                    f"Model SVD berhasil disimpan ke {RecommendationConfig.SVD_MODEL_FILE}"
                )
                # Update training timestamp
                RecommendationConfig.update_training_timestamp()
            else:
                logger.info(
                    "Model SVD dengan enhanced ratings selesai dilatih (tidak disimpan permanen)"
                )

            logger.info("Pelatihan model SVD selesai")
            return algo
