from app import create_app
from app.utils import app_logger as logger

# Create the application instance
app = create_app()

if __name__ == "__main__":
    logger.info("Memulai aplikasi GoFood API")
    app.run(debug=True, host="0.0.0.0")
    logger.info("Aplikasi GoFood API dihentikan")
