from app import create_app
from app.modules.user.models import User
from app.extensions import db
import os
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if admin user already exists
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        # Create admin user
        admin = User(
            username="admin",
            email=admin_email,
            name="Admin User",
            password=generate_password_hash("admin123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created with email: {admin_email} and password: admin123")
    else:
        print(f"Admin user with email: {admin_email} already exists.")
