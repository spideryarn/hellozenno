In Python, use lower-case types for type-hinting, e.g. `list` instead of `List`.

## Logging

- Backend logging uses Loguru and is configured in `utils/logging_utils.py`
- Use `from loguru import logger` for importing the logger
- Log with appropriate levels: `logger.debug()`, `logger.info()`, `logger.warning()`, `logger.error()`
- Flask and Werkzeug logs are automatically redirected to Loguru
- Frontend (Vite) logs are captured in `logs/vite_dev.log`

see also REFACTORING.md