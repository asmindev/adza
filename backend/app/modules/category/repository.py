from app.extensions import db
from .models import Category, UserFavoriteCategory
from sqlalchemy import and_, desc


class CategoryRepository:

    @staticmethod
    def get_all_active():
        """Get all active categories"""
        return Category.query.filter_by(is_active=True).order_by(Category.name).all()

    @staticmethod
    def get_all():
        """Get all categories including inactive ones"""
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        return Category.query.filter_by(id=category_id, is_active=True).first()

    @staticmethod
    def get_by_name(name):
        """Get category by name"""
        return Category.query.filter_by(name=name, is_active=True).first()

    @staticmethod
    def create(data):
        """Create new category"""
        category = Category(**data)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update(category_id, data):
        """Update category"""
        category = Category.query.get(category_id)
        if category:
            for key, value in data.items():
                setattr(category, key, value)
            db.session.commit()
        return category

    @staticmethod
    def soft_delete(category_id):
        """Soft delete category by setting is_active to False"""
        category = Category.query.get(category_id)
        if category:
            category.is_active = False
            db.session.commit()
        return category

    @staticmethod
    def delete(category_id):
        """Hard delete category"""
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
        return True

    @staticmethod
    def search_by_name(search_term):
        """Search categories by name"""
        return (
            Category.query.filter(
                Category.name.ilike(f"%{search_term}%"), Category.is_active == True
            )
            .order_by(Category.name)
            .all()
        )


class UserFavoriteCategoryRepository:

    @staticmethod
    def get_user_favorites(user_id):
        """Get all favorite categories for a user"""
        return (
            UserFavoriteCategory.query.filter_by(user_id=user_id)
            .order_by(desc(UserFavoriteCategory.created_at))
            .all()
        )

    @staticmethod
    def get_user_favorite_categories(user_id):
        """Get user's favorite categories with category details"""
        return (
            db.session.query(UserFavoriteCategory, Category)
            .join(Category, UserFavoriteCategory.category_id == Category.id)
            .filter(UserFavoriteCategory.user_id == user_id, Category.is_active == True)
            .order_by(desc(UserFavoriteCategory.created_at))
            .all()
        )

    @staticmethod
    def is_favorite(user_id, category_id):
        """Check if a category is favorite for a user"""
        return (
            UserFavoriteCategory.query.filter_by(
                user_id=user_id, category_id=category_id
            ).first()
            is not None
        )

    @staticmethod
    def add_favorite(user_id, category_id):
        """Add category to user favorites"""
        # Check if already exists
        existing = UserFavoriteCategory.query.filter_by(
            user_id=user_id, category_id=category_id
        ).first()

        if existing:
            return existing

        favorite = UserFavoriteCategory(user_id=user_id, category_id=category_id)
        db.session.add(favorite)
        db.session.commit()
        return favorite

    @staticmethod
    def remove_favorite(user_id, category_id):
        """Remove category from user favorites"""
        favorite = UserFavoriteCategory.query.filter_by(
            user_id=user_id, category_id=category_id
        ).first()

        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_category_favorite_count(category_id):
        """Get number of users who have this category as favorite"""
        return UserFavoriteCategory.query.filter_by(category_id=category_id).count()

    @staticmethod
    def get_most_favorite_categories(limit=10):
        """Get most favorited categories"""
        return (
            db.session.query(
                Category, db.func.count(UserFavoriteCategory.id).label("favorite_count")
            )
            .outerjoin(UserFavoriteCategory)
            .filter(Category.is_active == True)
            .group_by(Category.id)
            .order_by(desc("favorite_count"), Category.name)
            .limit(limit)
            .all()
        )
