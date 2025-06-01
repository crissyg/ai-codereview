"""
AI-CodeReview Backend Application Package

This is the main application package for the AI-CodeReview backend system.
It provides AI-powered code analysis, GitHub integration, and automated
code review capabilities through a FastAPI web service.

The application coordinates multiple AI models to analyze code for:
- Security vulnerabilities
- Code quality metrics  
- Improvement suggestions
- Automatic documentation generation
- Complexity analysis

Main components:
- API layer: REST endpoints for code analysis and GitHub webhooks
- Services: Business logic for AI analysis and GitHub integration
- Models: Data structures and validation schemas
- Utils: Configuration, logging, and helper functions
"""

# Package metadata
__version__ = "1.0.1"
__title__ = "AI-CodeReview Backend"
__description__ = "AI-powered code review and security analysis system"
__author__ = "AI-CodeReview Developer"
__license__ = "MIT"

# Import key components for easy access
from .main import app
from .utils.config import Settings

# Make main application and settings available at package level
__all__ = [
    "app",
    "Settings",
    "__version__",
    "__title__", 
    "__description__",
]

# Application configuration
APP_NAME = "AI-CodeReview"
APP_VERSION = __version__
DEBUG_MODE = False  # Override in settings for development

# Supported programming languages for analysis
SUPPORTED_LANGUAGES = [
    "python",
    "javascript", 
    "typescript",
    "java",
    "cpp",
    "c",
    "go",
    "rust",
    "php",
    "ruby",
]

# AI model configuration
AI_MODELS_CONFIG = {
    "text_classification": "microsoft/codebert-base",
    "text_generation": "microsoft/DialoGPT-medium", 
    "question_answering": "deepset/roberta-base-squad2",
    "security_analysis": "huggingface/CodeBERTa-small-v1",
    "code_completion": "microsoft/codebert-base-mlm",
}

# API rate limiting defaults
DEFAULT_RATE_LIMITS = {
    "analysis_per_minute": 10,
    "webhook_per_minute": 100,
    "general_per_minute": 60,
}