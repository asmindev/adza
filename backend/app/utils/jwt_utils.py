import jwt
import datetime
from flask import current_app
import os
from dotenv import load_dotenv
from app.utils import app_logger as logger

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-for-development")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)  # 24 hours token validity


def generate_token(user_id, is_admin=False, username=None):
    """
    Generate a JWT token for a user

    Args:
        user_id (int): The user's ID
        is_admin (bool): Whether the user is an admin
        username (str): The user's username

    Returns:
        str: JWT token
    """
    try:
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "exp": utc_now + JWT_ACCESS_TOKEN_EXPIRES,
            "iat": utc_now,  # Fixed: set issued-at time to current time
            "sub": str(user_id),  # Convert user_id to string to meet JWT specification
            "admin": is_admin,
            "username": username,
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        logger.info(f"Generated token for user {user_id}")
        return token
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        return None


def decode_token(token):
    """
    Decode a JWT token

    Args:
        token (str): JWT token

    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        logger.info(f"Decoding token: {token}")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        return None
