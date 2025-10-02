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
                "id": "1352f7a7-2842-4d12-ac3b-098e4ad13788",
                "name": "Martabak Kornet Rica Rica Telur Ayam",
                "review": {
                    "rating_details": {
                        "flavor": 4.5,
                        "serving": 4.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Martabak Kornet Rica Rica Telur Ayam yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "1e323138-efdc-4bb9-bae1-d021bf9edfce",
                "name": "KEJU KETAN",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 4.0,
                        "price": 3.5,
                        "place": 4.0,
                    },
                    "content": "KEJU KETAN yang manis dan memuaskan.",
                },
            },
            {
                "id": "7bdfae86-5901-4ac2-bb67-1e46dcb94310",
                "name": "Martabak Kornet Tripel chesee Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Martabak Kornet Tripel chesee Telur Bebek yang enak.",
                },
            },
            {
                "id": "25a21cef-d91e-49a6-8b88-35778037c49c",
                "name": "Nasi + Udang + Sayur + Sambal",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Nasi + Udang + Sayur + Sambal yang enak.",
                },
            },
            {
                "id": "5147fc6b-8031-4252-b1a0-92e1e490cf26",
                "name": "Nasi Biasa Ayam Bakar+tempe+sop",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Nasi Biasa Ayam Bakar+tempe+sop yang enak.",
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
                "id": "1352f7a7-2842-4d12-ac3b-098e4ad13788",
                "name": "Martabak Kornet Rica Rica Telur Ayam",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Martabak Kornet Rica Rica Telur Ayam yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "1e323138-efdc-4bb9-bae1-d021bf9edfce",
                "name": "KEJU KETAN",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "KEJU KETAN yang manis dan memuaskan.",
                },
            },
            {
                "id": "7bdfae86-5901-4ac2-bb67-1e46dcb94310",
                "name": "Martabak Kornet Tripel chesee Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Martabak Kornet Tripel chesee Telur Bebek yang enak.",
                },
            },
            {
                "id": "25a21cef-d91e-49a6-8b88-35778037c49c",
                "name": "Nasi + Udang + Sayur + Sambal",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Nasi + Udang + Sayur + Sambal yang enak.",
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
                "id": "1352f7a7-2842-4d12-ac3b-098e4ad13788",
                "name": "Martabak Kornet Rica Rica Telur Ayam",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 3.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Martabak Kornet Rica Rica Telur Ayam yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "1e323138-efdc-4bb9-bae1-d021bf9edfce",
                "name": "KEJU KETAN",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "KEJU KETAN yang manis dan memuaskan.",
                },
            },
            {
                "id": "7bdfae86-5901-4ac2-bb67-1e46dcb94310",
                "name": "Martabak Kornet Tripel chesee Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 5,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Martabak Kornet Tripel chesee Telur Bebek yang enak.",
                },
            },
            {
                "id": "25a21cef-d91e-49a6-8b88-35778037c49c",
                "name": "Nasi + Udang + Sayur + Sambal",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Nasi + Udang + Sayur + Sambal yang enak.",
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
                "id": "1352f7a7-2842-4d12-ac3b-098e4ad13788",
                "name": "Martabak Kornet Rica Rica Telur Ayam",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Martabak Kornet Rica Rica Telur Ayam yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "1e323138-efdc-4bb9-bae1-d021bf9edfce",
                "name": "KEJU KETAN",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "KEJU KETAN yang manis dan memuaskan.",
                },
            },
            {
                "id": "7bdfae86-5901-4ac2-bb67-1e46dcb94310",
                "name": "Martabak Kornet Tripel chesee Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Martabak Kornet Tripel chesee Telur Bebek yang enak.",
                },
            },
            {
                "id": "25a21cef-d91e-49a6-8b88-35778037c49c",
                "name": "Nasi + Udang + Sayur + Sambal",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Nasi + Udang + Sayur + Sambal yang enak.",
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
                "id": "1843ba6d-00a4-4f87-8650-1593c7c34370",
                "name": "Mie Ayam Pangsit Bakso",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 5,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Mie Ayam Pangsit Bakso",
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
                "id": "1352f7a7-2842-4d12-ac3b-098e4ad13788",
                "name": "Martabak Kornet Rica Rica Telur Ayam",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 5.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Martabak Kornet Rica Rica Telur Ayam yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "1e323138-efdc-4bb9-bae1-d021bf9edfce",
                "name": "KEJU KETAN",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 5.0,
                        "price": 4,
                        "place": 4.0,
                    },
                    "content": "KEJU KETAN yang manis dan memuaskan.",
                },
            },
            {
                "id": "7bdfae86-5901-4ac2-bb67-1e46dcb94310",
                "name": "Martabak Kornet Tripel chesee Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 5,
                        "price": 4,
                        "place": 3,
                    },
                    "content": "Martabak Kornet Tripel chesee Telur Bebek yang enak.",
                },
            },
            {
                "id": "25a21cef-d91e-49a6-8b88-35778037c49c",
                "name": "Nasi + Udang + Sayur + Sambal",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 3,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "Nasi + Udang + Sayur + Sambal yang enak.",
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
                "id": "f2b8881d-f892-4114-b1ba-0da3bda4141c",
                "name": "BEEF BULGOGI",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 4,
                        "price": 4,
                        "place": 5,
                    },
                    "content": "BEEF BULGOGI Teh yang lezat.",  # Add content here
                },
            },
            {
                "id": "7a4d2518-c57e-4b81-b37b-309ed5ca4e78",
                "name": "Mie Goreng Bakso + Telur",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 4,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Mie Goreng Bakso + Telur",  # Add content here
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
                "id": "6665468b-9e7e-4ab1-80b5-61af85753917",
                "name": "Ayam Sambal Bajak",
                "review": {
                    "rating_details": {
                        "flavor": 5,
                        "serving": 4.0,
                        "price": 5.0,
                        "place": 4.0,
                    },
                    "content": "Ayam Sambal Bajak yang lezat dan menyegarkan.",
                },
            },
            {
                "id": "035a735d-bf9d-4263-9432-dc0c41457511",
                "name": "Lontong Pecel Tempe Tahu Bacem",
                "review": {
                    "rating_details": {
                        "flavor": 4.0,
                        "serving": 4,
                        "price": 5,
                        "place": 4,
                    },
                    "content": "Lontong Pecel Tempe Tahu Bacem dan besar porsinya",
                },
            },
            {
                "id": "2e077903-805e-43ca-9864-60d991a75eb0",
                "name": "Martabak Kornet Rica+Moza Full Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 4,
                        "serving": 4,
                        "price": 4,
                        "place": 4,
                    },
                    "content": "Martabak Kornet Rica+Moza Full Telur Bebek yang lezat.",
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
                "id": "55601544-4e29-4518-a9d5-ad1134ca54b4",
                "name": "Martabak Sapi Tripel chesee Telur Ayam",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Martabak Sapi Tripel chesee Telur Ayam yang lezat.",
                },
            },
            {
                "id": "4f74e939-5439-4c4b-9f30-a985ef67855b",
                "name": "Nasi Pecel + Telur + Es Teh",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Nasi Pecel + Telur + Es Teh yang lezat.",
                },
            },
            #
            {
                "id": "5321c047-3c42-4bcd-88f9-9004bc7d418b",
                "name": "Martabak Sapi Mozarella Telur Bebek",
                "review": {
                    "rating_details": {
                        "flavor": 5.0,
                        "serving": 4,
                        "price": 5,
                        "place": 5,
                    },
                    "content": "Martabak Sapi Mozarella Telur Bebek yang lezat.",
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
