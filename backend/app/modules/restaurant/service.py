from app.modules.restaurant.repository import RestaurantRepository
from app.modules.restaurant.validators import RestaurantValidator
from app.modules.restaurant.data_service import RestaurantDataService
from app.utils import get_logger
logger = get_logger(__name__)


class RestaurantService:
    """Pure business logic for restaurant operations"""

    @staticmethod
    @staticmethod
    def create_restaurant(restaurant_data):
        """Create a new restaurant with validation"""
        try:
            # Log what fields are being processed
            logger.info(
                f"Restaurant service: Creating restaurant with fields: {list(restaurant_data.keys())}"
            )

            # Validate all data using validator
            validated_data = RestaurantValidator.validate_restaurant_creation_data(
                restaurant_data
            )

            # Create restaurant using repository
            restaurant = RestaurantRepository.create(validated_data)
            logger.info(f"Restaurant service: Created restaurant {restaurant.name}")
            return restaurant

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Restaurant service: Error creating restaurant - {str(e)}")
            raise e

    @staticmethod
    def get_all_restaurants(page=1, limit=20, search=None):
        """Get all restaurants with pagination and search"""
        try:
            # Validate pagination parameters
            validated_page, validated_limit = RestaurantValidator.validate_pagination(
                page, limit
            )

            # Validate search term
            validated_search = RestaurantValidator.validate_search_term(search)

            # Get enriched data from data service
            result = RestaurantDataService.get_enriched_restaurant_list(
                page=validated_page, limit=validated_limit, search=validated_search
            )

            logger.info(
                f"Restaurant service: Retrieved {result['metadata']['count']} restaurants"
            )
            return result

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Restaurant service: Error retrieving restaurants - {str(e)}")
            raise e

    @staticmethod
    def get_restaurant_by_id(restaurant_id):
        """Get restaurant by ID with validation"""
        try:
            # Validate restaurant ID
            validated_id = RestaurantValidator.validate_restaurant_id(restaurant_id)

            # Get restaurant with context from data service
            result = RestaurantDataService.get_restaurant_with_context(validated_id)

            if result:
                logger.info(
                    f"Restaurant service: Found restaurant {result['restaurant']['name']}"
                )
                return result[
                    "restaurant"
                ]  # Return just the restaurant data for consistency
            else:
                logger.warning(
                    f"Restaurant service: Restaurant not found with ID {restaurant_id}"
                )
                return None

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Restaurant service: Error retrieving restaurant - {str(e)}")
            raise e

    @staticmethod
    def get_active_restaurants():
        """Get all active restaurants"""
        try:
            result = RestaurantDataService.get_active_restaurants_summary()
            restaurants = result["restaurants"]

            logger.info(
                f"Restaurant service: Retrieved {len(restaurants)} active restaurants"
            )
            return restaurants

        except Exception as e:
            logger.error(
                f"Restaurant service: Error retrieving active restaurants - {str(e)}"
            )
            raise e

    @staticmethod
    def get_restaurants_near_location(latitude, longitude, radius_km=5):
        """Get restaurants near a specific location with validation"""
        try:
            # Validate coordinates
            validated_lat, validated_lng = RestaurantValidator.validate_coordinates(
                latitude, longitude
            )

            # Validate radius
            validated_radius = RestaurantValidator.validate_radius(radius_km)

            # Get location-based data from data service
            result = RestaurantDataService.get_location_based_restaurants(
                validated_lat, validated_lng, int(validated_radius)
            )

            restaurants = result["restaurants"]
            logger.info(
                f"Restaurant service: Found {len(restaurants)} restaurants near location"
            )
            return restaurants

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(
                f"Restaurant service: Error finding restaurants near location - {str(e)}"
            )
            raise e

    @staticmethod
    def search_restaurants(name):
        """Search restaurants by name with validation"""
        try:
            # Validate search term
            validated_name = RestaurantValidator.validate_search_term(name)

            if not validated_name:
                raise ValueError("Search name cannot be empty")

            # Get enhanced search results from data service
            result = RestaurantDataService.search_restaurants_enhanced(validated_name)
            restaurants = result["restaurants"]

            logger.info(
                f"Restaurant service: Found {len(restaurants)} restaurants matching '{name}'"
            )
            return restaurants

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Restaurant service: Error searching restaurants - {str(e)}")
            raise e

    @staticmethod
    def update_restaurant(restaurant_id, update_data):
        """Update restaurant with validation"""
        try:
            # Validate restaurant ID
            validated_id = RestaurantValidator.validate_restaurant_id(restaurant_id)

            # Validate update data
            validated_data = RestaurantValidator.validate_restaurant_update_data(
                update_data
            )

            # Get original restaurant for comparison
            original_restaurant = RestaurantRepository.get_by_id(validated_id)
            if not original_restaurant:
                logger.warning(
                    f"Restaurant service: Restaurant not found for update with ID {restaurant_id}"
                )
                return None

            # Log what fields are being updated
            updated_fields = list(validated_data.keys())
            logger.info(
                f"Restaurant service: Updating fields {updated_fields} for restaurant {original_restaurant.name}"
            )

            # Update using repository
            restaurant = RestaurantRepository.update(validated_id, validated_data)

            if restaurant:
                logger.info(
                    f"Restaurant service: Successfully updated restaurant {restaurant.name}"
                )

            return restaurant

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Restaurant service: Error updating restaurant - {str(e)}")
            raise e

    @staticmethod
    def delete_restaurant(restaurant_id):
        """Delete restaurant with validation"""
        try:
            # Validate restaurant ID
            validated_id = RestaurantValidator.validate_restaurant_id(restaurant_id)

            # Delete using repository
            result = RestaurantRepository.delete(validated_id)

            if result:
                logger.info(
                    f"Restaurant service: Deleted restaurant with ID {restaurant_id}"
                )
            else:
                logger.warning(
                    f"Restaurant service: Restaurant not found for deletion with ID {restaurant_id}"
                )

            return result

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Restaurant service: Error deleting restaurant - {str(e)}")
            raise e

    @staticmethod
    def toggle_restaurant_status(restaurant_id):
        """Toggle restaurant active status with validation"""
        try:
            # Validate restaurant ID
            validated_id = RestaurantValidator.validate_restaurant_id(restaurant_id)

            # Get current restaurant
            restaurant = RestaurantRepository.get_by_id(validated_id)
            if not restaurant:
                logger.warning(
                    f"Restaurant service: Restaurant not found with ID {restaurant_id}"
                )
                return None

            # Toggle status
            new_status = not restaurant.is_active
            updated_restaurant = RestaurantRepository.update(
                validated_id, {"is_active": new_status}
            )

            if updated_restaurant:
                status_text = "activated" if new_status else "deactivated"
                logger.info(
                    f"Restaurant service: Restaurant {updated_restaurant.name} {status_text}"
                )

            return updated_restaurant

        except ValueError as e:
            logger.warning(f"Restaurant service: Validation error - {str(e)}")
            raise e
        except Exception as e:
            logger.error(
                f"Restaurant service: Error toggling restaurant status - {str(e)}"
            )
            raise e

    @staticmethod
    def get_restaurant_list():
        """Get simple restaurant list for selection purposes"""
        try:
            return RestaurantDataService.get_simple_restaurant_list()
        except Exception as e:
            logger.error(
                f"Restaurant service: Error getting restaurant list - {str(e)}"
            )
            raise e

    @staticmethod
    def get_restaurant_statistics():
        """Get restaurant statistics"""
        try:
            return RestaurantDataService.get_restaurant_statistics()
        except Exception as e:
            logger.error(
                f"Restaurant service: Error getting restaurant statistics - {str(e)}"
            )
            raise e
