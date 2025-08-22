from app.extensions import db
from app.modules.review.models import Review
from app.utils import db_logger as logger


class ReviewRepository:
    @staticmethod
    def get_by_food_id(food_id):
        logger.debug(f"Mengambil review untuk makanan dengan ID: {food_id}")
        reviews = Review.query.filter_by(food_id=food_id).all()
        logger.info(f"Berhasil mengambil {len(reviews)} review untuk makanan {food_id}")
        return reviews

    @staticmethod
    def get_by_user_id(user_id):
        logger.debug(f"Mengambil review dari pengguna dengan ID: {user_id}")
        reviews = Review.query.filter_by(user_id=user_id).all()
        logger.info(f"Berhasil mengambil {len(reviews)} review dari pengguna {user_id}")
        return reviews

    @staticmethod
    def get_by_user_and_food(user_id, food_id):
        logger.debug(f"Mencari review untuk makanan {food_id} dari pengguna {user_id}")
        review = Review.query.filter_by(user_id=user_id, food_id=food_id).first()
        if review:
            logger.info(f"Review ditemukan dengan ID: {review.id}")
        else:
            logger.info(
                f"Tidak ada review untuk makanan {food_id} dari pengguna {user_id}"
            )
        return review

    @staticmethod
    def create(review):
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
        try:
            db.session.delete(review)
            db.session.commit()
            logger.info(f"Review dengan ID {review.id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(f"Gagal menghapus review dengan ID {review.id}: {str(e)}")
            db.session.rollback()
            return False
