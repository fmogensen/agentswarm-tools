"""
Logging configuration for AgentSwarm Tools.

Provides centralized logging setup for all tools with consistent formatting,
log levels, and output destinations.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# ========== LOGGING CONFIGURATION ==========

# Default log level from environment or INFO
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log file path (optional)
LOG_FILE = os.getenv("LOG_FILE", None)


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    console: bool = True,
) -> logging.Logger:
    """
    Create and configure a logger for a tool.

    Args:
        name: Logger name (usually __name__ from the calling module)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to env LOG_LEVEL or INFO
        log_file: Optional file path to write logs. Defaults to env LOG_FILE
        console: Whether to output to console (default True)

    Returns:
        Configured logger instance

    Example:
        >>> from shared.logging import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("Tool execution started")
    """
    logger = logging.getLogger(name)

    # Set log level
    log_level = level or DEFAULT_LOG_LEVEL
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    file_path = log_file or LOG_FILE
    if file_path:
        # Ensure log directory exists
        log_dir = Path(file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger (avoids duplicate logs)
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with default configuration.

    Convenience method for quick logger setup.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from shared.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    return setup_logger(name)


# ========== CONTEXT MANAGER ==========


class LogContext:
    """
    Context manager for temporary log level changes.

    Example:
        >>> from shared.logging import get_logger, LogContext
        >>> logger = get_logger(__name__)
        >>> with LogContext(logger, "DEBUG"):
        ...     logger.debug("This will be logged")
    """

    def __init__(self, logger: logging.Logger, level: str):
        """
        Initialize log context.

        Args:
            logger: Logger instance to modify
            level: Temporary log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logger
        self.new_level = getattr(logging, level.upper(), logging.INFO)
        self.original_level = logger.level

    def __enter__(self):
        """Set temporary log level."""
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log level."""
        self.logger.setLevel(self.original_level)


# ========== HELPER FUNCTIONS ==========


def set_global_log_level(level: str) -> None:
    """
    Set log level for all existing loggers.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> from shared.logging import set_global_log_level
        >>> set_global_log_level("DEBUG")
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.root.setLevel(log_level)

    # Update all existing loggers
    for logger_name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)


def disable_logger(name: str) -> None:
    """
    Disable a specific logger.

    Args:
        name: Logger name to disable

    Example:
        >>> from shared.logging import disable_logger
        >>> disable_logger("noisy_module")
    """
    logger = logging.getLogger(name)
    logger.disabled = True


def enable_logger(name: str) -> None:
    """
    Enable a previously disabled logger.

    Args:
        name: Logger name to enable

    Example:
        >>> from shared.logging import enable_logger
        >>> enable_logger("module_name")
    """
    logger = logging.getLogger(name)
    logger.disabled = False
