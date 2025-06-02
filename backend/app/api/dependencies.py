"""
API Dependencies

This module contains shared dependencies that get injected into API routes.
Dependencies handle common functionality like database connections, authentication,
rate limiting, and request validation.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Generator
import time
import logging
from functools import wraps

from ..database.connection import get_db_session
from ..utils.config import Settings
from ..services.github_integration import GitHubIntegration

logger = logging.getLogger(__name__)

# Security scheme for API authentication (when I add it later)
security = HTTPBearer(auto_error=False)

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """
    Get application settings.
    
    This is a dependency that provides access to configuration settings
    throughout the application. FastAPI will cache this automatically.
    """
    return settings

def get_database() -> Generator[Session, None, None]:
    """
    Database session dependency.
    
    Provides a database session to API endpoints. The session gets
    automatically closed after the request completes, even if an
    exception occurs. 
    """
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

def get_github_client(settings: Settings = Depends(get_settings)) -> GitHubIntegration:
    """
    GitHub API client dependency.
    
    Creates a GitHub integration client with the configured token.
    This gets reused across endpoints that need to interact with GitHub.
    """
    return GitHubIntegration(settings.github_token)

async def verify_github_webhook(
    request: Request,
    settings: Settings = Depends(get_settings)
) -> bool:
    """
    Verify GitHub webhook signature for security.
    
    This validates that webhook requests actually come from GitHub
    by checking the signature against our webhook secret. It's important
    for security since webhooks can trigger code analysis.
    """
    if not settings.github_webhook_secret:
        logger.warning("No GitHub webhook secret configured - skipping verification")
        return True
    
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        logger.error("Missing GitHub webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    # Get the raw request body for signature verification
    body = await request.body()
    
    # Use the GitHub integration to verify the signature
    github_client = GitHubIntegration("")  # Empty token for signature verification
    is_valid = github_client.validate_webhook_signature(
        body, signature, settings.github_webhook_secret
    )
    
    if not is_valid:
        logger.error("Invalid GitHub webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    return True

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Rate limiting decorator for API endpoints.
    
    This is a simple in-memory rate limiter. 
    
    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
    """
    # Simple in-memory storage for request counts
    # In production, this should use Redis or similar
    request_counts = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean up old entries (simple cleanup)
            cutoff_time = current_time - window_seconds
            request_counts[client_ip] = [
                timestamp for timestamp in request_counts.get(client_ip, [])
                if timestamp > cutoff_time
            ]
            
            # Check if rate limit exceeded
            if len(request_counts.get(client_ip, [])) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            # Add current request timestamp
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            request_counts[client_ip].append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Get current authenticated user (placeholder for future auth).
    
    Right now this just returns None since I haven't implemented
    authentication yet. When I do add user auth, this will validate
    JWT tokens and return user information.
    """
    if not credentials:
        return None
    
    # TODO: Implement actual JWT token validation
    # For now, just return None (no authentication)
    logger.debug("Authentication not implemented yet")
    return None

def require_auth(
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    Require authentication for protected endpoints.
    
    This dependency will raise an HTTP 401 error if the user
    isn't authenticated. 
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def validate_file_type(file_path: str) -> bool:
    """
    Validate that a file type is supported for analysis.
    
    Checks the file extension against our list of supported
    programming languages. This prevents people from trying
    to analyze binary files or unsupported formats.
    """
    if not file_path:
        return True  # Allow empty file paths
    
    # Get file extension
    extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
    
    # Map extensions to supported languages
    supported_extensions = {
        'py': 'python',
        'js': 'javascript', 
        'ts': 'typescript',
        'java': 'java',
        'cpp': 'cpp',
        'cc': 'cpp',
        'cxx': 'cpp',
        'c': 'c',
        'h': 'c',
        'go': 'go',
        'rs': 'rust',
        'php': 'php',
        'rb': 'ruby',
    }
    
    return extension in supported_extensions

def get_request_id(request: Request) -> str:
    """
    Generate or extract a request ID for tracking.
    
    This helps with debugging and logging by giving each request
    a unique identifier. The frontend can send an ID, or we'll
    generate one automatically.
    """
    # Check if request ID was provided in headers
    request_id = request.headers.get("X-Request-ID")
    
    if not request_id:
        # Generate a simple request ID based on timestamp
        import uuid
        request_id = str(uuid.uuid4())[:8]
    
    return request_id

async def log_request_info(
    request: Request,
    request_id: str = Depends(get_request_id)
) -> dict:
    """
    Log request information for debugging and monitoring.
    
    This captures useful information about incoming requests
    that helps with debugging issues and monitoring system usage.
    """
    request_info = {
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("User-Agent", ""),
        "timestamp": time.time(),
    }
    
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    return request_info

# Common dependency combinations for convenience
CommonDeps = {
    "db": Depends(get_database),
    "settings": Depends(get_settings),
    "github": Depends(get_github_client),
    "request_info": Depends(log_request_info),
}

# Rate limiting presets for different endpoint types
RateLimits = {
    "analysis": rate_limit(max_requests=10, window_seconds=60),    # Analysis endpoints
    "webhook": rate_limit(max_requests=100, window_seconds=60),   # GitHub webhooks
    "general": rate_limit(max_requests=60, window_seconds=60),    # General API endpoints
}