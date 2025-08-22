from app.extensions import db
from app.modules.rating.models import FoodRating, RestaurantRating
from app.utils import api_logger as logger
from sqlalchemy import func


class FoodRatingRepository:
    @staticmethod
    def get_by_food_id(food_id):
        """Get all ratings for a specific food"""
        logger.debug(f"Mengambil rating untuk makanan dengan ID: {food_id}")
        ratings = FoodRating.query.filter_by(food_id=food_id).all()
        logger.info(f"Berhasil mengambil {len(ratings)} rating untuk makanan {food_id}")
        return ratings

    @staticmethod
    def get_by_user_id(user_id):
        """Get all ratings given by a specific user"""
        logger.debug(f"Mengambil rating dari pengguna dengan ID: {user_id}")
        ratings = FoodRating.query.filter_by(user_id=user_id).all()
        logger.info(f"Berhasil mengambil {len(ratings)} rating dari pengguna {user_id}")
        return ratings

    @staticmethod
    def get_user_rating(user_id, food_id):
        """Get specific rating by user for a food"""
        logger.debug(f"Mencari rating untuk makanan {food_id} dari pengguna {user_id}")
        rating = FoodRating.query.filter_by(user_id=user_id, food_id=food_id).first()
        if rating:
            logger.info(f"Rating ditemukan: {rating.rating}")
        else:
            logger.info(
                f"Tidak ada rating untuk makanan {food_id} dari pengguna {user_id}"
            )
        return rating

    @staticmethod
    def get_food_average_rating(food_id):
        """Calculate average rating for a food"""
        logger.debug(f"Menghitung rata-rata rating untuk makanan {food_id}")
        result = (
            db.session.query(func.avg(FoodRating.rating))
            .filter_by(food_id=food_id)
            .scalar()
        )
        avg_rating = round(float(result), 2) if result else 0.0
        logger.info(f"Rata-rata rating untuk makanan {food_id}: {avg_rating}")
        return avg_rating

    @staticmethod
    def get_food_rating_count(food_id):
        """Get total number of ratings for a food"""
        logger.debug(f"Menghitung jumlah rating untuk makanan {food_id}")
        count = FoodRating.query.filter_by(food_id=food_id).count()
        logger.info(f"Jumlah rating untuk makanan {food_id}: {count}")
        return count

    @staticmethod
    def create(rating_data):
        """Create new rating"""
        try:
            rating = FoodRating(**rating_data)
            db.session.add(rating)
            db.session.commit()
            logger.info(f"Rating baru berhasil dibuat dengan ID: {rating.id}")
            return rating
        except Exception as e:
            logger.error(f"Gagal membuat rating: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update(rating, update_data):
        """Update existing rating"""
        try:
            for key, value in update_data.items():
                if hasattr(rating, key):
                    setattr(rating, key, value)
            db.session.commit()
            logger.info(f"Rating dengan ID {rating.id} berhasil diperbarui")
            return rating
        except Exception as e:
            logger.error(f"Gagal memperbarui rating dengan ID {rating.id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def delete(rating):
        """Delete rating"""
        try:
            db.session.delete(rating)
            db.session.commit()
            logger.info(f"Rating dengan ID {rating.id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(f"Gagal menghapus rating dengan ID {rating.id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def get_all():
        """Get all ratings"""
        return FoodRating.query.all()


# Legacy alias for backward compatibility
RatingRepository = FoodRatingRepository


class RestaurantRatingRepository:
    @staticmethod
    def get_by_restaurant_id(restaurant_id):
        logger.debug(f"Mengambil rating untuk restaurant dengan ID: {restaurant_id}")
        ratings = RestaurantRating.query.filter_by(restaurant_id=restaurant_id).all()
        return ratings

    @staticmethod
    def get_by_user_id(user_id):
        logger.debug(f"Mengambil rating restaurant dari pengguna dengan ID: {user_id}")
        ratings = RestaurantRating.query.filter_by(user_id=user_id).all()
        logger.info(
            f"Berhasil mengambil {len(ratings)} rating restaurant dari pengguna {user_id}"
        )
        return ratings

    @staticmethod
    def get_user_rating(user_id, restaurant_id):
        logger.debug(
            f"Mencari rating restaurant {restaurant_id} dari pengguna {user_id}"
        )
        rating = RestaurantRating.query.filter_by(
            user_id=user_id, restaurant_id=restaurant_id
        ).first()
        if rating:
            logger.info(f"Rating restaurant ditemukan: {rating.rating}")
        else:
            logger.info(
                f"Tidak ada rating untuk restaurant {restaurant_id} dari pengguna {user_id}"
            )
        return rating

    @staticmethod
    def get_restaurant_average_rating(restaurant_id):
        logger.debug(f"Menghitung rata-rata rating untuk restaurant {restaurant_id}")
        result = (
            db.session.query(func.avg(RestaurantRating.rating))
            .filter_by(restaurant_id=restaurant_id)
            .scalar()
        )
        avg_rating = float(result) if result else None
        logger.info(f"Rata-rata rating untuk restaurant {restaurant_id}: {avg_rating}")
        return avg_rating

    @staticmethod
    def get_restaurant_rating_count(restaurant_id):
        logger.debug(f"Menghitung jumlah rating untuk restaurant {restaurant_id}")
        count = RestaurantRating.query.filter_by(restaurant_id=restaurant_id).count()
        logger.info(f"Jumlah rating untuk restaurant {restaurant_id}: {count}")
        return count

    @staticmethod
    def create(rating):
        try:
            db.session.add(rating)
            db.session.commit()
            logger.info(
                f"Rating restaurant baru berhasil dibuat dengan ID: {rating.id}"
            )
            return rating
        except Exception as e:
            logger.error(f"Gagal membuat rating restaurant: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update(rating):
        try:
            db.session.commit()
            logger.info(f"Rating restaurant dengan ID {rating.id} berhasil diperbarui")
            return rating
        except Exception as e:
            logger.error(
                f"Gagal memperbarui rating restaurant dengan ID {rating.id}: {str(e)}"
            )
            db.session.rollback()
            raise

    @staticmethod
    def delete(rating):
        try:
            db.session.delete(rating)
            db.session.commit()
            logger.info(f"Rating restaurant dengan ID {rating.id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(
                f"Gagal menghapus rating restaurant dengan ID {rating.id}: {str(e)}"
            )
            db.session.rollback()
            return False
