"""
AI-CodeReview - Main Application Entry Point

This is the heart of the AI-powered code review system. It sets up the web server
that receives code from GitHub and analyzes it using multiple AI models.

Think of this as the "front desk" of the AI system - it receives requests,
coordinates the analysis, and sends back results.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from .services.code_analyzer import CodeAnalyzer
from .services.github_integration import GitHubIntegration
from .api.routes import router
from .utils.config import Settings

# Configure logging to track what the system is doing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AICodeReviewApplication:
    """
    Main application class that orchestrates the AI code review system.
    
    This class is similar to the conductor of an orchestra - it coordinates all the
    different components (AI models, GitHub integration, database) to work together.
    """
    
    def __init__(self):
        """Initialize the application with all necessary components."""
        self.app = FastAPI(
            title="AI-CodeReview",
            description="AI-powered code review and security analysis system",
            version="1.0.0"
        )
        
        # Load configuration settings
        self.settings = Settings()
        
        # Initialize the AI analysis engine
        self.code_analyzer = CodeAnalyzer()
        
        # Initialize GitHub integration for fetching code
        self.github_integration = GitHubIntegration(self.settings.github_token)
        
        # Set up the web application
        self._setup_middleware()
        self._setup_routes()
        
        logger.info("AI-CodeReview application initialized successfully")
    
    def _setup_middleware(self):
        """
        Configure middleware for handling web requests.
        
        Middleware is similar to security guards and translators at the entrance -
        they handle authentication, enable cross-origin requests, etc.
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify exact domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Connect URL endpoints to the application logic."""
        self.app.include_router(router, prefix="/api/v1")
        
        @self.app.get("/health")
        async def health_check():
            """Simple endpoint to check if the system is running."""
            return {"status": "healthy", "service": "AI-CodeReview"}

# Create the application instance
app_instance = AICodeReviewApplication()
app = app_instance.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)