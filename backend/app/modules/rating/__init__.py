# Import all models and controllers to make them available
from app.modules.rating.models import FoodRating
from app.modules.rating.models import RestaurantRating
from app.modules.rating.controller import rating_blueprint
