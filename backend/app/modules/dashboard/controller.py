from flask import Blueprint
from app.modules.dashboard.service import DashboardService
from app.utils import api_logger as logger
from app.utils.response import ResponseHelper

dashboard_blueprint = Blueprint("dashboard", __name__)


@dashboard_blueprint.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics.

    Returns statistics including:
    - Total users, restaurants, foods, and ratings
    - Average rating across all foods
    - Popular foods by rating count (top 10)
    - Top rated foods (minimum 5 ratings, ordered by average rating)

    Returns:
        JSON response with dashboard statistics
    """
    logger.info("GET /dashboard/stats - Fetching dashboard statistics")

    try:
        stats = DashboardService.get_stats()

        logger.info("Successfully retrieved dashboard statistics")
        return ResponseHelper.success(
            data=stats, message="Dashboard statistics retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Failed to retrieve dashboard statistics: {str(e)}")
        return ResponseHelper.internal_server_error(
            "Failed to retrieve dashboard statistics"
        )
