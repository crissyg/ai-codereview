"""
Services Package - Business Logic and External Integrations

Core business logic and external service integrations for AI-CodeReview.
Services handle code analysis, GitHub integration, and webhook processing.

Main Services:
- CodeAnalyzer: AI-powered code analysis using multiple models
- GitHubIntegration: GitHub API interactions and data fetching
- WebhookHandler: GitHub webhook event processing
"""

from .code_analyzer import CodeAnalyzer, AIModelManager, CodeAnalysisResult
from .github_integration import GitHubIntegration, PullRequestInfo
from .webhook_handler import WebhookHandler, WebhookProcessor, WebhookEvent, WebhookEventType

# Export main service classes
__all__ = [
    # Core analysis services
    "CodeAnalyzer",
    "AIModelManager", 
    "CodeAnalysisResult",
    
    # GitHub integration services
    "GitHubIntegration",
    "PullRequestInfo",
    
    # Webhook processing services
    "WebhookHandler",
    "WebhookProcessor", 
    "WebhookEvent",
    "WebhookEventType",
]

# Service configuration
SERVICES_VERSION = "1.0.0"

# AI model configuration
AI_MODELS_CONFIG = {
    "text_classification": {
        "model": "microsoft/codebert-base",
        "description": "Categorizes code issues and quality metrics",
        "max_length": 512,
    },
    "text_generation": {
        "model": "microsoft/DialoGPT-medium",
        "description": "Generates code documentation", 
        "max_length": 150,
    },
    "question_answering": {
        "model": "deepset/roberta-base-squad2",
        "description": "Answers questions about code",
        "max_length": 384,
    },
    "security_analysis": {
        "model": "huggingface/CodeBERTa-small-v1", 
        "description": "Detects security vulnerabilities",
        "max_length": 512,
    },
    "code_completion": {
        "model": "microsoft/codebert-base-mlm",
        "description": "Suggests code improvements",
        "max_length": 512,
    },
}

# GitHub API configuration
GITHUB_CONFIG = {
    "api_version": "v3",
    "base_url": "https://api.github.com",
    "timeout": 30,
    "max_retries": 3,
    "rate_limit_buffer": 100,
}

# Webhook processing configuration
WEBHOOK_CONFIG = {
    "supported_events": ["pull_request", "push", "pull_request_review", "check_run"],
    "analysis_timeout": 300,  # 5 minutes max
    "max_files_per_pr": 50,
    "max_file_size": 1024 * 1024,  # 1MB
}

# Analysis quality thresholds
ANALYSIS_THRESHOLDS = {
    "quality_score": {
        "excellent": 90,
        "good": 80, 
        "average": 70,
        "needs_improvement": 60,
    },
    "security_severity": {
        "high_confidence": 0.9,
        "medium_confidence": 0.7,
        "low_confidence": 0.5,
    },
    "complexity": {
        "high_lines": 200,
        "medium_lines": 100,
        "max_functions": 20,
    },
}

def get_service_info() -> dict:
    """Get service information and configuration for debugging/monitoring."""
    return {
        "version": SERVICES_VERSION,
        "available_services": list(__all__),
        "ai_models": AI_MODELS_CONFIG,
        "github_config": GITHUB_CONFIG,
        "webhook_config": WEBHOOK_CONFIG,
        "analysis_thresholds": ANALYSIS_THRESHOLDS,
    }

def validate_service_dependencies() -> bool:
    """Check if all required dependencies are available."""
    try:
        import transformers
        from transformers import pipeline
        
        # Basic validation - create test pipeline
        test_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        return True
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"Dependency validation failed: {e}")
        return False

class ServiceManager:
    """Manages service lifecycle and dependencies with lazy loading."""
    
    def __init__(self, settings):
        self.settings = settings
        self._services = {}
        
    def get_code_analyzer(self) -> CodeAnalyzer:
        """Get or create CodeAnalyzer instance (lazy loaded)."""
        if "code_analyzer" not in self._services:
            self._services["code_analyzer"] = CodeAnalyzer()
        return self._services["code_analyzer"]
    
    def get_github_client(self) -> GitHubIntegration:
        """Get or create GitHubIntegration instance."""
        if "github_client" not in self._services:
            self._services["github_client"] = GitHubIntegration(self.settings.github_token)
        return self._services["github_client"]
    
    def get_webhook_handler(self) -> WebhookHandler:
        """Get or create WebhookHandler instance."""
        if "webhook_handler" not in self._services:
            self._services["webhook_handler"] = WebhookHandler(self.settings)
        return self._services["webhook_handler"]
    
    def health_check(self) -> dict:
        """Perform health checks on all services."""
        health_status = {
            "dependencies": validate_service_dependencies(),
            "services": {},
        }
        
        # Check each initialized service
        for service_name, service_instance in self._services.items():
            try:
                if hasattr(service_instance, '__class__'):
                    health_status["services"][service_name] = "healthy"
                else:
                    health_status["services"][service_name] = "unknown"
            except Exception as e:
                health_status["services"][service_name] = f"error: {str(e)}"
        
        return health_status