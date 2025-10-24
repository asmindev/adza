from app import create_app
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create the application instance
app = create_app()

if __name__ == "__main__":
    logger.info("Memulai aplikasi GoFood API")
    app.run(debug=True, host="0.0.0.0")
    logger.info("Aplikasi GoFood API dihentikan")
