from .repository import CategoryRepository, UserFavoriteCategoryRepository
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class CategoryService:

    @staticmethod
    def get_all_categories():
        """Get all active categories"""
        try:
            categories = CategoryRepository.get_all_active()
            return {
                "success": True,
                "data": [category.to_dict() for category in categories],
                "message": "Categories retrieved successfully",
            }
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"Error retrieving categories: {str(e)}",
            }

    @staticmethod
    def get_category_by_id(category_id):
        """Get category by ID"""
        try:
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return {"success": False, "data": None, "message": "Category not found"}

            return {
                "success": True,
                "data": category.to_dict(),
                "message": "Category retrieved successfully",
            }
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error retrieving category: {str(e)}",
            }

    @staticmethod
    def create_category(data):
        """Create new category"""
        try:
            # Check if category name already exists
            existing = CategoryRepository.get_by_name(data.get("name"))
            if existing:
                return {
                    "success": False,
                    "data": None,
                    "message": "Category name already exists",
                }

            category = CategoryRepository.create(data)
            return {
                "success": True,
                "data": category.to_dict(),
                "message": "Category created successfully",
            }
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error creating category: {str(e)}",
            }

    @staticmethod
    def update_category(category_id, data):
        """Update category"""
        try:
            # Check if category exists
            existing = CategoryRepository.get_by_id(category_id)
            if not existing:
                return {"success": False, "data": None, "message": "Category not found"}

            # Check if new name conflicts with existing category
            if "name" in data:
                name_conflict = CategoryRepository.get_by_name(data["name"])
                if name_conflict and name_conflict.id != category_id:
                    return {
                        "success": False,
                        "data": None,
                        "message": "Category name already exists",
                    }

            category = CategoryRepository.update(category_id, data)
            if category:
                return {
                    "success": True,
                    "data": category.to_dict(),
                    "message": "Category updated successfully",
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Failed to update category",
                }
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error updating category: {str(e)}",
            }

    @staticmethod
    def delete_category(category_id):
        """Soft delete category"""
        try:
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return {"success": False, "message": "Category not found"}

            CategoryRepository.soft_delete(category_id)
            return {"success": True, "message": "Category deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            return {"success": False, "message": f"Error deleting category: {str(e)}"}

    @staticmethod
    def search_categories(search_term):
        """Search categories by name"""
        try:
            categories = CategoryRepository.search_by_name(search_term)
            return {
                "success": True,
                "data": [category.to_dict() for category in categories],
                "message": "Categories found successfully",
            }
        except Exception as e:
            logger.error(f"Error searching categories: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"Error searching categories: {str(e)}",
            }


class UserFavoriteCategoryService:

    @staticmethod
    def get_user_favorite_categories(user_id):
        """Get user's favorite categories"""
        try:
            favorites = UserFavoriteCategoryRepository.get_user_favorite_categories(
                user_id
            )
            result = []

            for favorite, category in favorites:
                category_data = category.to_dict()
                category_data["is_favorite"] = True
                category_data["favorited_at"] = (
                    favorite.created_at.isoformat() + "Z"
                    if favorite.created_at
                    else None
                )
                result.append(category_data)

            return {
                "success": True,
                "data": result,
                "message": "User favorite categories retrieved successfully",
            }
        except Exception as e:
            logger.error(f"Error getting user favorite categories: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"Error retrieving favorite categories: {str(e)}",
            }

    @staticmethod
    def add_favorite_category(user_id, category_id):
        """Add category to user favorites"""
        try:
            # Check if category exists
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return {"success": False, "message": "Category not found"}

            favorite = UserFavoriteCategoryRepository.add_favorite(user_id, category_id)
            return {
                "success": True,
                "data": favorite.to_dict(),
                "message": "Category added to favorites successfully",
            }
        except Exception as e:
            logger.error(f"Error adding favorite category: {str(e)}")
            return {
                "success": False,
                "message": f"Error adding category to favorites: {str(e)}",
            }

    @staticmethod
    def remove_favorite_category(user_id, category_id):
        """Remove category from user favorites"""
        try:
            success = UserFavoriteCategoryRepository.remove_favorite(
                user_id, category_id
            )
            if success:
                return {
                    "success": True,
                    "message": "Category removed from favorites successfully",
                }
            else:
                return {"success": False, "message": "Category was not in favorites"}
        except Exception as e:
            logger.error(f"Error removing favorite category: {str(e)}")
            return {
                "success": False,
                "message": f"Error removing category from favorites: {str(e)}",
            }

    @staticmethod
    def check_is_favorite(user_id, category_id):
        """Check if category is in user favorites"""
        try:
            is_favorite = UserFavoriteCategoryRepository.is_favorite(
                user_id, category_id
            )
            return {
                "success": True,
                "data": {"is_favorite": is_favorite},
                "message": "Check completed successfully",
            }
        except Exception as e:
            logger.error(f"Error checking favorite status: {str(e)}")
            return {
                "success": False,
                "data": {"is_favorite": False},
                "message": f"Error checking favorite status: {str(e)}",
            }

    @staticmethod
    def get_most_favorite_categories(limit=10):
        """Get most favorited categories"""
        try:
            categories = UserFavoriteCategoryRepository.get_most_favorite_categories(
                limit
            )
            result = []

            for category, favorite_count in categories:
                category_data = category.to_dict()
                category_data["favorite_count"] = favorite_count
                result.append(category_data)

            return {
                "success": True,
                "data": result,
                "message": "Most favorite categories retrieved successfully",
            }
        except Exception as e:
            logger.error(f"Error getting most favorite categories: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"Error retrieving most favorite categories: {str(e)}",
            }
