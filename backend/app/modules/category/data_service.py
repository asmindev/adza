"""
Category data service for handling complex category data operations
This handles data aggregation and business logic related to category data presentation
"""

from .models import Category, UserFavoriteCategory
from .repository import CategoryRepository, UserFavoriteCategoryRepository
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CategoryDataService:
    """Service for handling category data aggregation and complex operations"""

    @staticmethod
    def get_categories_with_stats() -> List[Dict[str, Any]]:
        """
        Get all categories with additional statistics
        """
        logger.debug("Getting categories with statistics")

        try:
            categories = CategoryRepository.get_all_active()
            result = []

            for category in categories:
                category_data = category.to_dict()

                # Add favorite count
                favorite_count = (
                    UserFavoriteCategoryRepository.get_category_favorite_count(
                        category.id
                    )
                )
                category_data["favorite_count"] = favorite_count

                # Add restaurant count (if needed - would require restaurant service)
                # restaurant_count = RestaurantRepository.count_by_category(category.id)
                # category_data["restaurant_count"] = restaurant_count

                result.append(category_data)

            # Sort by favorite count (most popular first)
            result.sort(key=lambda x: x.get("favorite_count", 0), reverse=True)

            logger.info(f"Successfully retrieved {len(result)} categories with stats")
            return result

        except Exception as e:
            logger.error(f"Error getting categories with stats: {str(e)}")
            return []

    @staticmethod
    def get_category_with_details(category_id: str) -> Optional[Dict[str, Any]]:
        """
        Get category with detailed information including statistics
        """
        logger.debug(f"Getting detailed information for category: {category_id}")

        try:
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return None

            category_data = category.to_dict()

            # Add statistics
            favorite_count = UserFavoriteCategoryRepository.get_category_favorite_count(
                category.id
            )
            category_data["favorite_count"] = favorite_count

            # Add related data counts
            category_data["statistics"] = {
                "total_favorites": favorite_count,
                # "total_restaurants": RestaurantRepository.count_by_category(category.id),
                # "total_foods": FoodRepository.count_by_category(category.id),
            }

            logger.info(
                f"Successfully retrieved detailed info for category {category_id}"
            )
            return category_data

        except Exception as e:
            logger.error(f"Error getting category details for {category_id}: {str(e)}")
            return None

    @staticmethod
    def get_user_favorite_categories_with_details(user_id: str) -> List[Dict[str, Any]]:
        """
        Get user's favorite categories with additional details and proper sorting
        """
        logger.debug(f"Getting favorite categories with details for user: {user_id}")

        try:
            favorites = UserFavoriteCategoryRepository.get_user_favorite_categories(
                user_id
            )
            result = []

            for favorite, category in favorites:
                category_data = category.to_dict()

                # Add favorite-specific data
                category_data["is_favorite"] = True
                category_data["favorited_at"] = (
                    favorite.created_at.isoformat() + "Z"
                    if favorite.created_at
                    else None
                )

                # Add additional stats
                favorite_count = (
                    UserFavoriteCategoryRepository.get_category_favorite_count(
                        category.id
                    )
                )
                category_data["favorite_count"] = favorite_count

                result.append(category_data)

            # Result is already sorted by favorited_at (most recent first) from repository

            logger.info(
                f"Successfully retrieved {len(result)} favorite categories for user {user_id}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Error getting user favorite categories for {user_id}: {str(e)}"
            )
            return []

    @staticmethod
    def get_trending_categories(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending categories based on recent favorites and activity
        """
        logger.debug(f"Getting trending categories (limit: {limit})")

        try:
            # Get most favorited categories
            trending = UserFavoriteCategoryRepository.get_most_favorite_categories(
                limit
            )
            result = []

            for category, favorite_count in trending:
                category_data = category.to_dict()
                category_data["favorite_count"] = favorite_count
                category_data["is_trending"] = True

                # Calculate trend score (can be enhanced with more complex logic)
                category_data["trend_score"] = favorite_count

                result.append(category_data)

            logger.info(f"Successfully retrieved {len(result)} trending categories")
            return result

        except Exception as e:
            logger.error(f"Error getting trending categories: {str(e)}")
            return []

    @staticmethod
    def search_categories_with_details(search_term: str) -> List[Dict[str, Any]]:
        """
        Search categories with additional details
        """
        logger.debug(f"Searching categories with details for term: {search_term}")

        try:
            categories = CategoryRepository.search_by_name(search_term)
            result = []

            for category in categories:
                category_data = category.to_dict()

                # Add stats for search results
                favorite_count = (
                    UserFavoriteCategoryRepository.get_category_favorite_count(
                        category.id
                    )
                )
                category_data["favorite_count"] = favorite_count

                # Add relevance score (simple text matching for now)
                name_lower = category.name.lower()
                search_lower = search_term.lower()

                if name_lower == search_lower:
                    category_data["relevance_score"] = 100
                elif name_lower.startswith(search_lower):
                    category_data["relevance_score"] = 80
                elif search_lower in name_lower:
                    category_data["relevance_score"] = 60
                else:
                    category_data["relevance_score"] = 40

                result.append(category_data)

            # Sort by relevance score, then by favorite count
            result.sort(
                key=lambda x: (x.get("relevance_score", 0), x.get("favorite_count", 0)),
                reverse=True,
            )

            logger.info(
                f"Successfully found {len(result)} categories for search term: {search_term}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Error searching categories for term '{search_term}': {str(e)}"
            )
            return []

    @staticmethod
    def get_category_analytics(category_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analytics data for a specific category
        """
        logger.debug(f"Getting analytics for category: {category_id}")

        try:
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return None

            # Basic analytics
            favorite_count = UserFavoriteCategoryRepository.get_category_favorite_count(
                category.id
            )

            analytics = {
                "category_id": category.id,
                "category_name": category.name,
                "total_favorites": favorite_count,
                "created_at": (
                    category.created_at.isoformat() + "Z"
                    if category.created_at
                    else None
                ),
                "last_updated": (
                    category.updated_at.isoformat() + "Z"
                    if category.updated_at
                    else None
                ),
                # More analytics can be added here:
                # "monthly_growth": calculate_monthly_growth(category.id),
                # "popular_times": get_popular_times(category.id),
                # "related_categories": get_related_categories(category.id),
            }

            logger.info(f"Successfully retrieved analytics for category {category_id}")
            return analytics

        except Exception as e:
            logger.error(
                f"Error getting analytics for category {category_id}: {str(e)}"
            )
            return None
