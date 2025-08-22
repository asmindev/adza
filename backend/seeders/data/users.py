"""
User data generation for database seeding
"""

from werkzeug.security import generate_password_hash
from .common import user_uuids


def generate_users_data():
    """Generate sample user data"""
    users_data = []

    # Admin user
    admin = {
        "name": "Admin",
        "id": user_uuids["user1"],
        "username": "admin",
        "email": "admin@example.com",
        "password": generate_password_hash("admin123"),
        "role": "admin",
    }
    users_data.append(admin)

    # Regular users with different personas
    user_personas = [
        {"name": "Budget Budi", "username": "budi_budget", "email": "budi@example.com"},
        {
            "name": "Premium Sari",
            "username": "sari_premium",
            "email": "sari@example.com",
        },
        {
            "name": "Student Andi",
            "username": "andi_student",
            "email": "andi@example.com",
        },
        {"name": "Foodie Maya", "username": "maya_foodie", "email": "maya@example.com"},
        {
            "name": "Office Worker Rini",
            "username": "rini_office",
            "email": "rini@example.com",
        },
        {
            "name": "Family Dad Joko",
            "username": "joko_family",
            "email": "joko@example.com",
        },
        {
            "name": "Health Conscious Lisa",
            "username": "lisa_health",
            "email": "lisa@example.com",
        },
        {
            "name": "Traditional Pak Umar",
            "username": "umar_traditional",
            "email": "umar@example.com",
        },
        {
            "name": "Modern Millenial Alex",
            "username": "alex_modern",
            "email": "alex@example.com",
        },
    ]

    for i, persona in enumerate(user_personas, 2):
        users_data.append(
            {
                "name": persona["name"],
                "id": user_uuids[f"user{i}"],
                "username": persona["username"],
                "email": persona["email"],
                "password": generate_password_hash("user123"),
                "role": "regular",
            }
        )

    return users_data
