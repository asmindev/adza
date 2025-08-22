"""
Enhanced Rating System with Additional Parameters
Incorporates place quality, price preferences, and food quality into rating calculations
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from app.modules.rating.models import FoodRating
from app.modules.food.models import Food
from app.modules.restaurant.models import Restaurant
from app.modules.user.models import User
from app.utils import training_logger as logger


class EnhancedRatingCalculator:
    """
    Enhanced rating calculator that adjusts ratings based on additional parameters:
    - Place quality (restaurant quality score 1-5)
    - Price preferences (user price preference vs actual price)
    - Food quality (objective food quality score 1-5)
    """

    def __init__(self, alpha: float = 0.3, beta: float = 0.2, gamma: float = 0.2):
        """
        Initialize enhanced rating calculator

        Args:
            alpha: Weight for place quality adjustment (0-1)
            beta: Weight for price preference adjustment (0-1)
            gamma: Weight for food quality adjustment (0-1)
        """
        self.alpha = alpha  # Place quality weight
        self.beta = beta  # Price preference weight
        self.gamma = gamma  # Food quality weight

        # Ensure weights don't exceed 1.0 when combined
        total_weight = alpha + beta + gamma
        if total_weight > 1.0:
            logger.warning(
                f"Total adjustment weights ({total_weight}) exceed 1.0, normalizing..."
            )
            self.alpha = alpha / total_weight
            self.beta = beta / total_weight
            self.gamma = gamma / total_weight

    @staticmethod
    def normalize_to_range(value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range"""
        if max_val == min_val:
            return 0.5  # Return neutral if no variation
        return (value - min_val) / (max_val - min_val)

    def calculate_place_score(self, restaurant: Restaurant) -> float:
        """
        Calculate normalized place quality score using actual restaurant ratings
        This uses the RestaurantRating model to get real user ratings for the place/tempat

        Args:
            restaurant: Restaurant object

        Returns:
            Normalized place score (0-1)
        """
        if not restaurant:
            return 0.5  # Neutral score if no restaurant

        # Import here to avoid circular imports
        from app.modules.rating.repository import RestaurantRatingRepository

        try:
            # Get actual restaurant ratings from RestaurantRating table
            restaurant_ratings = RestaurantRatingRepository.get_by_restaurant_id(
                restaurant.id
            )

            if not restaurant_ratings:
                # If no specific restaurant ratings, fallback to restaurant.rating_average
                place_rating = restaurant.rating_average or 2.5
                logger.debug(
                    f"No restaurant ratings found for {restaurant.name}, using rating_average: {place_rating}"
                )
            else:
                # Calculate average from actual restaurant ratings (tempat/place quality)
                total_rating = sum(rating.rating for rating in restaurant_ratings)
                place_rating = total_rating / len(restaurant_ratings)
                logger.debug(
                    f"Calculated place quality for {restaurant.name}: {place_rating:.2f} from {len(restaurant_ratings)} ratings"
                )

            # Normalize to 0-1 range
            normalized_score = self.normalize_to_range(place_rating, 1.0, 5.0)
            logger.debug(
                f"Place score for {restaurant.name}: {normalized_score:.3f} (rating: {place_rating:.2f})"
            )

            return normalized_score

        except Exception as e:
            logger.warning(
                f"Error calculating place score for restaurant {restaurant.id}: {str(e)}"
            )
            # Fallback to restaurant rating_average
            place_rating = restaurant.rating_average or 2.5
            return self.normalize_to_range(place_rating, 1.0, 5.0)

    def calculate_price_score(self, food_price: float, user_price_pref: float) -> float:
        """
        Calculate normalized price preference score based on how close the food price
        is to the user's preferred price range

        Args:
            food_price: Actual price of the food
            user_price_pref: User's preferred price point

        Returns:
            Normalized price score (0-1), where 1.0 means perfect match
        """
        if not food_price or not user_price_pref:
            return 0.5  # Neutral score if price info unavailable

        # Calculate price difference ratio
        price_diff_ratio = abs(food_price - user_price_pref) / user_price_pref

        # Convert to similarity score (closer to preference = higher score)
        # Using exponential decay to penalize large price differences
        price_score = np.exp(-price_diff_ratio)

        return min(max(price_score, 0.0), 1.0)  # Ensure 0-1 range

    def calculate_food_quality_score(self, food: Food) -> float:
        """
        Calculate normalized food quality score
        For now, we'll use the food's average rating as a proxy for quality
        In future, this could be a separate field in the food model

        Args:
            food: Food object

        Returns:
            Normalized food quality score (0-1)
        """
        if not food or not food.ratings:
            return 0.5  # Neutral score if no ratings

        # Calculate average rating for the food
        total_rating = sum(rating.rating for rating in food.ratings)
        avg_rating = total_rating / len(food.ratings)

        return self.normalize_to_range(avg_rating, 1.0, 5.0)

    def calculate_adjusted_rating(
        self,
        original_rating: float,
        food: Food,
        user_price_pref: Optional[float] = None,
    ) -> float:
        """
        Calculate adjusted rating incorporating all additional parameters

        Args:
            original_rating: Original user rating (1-5)
            food: Food object
            user_price_pref: User's price preference

        Returns:
            Adjusted rating (1-5 range)
        """
        # Calculate component scores
        place_score = self.calculate_place_score(food.restaurant)
        price_score = (
            self.calculate_price_score(food.price, user_price_pref)
            if user_price_pref
            else 0.5
        )
        food_quality_score = self.calculate_food_quality_score(food)

        # Calculate adjustments (convert 0-1 scores to -2 to +2 adjustment range)
        place_adjustment = (place_score - 0.5) * 4  # -2 to +2
        price_adjustment = (price_score - 0.5) * 4  # -2 to +2
        quality_adjustment = (food_quality_score - 0.5) * 4  # -2 to +2

        # Apply weighted adjustments
        total_adjustment = (
            self.alpha * place_adjustment
            + self.beta * price_adjustment
            + self.gamma * quality_adjustment
        )

        # Calculate final adjusted rating
        adjusted_rating = original_rating + total_adjustment

        # Ensure rating stays within 1-5 range
        adjusted_rating = min(max(adjusted_rating, 1.0), 5.0)

        logger.debug(
            f"Rating adjustment: {original_rating:.2f} → {adjusted_rating:.2f} "
            f"(place: {place_adjustment:.2f}, price: {price_adjustment:.2f}, "
            f"quality: {quality_adjustment:.2f})"
        )

        return adjusted_rating

    def get_enhanced_ratings_dataset(
        self, user_price_preferences: Dict[str, float]
    ) -> List[Tuple[str, str, float]]:
        """
        Generate enhanced ratings dataset with adjusted ratings for SVD training

        Args:
            user_price_preferences: Dictionary mapping user_id to preferred price

        Returns:
            List of tuples (user_id, food_id, adjusted_rating) ready for SVD training
        """
        logger.info("Generating enhanced ratings dataset...")

        # Get all ratings
        ratings = FoodRating.query.all()
        enhanced_dataset = []

        for rating in ratings:
            # Get user price preference
            user_price_pref = user_price_preferences.get(rating.user_id)

            # Get food object to access price and restaurant info
            food = Food.query.get(rating.food_id)
            if not food:
                logger.warning(f"Food {rating.food_id} not found, skipping rating")
                continue

            # Calculate adjusted rating
            adjusted_rating = self.calculate_adjusted_rating(
                rating.rating, food, user_price_pref
            )

            enhanced_dataset.append((rating.user_id, rating.food_id, adjusted_rating))

        logger.info(f"Generated {len(enhanced_dataset)} enhanced ratings")
        return enhanced_dataset


# Convenience function for backward compatibility
def get_enhanced_ratings_for_svd(
    user_price_preferences: Dict[str, float],
    alpha: float = 0.3,
    beta: float = 0.2,
    gamma: float = 0.2,
) -> List[Tuple[str, str, float]]:
    """
    Convenience function to get enhanced ratings dataset

    Args:
        user_price_preferences: Dictionary mapping user_id to preferred price
        alpha: Weight for place quality adjustment
        beta: Weight for price preference adjustment
        gamma: Weight for food quality adjustment

    Returns:
        List of tuples (user_id, food_id, adjusted_rating)
    """
    calculator = EnhancedRatingCalculator(alpha=alpha, beta=beta, gamma=gamma)
    return calculator.get_enhanced_ratings_dataset(user_price_preferences)
