"""
API Package - REST API Endpoints and Routing

This package contains all the REST API endpoints for the AI-CodeReview system.
It handles HTTP requests, validates input data, and coordinates with the service
layer to process code analysis requests and return results.

The API follows RESTful conventions and uses FastAPI for automatic documentation,
request validation, and response serialization.
"""

from .routes import router

# Export the main router for use in the main application
__all__ = ["router"]

# API version information
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# API metadata for documentation
API_METADATA = {
    "title": "AI-CodeReview API",
    "description": "AI-powered code review and security analysis system",
    "version": "1.0.0",
    "contact": {
        "name": "AI-CodeReview Support",
        "email": "support@ai-codereview.com",
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# API tags for endpoint organization in documentation
API_TAGS = [
    {
        "name": "analysis",
        "description": "Code analysis endpoints - submit code for AI review and get results",
    },
    {
        "name": "webhooks", 
        "description": "GitHub webhook endpoints - receive notifications about pull requests",
    },
    {
        "name": "repositories",
        "description": "Repository management - configure GitHub repositories for analysis",
    },
    {
        "name": "health",
        "description": "System health and monitoring endpoints",
    },
    {
        "name": "stats",
        "description": "Analytics and statistics endpoints",
    },
]