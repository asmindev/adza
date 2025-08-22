"""
Food data generation for database seeding
"""

from .common import food_uuids, restaurant_uuids


def generate_foods_data():
    """Generate sample food data"""
    foods_data = [
        # Budget options (5k-15k)
        {
            "id": food_uuids["food1"],
            "name": "Nasi Putih + Tahu Tempe",
            "description": "Basic rice with tofu and tempeh",
            "price": 8000,
            "category": "Rice",
            "restaurant_id": restaurant_uuids["restaurant6"],
        },
        {
            "id": food_uuids["food2"],
            "name": "Mie Instan Rebus",
            "description": "Simple boiled instant noodles",
            "price": 12000,
            "category": "Noodles",
            "restaurant_id": restaurant_uuids["restaurant6"],
        },
        # Mid-range options (15k-25k)
        {
            "id": food_uuids["food3"],
            "name": "Nasi Kuning",
            "description": "Indonesian yellow rice made with coconut milk and turmeric",
            "price": 15000,
            "category": "Rice",
            "restaurant_id": restaurant_uuids["restaurant1"],
        },
        {
            "id": food_uuids["food4"],
            "name": "Ayam Geprek",
            "description": "Crushed fried chicken with spicy sauce",
            "price": 20000,
            "category": "Chicken",
            "restaurant_id": restaurant_uuids["restaurant1"],
        },
        {
            "id": food_uuids["food5"],
            "name": "Mie Bakso",
            "description": "Noodles with meatballs in savory broth",
            "price": 18000,
            "category": "Noodles",
            "restaurant_id": restaurant_uuids["restaurant2"],
        },
        {
            "id": food_uuids["food6"],
            "name": "Mie Ayam",
            "description": "Chicken noodles with savory chicken broth",
            "price": 18000,
            "category": "Noodles",
            "restaurant_id": restaurant_uuids["restaurant2"],
        },
        {
            "id": food_uuids["food7"],
            "name": "Burger Classic",
            "description": "Classic beef burger with cheese and vegetables",
            "price": 22000,
            "category": "Fast Food",
            "restaurant_id": restaurant_uuids["restaurant4"],
        },
        {
            "id": food_uuids["food8"],
            "name": "Fried Chicken Bucket",
            "description": "Crispy fried chicken with special seasoning",
            "price": 25000,
            "category": "Chicken",
            "restaurant_id": restaurant_uuids["restaurant4"],
        },
        # Higher-end options (25k-40k)
        {
            "id": food_uuids["food9"],
            "name": "Tonkotsu Ramen",
            "description": "Rich pork bone broth ramen with chashu",
            "price": 35000,
            "category": "Noodles",
            "restaurant_id": restaurant_uuids["restaurant3"],
        },
        {
            "id": food_uuids["food10"],
            "name": "Spicy Miso Ramen",
            "description": "Spicy miso-based ramen with bamboo shoots",
            "price": 32000,
            "category": "Noodles",
            "restaurant_id": restaurant_uuids["restaurant3"],
        },
        {
            "id": food_uuids["food11"],
            "name": "Grilled Salmon",
            "description": "Fresh grilled salmon with lemon butter sauce",
            "price": 45000,
            "category": "Seafood",
            "restaurant_id": restaurant_uuids["restaurant5"],
        },
        {
            "id": food_uuids["food12"],
            "name": "Seafood Platter",
            "description": "Mixed seafood platter with prawns, fish, and calamari",
            "price": 38000,
            "category": "Seafood",
            "restaurant_id": restaurant_uuids["restaurant5"],
        },
        # Premium options (40k+)
        {
            "id": food_uuids["food13"],
            "name": "Wagyu Steak",
            "description": "Premium wagyu beef steak with truffle sauce",
            "price": 85000,
            "category": "Steak",
            "restaurant_id": restaurant_uuids["restaurant7"],
        },
        {
            "id": food_uuids["food14"],
            "name": "Lobster Thermidor",
            "description": "Classic French lobster dish with cream sauce",
            "price": 95000,
            "category": "Seafood",
            "restaurant_id": restaurant_uuids["restaurant7"],
        },
        {
            "id": food_uuids["food15"],
            "name": "Duck Confit",
            "description": "Slow-cooked duck leg with garlic and herbs",
            "price": 75000,
            "category": "Duck",
            "restaurant_id": restaurant_uuids["restaurant7"],
        },
        # Additional variety
        {
            "id": food_uuids["food16"],
            "name": "Tom Yum Seafood",
            "description": "Spicy and sour Thai soup with mixed seafood",
            "price": 28000,
            "category": "Soup",
            "restaurant_id": restaurant_uuids["restaurant5"],
        },
        {
            "id": food_uuids["food17"],
            "name": "Nasi Gudeg",
            "description": "Traditional Yogyakarta sweet jackfruit curry with rice",
            "price": 16000,
            "category": "Rice",
            "restaurant_id": restaurant_uuids["restaurant1"],
        },
        {
            "id": food_uuids["food18"],
            "name": "Gado-Gado",
            "description": "Indonesian salad with peanut sauce",
            "price": 14000,
            "category": "Salad",
            "restaurant_id": restaurant_uuids["restaurant6"],
        },
        {
            "id": food_uuids["food19"],
            "name": "Beef Rendang",
            "description": "Slow-cooked spicy beef curry from Padang",
            "price": 30000,
            "category": "Beef",
            "restaurant_id": restaurant_uuids["restaurant1"],
        },
        {
            "id": food_uuids["food20"],
            "name": "Fish and Chips",
            "description": "Crispy battered fish with french fries",
            "price": 26000,
            "category": "Fish",
            "restaurant_id": restaurant_uuids["restaurant4"],
        },
    ]

    return foods_data
