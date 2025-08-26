from flask import Blueprint, request, jsonify, g
from app.modules.restaurant.service import RestaurantService
from app.utils import api_logger as logger
from app.utils.auth import token_required, admin_required
import requests

restaurant_blueprint = Blueprint("restaurant", __name__)


@restaurant_blueprint.route("/restaurants", methods=["POST"])
@admin_required
def create_restaurant():
    """Create a new restaurant (admin only)"""
    logger.info("POST /restaurants - Creating new restaurant")
    data = request.get_json()

    if not data:
        logger.warning("No data provided for restaurant creation")
        return jsonify({"error": True, "message": "No data provided"}), 400

    required_fields = ["name", "address", "latitude", "longitude"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
        return (
            jsonify(
                {
                    "error": True,
                    "message": f"Missing required fields: {', '.join(missing_fields)}",
                }
            ),
            400,
        )

    try:
        restaurant = RestaurantService.create_restaurant(
            name=data["name"],
            address=data["address"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            description=data.get("description"),
            phone=data.get("phone"),
            email=data.get("email"),
        )
        logger.info(f"Restaurant created successfully: {restaurant.name}")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "Restaurant created successfully",
                    "data": restaurant.to_dict(),
                }
            ),
            201,
        )
    except ValueError as e:
        logger.warning(f"Validation error creating restaurant: {str(e)}")
        return jsonify({"error": True, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating restaurant: {str(e)}")
        return jsonify({"error": True, "message": "Failed to create restaurant"}), 500


@restaurant_blueprint.route("/restaurants", methods=["GET"])
def get_restaurants():
    """Get all restaurants with optional filters and pagination"""
    logger.info("GET /restaurants - Retrieving restaurants")

    # Check query parameters
    active_only = request.args.get("active", "").lower() == "true"
    search = request.args.get("search", None, type=str)
    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    radius = request.args.get("radius", default=5, type=float)

    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    # Validate parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    # Log the pagination parameters
    logger.info(f"Pagination parameters: page={page}, limit={limit}, search={search}")

    try:
        if latitude is not None and longitude is not None:
            # Search by location
            restaurants = RestaurantService.get_restaurants_near_location(
                latitude, longitude, radius
            )
            logger.info(
                f"Location search results: {len(restaurants)} restaurants near ({latitude}, {longitude})"
            )

            # For location search, we don't paginate at the database level
            # but could implement manual pagination here if needed
            return (
                jsonify(
                    {
                        "error": False,
                        "data": {
                            "restaurants": [
                                restaurant.to_dict() for restaurant in restaurants
                            ],
                            "count": len(restaurants),
                        },
                    }
                ),
                200,
            )
        elif active_only:
            # Get only active restaurants
            restaurants = RestaurantService.get_active_restaurants()
            logger.info(f"Retrieved {len(restaurants)} active restaurants")

            # For active only, we don't paginate at the database level
            # but could implement manual pagination here if needed
            return (
                jsonify(
                    {
                        "error": False,
                        "data": {
                            "restaurants": [
                                restaurant.to_dict() for restaurant in restaurants
                            ],
                            "count": len(restaurants),
                        },
                    }
                ),
                200,
            )
        else:
            # Get all restaurants with pagination
            result = RestaurantService.get_all_restaurants(
                page=page, limit=limit, search=search
            )

            restaurants = result["items"]
            logger.info(
                f"Retrieved {len(restaurants)} restaurants from total {result['total']}"
            )

            return (
                jsonify(
                    {
                        "error": False,
                        "data": {
                            "restaurants": [
                                restaurant.to_dict() for restaurant in restaurants
                            ],
                            "count": len(restaurants),
                            "pagination": {
                                "page": result["page"],
                                "limit": result["limit"],
                                "total": result["total"],
                                "pages": result["pages"],
                            },
                        },
                    }
                ),
                200,
            )
    except ValueError as e:
        logger.warning(f"Validation error retrieving restaurants: {str(e)}")
        return jsonify({"error": True, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error retrieving restaurants: {str(e)}")
        return (
            jsonify({"error": True, "message": "Failed to retrieve restaurants"}),
            500,
        )


@restaurant_blueprint.route("/restaurants/<string:restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    """Get restaurant by ID"""
    logger.info(f"GET /restaurants/{restaurant_id} - Retrieving restaurant details")

    try:
        restaurant = RestaurantService.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return jsonify({"error": True, "message": "Restaurant not found"}), 404

        logger.info(f"Restaurant retrieved: {restaurant.name}")
        return jsonify({"error": False, "data": restaurant.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error retrieving restaurant {restaurant_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to retrieve restaurant"}), 500


@restaurant_blueprint.route("/restaurants/<string:restaurant_id>", methods=["PUT"])
@admin_required
def update_restaurant(restaurant_id):
    """Update restaurant (admin only)"""
    logger.info(f"PUT /restaurants/{restaurant_id} - Updating restaurant")
    data = request.get_json()

    if not data:
        logger.warning("No data provided for restaurant update")
        return jsonify({"error": True, "message": "No data provided"}), 400

    try:
        restaurant = RestaurantService.update_restaurant(restaurant_id, data)
        if not restaurant:
            logger.warning(f"Restaurant not found for update: {restaurant_id}")
            return jsonify({"error": True, "message": "Restaurant not found"}), 404

        logger.info(f"Restaurant updated successfully: {restaurant.name}")
        return (
            jsonify(
                {
                    "error": False,
                    "message": "Restaurant updated successfully",
                    "data": restaurant.to_dict(),
                }
            ),
            200,
        )
    except ValueError as e:
        logger.warning(f"Validation error updating restaurant: {str(e)}")
        return jsonify({"error": True, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating restaurant {restaurant_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to update restaurant"}), 500


@restaurant_blueprint.route("/restaurants/<string:restaurant_id>", methods=["DELETE"])
@admin_required
def delete_restaurant(restaurant_id):
    """Delete restaurant (admin only)"""
    logger.info(f"DELETE /restaurants/{restaurant_id} - Deleting restaurant")

    try:
        result = RestaurantService.delete_restaurant(restaurant_id)
        if not result:
            logger.warning(f"Restaurant not found for deletion: {restaurant_id}")
            return jsonify({"error": True, "message": "Restaurant not found"}), 404

        logger.info(f"Restaurant deleted successfully: {restaurant_id}")
        return (
            jsonify({"error": False, "message": "Restaurant deleted successfully"}),
            200,
        )
    except Exception as e:
        logger.error(f"Error deleting restaurant {restaurant_id}: {str(e)}")
        return jsonify({"error": True, "message": "Failed to delete restaurant"}), 500


@restaurant_blueprint.route(
    "/restaurants/<string:restaurant_id>/toggle-status", methods=["PATCH"]
)
@admin_required
def toggle_restaurant_status(restaurant_id):
    """Toggle restaurant active status (admin only)"""
    logger.info(
        f"PATCH /restaurants/{restaurant_id}/toggle-status - Toggling restaurant status"
    )

    try:
        restaurant = RestaurantService.toggle_restaurant_status(restaurant_id)
        if not restaurant:
            logger.warning(f"Restaurant not found for status toggle: {restaurant_id}")
            return jsonify({"error": True, "message": "Restaurant not found"}), 404

        status_text = "activated" if restaurant.is_active else "deactivated"
        logger.info(
            f"Restaurant status toggled: {restaurant.name} is now {status_text}"
        )
        return (
            jsonify(
                {
                    "error": False,
                    "message": f"Restaurant {status_text} successfully",
                    "data": restaurant.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error toggling restaurant status {restaurant_id}: {str(e)}")
        return (
            jsonify({"error": True, "message": "Failed to toggle restaurant status"}),
            500,
        )


@restaurant_blueprint.route("/restaurants/nearby", methods=["GET"])
def get_nearby_restaurants():
    """Get restaurants near a specific location"""
    logger.info("GET /restaurants/nearby - Finding nearby restaurants")

    latitude = request.args.get("latitude", type=float)
    longitude = request.args.get("longitude", type=float)
    radius = request.args.get("radius", default=5, type=float)

    if latitude is None or longitude is None:
        logger.warning("Latitude and longitude are required for nearby search")
        return (
            jsonify({"error": True, "message": "Latitude and longitude are required"}),
            400,
        )

    try:
        restaurants = RestaurantService.get_restaurants_near_location(
            latitude, longitude, radius
        )
        logger.info(
            f"Found {len(restaurants)} restaurants near ({latitude}, {longitude}) within {radius}km"
        )
        return (
            jsonify(
                {
                    "error": False,
                    "data": {
                        "restaurants": [
                            restaurant.to_dict() for restaurant in restaurants
                        ],
                        "count": len(restaurants),
                        "search_location": {
                            "latitude": latitude,
                            "longitude": longitude,
                            "radius_km": radius,
                        },
                    },
                }
            ),
            200,
        )
    except ValueError as e:
        logger.warning(f"Validation error in nearby search: {str(e)}")
        return jsonify({"error": True, "message": str(e)}), 400
    except Exception as e:
        logger.error(f"Error finding nearby restaurants: {str(e)}")
        return (
            jsonify({"error": True, "message": "Failed to find nearby restaurants"}),
            500,
        )


@restaurant_blueprint.route("/restaurants/list", methods=["GET"])
def get_restaurant_list():
    """Get a list of all names of restaurants"""
    logger.info("GET /restaurants/list - Retrieving restaurant list")

    try:
        restaurants = RestaurantService.get_restaurant_list()
        if not restaurants:
            logger.info("No restaurants found")
            return jsonify({"error": False, "data": {"restaurants": []}}), 200

        return jsonify({"error": False, "data": {"restaurants": restaurants}}), 200
    except Exception as e:
        logger.error(f"Error retrieving restaurant list: {str(e)}")
        return (
            jsonify({"error": True, "message": "Failed to retrieve restaurant list"}),
            500,
        )


# route by osrm
@restaurant_blueprint.route("/restaurants/route", methods=["POST"])
def get_restaurant_route():
    """Get restaurant route by OSRM"""
    logger.info(f"POST /restaurants/route - Retrieving restaurant route")
    coordinates = request.json.get("coordinates")
    restaurant_id = request.json.get("restaurant_id")

    try:
        # https://router.project-osrm.org/route/v1/driving/120.03,-4.1279;110.368,-7.7897?overview=full&geometries=geojson&steps=true
        osrm = "http://router.project-osrm.org"
        restaurant = RestaurantService.get_restaurant_by_id(restaurant_id)
        response = requests.post(
            f"{osrm}/route/v1/driving/{coordinates[0]},{coordinates[1]};{restaurant.latitude},{restaurant.longitude}"
        )
        route = response.json()
        return jsonify({"error": False, "data": route}), 200
    except Exception as e:
        logger.error(f"Error retrieving restaurant route {restaurant_id}: {str(e)}")
        return (
            jsonify({"error": True, "message": "Failed to retrieve restaurant route"}),
            500,
        )
