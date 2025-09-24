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


# get food list to get food ids: 10 foods
def get_foods():
    url = BASE_URL + FOODS
    response = requests.get(url, params={"limit": 10, "page": 1})
    if response.status_code == 200:
        data = response.json()
        return data["data"]["foods"]
    else:
        print(f"Error getting foods: {response.status_code}")
        return []


def create_review(token, food_id, rating, comment):
    # Expected JSON payload (Detailed rating format):
    {
        "food_id": "string",
        "content": "string",
        "rating_details": {
            "flavor": float(1 - 5),
            "serving": float(1 - 5),
            "price": float(1 - 5),
            "place": float(1 - 5),
        },
    }
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
    },
    {
        "username": "osin",
        "password": "user123",
        "email": "osin@example.com",
        "name": "Osin",
    },
    {
        "username": "nisa",
        "password": "user123",
        "email": "nisa@example.com",
        "name": "Nisa",
    },
    {
        "username": "anggi",
        "password": "user123",
        "email": "anggi@example.com",
        "name": "Anggi",
    },
    {
        "username": "ella",
        "password": "user123",
        "email": "ella@example.com",
        "name": "Ella",
    },
    {
        "username": "sarah",
        "password": "user123",
        "email": "sarah@example.com",
        "name": "Sarah",
    },
    {
        "username": "aci",
        "password": "user123",
        "email": "aci@example.com",
        "name": "Aci",
    },
]

foods = get_foods()


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
    print(f"Response: {response.json()}")

    # login to get token
    response = login_user(user["username"], user["password"])
    print(f"Logging in {user['username']}: {response.status_code}")
    print(f"Response: {response.json()}")
    token = response.json()["data"]["token"]
    print(f"Token: {token}")
    # create 10 reviews for random foods
    for i in foods:
        rating = {
            "flavor": 4.0,
            "serving": 4.0,
            "price": 4.0,
            "place": 4.0,
        }
        comment = f"This is a review for food {i['id']} by {user['username']}"
        response = create_review(token, i["id"], rating, comment)
        print(f"Creating review for food {i['id']}: {response.status_code}")
