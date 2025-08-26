"""
Restaurant Data Service

This module handles complex data aggregation, statistics, and enriched data operations
for restaurants. It provides a clean separation between simple repository operations
and complex business data logic.
"""

from app.modules.restaurant.repository import RestaurantRepository
from app.utils import api_logger as logger


class RestaurantDataService:
    """Service for complex restaurant data operations and aggregation"""

    @staticmethod
    def get_enriched_restaurant_list(page=1, limit=20, search=None):
        """
        Get enriched restaurant list with statistics and metadata.

        Args:
            page (int): Page number
            limit (int): Items per page
            search (str): Search term

        Returns:
            dict: Enriched restaurant data with statistics
        """
        try:
            # Get basic repository data
            result = RestaurantRepository.get_all(page=page, limit=limit, search=search)

            # Enrich the data with additional information
            enriched_restaurants = []
            for restaurant in result["items"]:
                enriched_data = restaurant.to_dict()
                # Add any additional computed fields here if needed
                enriched_restaurants.append(enriched_data)

            # Add metadata
            return {
                "restaurants": enriched_restaurants,
                "pagination": {
                    "page": result["page"],
                    "limit": result["limit"],
                    "total": result["total"],
                    "pages": result["pages"],
                },
                "metadata": {
                    "count": len(enriched_restaurants),
                    "search_applied": search is not None,
                    "search_term": search,
                },
            }
        except Exception as e:
            logger.error(f"Error getting enriched restaurant list: {str(e)}")
            raise e

    @staticmethod
    def get_active_restaurants_summary():
        """
        Get summary of active restaurants.

        Returns:
            dict: Summary of active restaurants
        """
        try:
            restaurants = RestaurantRepository.get_active()

            # Calculate summary statistics
            total_count = len(restaurants)

            # Group by additional criteria if needed
            summary = {
                "total_active_restaurants": total_count,
                "restaurants": [restaurant.to_dict() for restaurant in restaurants],
            }

            return summary
        except Exception as e:
            logger.error(f"Error getting active restaurants summary: {str(e)}")
            raise e

    @staticmethod
    def get_location_based_restaurants(latitude, longitude, radius_km=5):
        """
        Get restaurants near location with distance calculations and enriched data.

        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            radius_km (float): Search radius in kilometers

        Returns:
            dict: Location-based restaurant data with distances
        """
        try:
            restaurants = RestaurantRepository.get_by_location(
                latitude, longitude, radius_km
            )

            # Enrich with distance calculations and additional data
            enriched_restaurants = []
            for restaurant in restaurants:
                restaurant_data = restaurant.to_dict()

                # Calculate approximate distance using Haversine formula
                distance = RestaurantDataService._calculate_distance(
                    latitude, longitude, restaurant.latitude, restaurant.longitude
                )
                restaurant_data["distance_km"] = round(distance, 2)

                enriched_restaurants.append(restaurant_data)

            # Sort by distance
            enriched_restaurants.sort(key=lambda x: x["distance_km"])

            return {
                "restaurants": enriched_restaurants,
                "search_criteria": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_km": radius_km,
                },
                "metadata": {
                    "count": len(enriched_restaurants),
                    "max_distance_km": (
                        max([r["distance_km"] for r in enriched_restaurants])
                        if enriched_restaurants
                        else 0
                    ),
                    "min_distance_km": (
                        min([r["distance_km"] for r in enriched_restaurants])
                        if enriched_restaurants
                        else 0
                    ),
                },
            }
        except Exception as e:
            logger.error(f"Error getting location-based restaurants: {str(e)}")
            raise e

    @staticmethod
    def get_restaurant_statistics():
        """
        Get overall restaurant statistics.

        Returns:
            dict: Restaurant statistics
        """
        try:
            # Get all restaurants for statistics
            all_restaurants_result = RestaurantRepository.get_all(
                page=1, limit=1000
            )  # Get a large number to cover all
            all_restaurants = all_restaurants_result["items"]
            active_restaurants = RestaurantRepository.get_active()

            # Calculate statistics
            total_restaurants = all_restaurants_result["total"]
            active_count = len(active_restaurants)
            inactive_count = total_restaurants - active_count

            # Calculate rating statistics if restaurants have ratings
            ratings_data = []
            for restaurant in all_restaurants:
                if hasattr(restaurant, "rating_average") and restaurant.rating_average:
                    ratings_data.append(restaurant.rating_average)

            avg_rating = sum(ratings_data) / len(ratings_data) if ratings_data else 0

            return {
                "total_restaurants": total_restaurants,
                "active_restaurants": active_count,
                "inactive_restaurants": inactive_count,
                "activity_percentage": (
                    round((active_count / total_restaurants * 100), 2)
                    if total_restaurants > 0
                    else 0
                ),
                "rating_statistics": {
                    "restaurants_with_ratings": len(ratings_data),
                    "average_rating": round(avg_rating, 2),
                    "highest_rating": max(ratings_data) if ratings_data else 0,
                    "lowest_rating": min(ratings_data) if ratings_data else 0,
                },
            }
        except Exception as e:
            logger.error(f"Error getting restaurant statistics: {str(e)}")
            raise e

    @staticmethod
    def search_restaurants_enhanced(search_term):
        """
        Enhanced restaurant search with additional context.

        Args:
            search_term (str): Search term

        Returns:
            dict: Enhanced search results
        """
        try:
            restaurants = RestaurantRepository.search_by_name(search_term)

            # Enrich search results
            enriched_results = []
            for restaurant in restaurants:
                restaurant_data = restaurant.to_dict()
                # Add search relevance or other computed fields if needed
                enriched_results.append(restaurant_data)

            return {
                "restaurants": enriched_results,
                "search_term": search_term,
                "metadata": {
                    "count": len(enriched_results),
                    "has_results": len(enriched_results) > 0,
                },
            }
        except Exception as e:
            logger.error(f"Error in enhanced restaurant search: {str(e)}")
            raise e

    @staticmethod
    def get_restaurant_with_context(restaurant_id):
        """
        Get restaurant with additional context and related data.

        Args:
            restaurant_id (str): Restaurant ID

        Returns:
            dict: Restaurant with enriched context and detailed information
        """
        try:
            restaurant = RestaurantRepository.get_by_id(restaurant_id)
            if not restaurant:
                return None

            restaurant_data = restaurant.to_dict()

            # Add enhanced context with detailed information
            context = {
                "location": {
                    "latitude": restaurant.latitude,
                    "longitude": restaurant.longitude,
                    "address": restaurant.address,
                },
                "status": {
                    "is_active": restaurant.is_active,
                    "rating_level": RestaurantDataService._get_rating_level(
                        restaurant.rating_average
                    ),
                },
                "timestamps": {
                    "created_at": restaurant_data["created_at"],
                    "updated_at": restaurant_data["updated_at"],
                },
            }

            # Add related counts if available (foods, ratings, etc.)
            try:
                # Get categories
                categories = []
                if hasattr(restaurant, "categories") and restaurant.categories:
                    categories = [
                        category.to_dict() for category in restaurant.categories
                    ]

                # Get foods with main image
                foods = []
                if hasattr(restaurant, "foods") and restaurant.foods:
                    from app.modules.food.service import FoodService

                    foods = [
                        FoodService.to_dict_with_main_image(food)
                        for food in restaurant.foods
                    ]

                context["related_data"] = {
                    "categories": categories,
                    "foods": foods,
                }
            except Exception as e:
                logger.warning(f"Could not load related data counts: {str(e)}")
                context["related_data"] = {
                    "categories": [],
                    "foods": [],
                }

            return {
                "restaurant": restaurant_data,
                "context": context,
            }
        except Exception as e:
            logger.error(f"Error getting restaurant with context: {str(e)}")
            raise e

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates

        Returns:
            float: Distance in kilometers
        """
        import math

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers
        r = 6371

        return c * r

    @staticmethod
    def _get_rating_level(rating):
        """
        Get rating level description based on numeric rating.

        Args:
            rating (float): Numeric rating

        Returns:
            str: Rating level description
        """
        if rating >= 4.5:
            return "Excellent"
        elif rating >= 4.0:
            return "Very Good"
        elif rating >= 3.5:
            return "Good"
        elif rating >= 3.0:
            return "Average"
        elif rating > 0:
            return "Below Average"
        else:
            return "No Rating"

    @staticmethod
    def _is_recently_updated(updated_at):
        """
        Check if restaurant was recently updated (within last 30 days).

        Args:
            updated_at (datetime): Last update timestamp

        Returns:
            bool: True if recently updated
        """
        if not updated_at:
            return False

        from datetime import datetime, timezone, timedelta

        # Calculate days since last update
        now = datetime.now(timezone.utc)
        # Ensure updated_at is timezone aware
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        days_since_update = (now - updated_at).days
        return days_since_update <= 30

    @staticmethod
    def _calculate_age_days(created_at):
        """
        Calculate age of restaurant in days.

        Args:
            created_at (datetime): Creation timestamp

        Returns:
            int: Age in days
        """
        if not created_at:
            return 0

        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        # Ensure created_at is timezone aware
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return (now - created_at).days

    @staticmethod
    def get_simple_restaurant_list():
        """
        Get simple restaurant list for dropdown/selection purposes.

        Returns:
            list: Simple list of restaurants with id and name
        """
        try:
            return RestaurantRepository.get_restaurant_list()
        except Exception as e:
            logger.error(f"Error getting simple restaurant list: {str(e)}")
            raise e
