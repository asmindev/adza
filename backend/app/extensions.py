from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
