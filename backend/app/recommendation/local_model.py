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

            # Determine optimal number of components
            max_components = min(self.n_components, min(self.n_users, self.n_items) - 1)
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

            logger.info(
                f"SVD training completed: {max_components} factors, "
                f"explained variance ratio: {self.svd_model.explained_variance_ratio_.sum():.3f}"
            )

            return True

        except Exception as e:
            logger.error(f"Error training SVD model: {e}")
            self.is_fitted = False
            return False

    def predict_user_item(self, user_idx: int, item_idx: int) -> float:
        """
        Predict rating for specific user-item pair

        Args:
            user_idx: User index
            item_idx: Item index

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

                predicted_rating = self.predict_user_item(user_idx, item_idx)
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
        Evaluate model performance on test data

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

            # Calculate coverage (percentage of items that can be recommended)
            coverage = (
                self.n_items - len(exclude_items if "exclude_items" in locals() else [])
            ) / self.n_items

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
