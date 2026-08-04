"""
===============================================================================
Module: utils.logger
===============================================================================

Purpose
-------
Provides a centralized logging framework for QA Sentinel AI.

This module is responsible for configuring application-wide logging and
providing logger instances that can be used consistently across all modules.

Why This Module Exists
----------------------
Logging is a cross-cutting concern used by every layer of the application.

Instead of allowing each module to configure logging independently, this
module centralizes logging configuration to ensure consistency,
maintainability, and extensibility.

Responsibilities
----------------
- Configure application logging.
- Create the log directory if it does not exist.
- Write logs to both the console and a log file.
- Provide a reusable logger instance.

Out of Scope
------------
This module MUST NOT:

- Parse Playwright artifacts.
- Perform AI analysis.
- Generate reports.
- Contain business logic.

Architecture
------------
                    configure_logging()
                             │
                             ▼
                   Configure Loguru Once
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
        Parser          Classifier       Reports
            │                │                │
            └────────────────┴────────────────┘
                             │
                             ▼
                     logger.info(...)

Impact
------
Every module depends on this logging framework.

Changes to this module affect the application's logging behavior globally.
Therefore, the public API should remain stable.

===============================================================================
"""

from pathlib import Path

from loguru import logger

# Directory where application log files will be stored.
LOG_DIRECTORY = Path("logs")

# Default log file name.
LOG_FILE = LOG_DIRECTORY / "qa-sentinel.log"


def configure_logging() -> None:
    """
    Configure application-wide logging.

    This function should be called exactly once during application startup.

    Responsibilities:
        - Create the log directory if required.
        - Configure console logging.
        - Configure file logging.

    Raises:
        OSError:
            If the log directory cannot be created.
    """

    # Ensure the logs directory exists.
    LOG_DIRECTORY.mkdir(exist_ok=True)

    # Remove Loguru's default logger configuration.
    logger.remove()

    # Console logging.
    logger.add(
        sink=lambda message: print(message, end=""),
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan> | "
            "{message}"
        ),
    )

    # File logging.
    logger.add(
        LOG_FILE,
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        enqueue=True,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name} | "
            "{message}"
        ),
    )


def get_logger(__name__):
    """
    Return the shared application logger.

    Returns:
        The configured Loguru logger instance.

    Notes:
        Logging must be configured by calling configure_logging()
        before requesting the logger.
    """

    return logger