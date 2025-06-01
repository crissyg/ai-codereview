"""
API Routes - The Public Interface of the System

These are the "doors" through which external systems ( GitHub webhooks
or the web dashboard) can interact with the AI code review system.

Each route handles a specific type of request and returns appropriate responses.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from ..services.code_analyzer import CodeAnalyzer
from ..services.github_integration import GitHubIntegration
from ..utils.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize the services
settings = Settings()
code_analyzer = CodeAnalyzer()
github_integration = GitHubIntegration(settings.github_token)

# ... (rest of the routes remain the same, but update these specific functions)

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint.
    
    For e.g.  asking "Are you alive?" - returns a simple response to confirm
    the system is running and ready to handle requests.
    """
    return {
        "status": "healthy",
        "service": "AI-CodeReview",
        "version": "1.0.0"
    }

def _format_analysis_comment(analysis_result, file_path: str) -> str:
    """Format analysis results into a nice comment for GitHub."""
    comment = f"## 🤖 AI-CodeReview Analysis for `{file_path}`\n\n"
    comment += f"**Overall Rating:** {analysis_result.overall_rating}\n"
    comment += f"**Quality Score:** {analysis_result.quality_score:.1f}/100\n\n"
    
    if analysis_result.security_issues:
        comment += "### 🔒 Security Issues Found:\n"
        for issue in analysis_result.security_issues:
            comment += f"- **{issue['severity']}**: {issue['description']}\n"
        comment += "\n"
    
    if analysis_result.suggestions:
        comment += "### 💡 Suggestions for Improvement:\n"
        for suggestion in analysis_result.suggestions[:3]:  # Limit to top 3
            comment += f"- {suggestion}\n"
        comment += "\n"
    
    comment += f"### 📖 AI-Generated Documentation:\n{analysis_result.documentation}\n\n"
    comment += "*This analysis was generated automatically by AI-CodeReview*"
    
    return comment

def _format_summary_comment(analysis_summary: List[Dict], total_issues: int) -> str:
    """Format a summary comment for the entire pull request."""
    comment = "## 🤖 AI-CodeReview - Pull Request Summary\n\n"
    comment += f"**Total Files Analyzed:** {len(analysis_summary)}\n"
    comment += f"**Total Issues Found:** {total_issues}\n\n"
    
    if analysis_summary:
        comment += "### 📊 File Analysis Results:\n"
        for file_summary in analysis_summary:
            status_emoji = "✅" if file_summary["issues_found"] == 0 else "⚠️"
            comment += f"{status_emoji} `{file_summary['file']}` - "
            comment += f"Quality: {file_summary['quality_score']:.1f}/100, "
            comment += f"Issues: {file_summary['issues_found']}, "
            comment += f"Rating: {file_summary['rating']}\n"
    
    comment += "\n*Powered by AI-CodeReview - Automated Code Review System*"
    return comment