"""
Restaurant module for managing restaurant data including location coordinates.
This module provides CRUD operations for restaurants with latitude/longitude support.
"""

from .models import Restaurant
from .repository import RestaurantRepository
from .service import RestaurantService
from .controller import restaurant_blueprint

__all__ = [
    "Restaurant",
    "RestaurantRepository",
    "RestaurantService",
    "restaurant_blueprint",
]
