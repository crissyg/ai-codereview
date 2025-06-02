"""
Helper Utilities

Common utility functions used across the application including
validation, formatting, retry logic, and general-purpose helpers.
"""

import re
import hashlib
import uuid
import asyncio
import time
from typing import Any, Callable, Optional, Union, Dict, List
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
import aiohttp
import logging

logger = logging.getLogger(__name__)

def generate_request_id() -> str:
    """
    Generate a unique request ID for tracking.
    
    Returns:
        8-character unique identifier
    """
    return str(uuid.uuid4())[:8]

def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid GitHub repo URL, False otherwise
    """
    pattern = r"^https://github\.com/[\w\-\.]+/[\w\-\.]+/?$"
    return bool(re.match(pattern, url))

def extract_repo_info(github_url: str) -> Optional[Dict[str, str]]:
    """
    Extract owner and repository name from GitHub URL.
    
    Args:
        github_url: GitHub repository URL
        
    Returns:
        Dictionary with 'owner' and 'repo' keys, or None if invalid
    """
    if not validate_github_url(github_url):
        return None
    
    # Remove trailing slash and split
    clean_url = github_url.rstrip('/')
    parts = clean_url.split('/')
    
    if len(parts) >= 2:
        return {
            "owner": parts[-2],
            "repo": parts[-1]
        }
    
    return None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        sanitized = name[:max_name_length] + ('.' + ext if ext else '')
    
    return sanitized

def calculate_file_hash(content: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Calculate hash of file content.
    
    Args:
        content: File content as string or bytes
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hexadecimal hash string
    """
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    hash_func = getattr(hashlib, algorithm.lower())
    return hash_func(content).hexdigest()

def format_datetime(dt: datetime, format_type: str = "iso") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object to format
        format_type: Format type ('iso', 'human', 'compact')
        
    Returns:
        Formatted datetime string
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "human":
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    elif format_type == "compact":
        return dt.strftime("%Y%m%d_%H%M%S")
    else:
        return dt.isoformat()

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_size_string(size_str: str) -> int:
    """
    Parse size string (e.g., "10MB", "1GB") to bytes.
    
    Args:
        size_str: Size string with unit
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    # Extract number and unit
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$", size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number, unit = match.groups()
    number = float(number)
    
    # Size multipliers
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "": 1,  # No unit defaults to bytes
    }
    
    return int(number * multipliers.get(unit, 1))

def format_size(size_bytes: int) -> str:
    """
    Format byte size to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries")
                        raise
                    
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def async_retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Async function {func.__name__} failed after {max_retries} retries")
                        raise
                    
                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(f"Async function {func.__name__} failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    try:
        import json
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten nested dictionary with dot notation.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)

def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Filename to extract extension from
        
    Returns:
        File extension without dot, or empty string if none
    """
    return Path(filename).suffix.lstrip('.')

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

async def async_timeout(coro, timeout_seconds: float):
    """
    Run coroutine with timeout.
    
    Args:
        coro: Coroutine to run
        timeout_seconds: Timeout in seconds
        
    Returns:
        Coroutine result
        
    Raises:
        asyncio.TimeoutError: If timeout exceeded
    """
    return await asyncio.wait_for(coro, timeout=timeout_seconds)

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def get_env_bool(env_var: str, default: bool = False) -> bool:
    """
    Get boolean value from environment variable.
    
    Args:
        env_var: Environment variable name
        default: Default value if not set
        
    Returns:
        Boolean value
    """
    import os
    value = os.getenv(env_var, '').lower()
    return value in ('true', '1', 'yes', 'on')