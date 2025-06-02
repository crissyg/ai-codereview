"""
Utilities Package

Common utilities, configuration management, logging setup,
and helper functions used across the application.

Modules:
- Config: Environment variables and application settings
- Logging: Centralized logging configuration
- Helpers: Common utility functions and decorators
"""

from .config import Settings, get_settings
from .logging import setup_logging, get_logger
from .helpers import (
    generate_request_id,
    validate_github_url,
    sanitize_filename,
    calculate_file_hash,
    format_datetime,
    truncate_text,
    retry_with_backoff
)

# Export main utilities
__all__ = [
    # Configuration
    "Settings",
    "get_settings",
    
    # Logging
    "setup_logging", 
    "get_logger",
    
    # Helper functions
    "generate_request_id",
    "validate_github_url",
    "sanitize_filename",
    "calculate_file_hash",
    "format_datetime",
    "truncate_text",
    "retry_with_backoff",
]

# Utility constants
UTILS_VERSION = "1.0.0"

# Common regex patterns
PATTERNS = {
    "github_repo": r"^https://github\.com/[\w\-\.]+/[\w\-\.]+/?$",
    "commit_sha": r"^[a-f0-9]{40}$",
    "branch_name": r"^[\w\-\./]+$",
    "file_extension": r"\.[a-zA-Z0-9]+$",
}

# Default configuration values
DEFAULTS = {
    "request_timeout": 30,
    "max_retries": 3,
    "log_level": "INFO",
    "date_format": "%Y-%m-%d %H:%M:%S UTC",
}

def initialize_utils(settings: Settings = None) -> None:
    """Initialize utilities with application settings."""
    if settings is None:
        settings = get_settings()
    
    # Setup logging with configured level
    setup_logging(level=settings.log_level or DEFAULTS["log_level"])
    
    # Log initialization
    logger = get_logger(__name__)
    logger.info(f"Utils package initialized (version {UTILS_VERSION})")

def get_utils_info() -> dict:
    """Get information about available utilities."""
    return {
        "version": UTILS_VERSION,
        "available_functions": __all__,
        "patterns": PATTERNS,
        "defaults": DEFAULTS,
    }