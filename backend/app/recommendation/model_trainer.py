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
            SVD model trained on the full dataset or None if training failed
        """
        try:
            # Use default values from config if not provided
            if alpha is None:
                alpha = RecommendationConfig.DEFAULT_ALPHA
            if beta is None:
                beta = RecommendationConfig.DEFAULT_BETA
            if gamma is None:
                gamma = RecommendationConfig.DEFAULT_GAMMA

            # Validate enhancement parameters if using enhanced ratings
            if use_enhanced_ratings:
                valid, message = RecommendationConfig.validate_enhancement_params(
                    alpha, beta, gamma
                )
                if not valid:
                    logger.error(f"Invalid enhancement parameters: {message}")
                    return None

            # Check if retraining is needed
            should_train = force or RecommendationConfig.needs_retraining()

            # If no retraining needed and not using enhanced ratings, load existing model
            if not should_train and not use_enhanced_ratings:
                try:
                    if os.path.exists(RecommendationConfig.SVD_MODEL_FILE):
                        logger.debug("Memuat model SVD dari file")
                        _, algo = dump.load(RecommendationConfig.SVD_MODEL_FILE)
                        return algo
                    else:
                        logger.info(
                            "Model file tidak ditemukan, akan melatih model baru"
                        )
                        should_train = True
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
                            "Enhanced ratings diminta tapi user price preferences tidak disediakan, menggunakan rating standar"
                        )
                        use_enhanced_ratings = False
                else:
                    logger.info("Memulai pelatihan model SVD dengan rating standar")

                # Prepare dataset
                dataset = None
                if use_enhanced_ratings and user_price_preferences:
                    try:
                        # Prepare enhanced dataset
                        enhanced_ratings = get_enhanced_ratings_for_svd(
                            user_price_preferences, alpha=alpha, beta=beta, gamma=gamma
                        )
                        if enhanced_ratings:
                            dataset = DataPreparer.prepare_rating_data_from_tuples(
                                enhanced_ratings
                            )
                        else:
                            logger.warning(
                                "Enhanced ratings kosong, fallback ke rating standar"
                            )
                            use_enhanced_ratings = False
                    except Exception as e:
                        logger.error(
                            f"Error dalam enhanced ratings preparation: {str(e)}"
                        )
                        logger.info("Fallback ke rating standar")
                        use_enhanced_ratings = False

                # Use standard ratings if enhanced ratings failed or not requested
                if not use_enhanced_ratings or dataset is None:
                    dataset = DataPreparer.prepare_rating_data()

                if dataset is None:
                    logger.error(
                        "Tidak dapat memulai pelatihan: dataset kosong atau tidak valid"
                    )
                    return None

                # Train on the entire dataset
                try:
                    trainset = dataset.build_full_trainset()  # type: ignore
                    logger.info(
                        f"Melatih model dengan {trainset.n_users} pengguna dan {trainset.n_items} item"
                    )

                    # Use SVD algorithm with config parameters
                    algo = SVD(
                        n_factors=RecommendationConfig.SVD_N_FACTORS,
                        n_epochs=RecommendationConfig.SVD_N_EPOCHS,
                        random_state=RecommendationConfig.SVD_RANDOM_STATE,
                    )

                    logger.info("Memulai training SVD model...")
                    algo.fit(trainset)
                    logger.info("Training SVD model selesai")

                    # Save the trained model only if not using enhanced ratings (to preserve standard model)
                    if not use_enhanced_ratings:
                        try:
                            # Ensure directory exists
                            os.makedirs(
                                os.path.dirname(RecommendationConfig.SVD_MODEL_FILE),
                                exist_ok=True,
                            )

                            dump.dump(RecommendationConfig.SVD_MODEL_FILE, algo=algo)
                            logger.info(
                                f"Model SVD berhasil disimpan ke {RecommendationConfig.SVD_MODEL_FILE}"
                            )
                            # Update training timestamp
                            RecommendationConfig.update_training_timestamp()
                        except Exception as e:
                            logger.error(f"Error saving model: {str(e)}")
                            # Model is still trained in memory, continue
                    else:
                        logger.info(
                            "Model SVD dengan enhanced ratings selesai dilatih (tidak disimpan permanen)"
                        )

                    logger.info("Pelatihan model SVD selesai")
                    return algo

                except Exception as e:
                    logger.error(f"Error during model training: {str(e)}")
                    return None

        except Exception as e:
            logger.error(f"Unexpected error in train_svd_model: {str(e)}")
            return None

    @staticmethod
    def validate_model(algo):
        """
        Validate the trained model

        Args:
            algo: Trained SVD algorithm

        Returns:
            bool: True if model is valid, False otherwise
        """
        try:
            if algo is None:
                return False

            # Check if model has required attributes
            required_attrs = ["trainset", "pu", "qi", "bu", "bi"]
            for attr in required_attrs:
                if not hasattr(algo, attr):
                    logger.error(f"Model missing required attribute: {attr}")
                    return False

            logger.debug("Model validation passed")
            return True

        except Exception as e:
            logger.error(f"Error validating model: {str(e)}")
            return False
