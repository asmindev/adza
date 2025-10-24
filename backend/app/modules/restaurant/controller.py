from flask import Blueprint, request, g
from app.modules.restaurant.service import RestaurantService
from app.utils import get_logger
logger = get_logger(__name__)
from app.utils.auth import token_required, admin_required
from app.utils.response import ResponseHelper
import requests

restaurant_blueprint = Blueprint("restaurant", __name__)


@restaurant_blueprint.route("/restaurants", methods=["POST"])
@admin_required
def create_restaurant():
    """Create a new restaurant (admin only)"""
    logger.info("POST /restaurants - Creating new restaurant")

    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("No data provided")

        # Log what fields are being sent for creation
        logger.info(f"Creating restaurant with fields: {list(data.keys())}")

        # Use service layer for validation and creation
        restaurant = RestaurantService.create_restaurant(data)

        logger.info(f"Restaurant created successfully: {restaurant.name}")
        return ResponseHelper.success(
            data=restaurant.to_dict(),
            message="Restaurant created successfully",
            status_code=201,
        )

    except ValueError as e:
        logger.warning(f"Validation error creating restaurant: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error creating restaurant: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to create restaurant")


@restaurant_blueprint.route("/restaurants", methods=["GET"])
def get_restaurants():
    """Get all restaurants with optional filters and pagination"""
    logger.info("GET /restaurants - Retrieving restaurants")

    try:
        # Get query parameters - let service handle validation
        active_only = request.args.get("active", "").lower() == "true"
        search = request.args.get("search", None, type=str)
        latitude = request.args.get("latitude", type=float)
        longitude = request.args.get("longitude", type=float)
        radius = request.args.get("radius", default=5, type=float)
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 20, type=int)

        logger.info(
            f"Query parameters: page={page}, limit={limit}, search={search}, active_only={active_only}"
        )

        if latitude is not None and longitude is not None:
            # Location-based search - use service layer
            restaurants = RestaurantService.get_restaurants_near_location(
                latitude, longitude, int(radius)
            )

            logger.info(f"Location search results: {len(restaurants)} restaurants")
            return ResponseHelper.success(
                data={
                    "restaurants": restaurants,
                    "count": len(restaurants),
                    "search_criteria": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "radius_km": radius,
                    },
                }
            )

        elif active_only:
            # Get only active restaurants - use service layer
            restaurants = RestaurantService.get_active_restaurants()

            logger.info(f"Retrieved {len(restaurants)} active restaurants")
            return ResponseHelper.success(
                data={
                    "restaurants": restaurants,
                    "count": len(restaurants),
                }
            )

        else:
            # Get all restaurants with pagination - use service layer
            result = RestaurantService.get_all_restaurants(
                page=page, limit=limit, search=search
            )

            logger.info(f"Retrieved {result['metadata']['count']} restaurants")
            return ResponseHelper.success(
                data={
                    "restaurants": result["restaurants"],
                    "count": result["metadata"]["count"],
                    "pagination": result["pagination"],
                    "metadata": result["metadata"],
                }
            )

    except ValueError as e:
        logger.warning(f"Validation error retrieving restaurants: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error retrieving restaurants: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve restaurants")


@restaurant_blueprint.route("/restaurants/<string:restaurant_id>", methods=["GET"])
def get_restaurant(restaurant_id):
    """Get restaurant by ID with detailed information"""
    logger.info(f"GET /restaurants/{restaurant_id} - Retrieving restaurant details")

    try:
        # Get restaurant with full context from data service
        from app.modules.restaurant.data_service import RestaurantDataService
        from app.modules.restaurant.validators import RestaurantValidator

        # Validate restaurant ID
        validated_id = RestaurantValidator.validate_restaurant_id(restaurant_id)

        # Get restaurant with full context including related data
        result = RestaurantDataService.get_restaurant_with_context(validated_id)

        if not result:
            logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return ResponseHelper.not_found("Restaurant")

        restaurant_data = result["restaurant"]
        context_data = result["context"]
        related_data = context_data.get("related_data", {})

        # Build detailed response with additional information including categories and foods
        detailed_response = {
            **restaurant_data,  # All basic restaurant fields
            "categories": related_data.get("categories", []),
            "foods": related_data.get("foods", []),
        }

        logger.info(f"Restaurant details retrieved: {restaurant_data['name']}")
        return ResponseHelper.success(data=detailed_response)

    except ValueError as e:
        logger.warning(f"Validation error retrieving restaurant: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error retrieving restaurant {restaurant_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to retrieve restaurant")


@restaurant_blueprint.route("/restaurants/<string:restaurant_id>", methods=["PUT"])
@admin_required
def update_restaurant(restaurant_id):
    """Update restaurant (admin only)"""
    logger.info(f"PUT /restaurants/{restaurant_id} - Updating restaurant")

    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("No data provided")

        # Log what fields are being updated
        updated_fields = list(data.keys())
        logger.info(
            f"Updating restaurant {restaurant_id} with fields: {updated_fields}"
        )

        # Use service layer for validation and update
        restaurant = RestaurantService.update_restaurant(restaurant_id, data)

        if not restaurant:
            logger.warning(f"Restaurant not found for update: {restaurant_id}")
            return ResponseHelper.not_found("Restaurant")

        logger.info(f"Restaurant updated successfully: {restaurant.name}")
        return ResponseHelper.success(
            data=restaurant.to_dict(),
            message=f"Restaurant updated successfully. {len(updated_fields)} field(s) modified: {', '.join(updated_fields)}",
        )

    except ValueError as e:
        logger.warning(f"Validation error updating restaurant: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error updating restaurant {restaurant_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to update restaurant")


@restaurant_blueprint.route("/restaurants/<string:restaurant_id>", methods=["DELETE"])
@admin_required
def delete_restaurant(restaurant_id):
    """Delete restaurant (admin only)"""
    logger.info(f"DELETE /restaurants/{restaurant_id} - Deleting restaurant")

    try:
        # Use service layer for validation and deletion
        result = RestaurantService.delete_restaurant(restaurant_id)

        if not result:
            logger.warning(f"Restaurant not found for deletion: {restaurant_id}")
            return ResponseHelper.not_found("Restaurant")

        logger.info(f"Restaurant deleted successfully: {restaurant_id}")
        return ResponseHelper.success(message="Restaurant deleted successfully")

    except ValueError as e:
        logger.warning(f"Validation error deleting restaurant: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error deleting restaurant {restaurant_id}: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to delete restaurant")


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
        # Use service layer for validation and toggle
        restaurant = RestaurantService.toggle_restaurant_status(restaurant_id)

        if not restaurant:
            logger.warning(f"Restaurant not found for status toggle: {restaurant_id}")
            return ResponseHelper.not_found("Restaurant")

        status_text = "activated" if restaurant.is_active else "deactivated"
        logger.info(
            f"Restaurant status toggled: {restaurant.name} is now {status_text}"
        )

        return ResponseHelper.success(
            data=restaurant.to_dict(), message=f"Restaurant {status_text} successfully"
        )

    except ValueError as e:
        logger.warning(f"Validation error toggling restaurant status: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error toggling restaurant status {restaurant_id}: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to toggle restaurant status"
        )


@restaurant_blueprint.route("/restaurants/nearby", methods=["GET"])
def get_nearby_restaurants():
    """Get restaurants near a specific location"""
    logger.info("GET /restaurants/nearby - Finding nearby restaurants")

    try:
        # Get query parameters - let service handle validation
        latitude = request.args.get("latitude", type=float)
        longitude = request.args.get("longitude", type=float)
        radius = request.args.get("radius", default=5, type=float)

        # Basic parameter check
        if latitude is None or longitude is None:
            return ResponseHelper.validation_error(
                "Latitude and longitude are required"
            )

        # Use service layer for validation and location search
        restaurants = RestaurantService.get_restaurants_near_location(
            latitude, longitude, int(radius)
        )

        logger.info(
            f"Found {len(restaurants)} restaurants near ({latitude}, {longitude}) within {radius}km"
        )

        return ResponseHelper.success(
            data={
                "restaurants": restaurants,
                "count": len(restaurants),
                "search_location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_km": radius,
                },
            }
        )

    except ValueError as e:
        logger.warning(f"Validation error in nearby search: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error finding nearby restaurants: {str(e)}")
        return ResponseHelper.internal_server_error("Failed to find nearby restaurants")


@restaurant_blueprint.route("/restaurants/list", methods=["GET"])
def get_restaurant_list():
    """Get a list of all names of restaurants"""
    logger.info("GET /restaurants/list - Retrieving restaurant list")

    try:
        # Use service layer
        restaurants = RestaurantService.get_restaurant_list()

        logger.info(f"Retrieved restaurant list with {len(restaurants)} items")
        return ResponseHelper.success(data={"restaurants": restaurants})

    except Exception as e:
        logger.error(f"Error retrieving restaurant list: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to retrieve restaurant list"
        )


@restaurant_blueprint.route("/restaurants/route", methods=["POST"])
def get_restaurant_route():
    """Get restaurant route by OSRM"""
    logger.info("POST /restaurants/route - Retrieving restaurant route")

    try:
        data = request.get_json()
        if not data:
            return ResponseHelper.validation_error("Request data is required")

        # Use service layer for basic validation
        coordinates = data.get("coordinates")
        restaurant_id = data.get("restaurant_id")

        if not coordinates or not restaurant_id:
            return ResponseHelper.validation_error(
                "Coordinates and restaurant_id are required"
            )

        # Get restaurant to verify it exists (using service layer)
        restaurant = RestaurantService.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            logger.warning(f"Restaurant not found with ID: {restaurant_id}")
            return ResponseHelper.not_found("Restaurant")

        # Call OSRM API
        osrm = "http://router.project-osrm.org"
        response = requests.post(
            f"{osrm}/route/v1/driving/{coordinates[0]},{coordinates[1]};{restaurant['latitude']},{restaurant['longitude']}"
        )
        route = response.json()

        logger.info(f"Route retrieved for restaurant {restaurant_id}")
        return ResponseHelper.success(data=route)

    except ValueError as e:
        logger.warning(f"Validation error in route calculation: {str(e)}")
        return ResponseHelper.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error retrieving restaurant route: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to retrieve restaurant route"
        )


@restaurant_blueprint.route("/restaurants/statistics", methods=["GET"])
def get_restaurant_statistics():
    """Get restaurant statistics"""
    logger.info("GET /restaurants/statistics - Retrieving restaurant statistics")

    try:
        # Use service layer
        statistics = RestaurantService.get_restaurant_statistics()

        logger.info("Restaurant statistics retrieved successfully")
        return ResponseHelper.success(data=statistics)

    except Exception as e:
        logger.error(f"Error retrieving restaurant statistics: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to retrieve restaurant statistics"
        )
