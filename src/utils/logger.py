"""
Logging configuration for WATCHDOG
Provides structured logging to files and console with user-friendly error messages
"""

import logging
import os
import re
import stat
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from cryptography.fernet import Fernet

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


class SanitizingFormatter(logging.Formatter):
    """Custom formatter that redacts sensitive data from log messages"""

    # Patterns to redact
    IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    IPV6_PATTERN = re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b")
    MAC_PATTERN = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
    PORT_PATTERN = re.compile(r":(\d{1,5})\b")

    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        message = super().format(record)
        # Redact IPs
        message = self.IP_PATTERN.sub("[REDACTED_IP]", message)
        message = self.IPV6_PATTERN.sub("[REDACTED_IPV6]", message)
        # Redact MAC addresses
        message = self.MAC_PATTERN.sub("[REDACTED_MAC]", message)

        # Redact ports (keep common ones, redact others)
        def redact_port(match):
            port = int(match.group(1))
            if port in [80, 443, 22, 53, 21, 25, 110, 143, 993, 995]:
                return match.group(0)  # Keep common ports
            return ":[REDACTED_PORT]"

        message = self.PORT_PATTERN.sub(redact_port, message)
        return message


class EncryptedFileHandler(RotatingFileHandler):
    """File handler that encrypts log entries before writing"""

    def __init__(
        self, filename, key, mode="a", maxBytes=0, backupCount=0, encoding=None, delay=False
    ):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.cipher = Fernet(key)

    def emit(self, record):
        try:
            msg = self.format(record)
            # Encrypt the message
            encrypted_msg = self.cipher.encrypt(msg.encode(self.encoding))
            # Write to file with newline
            self.stream.write(encrypted_msg.decode("ascii") + "\n")
            self.stream.flush()
        except Exception:
            self.handleError(record)


class KeyManager:
    """Manages encryption key generation and storage"""

    def __init__(self, key_dir: str = "logs"):
        self.key_dir = Path(key_dir)
        self.key_file = self.key_dir / ".log_encryption_key"
        self._ensure_key()

    def _ensure_key(self):
        """Generate or load encryption key"""
        self.key_dir.mkdir(parents=True, exist_ok=True)

        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
            # Restrict key file permissions
            os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)

    def get_key(self) -> bytes:
        """Get the encryption key"""
        return self.key


class WatchdogLogger:
    """Centralized logging configuration for WATCHDOG application"""

    def __init__(
        self,
        log_dir: str = "logs",
        app_name: str = "watchdog",
        enable_encryption: bool = True,
        enable_sanitization: bool = True,
    ):
        """
        Initialize logger with file and console handlers

        Args:
            log_dir: Directory to store log files
            app_name: Name of the application for log file naming
            enable_encryption: Whether to encrypt log files
            enable_sanitization: Whether to sanitize sensitive data from logs
        """
        # Use user-specific logs directory on macOS if frozen or if CWD is /
        if log_dir == "logs":
            if hasattr(sys, "frozen") or os.getcwd() == "/":
                home = os.path.expanduser("~")
                log_dir = os.path.join(home, "Library", "Logs", "Watchdog")

        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.enable_encryption = enable_encryption
        self.enable_sanitization = enable_sanitization
        self.logger = None

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize key manager if encryption is enabled
        if self.enable_encryption:
            self.key_manager = KeyManager(str(self.log_dir))

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
        if self.enable_sanitization:
            detailed_formatter = SanitizingFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            detailed_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        simple_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler for all logs with rotation (with error handling)
        try:
            log_file = self.log_dir / f"{self.app_name}_{datetime.now().strftime('%Y%m%d')}.log"
            if self.enable_encryption:
                file_handler = EncryptedFileHandler(
                    log_file,
                    key=self.key_manager.get_key(),
                    maxBytes=10 * 1024 * 1024,  # 10 MB
                    backupCount=5,
                    encoding="utf-8",
                )
            else:
                file_handler = RotatingFileHandler(
                    log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10 MB
                )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            # Restrict file permissions to owner-only
            os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR)
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not create log file: {e}. Using console-only logging.")

        # File handler for errors only with rotation (with error handling)
        try:
            error_file = (
                self.log_dir / f"{self.app_name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
            )
            if self.enable_encryption:
                error_handler = EncryptedFileHandler(
                    error_file,
                    key=self.key_manager.get_key(),
                    maxBytes=5 * 1024 * 1024,  # 5 MB
                    backupCount=3,
                    encoding="utf-8",
                )
            else:
                error_handler = RotatingFileHandler(
                    error_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"  # 5 MB
                )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(error_handler)
            # Restrict file permissions to owner-only
            os.chmod(error_file, stat.S_IRUSR | stat.S_IWUSR)
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
