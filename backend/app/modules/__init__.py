"""
Modules package that organizes the application into feature-based modules.
Each module contains its own models, repositories, services, and controllers.
"""

from flask import Flask

# Import all module blueprints
from app.modules.user.controller import user_blueprint
from app.modules.food.controller import food_blueprint
from app.modules.rating.controller import rating_blueprint
from app.modules.review.controller import review_blueprint
from app.modules.recommendation.controller import recommendation_blueprint
from app.modules.restaurant.controller import restaurant_blueprint

# List of all module blueprints for easy registration
blueprints = [
    user_blueprint,
    food_blueprint,
    rating_blueprint,
    review_blueprint,
    recommendation_blueprint,
    restaurant_blueprint,
]


def register_blueprints(app: Flask, url_prefix="/api/v1"):
    """
    Register all module blueprints with the Flask application.

    Args:
        app: Flask application instance
        url_prefix: Common URL prefix for all routes (default: '/api/v1')
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        app.logger.debug(f"Registered blueprint: {blueprint.name} at {url_prefix}")
