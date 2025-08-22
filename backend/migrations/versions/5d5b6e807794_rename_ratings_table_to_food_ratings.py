"""rename ratings table to food_ratings

Revision ID: 5d5b6e807794
Revises: d4e8f2a1b3c5
Create Date: 2025-05-27 01:44:44.059772

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d5b6e807794"
down_revision = "d4e8f2a1b3c5"
branch_labels = None
depends_on = None


def upgrade():
    # Rename ratings table to food_ratings
    op.rename_table("ratings", "food_ratings")


def downgrade():
    # Rename food_ratings table back to ratings
    op.rename_table("food_ratings", "ratings")
