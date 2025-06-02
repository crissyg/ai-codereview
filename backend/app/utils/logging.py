"""
Logging Configuration

Centralized logging setup with structured formatting, file rotation,
and environment-specific configurations. Provides consistent logging
across all application components.
"""

import logging
import logging.handlers
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Outputs log records as JSON for better parsing in log aggregation systems.
    Includes timestamp, level, message, and additional context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ("name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "exc_info", "exc_text", "stack_info",
                          "lineno", "funcName", "created", "msecs", "relativeCreated",
                          "thread", "threadName", "processName", "process", "getMessage"):
                log_entry[key] = value
        
        return json.dumps(log_entry)

class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for development.
    
    Adds colors to different log levels for better readability
    during development and debugging.
    """
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
        
        return super().format(record)

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    json_format: bool = False,
    rotation: bool = True,
    max_size: str = "10MB",
    backup_count: int = 5
) -> None:
    """
    Setup application logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for console only)
        log_format: Custom log format string
        json_format: Use JSON formatting for structured logs
        rotation: Enable log file rotation
        max_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(numeric_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if json_format:
        console_formatter = JSONFormatter()
    else:
        # Use colored formatter for development
        console_formatter = ColoredFormatter(log_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if rotation:
            # Parse max_size (e.g., "10MB" -> 10*1024*1024)
            size_multipliers = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}
            size_unit = max_size[-2:].upper()
            size_value = int(max_size[:-2])
            max_bytes = size_value * size_multipliers.get(size_unit, 1)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
        else:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
        
        file_handler.setLevel(numeric_level)
        
        # Always use JSON format for file logs
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Log the logging setup
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={level}, file={log_file}, json={json_format}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def add_context_filter(logger_name: str, context: Dict[str, Any]) -> None:
    """
    Add context information to all log records from a specific logger.
    
    Args:
        logger_name: Name of the logger to add context to
        context: Dictionary of context information to add
    """
    class ContextFilter(logging.Filter):
        def filter(self, record):
            for key, value in context.items():
                setattr(record, key, value)
            return True
    
    logger = logging.getLogger(logger_name)
    logger.addFilter(ContextFilter())

def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Useful for debugging and performance monitoring.
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        # Log function entry
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def log_async_function_call(func):
    """
    Decorator to log async function calls with parameters and execution time.
    """
    import functools
    import time
    import asyncio
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        # Log function entry
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Async {func.__name__} completed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Async {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def configure_third_party_loggers() -> None:
    """Configure logging levels for third-party libraries to reduce noise."""
    # Reduce verbosity of common third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

def get_logging_stats() -> Dict[str, Any]:
    """Get statistics about current logging configuration."""
    root_logger = logging.getLogger()
    
    return {
        "level": logging.getLevelName(root_logger.level),
        "handlers": [
            {
                "type": type(handler).__name__,
                "level": logging.getLevelName(handler.level),
                "formatter": type(handler.formatter).__name__ if handler.formatter else None
            }
            for handler in root_logger.handlers
        ],
        "loggers_count": len(logging.Logger.manager.loggerDict),
    }