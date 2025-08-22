import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Buat direktori logs jika belum ada
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Format log
LOG_FORMAT = "%(asctime)s - %(pathname)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Setup logger
def setup_logger(name, log_file, level=logging.INFO):
    """
    Membuat logger dengan konfigurasi custom

    Args:
        name (str): Nama logger
        log_file (str): Path untuk menyimpan file log
        level (int): Level logging (default: INFO)

    Returns:
        Logger object
    """
    # Buat path file log yang lengkap
    log_file_path = os.path.join(LOG_DIR, log_file)

    # Setup formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Setup file handler dengan rotating
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB
    )
    file_handler.setFormatter(formatter)

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Setup logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Hapus handler yang sudah ada untuk menghindari duplikasi
    if logger.handlers:
        logger.handlers = []

    # Tambahkan handler baru
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Logger umum untuk aplikasi
app_logger = setup_logger("app", "app.log")

# Logger untuk rekomendasi
recommendation_logger = setup_logger("recommendation", "recommendation.log")

# Logger untuk model training
training_logger = setup_logger("training", "training.log")

# Logger untuk API
api_logger = setup_logger("api", "api.log")

# Logger untuk database
db_logger = setup_logger("database", "database.log")


def get_logger(name):
    """
    Mendapatkan logger berdasarkan nama

    Args:
        name (str): Nama modul atau komponen

    Returns:
        Logger yang sesuai dengan komponen
    """
    if "recommendation" in name.lower():
        return recommendation_logger
    elif "api" in name.lower() or "route" in name.lower():
        return api_logger
    elif "database" in name.lower() or "model" in name.lower():
        return db_logger
    elif "train" in name.lower():
        return training_logger
    else:
        return app_logger
