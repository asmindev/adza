# 📋 Logging System Documentation

## Overview

Sistem logging telah dikonsolidasasi menjadi **1 file log tunggal** untuk semua activity aplikasi.

## Configuration

### Single Log File

-   **Location**: `logs/app.log`
-   **Max Size**: 10 MB per file
-   **Backup Count**: 5 files (rotating)
-   **Output**: File only (tidak tampil di terminal)

### Logger Function

```python
from app.utils import get_logger

logger = get_logger(__name__)
logger.info("Your message here")
```

## Log Format

```
%(asctime)s - %(pathname)s - %(levelname)s - %(name)s - %(message)s
```

**Example:**

```
2025-10-24 20:22:26 - /home/user/backend/app/recommendation/service.py - INFO - app.recommendation.service - Successfully generated 4 recommendations
```

## Viewing Logs

### View Last 20 Lines

```bash
tail -20 logs/app.log
```

### Real-time Monitoring

```bash
tail -f logs/app.log
```

### Search Logs

```bash
grep "ERROR" logs/app.log
grep "recommendation" logs/app.log | tail -10
```

### Count Errors

```bash
grep -c "ERROR" logs/app.log
```

## Migration Notes

### Old System (Removed)

-   ❌ `app_logger` → Multiple log files
-   ❌ `api_logger` → logs/api.log
-   ❌ `db_logger` → logs/database.log
-   ❌ `recommendation_logger` → logs/recommendation.log
-   ❌ `training_logger` → logs/training.log
-   ❌ Console output (mengganggu Rich Console)

### New System (Current)

-   ✅ `get_logger(__name__)` → Single log file
-   ✅ `logs/app.log` → All activities
-   ✅ No console output (clean terminal)
-   ✅ Log rotation (10MB × 5 backups)
-   ✅ Consistent format

## Benefits

1. **Simplified Management**: 1 file untuk semua logs
2. **Clean Terminal**: Tidak ada log noise di terminal
3. **Better Rich Console**: Rich Console output tidak terganggu
4. **Easy Monitoring**: `tail -f logs/app.log` untuk real-time
5. **Consistent Format**: Semua logs menggunakan format yang sama
6. **Automatic Rotation**: Tidak perlu manual cleanup

## Usage Examples

### In Controllers

```python
from app.utils import get_logger

logger = get_logger(__name__)

@blueprint.route('/api/foods')
def get_foods():
    logger.info("Fetching all foods")
    # ... your code
    logger.info(f"Retrieved {len(foods)} foods")
```

### In Services

```python
from app.utils import get_logger

logger = get_logger(__name__)

class RecommendationService:
    def get_recommendations(self, user_id):
        logger.info(f"Getting recommendations for user {user_id}")
        # ... your code
        logger.info(f"Generated {len(results)} recommendations")
```

### Error Logging

```python
try:
    result = process_data()
except Exception as e:
    logger.error(f"Processing failed: {str(e)}", exc_info=True)
```

## Troubleshooting

### Log File Not Created

```bash
# Create logs directory if missing
mkdir -p logs
```

### Permission Issues

```bash
# Fix permissions
chmod 755 logs/
chmod 644 logs/app.log
```

### Log File Too Large

```bash
# Check size
ls -lh logs/app.log*

# Logs automatically rotate at 10MB
# Maximum 5 backup files kept
```

### View Specific Module Logs

```bash
# Filter by module name
grep "app.recommendation" logs/app.log | tail -20

# Filter by level
grep "ERROR" logs/app.log
grep "WARNING" logs/app.log
```

## Log Levels

-   `DEBUG`: Detailed diagnostic info
-   `INFO`: General informational messages (default)
-   `WARNING`: Warning messages
-   `ERROR`: Error messages
-   `CRITICAL`: Critical error messages

## Best Practices

1. **Use Descriptive Messages**: Include context and values

    ```python
    logger.info(f"User {user_id} rated food {food_id} with {rating} stars")
    ```

2. **Log Important Events**: User actions, errors, state changes

    ```python
    logger.info("Recommendation model trained successfully")
    ```

3. **Include Error Context**: Use exc_info=True for tracebacks

    ```python
    logger.error("Failed to process request", exc_info=True)
    ```

4. **Avoid Logging Sensitive Data**: Passwords, tokens, personal data

    ```python
    # ❌ Bad
    logger.info(f"User login: {username} with password {password}")

    # ✅ Good
    logger.info(f"User login: {username}")
    ```

5. **Use Appropriate Levels**:
    - Info: Normal operations
    - Warning: Unexpected but handled
    - Error: Failures that need attention

## File Structure

```
backend/
├── app/
│   └── utils/
│       └── logger.py        # Logger configuration
└── logs/
    ├── app.log              # Current log file
    ├── app.log.1            # Backup 1 (oldest: 10MB)
    ├── app.log.2            # Backup 2
    ├── app.log.3            # Backup 3
    ├── app.log.4            # Backup 4
    └── app.log.5            # Backup 5 (newest: 10MB)
```

## Monitoring Tools

### Watch Logs in Real-time

```bash
# Terminal 1: Run application
python main.py

# Terminal 2: Monitor logs
tail -f logs/app.log
```

### Filter by Time

```bash
# Logs from today
grep "2025-10-24" logs/app.log
```

### Count Log Entries

```bash
# Total lines
wc -l logs/app.log

# Entries per module
grep -c "app.recommendation" logs/app.log
grep -c "app.modules.user" logs/app.log
```

---

**Last Updated**: October 24, 2025
**Author**: Logging System Migration
