"""Logging configuration for SPU Processing Tool.

Uses loguru for beautiful, easy-to-use logging with file output.
"""

import sys
import os
from datetime import datetime
from loguru import logger

# Remove default handler
logger.remove()

# Log file path
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = None


def setup_logger(verbose: bool = False, log_to_file: bool = True):
    """Setup logging configuration.

    Args:
        verbose: If True, show DEBUG level messages to console
        log_to_file: If True, also write logs to file
    """
    global LOG_FILE

    # Remove any existing handlers
    logger.remove()

    # Console handler - colored output
    console_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=console_level,
        format="<level>{level: <8}</level> | <cyan>{message}</cyan>",
        colorize=True,
        filter=lambda record: record["level"].name not in ["DEBUG"] or verbose
    )

    # File handler - detailed logging
    if log_to_file:
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        LOG_FILE = os.path.join(LOG_DIR, f"spu_tool_{timestamp}.log")

        logger.add(
            LOG_FILE,
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8"
        )

        logger.info(f"Log file: {LOG_FILE}")


def get_logger():
    """Get the configured logger instance."""
    return logger


def get_log_file():
    """Get the current log file path."""
    return LOG_FILE


class ProcessingLogger:
    """Context manager for logging processing operations."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(f"Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type is None:
            logger.info(f"Completed: {self.operation_name} ({duration.total_seconds():.2f}s)")
        else:
            logger.error(f"Failed: {self.operation_name} ({duration.total_seconds():.2f}s) - {exc_val}")
        return False  # Don't suppress exceptions

    def log_step(self, message: str):
        """Log a step within the operation."""
        logger.debug(f"  {message}")

    def log_warning(self, message: str):
        """Log a warning."""
        logger.warning(f"  {message}")

    def log_error(self, message: str):
        """Log an error."""
        logger.error(f"  {message}")


# Export convenience functions
def info(message: str):
    """Log info message."""
    logger.info(message)


def debug(message: str):
    """Log debug message."""
    logger.debug(message)


def warning(message: str):
    """Log warning message."""
    logger.warning(message)


def error(message: str):
    """Log error message."""
    logger.error(message)


def exception(message: str):
    """Log exception with traceback."""
    logger.exception(message)
