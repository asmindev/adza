"""
Recommendation System Package
"""

from .service import RecommendationService
from .collaborative_filtering import CollaborativeFilteringRecommender
from .popular import PopularFoodRecommender

__all__ = [
    "RecommendationService",
    "CollaborativeFilteringRecommender",
    "PopularFoodRecommender",
]
