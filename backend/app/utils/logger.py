import logging
import os
from logging.handlers import RotatingFileHandler

# Buat direktori logs jika belum ada
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Single log file untuk semua activity
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Format log
LOG_FORMAT = "%(asctime)s - %(pathname)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name):
    """
    Mendapatkan logger yang hanya menulis ke file (tidak ke terminal)

    Args:
        name (str): Nama logger/module

    Returns:
        Logger object yang sudah dikonfigurasi
    """
    # Setup formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Setup file handler dengan rotating (10MB per file, max 5 backup)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB
    )
    file_handler.setFormatter(formatter)

    # Setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Hapus handler yang sudah ada untuk menghindari duplikasi
    if logger.handlers:
        logger.handlers = []

    # Tambahkan HANYA file handler (TIDAK ada console handler)
    logger.addHandler(file_handler)

    # Prevent propagation ke root logger (hindari double logging)
    logger.propagate = False

    return logger
