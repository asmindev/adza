"""
Restaurant data generation for database seeding
"""

from .common import restaurant_uuids


def generate_restaurants_data():
    """Generate sample restaurant data"""
    restaurants_data = [
        {
            "id": restaurant_uuids["restaurant1"],
            "name": "Warung Nasi Bu Sari",
            "description": "Warung tradisional yang menyajikan nasi kuning dan ayam geprek terbaik di kota",
            "address": "Jl. Malioboro No. 123, Yogyakarta",
            "phone": "+62274123456",
            "email": "warungbusari@gmail.com",
            "latitude": -7.7956,
            "longitude": 110.3695,
            "rating_average": 4.2,  # Good quality traditional place
            "is_active": True,
        },
        {
            "id": restaurant_uuids["restaurant2"],
            "name": "Mie Corner",
            "description": "Spesialis mie dengan berbagai varian - bakso, ayam, dan ramen",
            "address": "Jl. Kaliurang KM 5, Yogyakarta",
            "phone": "+62274234567",
            "email": "miecorner@gmail.com",
            "latitude": -7.7667,
            "longitude": 110.3833,
            "rating_average": 3.8,  # Decent noodle place
            "is_active": True,
        },
        {
            "id": restaurant_uuids["restaurant3"],
            "name": "Premium Ramen House",
            "description": "Authentic Japanese ramen with rich and flavorful broth",
            "address": "Jl. Solo No. 45, Yogyakarta",
            "phone": "+62274345678",
            "email": "ramenhouse@gmail.com",
            "latitude": -7.8014,
            "longitude": 110.3644,
            "rating_average": 4.7,  # High-end ramen place
            "is_active": True,
        },
        {
            "id": restaurant_uuids["restaurant4"],
            "name": "Burger King Local",
            "description": "Fast food burger joint with local Indonesian twist",
            "address": "Jl. Sudirman No. 78, Yogyakarta",
            "phone": "+62274456789",
            "email": "burgerkinglocal@gmail.com",
            "latitude": -7.7834,
            "longitude": 110.3672,
            "rating_average": 3.5,  # Average fast food
            "is_active": True,
        },
        {
            "id": restaurant_uuids["restaurant5"],
            "name": "Seafood Paradise",
            "description": "Fresh seafood restaurant with ocean-to-table concept",
            "address": "Jl. Pantai Parangtritis, Yogyakarta",
            "phone": "+62274567890",
            "email": "seafoodparadise@gmail.com",
            "latitude": -8.0250,
            "longitude": 110.3297,
            "rating_average": 4.5,  # High quality seafood
            "is_active": True,
        },
        {
            "id": restaurant_uuids["restaurant6"],
            "name": "Warung Tegal Pak Jono",
            "description": "Warteg murah meriah dengan menu lengkap",
            "address": "Jl. Gejayan No. 12, Yogyakarta",
            "phone": "+62274678901",
            "email": "wartegpakjono@gmail.com",
            "latitude": -7.7729,
            "longitude": 110.3755,
            "rating_average": 3.2,  # Cheap but basic quality
            "is_active": True,
        },
        {
            "id": restaurant_uuids["restaurant7"],
            "name": "Fine Dining Le Gourmet",
            "description": "Upscale restaurant with international cuisine",
            "address": "Jl. Jenderal Sudirman No. 1, Yogyakarta",
            "phone": "+62274789012",
            "email": "legourmet@gmail.com",
            "latitude": -7.7897,
            "longitude": 110.3678,
            "rating_average": 4.8,  # Premium fine dining
            "is_active": True,
        },
    ]

    return restaurants_data
