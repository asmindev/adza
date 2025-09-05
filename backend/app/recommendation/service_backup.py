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

from app.modules.rating.models import FoodRating, RestaurantRating
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant
from app.modules.user.models import User
from app.utils import training_logger as logger

warnings.filterwarnings('ignore')


class HybridRecommendationSystem:
    """
    Hybrid Recommendation System that combines:
    1. Food ratings (collaborative filtering with SVD)
    2. Restaurant ratings (collaborative filtering with SVD)
    Combined with alpha parameter weighting
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
        
        # Scalers for normalization
        self.food_scaler = MinMaxScaler()
        self.restaurant_scaler = MinMaxScaler()
        
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
            self.food_ratings_df = pd.DataFrame(food_data, columns=['user_id', 'food_id', 'rating'])
            
            # Get restaurant ratings
            restaurant_ratings = RestaurantRating.query.all()
            if not restaurant_ratings:
                logger.warning("No restaurant ratings found")
                return False
            
            # Convert restaurant ratings to DataFrame
            restaurant_data = [(r.user_id, r.restaurant_id, float(r.rating)) for r in restaurant_ratings]
            self.restaurant_ratings_df = pd.DataFrame(restaurant_data, columns=['user_id', 'restaurant_id', 'rating'])
            
            # Clean data
            self.food_ratings_df = self.food_ratings_df.dropna()
            self.restaurant_ratings_df = self.restaurant_ratings_df.dropna()
            
            # Validate rating ranges
            self.food_ratings_df = self.food_ratings_df[
                (self.food_ratings_df['rating'] >= 1.0) & 
                (self.food_ratings_df['rating'] <= 5.0)
            ]
            self.restaurant_ratings_df = self.restaurant_ratings_df[
                (self.restaurant_ratings_df['rating'] >= 1.0) & 
                (self.restaurant_ratings_df['rating'] <= 5.0)
            ]
            
            logger.info(f"✓ Food ratings: {len(self.food_ratings_df)} records")
            logger.info(f"✓ Restaurant ratings: {len(self.restaurant_ratings_df)} records")
            logger.info(f"✓ Food rating range: {self.food_ratings_df['rating'].min():.1f} - {self.food_ratings_df['rating'].max():.1f}")
            logger.info(f"✓ Restaurant rating range: {self.restaurant_ratings_df['rating'].min():.1f} - {self.restaurant_ratings_df['rating'].max():.1f}")
            
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
                self.food_ratings_df[['user_id', 'food_id', 'rating']], 
                food_reader
            )
            
            # Prepare restaurant ratings for Surprise
            restaurant_reader = Reader(rating_scale=(1, 5))
            restaurant_dataset = Dataset.load_from_df(
                self.restaurant_ratings_df[['user_id', 'restaurant_id', 'rating']], 
                restaurant_reader
            )
            
            # Train food SVD model
            logger.info("Training food rating SVD model...")
            self.food_svd_model = SVD(
                n_factors=self.n_factors,
                n_epochs=self.n_epochs,
                random_state=42
            )
            
            food_trainset = food_dataset.build_full_trainset()
            self.food_svd_model.fit(food_trainset)
            
            # Train restaurant SVD model
            logger.info("Training restaurant rating SVD model...")
            self.restaurant_svd_model = SVD(
                n_factors=self.n_factors,
                n_epochs=self.n_epochs,
                random_state=42
            )
            
            restaurant_trainset = restaurant_dataset.build_full_trainset()
            self.restaurant_svd_model.fit(restaurant_trainset)
            
            logger.info("✓ Both SVD models trained successfully")
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
                self.food_ratings_df[['user_id', 'food_id', 'rating']], 
                food_reader
            )
            
            food_cv_results = cross_validate(
                self.food_svd_model, 
                food_dataset, 
                measures=['RMSE', 'MAE'], 
                cv=min(5, len(self.food_ratings_df) // 10),
                verbose=False
            )
            
            results['food_model'] = {
                'rmse': float(np.mean(food_cv_results['test_rmse'])),
                'mae': float(np.mean(food_cv_results['test_mae'])),
                'rmse_std': float(np.std(food_cv_results['test_rmse'])),
                'mae_std': float(np.std(food_cv_results['test_mae']))
            }
            
            # Validate restaurant rating model
            logger.info("Validating restaurant rating model...")
            restaurant_reader = Reader(rating_scale=(1, 5))
            restaurant_dataset = Dataset.load_from_df(
                self.restaurant_ratings_df[['user_id', 'restaurant_id', 'rating']], 
                restaurant_reader
            )
            
            restaurant_cv_results = cross_validate(
                self.restaurant_svd_model, 
                restaurant_dataset, 
                measures=['RMSE', 'MAE'], 
                cv=min(5, len(self.restaurant_ratings_df) // 10),
                verbose=False
            )
            
            results['restaurant_model'] = {
                'rmse': float(np.mean(restaurant_cv_results['test_rmse'])),
                'mae': float(np.mean(restaurant_cv_results['test_mae'])),
                'rmse_std': float(np.std(restaurant_cv_results['test_rmse'])),
                'mae_std': float(np.std(restaurant_cv_results['test_mae']))
            }
            
            # Log validation results
            logger.info("✓ Validation Results:")
            logger.info(f"  Food Model - RMSE: {results['food_model']['rmse']:.4f} ± {results['food_model']['rmse_std']:.4f}")
            logger.info(f"  Food Model - MAE: {results['food_model']['mae']:.4f} ± {results['food_model']['mae_std']:.4f}")
            logger.info(f"  Restaurant Model - RMSE: {results['restaurant_model']['rmse']:.4f} ± {results['restaurant_model']['rmse_std']:.4f}")
            logger.info(f"  Restaurant Model - MAE: {results['restaurant_model']['mae']:.4f} ± {results['restaurant_model']['mae_std']:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Model validation failed: {str(e)}")
            return {}
    
    def predict_hybrid_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Step 5: Generate hybrid predictions combining food and restaurant ratings
        
        Args:
            user_id: User ID to generate recommendations for
            limit: Number of recommendations to return
            
        Returns:
            List of recommended foods with hybrid scores
        """
        try:
            logger.info(f"Generating hybrid recommendations for user {user_id}")
            
            # Get all foods and their restaurants
            foods = Food.query.all()
            if not foods:
                logger.warning("No foods found")
                return []
            
            # Get user's existing food ratings
            user_food_ratings = set(
                self.food_ratings_df[self.food_ratings_df['user_id'] == user_id]['food_id'].values
            )
            
            recommendations = []
            
            for food in foods:
                # Skip foods already rated by user
                if food.id in user_food_ratings:
                    continue
                
                try:
                    # Predict food rating
                    food_prediction = self.food_svd_model.predict(user_id, food.id)
                    food_score = food_prediction.est
                    
                    # Get restaurant for this food
                    restaurant = Restaurant.query.get(food.restaurant_id)
                    restaurant_score = 2.5  # default neutral score
                    
                    if restaurant:
                        # Predict restaurant rating
                        restaurant_prediction = self.restaurant_svd_model.predict(user_id, restaurant.id)
                        restaurant_score = restaurant_prediction.est
                    
                    # Normalize scores to 0-1 range
                    food_normalized = (food_score - 1.0) / 4.0  # Scale 1-5 to 0-1
                    restaurant_normalized = (restaurant_score - 1.0) / 4.0  # Scale 1-5 to 0-1
                    
                    # Calculate hybrid score using alpha parameter
                    hybrid_score = (self.alpha * food_normalized) + ((1 - self.alpha) * restaurant_normalized)
                    
                    # Convert back to 1-5 scale for final rating
                    final_rating = 1.0 + (hybrid_score * 4.0)
                    
                    recommendation = {
                        'food_id': food.id,
                        'food_name': food.name,
                        'food_description': food.description,
                        'food_price': food.price,
                        'restaurant_id': restaurant.id if restaurant else None,
                        'restaurant_name': restaurant.name if restaurant else None,
                        'predicted_food_rating': round(food_score, 2),
                        'predicted_restaurant_rating': round(restaurant_score, 2),
                        'food_score_normalized': round(food_normalized, 3),
                        'restaurant_score_normalized': round(restaurant_normalized, 3),
                        'hybrid_score': round(hybrid_score, 3),
                        'final_predicted_rating': round(final_rating, 2),
                        'alpha_weight': self.alpha
                    }
                    
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    logger.warning(f"Error predicting for food {food.id}: {str(e)}")
                    continue
            
            # Sort by hybrid score (descending) and limit results
            recommendations.sort(key=lambda x: x['hybrid_score'], reverse=True)
            top_recommendations = recommendations[:limit]
            
            logger.info(f"✓ Generated {len(top_recommendations)} hybrid recommendations")
            
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
            'success': False,
            'steps_completed': [],
            'validation_metrics': {},
            'error': None
        }
        
        try:
            # Step 1: Import modules
            if not self._import_modules():
                results['error'] = "Module import failed"
                return results
            results['steps_completed'].append('import_modules')
            
            # Step 2: Prepare data
            if not self._prepare_data():
                results['error'] = "Data preparation failed"
                return results
            results['steps_completed'].append('prepare_data')
            
            # Step 3: Train models
            if not self._train_and_test_models():
                results['error'] = "Model training failed"
                return results
            results['steps_completed'].append('train_models')
            
            # Step 4: Validate models
            validation_results = self._validate_models()
            if not validation_results:
                results['error'] = "Model validation failed"
                return results
            results['steps_completed'].append('validate_models')
            results['validation_metrics'] = validation_results
            
            results['success'] = True
            logger.info("✓ Hybrid recommendation system training completed successfully")
            
        except Exception as e:
            results['error'] = str(e)
            logger.error(f"✗ Training failed: {str(e)}")
        
        return results


# Convenience functions for easy usage
def create_and_train_hybrid_system(alpha: float = 0.7) -> HybridRecommendationSystem:
    """
    Create and train a new hybrid recommendation system
    
    Args:
        alpha: Weight for food ratings (0-1), restaurant weight = 1-alpha
        
    Returns:
        Trained HybridRecommendationSystem instance
    """
    system = HybridRecommendationSystem(alpha=alpha)
    results = system.train_full_system()
    
    if results['success']:
        logger.info("Hybrid recommendation system ready for predictions")
        return system
    else:
        logger.error(f"Failed to train system: {results['error']}")
        return None


def get_hybrid_recommendations(user_id: str, alpha: float = 0.7, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get hybrid recommendations for a user
    
    Args:
        user_id: User ID to generate recommendations for
        alpha: Weight for food ratings (0-1)
        limit: Number of recommendations to return
        
    Returns:
        List of recommended foods with hybrid scores
    """
    system = create_and_train_hybrid_system(alpha=alpha)
    if system:
        return system.predict_hybrid_recommendations(user_id, limit)
    return []
