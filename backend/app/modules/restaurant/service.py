from app.modules.restaurant.repository import RestaurantRepository
from app.utils import api_logger as logger


class RestaurantService:
    @staticmethod
    def create_restaurant(
        name, address, latitude, longitude, description=None, phone=None, email=None
    ):
        """Create a new restaurant"""
        try:
            # Validate required fields
            if not all([name, address, latitude, longitude]):
                raise ValueError("Name, address, latitude, and longitude are required")

            # Validate latitude and longitude ranges
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude must be between -180 and 180")

            restaurant_data = {
                "name": name,
                "description": description,
                "address": address,
                "phone": phone,
                "email": email,
                "latitude": latitude,
                "longitude": longitude,
            }

            restaurant = RestaurantRepository.create(restaurant_data)
            logger.info(f"Restaurant service: Created restaurant {restaurant.name}")
            return restaurant
        except Exception as e:
            logger.error(f"Restaurant service: Error creating restaurant - {str(e)}")
            raise e

    @staticmethod
    def get_all_restaurants(n: int = 20) -> list:
        """Get all restaurants"""
        try:
            restaurants = RestaurantRepository.get_all(n)
            logger.info(f"Restaurant service: Retrieved {len(restaurants)} restaurants")
            return restaurants
        except Exception as e:
            logger.error(f"Restaurant service: Error retrieving restaurants - {str(e)}")
            raise e

    @staticmethod
    def get_active_restaurants():
        """Get all active restaurants"""
        try:
            restaurants = RestaurantRepository.get_active()
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
    def get_restaurant_by_id(restaurant_id):
        """Get restaurant by ID"""
        try:
            restaurant = RestaurantRepository.get_by_id(restaurant_id)
            if restaurant:
                logger.info(f"Restaurant service: Found restaurant {restaurant.name}")
            else:
                logger.warning(
                    f"Restaurant service: Restaurant not found with ID {restaurant_id}"
                )
            return restaurant
        except Exception as e:
            logger.error(f"Restaurant service: Error retrieving restaurant - {str(e)}")
            raise e

    @staticmethod
    def get_restaurants_near_location(latitude, longitude, radius_km=5):
        """Get restaurants near a specific location"""
        try:
            # Validate latitude and longitude
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude must be between -180 and 180")
            if radius_km <= 0:
                raise ValueError("Radius must be greater than 0")

            restaurants = RestaurantRepository.get_by_location(
                latitude, longitude, radius_km
            )
            logger.info(
                f"Restaurant service: Found {len(restaurants)} restaurants near location"
            )
            return restaurants
        except Exception as e:
            logger.error(
                f"Restaurant service: Error finding restaurants near location - {str(e)}"
            )
            raise e

    @staticmethod
    def search_restaurants(name):
        """Search restaurants by name"""
        try:
            if not name or not name.strip():
                raise ValueError("Search name cannot be empty")

            restaurants = RestaurantRepository.search_by_name(name.strip())
            logger.info(
                f"Restaurant service: Found {len(restaurants)} restaurants matching '{name}'"
            )
            return restaurants
        except Exception as e:
            logger.error(f"Restaurant service: Error searching restaurants - {str(e)}")
            raise e

    @staticmethod
    def update_restaurant(restaurant_id, update_data):
        """Update restaurant"""
        try:
            # Validate latitude and longitude if provided
            if "latitude" in update_data and not (-90 <= update_data["latitude"] <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if "longitude" in update_data and not (
                -180 <= update_data["longitude"] <= 180
            ):
                raise ValueError("Longitude must be between -180 and 180")

            restaurant = RestaurantRepository.update(restaurant_id, update_data)
            if restaurant:
                logger.info(f"Restaurant service: Updated restaurant {restaurant.name}")
            else:
                logger.warning(
                    f"Restaurant service: Restaurant not found for update with ID {restaurant_id}"
                )
            return restaurant
        except Exception as e:
            logger.error(f"Restaurant service: Error updating restaurant - {str(e)}")
            raise e

    @staticmethod
    def delete_restaurant(restaurant_id):
        """Delete restaurant"""
        try:
            result = RestaurantRepository.delete(restaurant_id)
            if result:
                logger.info(
                    f"Restaurant service: Deleted restaurant with ID {restaurant_id}"
                )
            else:
                logger.warning(
                    f"Restaurant service: Restaurant not found for deletion with ID {restaurant_id}"
                )
            return result
        except Exception as e:
            logger.error(f"Restaurant service: Error deleting restaurant - {str(e)}")
            raise e

    @staticmethod
    def toggle_restaurant_status(restaurant_id):
        """Toggle restaurant active status"""
        try:
            restaurant = RestaurantRepository.get_by_id(restaurant_id)
            if not restaurant:
                logger.warning(
                    f"Restaurant service: Restaurant not found with ID {restaurant_id}"
                )
                return None

            new_status = not restaurant.is_active
            updated_restaurant = RestaurantRepository.update(
                restaurant_id, {"is_active": new_status}
            )
            status_text = "activated" if new_status else "deactivated"
            logger.info(
                f"Restaurant service: Restaurant {updated_restaurant.name} {status_text}"
            )
            return updated_restaurant
        except Exception as e:
            logger.error(
                f"Restaurant service: Error toggling restaurant status - {str(e)}"
            )
            raise e

    @staticmethod
    def get_restaurant_list():
        return RestaurantRepository.get_restaurant_list()
