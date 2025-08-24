from app.extensions import db
from app.modules.food.models import Food, FoodImage
from app.utils import db_logger as logger


class FoodRepository:
    @staticmethod
    def get_all():
        logger.debug("Mengambil semua makanan dari database")
        foods = Food.query.all()
        logger.info(f"Berhasil mengambil {len(foods)} makanan")
        return foods

    @staticmethod
    def get_all_with_limit(page=1, limit=10, search=None):
        logger.debug(
            f"Mengambil makanan dengan pagination: page={page}, limit={limit}, search={search}"
        )
        query = Food.query

        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Food.name.ilike(search_term),
                    Food.description.ilike(search_term),
                    Food.category.ilike(search_term),
                )
            )
            logger.info(f"Menerapkan filter pencarian: {search}")

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        foods = query.order_by(Food.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )

        logger.info(
            f"Berhasil mengambil {len(foods.items)} makanan (total {total_count})"
        )
        return {
            "items": foods.items,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": foods.pages,
        }

    @staticmethod
    def get_by_id(food_id):
        logger.debug(f"Mencari makanan dengan ID: {food_id}")
        food = Food.query.get(food_id)
        logger.info(f"Food found: {food.name}")
        if food:
            logger.info(f"Makanan dengan ID {food_id} ditemukan")
        else:
            logger.warning(f"Makanan dengan ID {food_id} tidak ditemukan")
        return food

    @staticmethod
    def get_by_category(category, limit=10):
        logger.debug(f"Mencari makanan dengan kategori: {category}")
        foods = Food.query.filter_by(category=category).limit(limit).all()
        logger.info(
            f"Berhasil mengambil {len(foods)} makanan dengan kategori {category}"
        )
        return foods

    @staticmethod
    def create(food):
        try:
            db.session.add(food)
            db.session.commit()
            logger.info(f"Makanan baru berhasil dibuat dengan ID: {food.id}")
            return food
        except Exception as e:
            logger.error(f"Gagal membuat makanan: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update(food):
        try:
            db.session.commit()
            logger.info(f"Makanan dengan ID {food.id} berhasil diperbarui")
            return food
        except Exception as e:
            logger.error(f"Gagal memperbarui makanan dengan ID {food.id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def delete(food):
        try:
            db.session.delete(food)
            db.session.commit()
            logger.info(f"Makanan dengan ID {food.id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(f"Gagal menghapus makanan dengan ID {food.id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def add_food_image(food_id, filename):
        """
        Add an image to a food item

        Args:
            food_id (int): The ID of the food
            file_path (str): The path to the image file

        Returns:
            FoodImage: The created food image object
        """
        try:
            food_image = FoodImage(food_id=food_id, filename=filename)
            db.session.add(food_image)
            db.session.commit()
            logger.info(f"Gambar berhasil ditambahkan untuk makanan ID: {food_id}")
            return food_image
        except Exception as e:
            logger.error(
                f"Gagal menambahkan gambar untuk makanan ID {food_id}: {str(e)}"
            )
            db.session.rollback()
            raise

    @staticmethod
    def get_food_images(food_id):
        """
        Get all images for a food item

        Args:
            food_id (int): The ID of the food

        Returns:
            list: List of FoodImage objects
        """
        logger.debug(f"Mengambil gambar untuk makanan ID: {food_id}")
        images = FoodImage.query.filter_by(food_id=food_id).all()
        logger.info(
            f"Berhasil mengambil {len(images)} gambar untuk makanan ID: {food_id}"
        )
        return images

    @staticmethod
    def delete_food_images(food_id):
        """
        Delete all images for a food item

        Args:
            food_id (int): The ID of the food

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            images = FoodImage.query.filter_by(food_id=food_id).all()
            for image in images:
                db.session.delete(image)
            db.session.commit()
            logger.info(f"Semua gambar untuk makanan ID {food_id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(f"Gagal menghapus gambar untuk makanan ID {food_id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def delete_food_image(image_id):
        """
        Delete a specific food image by ID

        Args:
            image_id (int): The ID of the image to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            image = FoodImage.query.get(image_id)
            if image:
                db.session.delete(image)
                db.session.commit()
                logger.info(f"Gambar dengan ID {image_id} berhasil dihapus")
                return True
            else:
                logger.warning(f"Gambar dengan ID {image_id} tidak ditemukan")
                return False
        except Exception as e:
            logger.error(f"Gagal menghapus gambar dengan ID {image_id}: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def get_food_image(image_id):
        """
        Get a specific food image by ID

        Args:
            image_id (int): The ID of the image

        Returns:
            FoodImage: The image object if found, None otherwise
        """
        logger.debug(f"Mencari gambar dengan ID: {image_id}")
        image = FoodImage.query.get(image_id)
        if image:
            logger.info(f"Gambar dengan ID {image_id} ditemukan")
        else:
            logger.warning(f"Gambar dengan ID {image_id} tidak ditemukan")
        return image
