import requests
import json
import sys
import os

# adjust the path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from app.extensions import db
from app.modules.user.models import User

from app import init_app

BASE_URL = "http://localhost:5000/api/v1"

REGISTER = "/auth/register"
LOGIN = "/auth/login"

REVIEWS = "/reviews"

FOODS = "/foods"


def register_user(username, password, email, name):
    url = BASE_URL + REGISTER
    data = {"username": username, "password": password, "email": email, "name": name}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response


def login_user(username, password):
    url = BASE_URL + LOGIN
    data = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response


def create_review(token, food_id, rating, comment):
    # Expected JSON payload (Detailed rating format):
    # {
    #     "food_id": "string",
    #     "content": "string",
    #     "rating_details": {
    #         "flavor": float(1 - 5),
    #         "serving": float(1 - 5),
    #         "price": float(1 - 5),
    #         "place": float(1 - 5),
    #     },
    # }
    url = BASE_URL + REVIEWS
    data = {"food_id": food_id, "content": comment, "rating_details": rating}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response


USERS = [
    {
        "username": "adza",
        "password": "user123",
        "email": "adza@example.com",
        "name": "Adza",
        "foods": [
            {
                "id": "6e2b46ad-0617-46a8-af12-cf6f7de94d26",
                "name": "Matcha Latte",
                "review": {
                    "rating_details": {
                        "flavor": 4.5,
                        "serving": 4.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Matcha latte yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "81986805-f023-4027-a095-04f704900995",
                "name": "Gembul Choco",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 4.0,
                        "price": 3.5,
                        "place": 4.0,
                    },
                    "content": "Gembul Choco yang manis dan memuaskan.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
            {
                "id": "41dbf87c-6f4d-48a1-a477-f3865d1efcba",
                "name": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk yang enak.",
                },
            },
            {
                "id": "1e0c4cd5-7018-4b22-b59e-1eebc8f3184a",
                "name": "Belgian Waffle",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
        ],
    },
    {
        "username": "osin",
        "password": "user123",
        "email": "osin@example.com",
        "name": "Osin",
        "foods": [
            {
                "id": "6e2b46ad-0617-46a8-af12-cf6f7de94d26",
                "name": "Matcha Latte",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Matcha latte yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "81986805-f023-4027-a095-04f704900995",
                "name": "Gembul Choco",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Gembul Choco yang manis dan memuaskan.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
            {
                "id": "41dbf87c-6f4d-48a1-a477-f3865d1efcba",
                "name": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk yang enak.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Mie ayam pangsit yang enak",
                },
            },
        ],
    },
    {
        "username": "nisa",
        "password": "user123",
        "email": "nisa@example.com",
        "name": "Nisa",
        "foods": [
            {
                "id": "6e2b46ad-0617-46a8-af12-cf6f7de94d26",
                "name": "Matcha Latte",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 3.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Matcha latte yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "81986805-f023-4027-a095-04f704900995",
                "name": "Gembul Choco",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Gembul Choco yang manis dan memuaskan.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
            {
                "id": "41dbf87c-6f4d-48a1-a477-f3865d1efcba",
                "name": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk yang enak.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 3,
                        "place": 5,
                    },
                    "content": "Mie ayam pangsit yang enak",
                },
            },
        ],
    },
    {
        "username": "anggi",
        "password": "user123",
        "email": "anggi@example.com",
        "name": "Anggi",
        "foods": [
            {
                "id": "6e2b46ad-0617-46a8-af12-cf6f7de94d26",
                "name": "Matcha Latte",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Matcha latte yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "81986805-f023-4027-a095-04f704900995",
                "name": "Gembul Choco",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Gembul Choco yang manis dan memuaskan.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
            {
                "id": "41dbf87c-6f4d-48a1-a477-f3865d1efcba",
                "name": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    }
                },
                "content": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk yang enak.",
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Mie ayam pangsit yang enak",
                },
            },
            {
                "id": "25863a81-bf21-4748-a72c-7850d6e44287",
                "name": "Gado Gado Biasa",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Gado gado yang lezat.",
                },
            },
            {
                "id": "43f8b528-f4d3-4e6b-9f1b-8ee1dc1f5447",
                "name": "Nasi Goreng Sunda Khas Cianjur",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 3,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Nasi goreng yang enak dan khas.",
                },
            },
        ],
    },
    {
        "username": "ella",
        "password": "user123",
        "email": "ella@example.com",
        "name": "Ella",
        "foods": [
            {
                "id": "6e2b46ad-0617-46a8-af12-cf6f7de94d26",
                "name": "Matcha Latte",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Matcha latte yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "81986805-f023-4027-a095-04f704900995",
                "name": "Gembul Choco",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Gembul Choco yang manis dan memuaskan.",
                },
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
            {
                "id": "41dbf87c-6f4d-48a1-a477-f3865d1efcba",
                "name": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    }
                },
                "content": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk yang enak.",
            },
            {
                "id": "52ed6c57-1dab-4fad-88fe-1222862f6828",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Mie ayam pangsit yang enak",
                },
            },
            {
                "id": "e35f8d83-a40b-4eeb-bc65-faa8e417aab9",
                "name": "Nasi Ikan Goreng Free Tempe + Sup Anget",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 4,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Nasi ikan goreng yang lezat.",  # Add content here
                },
            },
            {
                "id": "044229fd-571e-4a07-a20b-50e53c3194bf",
                "name": "MIE SUIT",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 4,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Mie suit yang enak dan kenyal.",  # Add content here
                },
            },
        ],
    },
    {
        "username": "sarah",
        "password": "user123",
        "email": "sarah@example.com",
        "name": "Sarah",
        "foods": [
            {
                "id": "4d2988f8-f982-455f-8abb-a955272d384d",
                "name": "Celebes Dessert (Pisang Ijo Khas Sunday)",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 4.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Pisang ijo-nya enakk dan segar",
                },
            },
            {
                "id": "778f5e1a-3bbb-4087-a34a-7c2db056f825",
                "name": "Nasi Goreng Sunday",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 4,
                        "price": 5,
                        "place": 4,
                    },
                    "content": "Nasi gorengnya banyak toppignya dan besar porsinya",
                },
            },
            {
                "id": "99a8447e-78a9-4a29-a5c2-071f51197ed2",
                "name": "Spaghetti Bolognese",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 4,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Spaghetti Bolognese yang lezat.",
                },
            },
        ],
    },
    {
        "username": "aci",
        "password": "user123",
        "email": "aci@example.com",
        "name": "Aci",
        "foods": [
            {
                "id": "41dbf87c-6f4d-48a1-a477-f3865d1efcba",
                "name": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk",
                "review": {
                    "rating_details": {
                        "flavor": 3.0,
                        "serving": 3,
                        "price": 3,
                        "place": 2,
                    },
                    "content": "Paket Nasi Ayam Geprek+Teh Kotak/Teh Pucuk yang enak.",
                },
            },
            {
                "id": "1e0c4cd5-7018-4b22-b59e-1eebc8f3184a",
                "name": "Belgian Waffle",
                "review": {
                    "rating_details": {
                        "flavor": 2.0,
                        "serving": 3,
                        "price": 2,
                        "place": 2,
                    },
                    "content": "Mie ayam pangsit yang enak.",
                },
            },
            {
                "id": "b7b7e596-44d0-4095-9b1e-e0cfbd627cf5",
                "name": "Ayam Kampung Geprek Sambal Matah",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Ayam Kampung Geprek Sambal Matah yang lezat.",
                },
            },
        ],
    },
]


# delete existing users and create new ones
app = create_app()
with app.app_context():
    print("Cleaning up existing users...")
    # delete all users except admin
    User.query.filter(User.role != "admin").delete()
    db.session.commit()

for user in USERS:
    response = register_user(
        user["username"], user["password"], user["email"], user["name"]
    )
    # print(f"Registering {user['username']}: {response.status_code}")

    # login to get token
    response = login_user(user["username"], user["password"])
    print(f"Logging in {user['username']}: {response.status_code}")
    token = response.json()["data"]["token"]

    # create reviews for foods
    for food_review in user["foods"]:
        food_id = food_review["id"]
        rating = food_review["review"]["rating_details"]
        comment = food_review["review"].get("content", "")
        response = create_review(token, food_id, rating, comment)
        print(
            f"Creating review for {user['username']} on {food_review['name']}: {response.status_code}"
        )
