"""
Hybrid Recommendation System with Collaborative Filtering + SVD
Combines food ratings and restaurant ratings with alpha parameter weighting
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import cross_validate
import warnings

from app.extensions import db
from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant
from app.modules.user.models import User
from app.utils import training_logger as logger

warnings.filterwarnings("ignore")


class Recommendations:
    """
    Hybrid Recommendation System that combines:
    1. Food ratings (collaborative filtering with SVD)
    2. Restaurant ratings (collaborative filtering with SVD)
    Combined with alpha parameter weighting

    This is the main and only class for the recommendation system.
    It includes all functionality:
    - Data preparation and cleaning
    - SVD model training for both food and restaurant ratings
    - Model validation with RMSE/MAE metrics
    - Hybrid prediction combining both rating types
    - Compatibility methods for existing applications
    """

    def __init__(self, alpha: float = 0.7, n_factors: int = 100, n_epochs: int = 20):
        """
        Initialize the hybrid recommendation system

        Args:
            alpha: Weight for food ratings (0-1), restaurant weight = 1-alpha
            n_factors: Number of factors for SVD
            n_epochs: Number of training epochs
        """
        self.alpha = alpha
        self.n_factors = n_factors
        self.n_epochs = n_epochs

        # SVD models
        self.food_svd_model = None
        self.restaurant_svd_model = None

        # Data containers
        self.food_ratings_df = None
        self.restaurant_ratings_df = None

        # User and item mappings from Surprise
        self.food_trainset = None
        self.restaurant_trainset = None

        # Scalers for normalization (if needed, but removed unnecessary usage)
        # self.food_scaler = MinMaxScaler()
        # self.restaurant_scaler = MinMaxScaler()

        logger.info(f"Initialized HybridRecommendationSystem with alpha={alpha}")

    def _import_modules(self):
        """Step 1: Import and validate required modules"""
        try:
            logger.info("Step 1: Importing modules and validating dependencies")

            # Test imports
            import surprise
            import sklearn
            import pandas
            import numpy

            logger.info("✓ All required modules imported successfully")
            return True

        except ImportError as e:
            logger.error(f"✗ Module import failed: {str(e)}")
            return False

    def _prepare_data(self) -> bool:
        """Step 2: Prepare and clean rating data"""
        try:
            logger.info("Step 2: Preparing rating data")

            # Get food ratings
            food_ratings = FoodRating.query.all()
            if not food_ratings:
                logger.warning("No food ratings found")
                return False

            # Convert food ratings to DataFrame
            food_data = [(r.user_id, r.food_id, float(r.rating)) for r in food_ratings]
            self.food_ratings_df = pd.DataFrame(
                food_data, columns=["user_id", "food_id", "rating"]
            )

            # Get restaurant ratings
            restaurant_ratings = RestaurantRating.query.all()
            if not restaurant_ratings:
                logger.warning("No restaurant ratings found - using food ratings only")
                self.restaurant_ratings_df = pd.DataFrame(
                    columns=["user_id", "restaurant_id", "rating"]
                )
            else:
                # Convert restaurant ratings to DataFrame
                restaurant_data = [
                    (r.user_id, r.restaurant_id, float(r.rating))
                    for r in restaurant_ratings
                ]
                self.restaurant_ratings_df = pd.DataFrame(
                    restaurant_data, columns=["user_id", "restaurant_id", "rating"]
                )

            # Clean data
            self.food_ratings_df = self.food_ratings_df.dropna()
            if not self.restaurant_ratings_df.empty:
                self.restaurant_ratings_df = self.restaurant_ratings_df.dropna()

            # Validate rating ranges
            self.food_ratings_df = self.food_ratings_df[
                (self.food_ratings_df["rating"] >= 1.0)
                & (self.food_ratings_df["rating"] <= 5.0)
            ]
            if not self.restaurant_ratings_df.empty:
                self.restaurant_ratings_df = self.restaurant_ratings_df[
                    (self.restaurant_ratings_df["rating"] >= 1.0)
                    & (self.restaurant_ratings_df["rating"] <= 5.0)
                ]

            logger.info(f"✓ Food ratings: {len(self.food_ratings_df)} records")
            logger.info(
                f"✓ Restaurant ratings: {len(self.restaurant_ratings_df)} records"
            )
            logger.info(
                f"✓ Food rating range: {self.food_ratings_df['rating'].min():.1f} - {self.food_ratings_df['rating'].max():.1f}"
            )
            if not self.restaurant_ratings_df.empty:
                logger.info(
                    f"✓ Restaurant rating range: {self.restaurant_ratings_df['rating'].min():.1f} - {self.restaurant_ratings_df['rating'].max():.1f}"
                )
            else:
                logger.info(
                    "✓ Restaurant ratings: No data available - will use food ratings only"
                )

            return True

        except Exception as e:
            logger.error(f"✗ Data preparation failed: {str(e)}")
            return False

    def _train_and_test_models(self) -> bool:
        """Step 3: Train SVD models and split data for testing"""
        try:
            logger.info("Step 3: Training SVD models")

            # Prepare food ratings for Surprise
            food_reader = Reader(rating_scale=(1, 5))
            food_dataset = Dataset.load_from_df(
                self.food_ratings_df[["user_id", "food_id", "rating"]], food_reader
            )

            # Train food SVD model
            logger.info("Training food rating SVD model...")
            self.food_svd_model = SVD(
                n_factors=self.n_factors, n_epochs=self.n_epochs, random_state=42
            )

            self.food_trainset = food_dataset.build_full_trainset()
            self.food_svd_model.fit(self.food_trainset)

            # Train restaurant SVD model only if we have restaurant ratings
            if not self.restaurant_ratings_df.empty:
                # Prepare restaurant ratings for Surprise
                restaurant_reader = Reader(rating_scale=(1, 5))
                restaurant_dataset = Dataset.load_from_df(
                    self.restaurant_ratings_df[["user_id", "restaurant_id", "rating"]],
                    restaurant_reader,
                )

                logger.info("Training restaurant rating SVD model...")
                self.restaurant_svd_model = SVD(
                    n_factors=self.n_factors, n_epochs=self.n_epochs, random_state=42
                )

                self.restaurant_trainset = restaurant_dataset.build_full_trainset()
                self.restaurant_svd_model.fit(self.restaurant_trainset)
            else:
                logger.info("Skipping restaurant rating SVD model - no data available")
                self.restaurant_svd_model = None
                self.restaurant_trainset = None

            logger.info("✓ Both SVD models trained successfully")
            if self.restaurant_svd_model is None:
                logger.info("✓ Operating in food-only mode")
            return True

        except Exception as e:
            logger.error(f"✗ Model training failed: {str(e)}")
            return False

    def _validate_models(self) -> Dict[str, Dict[str, float]]:
        """Step 4: Validate models using RMSE and MAE"""
        try:
            logger.info("Step 4: Validating models with RMSE and MAE")

            results = {}

            # Validate food rating model
            logger.info("Validating food rating model...")
            food_reader = Reader(rating_scale=(1, 5))
            food_dataset = Dataset.load_from_df(
                self.food_ratings_df[["user_id", "food_id", "rating"]], food_reader
            )

            # Calculate appropriate cv folds based on data size
            food_data_size = len(self.food_ratings_df)
            max_possible_folds = food_data_size
            food_cv_folds = max(2, min(5, max_possible_folds - 1))

            if food_data_size < 3:
                logger.warning(
                    f"Too few food ratings ({food_data_size}) for cross-validation. Using simple validation."
                )
                results["food_model"] = {
                    "rmse": 0.0,
                    "mae": 0.0,
                    "rmse_std": 0.0,
                    "mae_std": 0.0,
                    "note": f"Insufficient data for cross-validation ({food_data_size} ratings)",
                }
            else:
                food_cv_folds = min(food_cv_folds, food_data_size - 1)
                if food_cv_folds < 2:
                    food_cv_folds = 2

                logger.info(
                    f"Using {food_cv_folds}-fold cross-validation for {food_data_size} food ratings"
                )

                food_cv_results = cross_validate(
                    SVD(
                        n_factors=self.n_factors,
                        n_epochs=self.n_epochs,
                        random_state=42,
                    ),
                    food_dataset,
                    measures=["RMSE", "MAE"],
                    cv=food_cv_folds,
                    verbose=False,
                )

                results["food_model"] = {
                    "rmse": float(np.mean(food_cv_results["test_rmse"])),
                    "mae": float(np.mean(food_cv_results["test_mae"])),
                    "rmse_std": float(np.std(food_cv_results["test_rmse"])),
                    "mae_std": float(np.std(food_cv_results["test_mae"])),
                }

            # Validate restaurant rating model only if we have data and model
            if (
                not self.restaurant_ratings_df.empty
                and self.restaurant_svd_model is not None
            ):
                logger.info("Validating restaurant rating model...")
                restaurant_reader = Reader(rating_scale=(1, 5))
                restaurant_dataset = Dataset.load_from_df(
                    self.restaurant_ratings_df[["user_id", "restaurant_id", "rating"]],
                    restaurant_reader,
                )

                restaurant_data_size = len(self.restaurant_ratings_df)
                max_possible_folds = restaurant_data_size
                restaurant_cv_folds = max(2, min(5, max_possible_folds - 1))

                if restaurant_data_size < 3:
                    logger.warning(
                        f"Too few restaurant ratings ({restaurant_data_size}) for cross-validation. Using simple validation."
                    )
                    results["restaurant_model"] = {
                        "rmse": 0.0,
                        "mae": 0.0,
                        "rmse_std": 0.0,
                        "mae_std": 0.0,
                        "note": f"Insufficient data for cross-validation ({restaurant_data_size} ratings)",
                    }
                else:
                    restaurant_cv_folds = min(
                        restaurant_cv_folds, restaurant_data_size - 1
                    )
                    if restaurant_cv_folds < 2:
                        restaurant_cv_folds = 2

                    logger.info(
                        f"Using {restaurant_cv_folds}-fold cross-validation for {restaurant_data_size} restaurant ratings"
                    )

                    restaurant_cv_results = cross_validate(
                        SVD(
                            n_factors=self.n_factors,
                            n_epochs=self.n_epochs,
                            random_state=42,
                        ),
                        restaurant_dataset,
                        measures=["RMSE", "MAE"],
                        cv=restaurant_cv_folds,
                        verbose=False,
                    )

                    results["restaurant_model"] = {
                        "rmse": float(np.mean(restaurant_cv_results["test_rmse"])),
                        "mae": float(np.mean(restaurant_cv_results["test_mae"])),
                        "rmse_std": float(np.std(restaurant_cv_results["test_rmse"])),
                        "mae_std": float(np.std(restaurant_cv_results["test_mae"])),
                    }
            else:
                logger.info(
                    "Skipping restaurant rating model validation - no data/model available"
                )
                results["restaurant_model"] = {
                    "rmse": None,
                    "mae": None,
                    "rmse_std": None,
                    "mae_std": None,
                    "note": "No restaurant ratings available",
                }

            # Log validation results
            logger.info("✓ Validation Results:")
            if "note" in results["food_model"]:
                logger.info(f"  Food Model - {results['food_model']['note']}")
            else:
                logger.info(
                    f"  Food Model - RMSE: {results['food_model']['rmse']:.4f} ± {results['food_model']['rmse_std']:.4f}"
                )
                logger.info(
                    f"  Food Model - MAE: {results['food_model']['mae']:.4f} ± {results['food_model']['mae_std']:.4f}"
                )

            if results["restaurant_model"]["rmse"] is not None:
                if "note" in results["restaurant_model"]:
                    logger.info(
                        f"  Restaurant Model - {results['restaurant_model']['note']}"
                    )
                else:
                    logger.info(
                        f"  Restaurant Model - RMSE: {results['restaurant_model']['rmse']:.4f} ± {results['restaurant_model']['rmse_std']:.4f}"
                    )
                    logger.info(
                        f"  Restaurant Model - MAE: {results['restaurant_model']['mae']:.4f} ± {results['restaurant_model']['mae_std']:.4f}"
                    )
            else:
                logger.info(
                    f"  Restaurant Model - {results['restaurant_model']['note']}"
                )

            return results

        except Exception as e:
            logger.error(f"✗ Model validation failed: {str(e)}")
            return {}

    def predict_hybrid_recommendations(
        self, user_id: Any, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Step 5: Generate hybrid predictions combining food and restaurant ratings
        Optimized by using anti_testset for batch predictions instead of individual loops.

        Args:
            user_id: User ID to generate recommendations for
            limit: Number of recommendations to return

        Returns:
            List of recommended foods with hybrid scores
        """
        try:
            logger.info(f"Generating hybrid recommendations for user {user_id}")

            # Ensure user_id matches the type in data (assuming it's consistent, e.g., int or str)
            # If needed, convert: user_id = int(user_id) if isinstance(user_id, str) else user_id

            # Get all foods
            foods = Food.query.all()
            if not foods:
                logger.warning("No foods found")
                return []

            # Get user's existing food ratings to exclude
            user_food_ratings = set(
                self.food_ratings_df[self.food_ratings_df["user_id"] == user_id][
                    "food_id"
                ].values
            )

            # Build anti-testset for food: only unseen foods
            food_anti_testset = [
                (user_id, food.id, 0)  # dummy rating 0
                for food in foods
                if food.id not in user_food_ratings
            ]

            if not food_anti_testset:
                logger.warning("No unseen foods for user")
                return []

            # Predict batch for foods
            food_predictions = self.food_svd_model.test(food_anti_testset)
            food_pred_dict = {pred.iid: pred.est for pred in food_predictions}

            # For restaurants: get unique restaurants from foods
            restaurant_ids = set(
                food.restaurant_id for food in foods if food.restaurant_id
            )
            if self.restaurant_svd_model is not None:
                # Build anti-testset for restaurants (all, since we may not have user restaurant ratings)
                restaurant_anti_testset = [(user_id, rid, 0) for rid in restaurant_ids]
                restaurant_predictions = self.restaurant_svd_model.test(
                    restaurant_anti_testset
                )
                restaurant_pred_dict = {
                    pred.iid: pred.est for pred in restaurant_predictions
                }
            else:
                restaurant_pred_dict = {}

            recommendations = []

            # Now, process each unseen food
            for food in foods:
                if food.id in user_food_ratings:
                    continue

                try:
                    food_score = food_pred_dict.get(
                        food.id, 2.5
                    )  # default neutral if missing

                    restaurant_score = 2.5  # default neutral
                    if food.restaurant_id:
                        if self.restaurant_svd_model is not None:
                            restaurant_score = restaurant_pred_dict.get(
                                food.restaurant_id, 2.5
                            )
                        else:
                            restaurant_score = food_score  # Fallback to food score

                    # Normalize scores to 0-1 range
                    food_normalized = (food_score - 1.0) / 4.0
                    restaurant_normalized = (restaurant_score - 1.0) / 4.0

                    # Calculate hybrid score
                    effective_alpha = (
                        1.0 if self.restaurant_svd_model is None else self.alpha
                    )
                    hybrid_score = (effective_alpha * food_normalized) + (
                        (1 - effective_alpha) * restaurant_normalized
                    )

                    # Convert back to 1-5 scale
                    final_rating = 1.0 + (hybrid_score * 4.0)

                    recommendation = {
                        "food_id": food.id,
                        "food_name": food.name,
                        "food_description": food.description,
                        "food_price": food.price,
                        "restaurant_id": food.restaurant_id,
                        "restaurant_name": (
                            food.restaurant.name if food.restaurant_id else None
                        ),
                        "predicted_food_rating": round(food_score, 2),
                        "predicted_restaurant_rating": round(restaurant_score, 2),
                        "food_score_normalized": round(food_normalized, 3),
                        "restaurant_score_normalized": round(restaurant_normalized, 3),
                        "hybrid_score": round(hybrid_score, 3),
                        "final_predicted_rating": round(final_rating, 2),
                        "alpha_weight": effective_alpha,
                        "using_food_only": self.restaurant_svd_model is None,
                    }

                    recommendations.append(recommendation)

                except Exception as e:
                    logger.warning(f"Error predicting for food {food.id}: {str(e)}")
                    continue

            # Sort by hybrid score descending and limit
            recommendations.sort(key=lambda x: x["hybrid_score"], reverse=True)
            top_recommendations = recommendations[:limit]

            logger.info(
                f"✓ Generated {len(top_recommendations)} hybrid recommendations"
            )
            if self.restaurant_svd_model is None:
                logger.info(
                    "✓ Using food ratings only (no restaurant ratings available)"
                )

            return top_recommendations

        except Exception as e:
            logger.error(f"✗ Prediction failed: {str(e)}")
            return []

    def train_full_system(self) -> Dict[str, Any]:
        """
        Execute all 4 steps of the recommendation system

        Returns:
            Dictionary containing training results and validation metrics
        """
        logger.info("Starting full hybrid recommendation system training")

        results = {
            "success": False,
            "steps_completed": [],
            "validation_metrics": {},
            "error": None,
        }

        try:
            # Step 1: Import modules
            if not self._import_modules():
                results["error"] = "Module import failed"
                return results
            results["steps_completed"].append("import_modules")

            # Step 2: Prepare data
            if not self._prepare_data():
                results["error"] = "Data preparation failed"
                return results
            results["steps_completed"].append("prepare_data")

            # Step 3: Train models
            if not self._train_and_test_models():
                results["error"] = "Model training failed"
                return results
            results["steps_completed"].append("train_models")

            # Step 4: Validate models
            validation_results = self._validate_models()
            if not validation_results:
                results["error"] = "Model validation failed"
                return results
            results["steps_completed"].append("validate_models")
            results["validation_metrics"] = validation_results

            results["success"] = True
            logger.info(
                "✓ Hybrid recommendation system training completed successfully"
            )

        except Exception as e:
            results["error"] = str(e)
            logger.error(f"✗ Training failed: {str(e)}")

        return results

    def get_recommendations(
        self,
        user_id: Any,
        user_price_preferences: Optional[Dict] = None,
        price_filter: Optional[Dict] = None,
        n: int = 10,
        alpha: Optional[float] = None,
        beta: float = 0.2,
        gamma: float = 0.2,
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations using the hybrid system with detailed food and restaurant information
        """
        try:
            # Use instance alpha if not provided
            if alpha is None:
                alpha = self.alpha

            # Use hybrid system for recommendations
            recommendations = self.predict_hybrid_recommendations(
                user_id, n * 2
            )  # Get more for filtering

            if not recommendations:
                return []

            # Get detailed information for each food
            detailed_recommendations = []

            for rec in recommendations:
                try:
                    # Get food details
                    food = Food.query.get(rec["food_id"])
                    if not food:
                        continue

                    food_dict = food.to_dict()

                    # Add restaurant details if available
                    restaurant_dict = None
                    if food.restaurant_id:
                        restaurant = Restaurant.query.get(food.restaurant_id)
                        if restaurant:
                            restaurant_dict = restaurant.to_dict()

                            # Add restaurant ratings statistics
                            from sqlalchemy import func

                            restaurant_rating_stats = (
                                db.session.query(
                                    func.avg(RestaurantRating.rating).label("average"),
                                    func.count(RestaurantRating.rating).label("count"),
                                )
                                .filter(RestaurantRating.restaurant_id == restaurant.id)
                                .first()
                            )

                            restaurant_dict["average_rating"] = round(
                                float(restaurant_rating_stats.average or 0), 2
                            )
                            restaurant_dict["rating_count"] = (
                                restaurant_rating_stats.count or 0
                            )

                    # Add food rating statistics
                    from sqlalchemy import func

                    food_rating_stats = (
                        db.session.query(
                            func.avg(FoodRating.rating).label("average"),
                            func.count(FoodRating.rating).label("count"),
                        )
                        .filter(FoodRating.food_id == food.id)
                        .first()
                    )

                    food_dict["average_rating"] = round(
                        float(food_rating_stats.average or 0), 2
                    )
                    food_dict["rating_count"] = food_rating_stats.count or 0

                    # Add restaurant to food dict
                    food_dict["restaurant"] = restaurant_dict

                    # Apply price filter if specified
                    if price_filter:
                        food_price = float(food_dict.get("price", 0))
                        min_price = price_filter.get("min_price")
                        max_price = price_filter.get("max_price")

                        if min_price and food_price < min_price:
                            continue
                        if max_price and food_price > max_price:
                            continue

                    # Calculate price score if preferences provided
                    price_score = 0.0
                    if user_price_preferences and user_id in user_price_preferences:
                        preferred_price = user_price_preferences[user_id]
                        food_price = float(food_dict.get("price", 0))
                        if preferred_price > 0:
                            price_diff = (
                                abs(food_price - preferred_price) / preferred_price
                            )
                            price_score = max(0, 1 - price_diff)  # 0-1 scale

                    # Calculate popularity score
                    popularity_score = min(
                        1.0, food_dict["rating_count"] / 10.0
                    )  # Normalize to 0-1

                    # Calculate final score
                    base_score = rec["final_predicted_rating"] / 5.0  # Normalize to 0-1
                    final_score = (
                        alpha * base_score
                        + beta * price_score
                        + gamma * popularity_score
                    )

                    formatted_rec = {
                        "food": food_dict,
                        "predicted_rating": rec["final_predicted_rating"],
                        "predicted_food_rating": rec["predicted_food_rating"],
                        "predicted_restaurant_rating": rec[
                            "predicted_restaurant_rating"
                        ],
                        "hybrid_score": rec["hybrid_score"],
                        "price_score": round(price_score, 3),
                        "popularity_score": round(popularity_score, 3),
                        "final_score": round(final_score, 3),
                        "alpha_weight": rec["alpha_weight"],
                        "using_food_only": rec["using_food_only"],
                    }

                    detailed_recommendations.append(formatted_rec)

                except Exception as food_error:
                    logger.warning(
                        f"Error processing food {rec.get('food_id')}: {str(food_error)}"
                    )
                    continue

            # Sort by final score and limit results
            detailed_recommendations.sort(key=lambda x: x["final_score"], reverse=True)
            final_recommendations = detailed_recommendations[:n]

            logger.info(
                f"Returning {len(final_recommendations)} detailed recommendations"
            )
            return final_recommendations

        except Exception as e:
            logger.error(f"Error in Recommendations.get_recommendations: {str(e)}")
            return []

    def get_popular_foods(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular foods with detailed information including ratings and restaurant data
        Optimized by using SQL query to aggregate and sort directly in the database.
        """
        try:
            from sqlalchemy import func, desc

            # Query popular foods with aggregate ratings, sorted by (avg_rating * 0.7 + normalized_count * 0.3) desc
            popular_query = (
                db.session.query(
                    Food,
                    func.coalesce(func.avg(FoodRating.rating), 0.0).label("avg_rating"),
                    func.coalesce(func.count(FoodRating.rating), 0).label(
                        "rating_count"
                    ),
                )
                .outerjoin(FoodRating, Food.id == FoodRating.food_id)
                .group_by(Food.id)
                .order_by(
                    desc(
                        (func.coalesce(func.avg(FoodRating.rating), 0.0) * 0.7)
                        + (
                            func.least(
                                func.coalesce(func.count(FoodRating.rating), 0) / 10.0,
                                1.0,
                            )
                            * 0.3
                        )
                    )
                )
                .limit(n)
            )

            popular_foods = popular_query.all()

            result = []

            for food, avg_rating, count_rating in popular_foods:
                try:
                    # Get food dictionary
                    food_dict = food.to_dict()

                    # Format ratings
                    food_dict["average_rating"] = round(float(avg_rating), 2)
                    food_dict["rating_count"] = int(count_rating)

                    # Get restaurant information with ratings
                    restaurant_info = None
                    if food.restaurant_id:
                        restaurant = Restaurant.query.get(food.restaurant_id)
                        if restaurant:
                            restaurant_dict = restaurant.to_dict()

                            # Get restaurant ratings
                            restaurant_rating_query = (
                                db.session.query(
                                    func.coalesce(
                                        func.avg(RestaurantRating.rating), 0.0
                                    ).label("average"),
                                    func.coalesce(
                                        func.count(RestaurantRating.rating), 0
                                    ).label("count"),
                                )
                                .filter(RestaurantRating.restaurant_id == restaurant.id)
                                .first()
                            )

                            restaurant_dict["average_rating"] = round(
                                float(restaurant_rating_query.average), 2
                            )
                            restaurant_dict["rating_count"] = int(
                                restaurant_rating_query.count
                            )

                            restaurant_info = restaurant_dict

                    # Add restaurant to food dict
                    food_dict["restaurant"] = restaurant_info

                    # Ensure price is a float
                    food_dict["price"] = float(food_dict.get("price", 0.0))

                    # Calculate popularity score for consistency
                    normalized_count = min(count_rating / 10.0, 1.0)
                    popularity_score = avg_rating * 0.7 + normalized_count * 0.3

                    # Add to result
                    result.append(
                        {
                            "food": food_dict,
                            "popularity_score": round(popularity_score, 3),
                            "predicted_rating": avg_rating if avg_rating > 0 else 3.0,
                        }
                    )

                except Exception as food_error:
                    logger.warning(
                        f"Error processing popular food {food.id}: {str(food_error)}"
                    )
                    continue

            logger.info(f"Returning {len(result)} popular foods")
            return result

        except Exception as e:
            logger.error(f"Error getting popular foods: {str(e)}")
            return []
