"""
Data Models Package

Pydantic models for request/response validation, data serialization,
and type safety across the AI-CodeReview application.

Models:
- Analysis: Code analysis requests, results, and metrics
- Repository: GitHub repository data and configuration
- User: Authentication and user management (future)
"""

from .analysis import (
    AnalysisRequest,
    AnalysisResult, 
    AnalysisResponse,
    AnalysisHistory,
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    SecurityIssue,
    ComplexityMetrics,
    AnalysisLanguage,
    SecuritySeverity,
    ComplexityRating,
    create_analysis_summary
)

from .repository import (
    Repository,
    RepositoryConfig,
    PullRequestInfo,
    FileChange,
    PullRequestAnalysis,
    WebhookPayload,
    RepositoryStats,
    AddRepositoryRequest,
    RepositoryListResponse,
    GitHubUser,
    RepositoryStatus,
    PullRequestState,
    WebhookEventType,
    extract_owner_repo,
    is_analyzable_file
)

# Export all models for easy importing
__all__ = [
    # Analysis models
    "AnalysisRequest",
    "AnalysisResult",
    "AnalysisResponse", 
    "AnalysisHistory",
    "BulkAnalysisRequest",
    "BulkAnalysisResponse",
    "SecurityIssue",
    "ComplexityMetrics",
    "AnalysisLanguage",
    "SecuritySeverity", 
    "ComplexityRating",
    "create_analysis_summary",
    
    # Repository models
    "Repository",
    "RepositoryConfig",
    "PullRequestInfo",
    "FileChange",
    "PullRequestAnalysis",
    "WebhookPayload",
    "RepositoryStats",
    "AddRepositoryRequest",
    "RepositoryListResponse",
    "GitHubUser",
    "RepositoryStatus",
    "PullRequestState",
    "WebhookEventType",
    "extract_owner_repo",
    "is_analyzable_file",
]

# Model validation configuration
VALIDATION_CONFIG = {
    "max_code_length": 100000,  # 100KB max code size
    "max_file_count": 50,       # Max files per bulk analysis
    "supported_languages": [lang.value for lang in AnalysisLanguage],
    "quality_score_range": (0.0, 100.0),
    "confidence_range": (0.0, 1.0),
}

def get_model_info() -> dict:
    """Get information about available models and validation rules."""
    return {
        "available_models": __all__,
        "validation_config": VALIDATION_CONFIG,
        "supported_languages": VALIDATION_CONFIG["supported_languages"],
    }