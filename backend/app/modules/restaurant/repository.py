from app.modules.restaurant.models import Restaurant
from app.extensions import db
from app.utils import get_logger
logger = get_logger(__name__)


class RestaurantRepository:
    @staticmethod
    def create(restaurant_data):
        """Create a new restaurant"""
        try:
            # Handle category_ids separately if provided
            category_ids = restaurant_data.pop("category_ids", None)

            restaurant = Restaurant(**restaurant_data)
            db.session.add(restaurant)

            # Handle categories if provided
            if category_ids:
                from app.modules.category.models import Category, restaurant_categories

                logger.info(
                    f"Processing category_ids for new restaurant: {category_ids}"
                )

                categories = Category.query.filter(Category.id.in_(category_ids)).all()
                logger.info(f"Found {len(categories)} categories to add")

                # Flush to get the restaurant ID
                db.session.flush()

                # Add categories using direct insert to association table
                for category in categories:
                    db.session.execute(
                        restaurant_categories.insert().values(
                            restaurant_id=restaurant.id, category_id=category.id
                        )
                    )
                    logger.info(f"Added category: {category.name}")

                logger.info(
                    f"Added restaurant categories: {len(categories)} categories"
                )
            else:
                logger.info("No categories provided for new restaurant")

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
    def get_by_category(category_id, page=1, limit=20):
        """Get restaurants by category with pagination"""
        try:
            # Use join to filter restaurants by category through many-to-many relationship
            from app.modules.category.models import restaurant_categories

            query = Restaurant.query.join(
                restaurant_categories,
                Restaurant.id == restaurant_categories.c.restaurant_id,
            ).filter(
                restaurant_categories.c.category_id == category_id,
                Restaurant.is_active == True,
            )

            # Get total count for pagination
            total_count = query.count()

            # Apply pagination
            restaurants = query.order_by(Restaurant.created_at.desc()).paginate(
                page=page, per_page=limit, error_out=False
            )

            logger.info(
                f"Retrieved {len(restaurants.items)} restaurants for category {category_id} (total {total_count})"
            )
            return {
                "items": restaurants.items,
                "total": total_count,
                "page": page,
                "limit": limit,
                "pages": restaurants.pages,
            }
        except Exception as e:
            logger.error(
                f"Error retrieving restaurants by category {category_id}: {str(e)}"
            )
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

            # Handle category_ids separately if provided
            category_ids = update_data.pop("category_ids", None)

            # Update regular fields
            for key, value in update_data.items():
                if hasattr(restaurant, key):
                    setattr(restaurant, key, value)

            # Handle categories if provided
            if category_ids is not None:
                from app.modules.category.models import Category, restaurant_categories

                logger.info(f"Processing category_ids: {category_ids}")

                # Clear existing categories by deleting from association table
                try:
                    db.session.execute(
                        restaurant_categories.delete().where(
                            restaurant_categories.c.restaurant_id == restaurant.id
                        )
                    )
                    logger.info("Categories cleared successfully")
                except Exception as e:
                    logger.error(f"Error clearing categories: {str(e)}")

                # Add new categories
                if category_ids:  # Only if not empty
                    try:
                        categories = Category.query.filter(
                            Category.id.in_(category_ids)
                        ).all()
                        logger.info(f"Found {len(categories)} categories to add")

                        # Add categories using direct insert to association table
                        for category in categories:
                            db.session.execute(
                                restaurant_categories.insert().values(
                                    restaurant_id=restaurant.id, category_id=category.id
                                )
                            )
                            logger.info(f"Added category: {category.name}")

                        logger.info(
                            f"Updated restaurant categories: {len(categories)} categories"
                        )
                    except Exception as e:
                        logger.error(f"Error adding categories: {str(e)}")
                else:
                    logger.info("No categories to add (empty category_ids)")

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
