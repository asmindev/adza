"""
Collaborative Filtering Recommender
"""

from collections import defaultdict
import numpy as np
from typing import Dict, Optional, List

from app.modules.food.models import Food
from app.modules.user.models import User
from app.modules.rating.models import FoodRating
from app.recommendation.model_trainer import ModelTrainer
from app.utils import training_logger as logger


class CollaborativeFilteringRecommender:
    @staticmethod
    def get_recommendations(user_id, n=10):
        """
        Get food recommendations based on collaborative filtering

        Args:
            user_id: ID of the user
            n: Number of recommendations to return

        Returns:
            List of food dictionaries with predicted ratings
        """
        logger.info(
            f"Generating collaborative filtering recommendations for user {user_id}"
        )

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User dengan ID {user_id} tidak ditemukan")
            return []

        # Load or train the SVD model
        algo = ModelTrainer.train_svd_model()
        if algo is None:
            logger.error("Model collaborative filtering tidak tersedia")
            # Fall back to the memory-based CF if model isn't available
            return (
                CollaborativeFilteringRecommender._memory_based_collaborative_filtering(
                    user_id, n
                )
            )

        # Validate model
        if not ModelTrainer.validate_model(algo):
            logger.error("Model SVD tidak valid")
            return (
                CollaborativeFilteringRecommender._memory_based_collaborative_filtering(
                    user_id, n
                )
            )

        # Get all foods
        foods = Food.query.all()
        logger.debug(f"Terdapat {len(foods)} makanan di database")

        # Get foods already rated by the user
        rated_foods = set(
            r.food_id for r in FoodRating.query.filter_by(user_id=user_id).all()
        )
        logger.debug(
            f"User {user_id} telah memberi rating pada {len(rated_foods)} makanan"
        )

        if not rated_foods:
            logger.warning(f"User {user_id} belum memberikan rating")
            return []

        # Predict ratings for unrated foods using SVD model
        predictions = []
        logger.info(f"Predicting ratings for {len(foods)} foods")
        for food in foods:
            if food.id not in rated_foods:
                try:
                    # Use the trained SVD model for predictions
                    prediction = algo.predict(user_id, food.id)
                    predicted_rating = prediction.est

                    # Ensure predicted rating is within valid range
                    predicted_rating = max(1.0, min(5.0, predicted_rating))

                    predictions.append((food, predicted_rating))
                except Exception as e:
                    logger.debug(
                        f"Error predicting rating for food {food.id}: {str(e)}"
                    )
                    # Skip this food if there's an error

        # Sort by predicted rating in descending order and take top n
        recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)[:n]
        logger.info(
            f"Berhasil menghasilkan {len(recommendations)} rekomendasi collaborative filtering untuk user {user_id}"
        )

        return [
            {
                "food": food.to_dict(),
                "predicted_rating": round(predicted_rating, 2),
                "normalized_rating_score": round(predicted_rating / 5, 2),
                "normalized_review_similarity": 0,  # Will be calculated in hybrid approach
                "hybrid_score": round(
                    predicted_rating / 5, 2
                ),  # Default to rating score
            }
            for food, predicted_rating in recommendations
        ]

    @staticmethod
    def get_enhanced_recommendations(
        user_id,
        user_price_preferences: Dict[str, float],
        price_filter: Dict[str, float],
        n=10,
        alpha=0.3,
        beta=0.2,
        gamma=0.2,
    ):
        """
        Get food recommendations based on enhanced collaborative filtering with additional parameters

        Args:
            user_id: ID of the user
            user_price_preferences: Dictionary mapping user_id to preferred price
            price_filter: Dictionary containing min_price and/or max_price for filtering
            n: Number of recommendations to return
            alpha: Weight for place quality adjustment
            beta: Weight for price preference adjustment
            gamma: Weight for food quality adjustment

        Returns:
            List of food dictionaries with predicted ratings using enhanced system
        """
        logger.info(
            f"Generating enhanced collaborative filtering recommendations for user {user_id}"
        )

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            logger.error(f"User dengan ID {user_id} tidak ditemukan")
            return []

        # Train SVD model with enhanced ratings
        algo = ModelTrainer.train_svd_model(
            use_enhanced_ratings=True,
            user_price_preferences=user_price_preferences,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )

        if algo is None:
            logger.error("Enhanced collaborative filtering model tidak tersedia")
            # Fall back to standard CF
            return CollaborativeFilteringRecommender.get_recommendations(user_id, n)

        # Validate model
        if not ModelTrainer.validate_model(algo):
            logger.error("Enhanced model SVD tidak valid")
            return CollaborativeFilteringRecommender.get_recommendations(user_id, n)

        # Get all foods with price filtering
        foods_query = Food.query

        # Apply price filtering if provided
        if price_filter:
            min_price = price_filter.get("min_price")
            max_price = price_filter.get("max_price")

            if min_price is not None:
                foods_query = foods_query.filter(Food.price >= min_price)
                logger.info(f"Applied min_price filter: >= {min_price}")

            if max_price is not None:
                foods_query = foods_query.filter(Food.price <= max_price)
                logger.info(f"Applied max_price filter: <= {max_price}")

        foods = foods_query.all()
        logger.debug(f"Terdapat {len(foods)} makanan setelah price filtering")

        # Get foods already rated by the user
        rated_foods = set(
            r.food_id for r in FoodRating.query.filter_by(user_id=user_id).all()
        )
        logger.debug(
            f"User {user_id} telah memberi rating pada {len(rated_foods)} makanan"
        )

        if not rated_foods:
            logger.warning(f"User {user_id} belum memberikan rating")
            return []

        # Predict ratings for unrated foods using enhanced SVD model
        predictions = []
        logger.info(f"Predicting enhanced ratings for {len(foods)} foods")
        for food in foods:
            if food.id not in rated_foods:
                try:
                    # Use the enhanced trained SVD model for predictions
                    prediction = algo.predict(user_id, food.id)
                    predicted_rating = prediction.est

                    # Ensure predicted rating is within valid range
                    predicted_rating = max(1.0, min(5.0, predicted_rating))

                    predictions.append((food, predicted_rating))
                except Exception as e:
                    logger.debug(
                        f"Error predicting enhanced rating for food {food.id}: {str(e)}"
                    )
                    # Skip this food if there's an error

        # Sort by predicted rating in descending order and take top n
        recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)[:n]
        logger.info(
            f"Berhasil menghasilkan {len(recommendations)} enhanced collaborative filtering recommendations untuk user {user_id}"
        )

        return [
            {
                "food": food.to_dict(),
                "predicted_rating": round(predicted_rating, 2),
                "normalized_rating_score": round(predicted_rating / 5, 2),
                "normalized_review_similarity": 0,  # Will be calculated in hybrid approach
                "hybrid_score": round(
                    predicted_rating / 5, 2
                ),  # Default to rating score
                "enhancement_weights": {"alpha": alpha, "beta": beta, "gamma": gamma},
                "price_filter_applied": price_filter if price_filter else None,
            }
            for food, predicted_rating in recommendations
        ]

    @staticmethod
    def _memory_based_collaborative_filtering(user_id, n=10):
        """
        Fallback method for collaborative filtering using memory-based approach
        This is used when the SVD model isn't available
        """
        logger.info(f"Using memory-based collaborative filtering for user {user_id}")

        try:
            # Get all ratings
            ratings = FoodRating.query.all()
            if not ratings:
                logger.warning("Tidak ada data rating untuk rekomendasi")
                return []

            # Create user-item rating matrix
            user_ratings = defaultdict(dict)
            for rating in ratings:
                user_ratings[rating.user_id][rating.food_id] = rating.rating

            # Check if user has ratings
            if user_id not in user_ratings or not user_ratings[user_id]:
                logger.warning(f"User {user_id} belum memberikan rating")
                return []

            # Calculate similarity between users
            target_user_ratings = user_ratings[user_id]
            similarities = {}

            for other_user_id, other_ratings in user_ratings.items():
                if other_user_id == user_id:
                    continue

                # Find common foods rated by both users
                common_foods = set(target_user_ratings.keys()) & set(
                    other_ratings.keys()
                )
                if len(common_foods) < 2:  # Need at least 2 common items
                    continue

                # Calculate Pearson correlation
                target_ratings_list = [
                    target_user_ratings[food_id] for food_id in common_foods
                ]
                other_ratings_list = [
                    other_ratings[food_id] for food_id in common_foods
                ]

                try:
                    # Check for constant ratings (zero variance)
                    if (
                        len(set(target_ratings_list)) == 1
                        or len(set(other_ratings_list)) == 1
                    ):
                        continue

                    correlation = np.corrcoef(target_ratings_list, other_ratings_list)[
                        0, 1
                    ]
                    if (
                        not np.isnan(correlation) and correlation > 0
                    ):  # Only positive correlations
                        similarities[other_user_id] = correlation
                except Exception as e:
                    logger.debug(
                        f"Error calculating correlation with user {other_user_id}: {str(e)}"
                    )
                    continue

            if not similarities:
                logger.warning(f"No similar users found for user {user_id}")
                return []

            # Get predicted ratings for foods the user hasn't rated yet
            all_foods = set()
            for ratings_dict in user_ratings.values():
                all_foods.update(ratings_dict.keys())

            unrated_foods = all_foods - set(target_user_ratings.keys())
            predicted_ratings = {}

            for food_id in unrated_foods:
                numerator = 0
                denominator = 0

                for other_user_id, similarity in similarities.items():
                    if food_id in user_ratings[other_user_id]:
                        numerator += similarity * user_ratings[other_user_id][food_id]
                        denominator += abs(similarity)

                if denominator > 0:
                    predicted_rating = numerator / denominator
                    # Ensure rating is within valid range
                    predicted_rating = max(1.0, min(5.0, predicted_rating))
                    predicted_ratings[food_id] = round(predicted_rating, 2)

            # Sort by predicted rating and get top n
            sorted_predictions = sorted(
                predicted_ratings.items(), key=lambda x: x[1], reverse=True
            )[:n]

            # Get food details
            recommendations = []
            for food_id, predicted_rating in sorted_predictions:
                food = Food.query.get(food_id)
                if food:
                    recommendations.append(
                        {
                            "food": food.to_dict(),
                            "predicted_rating": predicted_rating,
                            "normalized_rating_score": round(predicted_rating / 5, 2),
                            "normalized_review_similarity": 0,  # Will be calculated in hybrid approach
                            "hybrid_score": round(
                                predicted_rating / 5, 2
                            ),  # Default to rating score
                            "method": "memory_based_cf",
                        }
                    )

            logger.info(
                f"Berhasil menghasilkan {len(recommendations)} rekomendasi memory-based collaborative filtering"
            )
            return recommendations

        except Exception as e:
            logger.error(f"Error in memory-based collaborative filtering: {str(e)}")
            return []
