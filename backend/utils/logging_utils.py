"""Logging utilities for the application using loguru."""

import logging
from loguru import logger
import os
import sys
from typing import Optional

from utils.env_config import is_vercel


class LimitingFileWriter:
    """Custom file handler that keeps a maximum number of lines in the log file."""

    def __init__(self, filepath: str, max_lines: int):
        """Initialize the file writer with path and line limit.

        Args:
            filepath: Path to the log file
            max_lines: Maximum number of lines to keep in the file
        """
        self.filepath = filepath
        self.max_lines = max_lines
        self.buffer = []

        # Initialize from existing file if it exists
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    self.buffer = f.readlines()
                    # Only keep the last max_lines
                    self.buffer = self.buffer[-max_lines:]
            except Exception:
                self.buffer = []

    def write(self, message: str) -> None:
        """Write a new message to the log file, maintaining the line limit.

        Args:
            message: The log message to write
        """
        # Add to buffer
        self.buffer.append(message)
        # Trim to max size
        self.buffer = self.buffer[-self.max_lines :]
        # Write full buffer to file
        with open(self.filepath, "w") as f:
            f.writelines(self.buffer)

    def __call__(self, message: str) -> bool:
        """Handle the log message when called by loguru.

        Args:
            message: The log message

        Returns:
            False to indicate message was handled
        """
        self.write(message)
        return False  # Required for sink callbacks


class InterceptHandler(logging.Handler):
    """Handler to intercept standard logging messages and redirect to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Process log record by redirecting it to loguru.

        Args:
            record: The log record to process
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_to_file: bool = True,
    max_lines: int = 100,
    logs_dir: Optional[str] = None,
    for_cloud: bool = False,
):
    """Configure logging for the application.

    Args:
        log_to_file: Whether to log to a file
        max_lines: Maximum number of lines to keep in the log file
        logs_dir: Directory to store log files
        for_cloud: Whether to configure for cloud environment
    """
    # Remove default handler
    logger.remove()

    # Add console output with improved format including exception details
    log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}"
    logger.add(
        sys.stderr, format=log_format, level="INFO", backtrace=True, diagnose=True
    )

    # Add file logging if requested
    if log_to_file:
        if is_vercel():
            # In Vercel, only /tmp is writable
            logs_dir = "/tmp"
        elif logs_dir is None:
            # Default to a logs directory in the application root
            logs_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
            )

        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, "backend.log")

        # Set up line-limited file logging with full traceback and diagnostic information
        file_writer = LimitingFileWriter(log_file_path, max_lines)
        # Add backtrace=True to show traceback frames
        # Add diagnose=True to enable variables inspection in tracebacks
        logger.add(
            file_writer, format=log_format, level="INFO", backtrace=True, diagnose=True
        )

    # Configure standard library logging to use loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Specifically configure Flask and Werkzeug loggers
    for logger_name in ("werkzeug", "flask.app"):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    # Return the logger for backward compatibility
    return logger
