"""Convert all ID fields from integer to UUID string

Revision ID: ce759a7620f0
Revises: b1a0238b5c15
Create Date: 2025-05-26 22:33:16.809139

"""

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "ce759a7620f0"
down_revision = "b1a0238b5c15"
branch_labels = None
depends_on = None


def upgrade():
    # Create temporary tables with UUID primary keys

    # 1. Create new users table with UUID
    op.create_table(
        "users_new",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # 2. Create new restaurants table with UUID
    op.create_table(
        "restaurants_new",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("rating_average", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # 3. Create new foods table with UUID
    op.create_table(
        "foods_new",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("restaurant_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # 4. Create new food_images table with UUID
    op.create_table(
        "food_images_new",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("food_id", sa.String(36), nullable=False),
        sa.Column("image_url", sa.String(255), nullable=True),
        sa.Column("is_main", sa.Boolean(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # 5. Create new ratings table with UUID
    op.create_table(
        "ratings_new",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("food_id", sa.String(36), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # 6. Create new reviews table with UUID
    op.create_table(
        "reviews_new",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("food_id", sa.String(36), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Data migration with UUID generation
    connection = op.get_bind()

    # Migrate users data
    users_data = connection.execute(sa.text("SELECT * FROM users")).fetchall()
    user_id_mapping = {}
    for user in users_data:
        new_uuid = str(uuid.uuid4())
        user_id_mapping[user[0]] = new_uuid  # Map old ID to new UUID
        connection.execute(
            sa.text(
                "INSERT INTO users_new (id, name, username, email, password, role, created_at, updated_at) "
                "VALUES (:id, :name, :username, :email, :password, :role, :created_at, :updated_at)"
            ),
            {
                "id": new_uuid,
                "name": user[1],
                "username": user[2],
                "email": user[3],
                "password": user[4],
                "role": user[5],
                "created_at": user[6],
                "updated_at": user[7],
            },
        )

    # Migrate restaurants data
    restaurants_data = connection.execute(
        sa.text("SELECT * FROM restaurants")
    ).fetchall()
    restaurant_id_mapping = {}
    for restaurant in restaurants_data:
        new_uuid = str(uuid.uuid4())
        restaurant_id_mapping[restaurant[0]] = new_uuid  # Map old ID to new UUID
        connection.execute(
            sa.text(
                "INSERT INTO restaurants_new (id, name, description, address, phone, email, latitude, longitude, rating_average, is_active, created_at, updated_at) "
                "VALUES (:id, :name, :description, :address, :phone, :email, :latitude, :longitude, :rating_average, :is_active, :created_at, :updated_at)"
            ),
            {
                "id": new_uuid,
                "name": restaurant[1],
                "description": restaurant[2],
                "address": restaurant[3],
                "phone": restaurant[4],
                "email": restaurant[5],
                "latitude": restaurant[6],
                "longitude": restaurant[7],
                "rating_average": restaurant[8],
                "is_active": restaurant[9],
                "created_at": restaurant[10],
                "updated_at": restaurant[11],
            },
        )

    # Migrate foods data
    foods_data = connection.execute(sa.text("SELECT * FROM foods")).fetchall()
    food_id_mapping = {}
    for food in foods_data:
        new_uuid = str(uuid.uuid4())
        food_id_mapping[food[0]] = new_uuid  # Map old ID to new UUID
        restaurant_uuid = restaurant_id_mapping.get(food[5]) if food[5] else None
        connection.execute(
            sa.text(
                "INSERT INTO foods_new (id, name, description, category, price, restaurant_id, created_at, updated_at) "
                "VALUES (:id, :name, :description, :category, :price, :restaurant_id, :created_at, :updated_at)"
            ),
            {
                "id": new_uuid,
                "name": food[1],
                "description": food[2],
                "category": food[3],
                "price": food[4],
                "restaurant_id": restaurant_uuid,
                "created_at": food[6],
                "updated_at": food[7],
            },
        )

    # Migrate food_images data
    food_images_data = connection.execute(
        sa.text("SELECT * FROM food_images")
    ).fetchall()
    for food_image in food_images_data:
        new_uuid = str(uuid.uuid4())
        food_uuid = food_id_mapping.get(food_image[1])
        if food_uuid:  # Only migrate if food exists
            connection.execute(
                sa.text(
                    "INSERT INTO food_images_new (id, food_id, image_url, is_main, filename, created_at, updated_at) "
                    "VALUES (:id, :food_id, :image_url, :is_main, :filename, :created_at, :updated_at)"
                ),
                {
                    "id": new_uuid,
                    "food_id": food_uuid,
                    "image_url": food_image[2],
                    "is_main": food_image[3],
                    "filename": food_image[4],
                    "created_at": food_image[5],
                    "updated_at": food_image[6],
                },
            )

    # Migrate ratings data
    ratings_data = connection.execute(sa.text("SELECT * FROM ratings")).fetchall()
    for rating in ratings_data:
        new_uuid = str(uuid.uuid4())
        user_uuid = user_id_mapping.get(rating[1])
        food_uuid = food_id_mapping.get(rating[2])
        if user_uuid and food_uuid:  # Only migrate if both user and food exist
            connection.execute(
                sa.text(
                    "INSERT INTO ratings_new (id, user_id, food_id, rating, created_at, updated_at) "
                    "VALUES (:id, :user_id, :food_id, :rating, :created_at, :updated_at)"
                ),
                {
                    "id": new_uuid,
                    "user_id": user_uuid,
                    "food_id": food_uuid,
                    "rating": rating[3],
                    "created_at": rating[4],
                    "updated_at": rating[5],
                },
            )

    # Migrate reviews data
    reviews_data = connection.execute(sa.text("SELECT * FROM reviews")).fetchall()
    for review in reviews_data:
        new_uuid = str(uuid.uuid4())
        user_uuid = user_id_mapping.get(review[1])
        food_uuid = food_id_mapping.get(review[2])
        if user_uuid and food_uuid:  # Only migrate if both user and food exist
            connection.execute(
                sa.text(
                    "INSERT INTO reviews_new (id, user_id, food_id, review_text, created_at, updated_at) "
                    "VALUES (:id, :user_id, :food_id, :review_text, :created_at, :updated_at)"
                ),
                {
                    "id": new_uuid,
                    "user_id": user_uuid,
                    "food_id": food_uuid,
                    "review_text": review[3],
                    "created_at": review[4],
                    "updated_at": review[5],
                },
            )

    # Drop old tables
    op.drop_table("reviews")
    op.drop_table("ratings")
    op.drop_table("food_images")
    op.drop_table("foods")
    op.drop_table("restaurants")
    op.drop_table("users")

    # Rename new tables to original names
    op.rename_table("users_new", "users")
    op.rename_table("restaurants_new", "restaurants")
    op.rename_table("foods_new", "foods")
    op.rename_table("food_images_new", "food_images")
    op.rename_table("ratings_new", "ratings")
    op.rename_table("reviews_new", "reviews")

    # Create indexes and constraints
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint(
        "uq_user_food_rating", "ratings", ["user_id", "food_id"]
    )
    op.create_unique_constraint(
        "uq_user_food_review", "reviews", ["user_id", "food_id"]
    )

    # Create foreign key constraints
    op.create_foreign_key(
        "fk_foods_restaurant_id", "foods", "restaurants", ["restaurant_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_food_images_food_id", "food_images", "foods", ["food_id"], ["id"]
    )
    op.create_foreign_key("fk_ratings_user_id", "ratings", "users", ["user_id"], ["id"])
    op.create_foreign_key("fk_ratings_food_id", "ratings", "foods", ["food_id"], ["id"])
    op.create_foreign_key("fk_reviews_user_id", "reviews", "users", ["user_id"], ["id"])
    op.create_foreign_key("fk_reviews_food_id", "reviews", "foods", ["food_id"], ["id"])


def downgrade():
    # Reverse migration - convert UUID back to integer IDs
    # This is a destructive operation and should be used with caution

    # Drop foreign key constraints
    op.drop_constraint("fk_reviews_food_id", "reviews", type_="foreignkey")
    op.drop_constraint("fk_reviews_user_id", "reviews", type_="foreignkey")
    op.drop_constraint("fk_ratings_food_id", "ratings", type_="foreignkey")
    op.drop_constraint("fk_ratings_user_id", "ratings", type_="foreignkey")
    op.drop_constraint("fk_food_images_food_id", "food_images", type_="foreignkey")
    op.drop_constraint("fk_foods_restaurant_id", "foods", type_="foreignkey")

    # Create old tables with integer IDs
    op.create_table(
        "users_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "restaurants_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("rating_average", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "foods_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("restaurant_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "food_images_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(255), nullable=True),
        sa.Column("is_main", sa.Boolean(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "ratings_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "reviews_old",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Note: Data migration back to integer IDs would require
    # complex mapping and is not recommended for production use

    # Drop current tables
    op.drop_table("reviews")
    op.drop_table("ratings")
    op.drop_table("food_images")
    op.drop_table("foods")
    op.drop_table("restaurants")
    op.drop_table("users")

    # Rename old tables back
    op.rename_table("users_old", "users")
    op.rename_table("restaurants_old", "restaurants")
    op.rename_table("foods_old", "foods")
    op.rename_table("food_images_old", "food_images")
    op.rename_table("ratings_old", "ratings")
    op.rename_table("reviews_old", "reviews")
