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
                "id": "005fd1de-022f-43a5-8a7f-f2677201272c",
                "name": "Nasi Goreng Udang",
                "review": {
                    "rating_details": {
                        "flavor": 4.5,
                        "serving": 4.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Nasi Goreng Udang yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "0af18816-8f2b-42d1-94f7-2bbba515910c",
                "name": "Bubur Ayam Kuah Kuning",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 4.0,
                        "price": 3.5,
                        "place": 4.0,
                    },
                    "content": "Bubur Ayam Kuah Kuning yang manis dan memuaskan.",
                },
            },
            {
                "id": "073d3ef9-a31c-4190-940f-6716bf1c81c4",
                "name": "Nasi Ikan Baronang Bakar + Sup",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Nasi Ikan Baronang Bakar + Sup yang enak.",
                },
            },
            {
                "id": "01621fdf-0a6e-42de-b2b2-3c56555d4be5",
                "name": "Sandwich Telur Dadar+Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Sandwich Telur Dadar+Es Teh yang enak.",
                },
            },
            {
                "id": "108663d2-f89c-42a5-8d14-43817d8db1d9",
                "name": "Pisang Bantal Strobery + Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Pisang Bantal Strobery + Es Teh yang enak.",
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
                "id": "005fd1de-022f-43a5-8a7f-f2677201272c",
                "name": "Nasi Goreng Udang",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Nasi Goreng Udang yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "0af18816-8f2b-42d1-94f7-2bbba515910c",
                "name": "Bubur Ayam Kuah Kuning",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Bubur Ayam Kuah Kuning yang manis dan memuaskan.",
                },
            },
            {
                "id": "073d3ef9-a31c-4190-940f-6716bf1c81c4",
                "name": "Nasi Ikan Baronang Bakar + Sup",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Nasi Ikan Baronang Bakar + Sup yang enak.",
                },
            },
            {
                "id": "01621fdf-0a6e-42de-b2b2-3c56555d4be5",
                "name": "Sandwich Telur Dadar+Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Sandwich Telur Dadar+Es Teh yang enak.",
                },
            },
            {
                "id": "0b77a99e-b53d-4e4d-83c8-2ee729de1ed9",
                "name": "NASI GORENG SEAFOOD",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "NASI GORENG SEAFOOD yang enak",
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
                "id": "005fd1de-022f-43a5-8a7f-f2677201272c",
                "name": "Nasi Goreng Udang",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 3.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Nasi Goreng Udang yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "0af18816-8f2b-42d1-94f7-2bbba515910c",
                "name": "Bubur Ayam Kuah Kuning",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Bubur Ayam Kuah Kuning yang manis dan memuaskan.",
                },
            },
            {
                "id": "073d3ef9-a31c-4190-940f-6716bf1c81c4",
                "name": "Nasi Ikan Baronang Bakar + Sup",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Nasi Ikan Baronang Bakar + Sup yang enak.",
                },
            },
            {
                "id": "01621fdf-0a6e-42de-b2b2-3c56555d4be5",
                "name": "Sandwich Telur Dadar+Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Sandwich Telur Dadar+Es Teh yang enak.",
                },
            },
            {
                "id": "0b77a99e-b53d-4e4d-83c8-2ee729de1ed9",
                "name": "NASI GORENG SEAFOOD",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 3,
                        "place": 5,
                    },
                    "content": "NASI GORENG SEAFOOD yang enak",
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
                "id": "005fd1de-022f-43a5-8a7f-f2677201272c",
                "name": "Nasi Goreng Udang",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Nasi Goreng Udang yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "0af18816-8f2b-42d1-94f7-2bbba515910c",
                "name": "Bubur Ayam Kuah Kuning",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Bubur Ayam Kuah Kuning yang manis dan memuaskan.",
                },
            },
            {
                "id": "073d3ef9-a31c-4190-940f-6716bf1c81c4",
                "name": "Nasi Ikan Baronang Bakar + Sup",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Nasi Ikan Baronang Bakar + Sup yang enak.",
                },
            },
            {
                "id": "01621fdf-0a6e-42de-b2b2-3c56555d4be5",
                "name": "Sandwich Telur Dadar+Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Sandwich Telur Dadar+Es Teh yang enak.",
                },
            },
            {
                "id": "0b77a99e-b53d-4e4d-83c8-2ee729de1ed9",
                "name": "NASI GORENG SEAFOOD",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "NASI GORENG SEAFOOD yang enak",
                },
            },
            {
                "id": "2cf60ca5-5766-4af6-963e-3d5fd04bf511",
                "name": "Mie Ayam Pangsit Kecil",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Mie Ayam Pangsit Kecil",
                },
            },
            {
                "id": "1bd5c38d-36ce-4a1b-97ee-fe4c48df72f4",
                "name": "DOUBLE BEEF + Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 3,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "DOUBLE BEEF + Es Teh yang enak.",
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
                "id": "005fd1de-022f-43a5-8a7f-f2677201272c",
                "name": "Nasi Goreng Udang",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Nasi Goreng Udang yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "0af18816-8f2b-42d1-94f7-2bbba515910c",
                "name": "Bubur Ayam Kuah Kuning",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "Bubur Ayam Kuah Kuning yang manis dan memuaskan.",
                },
            },
            {
                "id": "073d3ef9-a31c-4190-940f-6716bf1c81c4",
                "name": "Nasi Ikan Baronang Bakar + Sup",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Nasi Ikan Baronang Bakar + Sup yang enak.",
                },
            },
            {
                "id": "01621fdf-0a6e-42de-b2b2-3c56555d4be5",
                "name": "Sandwich Telur Dadar+Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Sandwich Telur Dadar+Es Teh yang enak.",
                },
            },
            {
                "id": "0b77a99e-b53d-4e4d-83c8-2ee729de1ed9",
                "name": "NASI GORENG SEAFOOD",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "NASI GORENG SEAFOOD",
                },
            },
            {
                "id": "1b96cd25-0497-44a5-b49e-94f39152b2eb",
                "name": "Krabby Patty Daging Crispy Telur +Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 4,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Krabby Patty Daging Crispy Telur +Es Teh yang lezat.",  # Add content here
                },
            },
            {
                "id": "1bccc096-e344-41ee-8af8-5c61891fcd48",
                "name": "Ikan Palumara",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 4,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Ikan Palumara",  # Add content here
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
                "id": "031d3011-b79a-40b1-a7b6-bbb0d7455ab8",
                "name": "Nasi Lalapan Ayam Crispy",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 4.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Nasi Lalapan Ayam Crispy",
                },
            },
            {
                "id": "38d2f7a1-3cfa-49e9-888a-5ed04d19c77e",
                "name": "Pisang Goreng Keju + Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 4,
                        "price": 5,
                        "place": 4,
                    },
                    "content": "Pisang Goreng Keju + Es Teh dan besar porsinya",
                },
            },
            {
                "id": "08169f56-ec70-43b7-9968-8ded814082ce",
                "name": "Nasi Ikan Lele Tepung",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 4,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Nasi Ikan Lele Tepung yang lezat.",
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
                "id": "01790273-110f-4f9b-9467-2a8bc5df11d6",
                "name": "Gado gado",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Gado gado yang lezat.",
                },
            },
            {
                "id": "6ca7186c-1a2e-43f6-babc-19ffb21c5cfd",
                "name": "Pisang Goreng Topping Greentea Keju + Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Pisang Goreng Topping Greentea Keju + Es Teh",
                },
            },
            #
            {
                "id": "03dfb969-f5ee-450e-bbb4-03c28cc257ca",
                "name": "Iced Coffee Float",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Iced Coffee Float yang lezat.",
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
    print(f"\nLogging in {user['username']}: {response.status_code}")
    token = response.json()["data"]["token"]

    # create reviews for foods
    for food_review in user["foods"]:
        food_id = food_review["id"]
        rating = food_review["review"]["rating_details"]
        comment = food_review["review"].get("content", "")
        response = create_review(token, food_id, rating, comment)
        if response.status_code != 201:
            print(response.json())
        print(
            f"Creating review for {user['username']} on {food_review['name']}: {response.status_code}"
        )
