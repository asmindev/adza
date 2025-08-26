from app.modules.review.repository import ReviewRepository
from app.modules.review.models import Review
from app.modules.user.repository import UserRepository
from app.modules.food.repository import FoodRepository
from app.utils import db_logger as logger
import math


class ReviewService:
    @staticmethod
    def validate_pagination(page, limit):
        """Validate pagination parameters"""
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        return page, limit

    @staticmethod
    def validate_rating(rating):
        """Validate rating value"""
        if not rating or not isinstance(rating, (int, float)) or not (1 <= rating <= 5):
            raise ValueError("Rating is required and must be between 1 and 5")
        return float(rating)

    @staticmethod
    def validate_content(content):
        """Validate review content"""
        if not content or not content.strip():
            raise ValueError("Review content is required")
        return content.strip()

    @staticmethod
    def validate_user_and_food(user_id, food_id):
        """Validate if user and food exist"""
        user = UserRepository.get_by_id(user_id)
        food = FoodRepository.get_by_id(food_id)

        if not user:
            raise ValueError("User not found")
        if not food:
            raise ValueError("Food not found")

        return user, food

    @staticmethod
    def apply_pagination(query, page, limit):
        """Apply pagination to a query and return structured result"""
        # Validate pagination parameters
        page, limit = ReviewService.validate_pagination(page, limit)

        # Get total count
        total_count = query.count()

        # Calculate pages
        pages = math.ceil(total_count / limit) if total_count > 0 else 1

        # Apply pagination
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        logger.info(
            f"Pagination applied: page={page}, limit={limit}, total={total_count}"
        )

        return {
            "items": items,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    @staticmethod
    def get_food_reviews(food_id, page=1, limit=10):
        """Get paginated reviews for a specific food"""
        logger.info(f"Getting reviews for food {food_id} with pagination")

        query = ReviewRepository.get_by_food_id(food_id)
        result = ReviewService.apply_pagination(query, page, limit)

        logger.info(f"Retrieved {len(result['items'])} reviews for food {food_id}")
        return result

    @staticmethod
    def get_user_reviews(user_id, page=1, limit=10):
        """Get paginated reviews by a specific user"""
        logger.info(f"Getting reviews by user {user_id} with pagination")

        query = ReviewRepository.get_by_user_id(user_id)
        result = ReviewService.apply_pagination(query, page, limit)

        logger.info(f"Retrieved {len(result['items'])} reviews by user {user_id}")
        return result

    @staticmethod
    def get_review(user_id, food_id):
        """Get a specific review by user and food"""
        logger.info(f"Getting review for user {user_id} and food {food_id}")
        return ReviewRepository.get_by_user_and_food(user_id, food_id)

    @staticmethod
    def create_or_update_review(user_id, food_id, content, rating=None):
        """Create or update a review with validation"""
        logger.info(f"Creating/updating review for food {food_id} by user {user_id}")

        # Validate inputs
        ReviewService.validate_user_and_food(user_id, food_id)
        content = ReviewService.validate_content(content)

        if rating is not None:
            rating = ReviewService.validate_rating(rating)

        # Check if review already exists
        existing_review = ReviewRepository.get_by_user_and_food(user_id, food_id)

        if existing_review:
            # Update existing review
            logger.info(f"Updating existing review {existing_review.id}")
            existing_review.content = content
            return ReviewRepository.update(existing_review)
        else:
            # Create new review
            logger.info("Creating new review")
            new_review = Review(user_id=user_id, food_id=food_id, content=content)
            return ReviewRepository.create(new_review)

    @staticmethod
    def delete_review(user_id, food_id):
        """Delete a review with validation"""
        logger.info(f"Deleting review for food {food_id} by user {user_id}")

        review = ReviewRepository.get_by_user_and_food(user_id, food_id)
        if not review:
            logger.warning(f"Review not found for user {user_id} and food {food_id}")
            return False

        return ReviewRepository.delete(review)
