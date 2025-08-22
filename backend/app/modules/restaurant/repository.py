from app.modules.restaurant.models import Restaurant
from app.extensions import db
from app.utils import db_logger as logger


class RestaurantRepository:
    @staticmethod
    def create(restaurant_data):
        """Create a new restaurant"""
        try:
            restaurant = Restaurant(**restaurant_data)
            db.session.add(restaurant)
            db.session.commit()
            logger.info(f"Restaurant created: {restaurant.name}")
            return restaurant
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating restaurant: {str(e)}")
            raise e

    @staticmethod
    def get_all(page=1, limit=20, search=None):
        """Get all restaurants with pagination and search"""
        try:
            query = Restaurant.query

            # Apply search filter if provided
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        Restaurant.name.ilike(search_term),
                        Restaurant.address.ilike(search_term),
                        Restaurant.description.ilike(search_term),
                    )
                )
                logger.info(f"Applying search filter: {search}")

            # Get total count for pagination
            total_count = query.count()

            # Apply pagination
            restaurants = query.order_by(Restaurant.created_at.desc()).paginate(
                page=page, per_page=limit, error_out=False
            )

            logger.info(
                f"Retrieved {len(restaurants.items)} restaurants (total {total_count})"
            )
            return {
                "items": restaurants.items,
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": restaurants.pages,
            }
        except Exception as e:
            logger.error(f"Error retrieving restaurants: {str(e)}")
            raise e

    @staticmethod
    def get_by_id(restaurant_id):
        """Get restaurant by ID"""
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if restaurant:
                logger.info(f"Restaurant found: {restaurant.name}")
            else:
                logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return restaurant
        except Exception as e:
            logger.error(f"Error retrieving restaurant by ID {restaurant_id}: {str(e)}")
            raise e

    @staticmethod
    def get_active():
        """Get all active restaurants"""
        try:
            restaurants = Restaurant.query.filter_by(is_active=True).all()
            logger.info(f"Retrieved {len(restaurants)} active restaurants")
            return restaurants
        except Exception as e:
            logger.error(f"Error retrieving active restaurants: {str(e)}")
            raise e

    @staticmethod
    def get_by_location(latitude, longitude, radius_km=5):
        """Get restaurants within a specific radius from given coordinates"""
        try:
            # Using Haversine formula approximation for distance calculation
            # Note: This is a simplified version, for production use PostGIS or similar
            restaurants = Restaurant.query.filter(
                Restaurant.is_active == True,
                Restaurant.latitude.between(
                    latitude - radius_km / 111, latitude + radius_km / 111
                ),
                Restaurant.longitude.between(
                    longitude - radius_km / 111, longitude + radius_km / 111
                ),
            ).all()
            logger.info(f"Retrieved {len(restaurants)} restaurants near location")
            return restaurants
        except Exception as e:
            logger.error(f"Error retrieving restaurants by location: {str(e)}")
            raise e

    @staticmethod
    def update(restaurant_id, update_data):
        """Update restaurant"""
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if not restaurant:
                logger.warning(f"Restaurant not found for update: {restaurant_id}")
                return None

            for key, value in update_data.items():
                if hasattr(restaurant, key):
                    setattr(restaurant, key, value)

            db.session.commit()
            logger.info(f"Restaurant updated: {restaurant.name}")
            return restaurant
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating restaurant {restaurant_id}: {str(e)}")
            raise e

    @staticmethod
    def delete(restaurant_id):
        """Delete restaurant"""
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            if not restaurant:
                logger.warning(f"Restaurant not found for deletion: {restaurant_id}")
                return False

            db.session.delete(restaurant)
            db.session.commit()
            logger.info(f"Restaurant deleted: {restaurant.name}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting restaurant {restaurant_id}: {str(e)}")
            raise e

    @staticmethod
    def search_by_name(name):
        """Search restaurants by name"""
        try:
            restaurants = Restaurant.query.filter(
                Restaurant.name.ilike(f"%{name}%"), Restaurant.is_active == True
            ).all()
            logger.info(f"Found {len(restaurants)} restaurants matching '{name}'")
            return restaurants
        except Exception as e:
            logger.error(f"Error searching restaurants by name '{name}': {str(e)}")
            raise e

    @staticmethod
    def get_restaurant_list():
        # """Get a list of all restaurants with their IDs and names"""
        try:
            restaurants = Restaurant.query.with_entities(
                Restaurant.id, Restaurant.name
            ).all()
            restaurant_list = [{"id": r.id, "name": r.name} for r in restaurants]
            logger.info(f"Retrieved {len(restaurant_list)} restaurants for list")
            return restaurant_list
        except Exception as e:
            logger.error(f"Error retrieving restaurant list: {str(e)}")
            raise e
