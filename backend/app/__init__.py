from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.utils import app_logger as logger
from app.extensions import init_app, db
from app.modules import register_blueprints

# Load environment variables
load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Menggunakan logger kustom sebagai pengganti logger Flask
    app.logger = logger

    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI", "mysql://root:zett@localhost/food_recommendation"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # upload folder path

    app.config["UPLOAD_PATH"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "assets"
    )
    app.config["FOODS_IMAGES_PATH"] = os.path.join(
        app.config["UPLOAD_PATH"], "images", "foods"
    )
    app.config["USERS_IMAGES_PATH"] = os.path.join(
        app.config["UPLOAD_PATH"], "images", "users"
    )
    logger.debug(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize extensions
    init_app(app)
    logger.debug("Database dan migrasi diinisialisasi")

    # Register all module blueprints at once
    register_blueprints(app)
    logger.debug("All module blueprints registered at /api/v1")

    return app
