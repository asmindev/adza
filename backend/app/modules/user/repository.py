from app.extensions import db
from app.modules.user.models import User
from app.utils import db_logger as logger


class UserRepository:
    @staticmethod
    def get_all(page=1, limit=10, search=None):
        logger.debug(
            f"Mengambil pengguna dengan pagination: page={page}, limit={limit}, search={search}"
        )
        query = User.query

        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.name.ilike(search_term),
                )
            )
            logger.info(f"Menerapkan filter pencarian: {search}")

        # Get total count for pagination
        total_count = query.count()

        # Apply pagination
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )

        logger.info(
            f"Berhasil mengambil {len(users.items)} pengguna (total {total_count})"
        )
        return {
            "items": users.items,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": users.pages,
        }

    @staticmethod
    def get_by_id(user_id):
        logger.debug(f"Mencari pengguna dengan ID: {user_id}")
        user = User.query.get(user_id)
        if user:
            logger.info(f"Pengguna dengan ID {user_id} ditemukan")
        else:
            logger.warning(f"Pengguna dengan ID {user_id} tidak ditemukan")
        return user

    @staticmethod
    def get_by_username(username):
        logger.debug(f"Mencari pengguna dengan username: {username}")
        user = User.query.filter_by(username=username).first()
        if user:
            logger.info(f"Pengguna dengan username {username} ditemukan")
        else:
            logger.warning(f"Pengguna dengan username {username} tidak ditemukan")
        return user

    @staticmethod
    def create(user):
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"Pengguna baru berhasil dibuat dengan ID: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Gagal membuat pengguna: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def update(user):
        try:
            db.session.commit()
            logger.info(f"Pengguna dengan ID {user.id} berhasil diperbarui")
            return user
        except Exception as e:
            logger.error(f"Gagal memperbarui pengguna dengan ID {user.id}: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def delete(user):
        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Pengguna dengan ID {user.id} berhasil dihapus")
            return True
        except Exception as e:
            logger.error(f"Gagal menghapus pengguna dengan ID {user.id}: {str(e)}")
            db.session.rollback()
            return False
