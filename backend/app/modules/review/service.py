from app.modules.review.repository import ReviewRepository
from app.modules.review.models import Review
from app.modules.user.repository import UserRepository
from app.modules.food.repository import FoodRepository
from app.utils import db_logger as logger


class ReviewService:
    @staticmethod
    def get_food_reviews(food_id):
        return ReviewRepository.get_by_food_id(food_id)

    @staticmethod
    def get_user_reviews(user_id):
        return ReviewRepository.get_by_user_id(user_id)

    @staticmethod
    def get_review(user_id, food_id):
        return ReviewRepository.get_by_user_and_food(user_id, food_id)

    @staticmethod
    def create_or_update_review(user_id, food_id, review_text):
        logger.info(
            f"Membuat/memperbarui review untuk makanan {food_id} dari pengguna {user_id}"
        )

        # Verify user and food exist
        user = UserRepository.get_by_id(user_id)
        food = FoodRepository.get_by_id(food_id)

        if not user or not food:
            logger.warning(f"Pengguna {user_id} atau makanan {food_id} tidak ditemukan")
            return None

        # Check if review already exists
        existing_review = ReviewRepository.get_by_user_and_food(user_id, food_id)

        if existing_review:
            # Update existing review
            existing_review.review_text = review_text
            return ReviewRepository.update(existing_review)
        else:
            # Create new review
            new_review = Review(
                user_id=user_id, food_id=food_id, review_text=review_text
            )
            return ReviewRepository.create(new_review)

    @staticmethod
    def delete_review(user_id, food_id):
        logger.info(f"Menghapus review untuk makanan {food_id} dari pengguna {user_id}")
        review = ReviewRepository.get_by_user_and_food(user_id, food_id)

        if not review:
            return False

        return ReviewRepository.delete(review)
