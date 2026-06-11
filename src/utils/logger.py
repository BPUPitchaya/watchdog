"""
Logging configuration for WATCHDOG
Provides structured logging to files and console with user-friendly error messages
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Redirection for stdout/stderr when running without a console
if sys.stdout is None:

    class DummyWriter:
        def write(self, *args, **kwargs) -> None:
            pass

        def flush(self, *args, **kwargs) -> None:
            pass

    sys.stdout = DummyWriter()
if sys.stderr is None:

    class DummyWriter:
        def write(self, *args, **kwargs) -> None:
            pass

        def flush(self, *args, **kwargs) -> None:
            pass

    sys.stderr = DummyWriter()


class WatchdogLogger:
    """Centralized logging configuration for WATCHDOG application"""

    def __init__(self, log_dir: str = "logs", app_name: str = "watchdog"):
        """
        Initialize logger with file and console handlers

        Args:
            log_dir: Directory to store log files
            app_name: Name of the application for log file naming
        """
        # Use user-specific logs directory on macOS if frozen or if CWD is /
        if log_dir == "logs":
            if hasattr(sys, "frozen") or os.getcwd() == "/":
                home = os.path.expanduser("~")
                log_dir = os.path.join(home, "Library", "Logs", "Watchdog")

        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.logger = None

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self._setup_logger()

    def _setup_logger(self):
        """Configure logger with file and console handlers"""
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler for all logs (with error handling)
        try:
            log_file = self.log_dir / f"{self.app_name}_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not create log file: {e}. Using console-only logging.")

        # File handler for errors only (with error handling)
        try:
            error_file = (
                self.log_dir / f"{self.app_name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
            )
            error_handler = logging.FileHandler(error_file, encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not create error log file: {e}. Using console-only logging.")

        # Console handler (always available)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger


def get_logger(name: str = "watchdog") -> logging.Logger:
    """
    Get a logger instance for a specific module

    Args:
        name: Name of the module requesting the logger

    Returns:
        Logger instance
    """
    # Initialize global logger if not already done
    if not hasattr(get_logger, "_initialized"):
        get_logger._initialized = True
        get_logger._watchdog_logger = WatchdogLogger()

    # Return a child logger with the specified name
    return logging.getLogger(f"watchdog.{name}")


def log_exception(
    logger: logging.Logger, context: str, exception: Exception, user_message: str = None
) -> None:
    """
    Log an exception with context and user-friendly message

    Args:
        logger: Logger instance
        context: Context where the error occurred (e.g., "packet capture", "ML prediction")
        exception: The exception that occurred
        user_message: User-friendly error message (optional)
    """
    logger.error(f"Error in {context}: {type(exception).__name__}: {str(exception)}", exc_info=True)

    if user_message:
        logger.info(f"User message: {user_message}")


def log_performance(logger: logging.Logger, operation: str, duration_ms: float) -> None:
    """
    Log performance metrics

    Args:
        logger: Logger instance
        operation: Name of the operation
        duration_ms: Duration in milliseconds
    """
    logger.debug(f"Performance: {operation} took {duration_ms:.2f}ms")


# User-friendly error messages
ERROR_MESSAGES = {
    "permission_denied": "Permission denied. Please run the application with administrator/root privileges.",
    "network_interface": "Could not access network interface. Please check your network settings and permissions.",
    "ml_model_not_found": "ML model file not found. Please ensure the model is trained and available.",
    "ml_prediction_failed": "Failed to analyze network traffic. ML prediction service unavailable.",
    "firewall_error": "Firewall operation failed. Please check your firewall configuration and permissions.",
    "ollama_not_running": "AI assistant is not available. Please start the Ollama application.",
    "ollama_not_installed": "AI assistant is not installed. Please run the Ollama installer.",
    "packet_capture_failed": "Failed to capture network packets. Please check network permissions.",
    "settings_corrupted": "Settings file is corrupted. Resetting to default values.",
    "ui_error": "An error occurred in the user interface. Please try again.",
    "unknown_error": "An unexpected error occurred. Please check the logs for details.",
}


def get_user_message(error_key: str, **kwargs) -> str:
    """
    Get a user-friendly error message

    Args:
        error_key: Key from ERROR_MESSAGES dictionary
        **kwargs: Additional parameters for message formatting

    Returns:
        User-friendly error message
    """
    message = ERROR_MESSAGES.get(error_key, ERROR_MESSAGES["unknown_error"])
    try:
        return message.format(**kwargs)
    except (KeyError, ValueError):
        return message
