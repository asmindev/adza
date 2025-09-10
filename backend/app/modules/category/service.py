from .repository import CategoryRepository, UserFavoriteCategoryRepository
from .validators import CategoryValidator, CategoryBusinessRules
from .data_service import CategoryDataService
from flask import current_app
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CategoryService:
    """Main service for category business logic"""

    @staticmethod
    def get_all_categories(include_stats: bool = False) -> Dict[str, Any]:
        """
        Get all active categories

        Args:
            include_stats (bool): Whether to include statistics

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            if include_stats:
                categories_data = CategoryDataService.get_categories_with_stats()
            else:
                categories = CategoryRepository.get_all_active()
                categories_data = [category.to_dict() for category in categories]

            return {
                "success": True,
                "data": categories_data,
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
    def get_category_by_id(
        category_id: str, include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Get category by ID

        Args:
            category_id (str): Category ID
            include_details (bool): Whether to include detailed information

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            if include_details:
                category_data = CategoryDataService.get_category_with_details(
                    category_id
                )
                if not category_data:
                    return {
                        "success": False,
                        "data": None,
                        "message": "Category not found",
                    }
            else:
                category = CategoryRepository.get_by_id(category_id)
                if not category:
                    return {
                        "success": False,
                        "data": None,
                        "message": "Category not found",
                    }
                category_data = category.to_dict()

            return {
                "success": True,
                "data": category_data,
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
    def create_category(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new category with validation

        Args:
            data (dict): Category data

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            # Validate input data
            validation_result = CategoryValidator.validate_category_data(data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "data": None,
                    "message": "; ".join(validation_result["errors"]),
                }

            # Check if category name already exists
            existing = CategoryRepository.get_by_name(data.get("name"))
            if existing:
                return {
                    "success": False,
                    "data": None,
                    "message": "Category name already exists",
                }

            # Clean data
            clean_data = {
                "name": data["name"].strip(),
                "description": (
                    data.get("description", "").strip()
                    if data.get("description")
                    else None
                ),
                "icon": data.get("icon", "").strip() if data.get("icon") else None,
                "is_active": data.get("is_active", True),
            }

            category = CategoryRepository.create(clean_data)
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
    def update_category(
        category_id: str, data: Dict[str, Any], user=None
    ) -> Dict[str, Any]:
        """
        Update category with validation and authorization

        Args:
            category_id (str): Category ID
            data (dict): Update data
            user: User object for authorization

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            # Check if category exists
            existing = CategoryRepository.get_by_id(category_id)
            if not existing:
                return {"success": False, "data": None, "message": "Category not found"}

            # Check authorization if user is provided
            if user:
                auth_check = CategoryBusinessRules.can_modify_category(existing, user)
                if not auth_check["can_modify"]:
                    return {
                        "success": False,
                        "data": None,
                        "message": auth_check["reason"],
                    }

            # Validate input data (only validate fields that are being updated)
            update_data = {}

            if "name" in data:
                name_validation = CategoryValidator.validate_name(data["name"])
                if not name_validation["valid"]:
                    return {
                        "success": False,
                        "data": None,
                        "message": "; ".join(name_validation["errors"]),
                    }

                # Check if new name conflicts with existing category
                name_conflict = CategoryRepository.get_by_name(data["name"])
                if name_conflict and name_conflict.id != category_id:
                    return {
                        "success": False,
                        "data": None,
                        "message": "Category name already exists",
                    }

                update_data["name"] = data["name"].strip()

            if "description" in data:
                desc_validation = CategoryValidator.validate_description(
                    data["description"]
                )
                if not desc_validation["valid"]:
                    return {
                        "success": False,
                        "data": None,
                        "message": "; ".join(desc_validation["errors"]),
                    }
                update_data["description"] = (
                    data["description"].strip() if data["description"] else None
                )

            if "icon" in data:
                icon_validation = CategoryValidator.validate_icon(data["icon"])
                if not icon_validation["valid"]:
                    return {
                        "success": False,
                        "data": None,
                        "message": "; ".join(icon_validation["errors"]),
                    }
                update_data["icon"] = data["icon"].strip() if data["icon"] else None

            if "is_active" in data:
                update_data["is_active"] = bool(data["is_active"])

            if not update_data:
                return {
                    "success": False,
                    "data": None,
                    "message": "No valid fields to update",
                }

            category = CategoryRepository.update(category_id, update_data)
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
    def delete_category(category_id: str, user=None) -> Dict[str, Any]:
        """
        Soft delete category with authorization check

        Args:
            category_id (str): Category ID
            user: User object for authorization

        Returns:
            dict: Service response with success status and message
        """
        try:
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return {"success": False, "message": "Category not found"}

            # Check authorization if user is provided
            if user:
                auth_check = CategoryBusinessRules.can_delete_category(category, user)
                if not auth_check["can_delete"]:
                    return {"success": False, "message": auth_check["reason"]}

            CategoryRepository.soft_delete(category_id)
            return {"success": True, "message": "Category deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {str(e)}")
            return {"success": False, "message": f"Error deleting category: {str(e)}"}

    @staticmethod
    def search_categories(
        search_term: str, include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Search categories by name with optional details

        Args:
            search_term (str): Search term
            include_details (bool): Whether to include detailed information

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            if not search_term or not search_term.strip():
                return {
                    "success": False,
                    "data": [],
                    "message": "Search term is required",
                }

            search_term = search_term.strip()

            if include_details:
                categories_data = CategoryDataService.search_categories_with_details(
                    search_term
                )
            else:
                categories = CategoryRepository.search_by_name(search_term)
                categories_data = [category.to_dict() for category in categories]

            return {
                "success": True,
                "data": categories_data,
                "message": f"Found {len(categories_data)} categories",
            }
        except Exception as e:
            logger.error(f"Error searching categories: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"Error searching categories: {str(e)}",
            }


class UserFavoriteCategoryService:
    """Service for user favorite category operations"""

    @staticmethod
    def get_user_favorite_categories(
        user_id: str, include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get user's favorite categories

        Args:
            user_id (str): User ID
            include_details (bool): Whether to include detailed information

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            if include_details:
                categories_data = (
                    CategoryDataService.get_user_favorite_categories_with_details(
                        user_id
                    )
                )
            else:
                favorites = UserFavoriteCategoryRepository.get_user_favorite_categories(
                    user_id
                )
                categories_data = []

                for favorite, category in favorites:
                    category_data = category.to_dict()
                    category_data["is_favorite"] = True
                    category_data["favorited_at"] = (
                        favorite.created_at.isoformat() + "Z"
                        if favorite.created_at
                        else None
                    )
                    categories_data.append(category_data)

            return {
                "success": True,
                "data": categories_data,
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
    def add_favorite_category(user_id: str, category_id: str) -> Dict[str, Any]:
        """
        Add category to user favorites with validation

        Args:
            user_id (str): User ID
            category_id (str): Category ID

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            # Check if category exists and is active
            category = CategoryRepository.get_by_id(category_id)
            if not category:
                return {"success": False, "message": "Category not found"}

            # Business rule check (could be extended)
            if not CategoryBusinessRules.is_category_active(category):
                return {"success": False, "message": "Category is not active"}

            # Check if already in favorites
            is_already_favorite = UserFavoriteCategoryRepository.is_favorite(
                user_id, category_id
            )
            if is_already_favorite:
                return {
                    "success": False,
                    "message": "Category is already in favorites",
                }

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
    def remove_favorite_category(user_id: str, category_id: str) -> Dict[str, Any]:
        """
        Remove category from user favorites

        Args:
            user_id (str): User ID
            category_id (str): Category ID

        Returns:
            dict: Service response with success status and message
        """
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
    def clear_all_favorite_categories(user_id: str) -> Dict[str, Any]:
        """
        Clear all favorite categories for a user

        Args:
            user_id (str): User ID

        Returns:
            dict: Service response with success status and message
        """
        try:
            result = UserFavoriteCategoryRepository.clear_all_user_favorites(user_id)
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Cleared {result['deleted_count']} favorite categories",
                    "deleted_count": result["deleted_count"],
                }
            else:
                return {
                    "success": False,
                    "message": f"Error clearing favorites: {result['error']}",
                }
        except Exception as e:
            logger.error(f"Error clearing user favorite categories: {str(e)}")
            return {
                "success": False,
                "message": f"Error clearing favorite categories: {str(e)}",
            }

    @staticmethod
    def check_is_favorite(user_id: str, category_id: str) -> Dict[str, Any]:
        """
        Check if category is in user favorites

        Args:
            user_id (str): User ID
            category_id (str): Category ID

        Returns:
            dict: Service response with success status, data, and message
        """
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
    def get_most_favorite_categories(limit: int = 10) -> Dict[str, Any]:
        """
        Get most favorited categories

        Args:
            limit (int): Maximum number of categories to return

        Returns:
            dict: Service response with success status, data, and message
        """
        try:
            # Validate limit
            if limit < 1:
                limit = 10
            elif limit > 100:  # Prevent excessive requests
                limit = 100

            trending_data = CategoryDataService.get_trending_categories(limit)

            return {
                "success": True,
                "data": trending_data,
                "message": "Most favorite categories retrieved successfully",
            }
        except Exception as e:
            logger.error(f"Error getting most favorite categories: {str(e)}")
            return {
                "success": False,
                "data": [],
                "message": f"Error retrieving most favorite categories: {str(e)}",
            }
