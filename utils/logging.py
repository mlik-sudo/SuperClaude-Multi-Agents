#!/usr/bin/env python3
"""
🪵 Enhanced Logging System for SuperClaude

Provides structured logging with:
- JSON and text output formats
- Log rotation
- Performance tracking
- Context injection
- Multiple log levels
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import structlog
from pythonjsonlogger import jsonlogger

# Try to import config, fallback if not available
try:
    from config import settings
except ImportError:
    settings = None


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> None:
    """
    Configure comprehensive logging system.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' or 'text')
        log_dir: Directory for log files
        enable_console: Enable console output
        enable_file: Enable file output
    """
    # Get configuration from settings or use defaults
    if settings:
        log_level = log_level or settings.log_level
        log_format = log_format or settings.log_format
        log_dir = log_dir or settings.log_dir
    else:
        log_level = log_level or "INFO"
        log_format = log_format or "text"
        log_dir = log_dir or Path("./logs")

    # Ensure log directory exists
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if log_format == "json":
            console_formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s"
            )
        else:
            console_formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if enable_file:
        # Main log file with rotation (max 10MB, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "super_claude.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)

        if log_format == "json":
            file_formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
            )
        else:
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s | %(pathname)s:%(lineno)d",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Error-only log file
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

        # Time-based rotation (daily)
        timed_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / "super_claude_daily.log",
            when="midnight",
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding="utf-8"
        )
        timed_handler.setLevel(log_level)
        timed_handler.setFormatter(file_formatter)
        root_logger.addHandler(timed_handler)

    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging initialized: level={log_level}, format={log_format}, dir={log_dir}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def get_structlog_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structlog logger instance with context binding.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class PerformanceLogger:
    """
    Context manager for performance logging.

    Usage:
        with PerformanceLogger("agent_execution", agent_name="watch_collect"):
            # ... code to measure ...
    """

    def __init__(self, operation: str, **context):
        """
        Initialize performance logger.

        Args:
            operation: Name of operation being measured
            **context: Additional context to log
        """
        self.operation = operation
        self.context = context
        self.logger = get_logger(__name__)
        self.start_time = None

    def __enter__(self):
        """Start timing."""
        import time
        self.start_time = time.perf_counter()
        self.logger.debug(
            f"Starting {self.operation}",
            extra={"context": self.context}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        import time
        duration = time.perf_counter() - self.start_time

        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation} in {duration:.3f}s",
                extra={
                    "context": self.context,
                    "duration_seconds": duration,
                    "status": "success"
                }
            )
        else:
            self.logger.error(
                f"Failed {self.operation} after {duration:.3f}s: {exc_val}",
                extra={
                    "context": self.context,
                    "duration_seconds": duration,
                    "status": "error",
                    "exception": str(exc_val)
                },
                exc_info=True
            )
        return False  # Don't suppress exceptions


# Initialize logging on import if settings available
if settings:
    try:
        setup_logging()
    except Exception as e:
        # Fallback to basic logging if setup fails
        logging.basicConfig(level=logging.INFO)
        logging.warning(f"Failed to initialize enhanced logging: {e}")
