"""
Configuration Management

This file manages all the settings and configuration for the application.
Think of it as the "control panel" where we set up how the system should behave.
"""

from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings and configuration.
    
    This class automatically loads settings from environment variables,
    making it easy to configure the application for different environments
    (development, testing, production).
    """
    
    # GitHub Integration Settings
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_webhook_secret: Optional[str] = os.getenv("GITHUB_WEBHOOK_SECRET")
    
    # Database Settings (for future use)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///ai_codereview.db")
    
    # AI Model Settings
    model_cache_dir: str = os.getenv("MODEL_CACHE_DIR", "./cache")
    max_analysis_time: int = int(os.getenv("MAX_ANALYSIS_TIME", "300"))  # 5 minutes
    
    # API Settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug_mode: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Performance Settings
    max_concurrent_analyses: int = int(os.getenv("MAX_CONCURRENT_ANALYSES", "5"))
    analysis_timeout: int = int(os.getenv("ANALYSIS_TIMEOUT", "60"))  # seconds
    
    class Config:
        """Configuration for the Settings class itself."""
        env_file = ".env"  # Load settings from .env file if it exists
        case_sensitive = False