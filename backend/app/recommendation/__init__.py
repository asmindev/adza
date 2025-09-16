"""
Recommendation System Package
"""

from .recommender import Recommendations
from .service import RecommendationService, recommendation_service

__all__ = [
    "Recommendations",
    "RecommendationService",
    "recommendation_service",
]
