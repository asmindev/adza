from app.extensions import db
from app.modules.review.models import Review
from app.utils import db_logger as logger


class ReviewRepository:
    @staticmethod
    def get_by_food_id(food_id):
        """Get all reviews for a specific food, ordered by creation date"""
        logger.debug(f"Mengambil review untuk makanan dengan ID: {food_id}")
        return Review.query.filter_by(food_id=food_id).order_by(
            Review.created_at.desc()
        )

    @staticmethod
    def get_by_user_id(user_id):
        """Get all reviews by a specific user, ordered by creation date"""
        logger.debug(f"Mengambil review dari pengguna dengan ID: {user_id}")
        return Review.query.filter_by(user_id=user_id).order_by(
            Review.created_at.desc()
        )

    @staticmethod
    def get_by_user_and_food(user_id, food_id):
        """Get a specific review by user and food"""
        logger.debug(f"Mencari review untuk makanan {food_id} dari pengguna {user_id}")
        return Review.query.filter_by(user_id=user_id, food_id=food_id).first()

    @staticmethod
    def get_by_id(review_id):
        """Get review by ID"""
        logger.debug(f"Mencari review dengan ID: {review_id}")
        return Review.query.get(review_id)

    @staticmethod
    def create(review):
        """Create a new review"""
        try:
            db.session.add(review)
            db.session.commit()
            logger.info(f"Review baru berhasil dibuat dengan ID: {review.id}")
            return review
        except Exception as e:
            logger.error(f"Gagal membuat review: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update(review):
        """Update an existing review"""
        try:
            db.session.commit()
            logger.info(f"Review dengan ID {review.id} berhasil diperbarui")
            return review
        except Exception as e:
            logger.error(f"Gagal memperbarui review dengan ID {review.id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def delete(review):
        """Delete a review"""
        try:
            db.session.delete(review)
            db.session.commit()
            logger.info(f"Review dengan ID {review.id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(f"Gagal menghapus review dengan ID {review.id}: {str(e)}")
            db.session.rollback()
            return False
