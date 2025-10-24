# 🚀 Quick Reference - Logging System

## Import & Usage

```python
from app.utils import get_logger

logger = get_logger(__name__)
logger.info("Your message")
```

## Common Commands

```bash
# View last 20 lines
tail -20 logs/app.log

# Real-time monitoring (Ctrl+C to exit)
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# Search by module
grep "recommendation" logs/app.log | tail -10

# Count log entries
wc -l logs/app.log

# Clear logs (if needed)
echo "" > logs/app.log
```

## Log Levels

```python
logger.debug("Debug info")
logger.info("Normal operation")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")

# With exception traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

## File Structure

```
logs/
├── app.log         # Current log (max 10MB)
├── app.log.1       # Backup 1
├── app.log.2       # Backup 2
├── app.log.3       # Backup 3
├── app.log.4       # Backup 4
└── app.log.5       # Backup 5 (oldest)
```

## Benefits

✅ **Single file** - All logs in one place
✅ **Clean terminal** - No log noise
✅ **Auto-rotation** - 10MB max, 5 backups
✅ **Easy monitoring** - Use `tail -f`
✅ **Consistent format** - Same structure everywhere

## Migration Complete

-   ❌ Old: `app_logger`, `api_logger`, `db_logger`, etc.
-   ✅ New: `get_logger(__name__)` everywhere
-   ✅ No console output
-   ✅ Single log file: `logs/app.log`

---

**See LOGGING_INFO.md for detailed documentation**
