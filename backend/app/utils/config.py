import os
"""
Configuration Management

Centralized configuration using Pydantic settings with environment variable support.
Handles all application settings including API keys, database connections,
and feature flags with validation and type safety.
"""

from functools import lru_cache
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field, validator, SecretStr
from enum import Enum

class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    Sensitive values use SecretStr for security.
    """
    
    # Application settings
    app_name: str = Field(default="AI-CodeReview", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Runtime environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API port")
    api_workers: int = Field(default=1, ge=1, description="Number of API workers")
    api_reload: bool = Field(default=False, description="Enable auto-reload in development")
    
    # GitHub integration
    github_token: SecretStr = Field(..., description="GitHub personal access token")
    github_webhook_secret: Optional[SecretStr] = Field(None, description="GitHub webhook secret")
    github_api_timeout: int = Field(default=30, ge=1, description="GitHub API timeout in seconds")
    github_max_retries: int = Field(default=3, ge=0, description="Max GitHub API retries")
    
    # Database settings
    database_url: str = Field(default="sqlite:///ai_codereview.db", description="Database connection URL")
    database_pool_size: int = Field(default=10, ge=1, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, ge=0, description="Database pool overflow")
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # AI model settings
    model_cache_dir: str = Field(default="./cache", description="AI model cache directory")
    model_download_timeout: int = Field(default=300, ge=30, description="Model download timeout")
    max_analysis_time: int = Field(default=300, ge=30, description="Max analysis time per file")
    max_concurrent_analyses: int = Field(default=5, ge=1, description="Max concurrent analyses")
    
    # Security settings
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    rate_limit_requests: int = Field(default=100, ge=1, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, ge=1, description="Rate limit window in seconds")
    
    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    log_rotation: bool = Field(default=True, description="Enable log rotation")
    log_max_size: str = Field(default="10MB", description="Max log file size")
    log_backup_count: int = Field(default=5, ge=0, description="Number of log backups")
    
    # Analysis settings
    supported_languages: List[str] = Field(
        default=["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "php", "ruby"],
        description="Supported programming languages"
    )
    max_file_size: int = Field(default=1024*1024, ge=1024, description="Max file size for analysis (bytes)")
    max_files_per_pr: int = Field(default=50, ge=1, description="Max files per PR analysis")
    quality_threshold: float = Field(default=70.0, ge=0.0, le=100.0, description="Quality score threshold")
    
    # Feature flags
    enable_webhooks: bool = Field(default=True, description="Enable GitHub webhooks")
    enable_auto_analysis: bool = Field(default=True, description="Enable automatic PR analysis")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_caching: bool = Field(default=True, description="Enable response caching")
    
    # Performance settings
    request_timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    worker_timeout: int = Field(default=300, ge=30, description="Worker timeout in seconds")
    keepalive_timeout: int = Field(default=2, ge=1, description="Keep-alive timeout")
    
    @validator('github_token', pre=True)
    def validate_github_token(cls, v):
        """Validate GitHub token format."""
        if isinstance(v, str) and v:
            # GitHub tokens start with 'ghp_' for personal access tokens
            if not (v.startswith('ghp_') or v.startswith('github_pat_')):
                raise ValueError('Invalid GitHub token format')
        return v
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('sqlite://', 'postgresql://', 'mysql://')):
            raise ValueError('Unsupported database URL format')
        return v
    
    @validator('model_cache_dir')
    def validate_cache_dir(cls, v):
        """Ensure cache directory exists or can be created."""
        os.makedirs(v, exist_ok=True)
        return v
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v):
        """Validate CORS origins format."""
        for origin in v:
            if origin != "*" and not origin.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid CORS origin format: {origin}')
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "echo": self.database_echo,
        }
    
    def get_github_config(self) -> Dict[str, Any]:
        """Get GitHub configuration dictionary."""
        return {
            "token": self.github_token.get_secret_value() if self.github_token else None,
            "webhook_secret": self.github_webhook_secret.get_secret_value() if self.github_webhook_secret else None,
            "timeout": self.github_api_timeout,
            "max_retries": self.github_max_retries,
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI model configuration dictionary."""
        return {
            "cache_dir": self.model_cache_dir,
            "download_timeout": self.model_download_timeout,
            "max_analysis_time": self.max_analysis_time,
            "max_concurrent": self.max_concurrent_analyses,
            "supported_languages": self.supported_languages,
            "max_file_size": self.max_file_size,
            "quality_threshold": self.quality_threshold,
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration dictionary."""
        return {
            "cors_origins": self.cors_origins,
            "cors_allow_credentials": self.cors_allow_credentials,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window,
        }
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow environment variables to override settings
        env_prefix = ""

# Global settings instance with caching
@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Settings are cached to avoid re-reading environment variables
    on every access. Cache is cleared when process restarts.
    
    Returns:
        Configured Settings instance
    """
    return Settings()

def reload_settings() -> Settings:
    """
    Reload settings by clearing cache and creating new instance.
    
    Useful for testing or when environment variables change.
    
    Returns:
        Fresh Settings instance
    """
    get_settings.cache_clear()
    return get_settings()

def get_config_summary() -> Dict[str, Any]:
    """
    Get non-sensitive configuration summary for debugging.
    
    Returns configuration without secrets for logging/debugging.
    
    Returns:
        Configuration summary dictionary
    """
    settings = get_settings()
    
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "log_level": settings.log_level,
        "supported_languages": settings.supported_languages,
        "feature_flags": {
            "webhooks": settings.enable_webhooks,
            "auto_analysis": settings.enable_auto_analysis,
            "metrics": settings.enable_metrics,
            "caching": settings.enable_caching,
        },
        "github_configured": bool(settings.github_token),
        "webhook_secret_configured": bool(settings.github_webhook_secret),
    }

# Environment-specific configurations
DEVELOPMENT_OVERRIDES = {
    "debug": True,
    "api_reload": True,
    "log_level": LogLevel.DEBUG,
    "database_echo": True,
}

PRODUCTION_OVERRIDES = {
    "debug": False,
    "api_reload": False,
    "log_level": LogLevel.INFO,
    "database_echo": False,
    "cors_origins": [],  # Should be configured explicitly in production
}

TESTING_OVERRIDES = {
    "database_url": "sqlite:///:memory:",
    "log_level": LogLevel.WARNING,
    "enable_webhooks": False,
    "github_token": "test_token",
}

def apply_environment_overrides(settings: Settings) -> Settings:
    """
    Apply environment-specific configuration overrides.
    
    Args:
        settings: Base settings instance
        
    Returns:
        Settings with environment-specific overrides applied
    """
    overrides = {}
    
    if settings.environment == Environment.DEVELOPMENT:
        overrides = DEVELOPMENT_OVERRIDES
    elif settings.environment == Environment.PRODUCTION:
        overrides = PRODUCTION_OVERRIDES
    elif settings.environment == Environment.TESTING:
        overrides = TESTING_OVERRIDES
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    return settings