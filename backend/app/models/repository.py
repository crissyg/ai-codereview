"""
Repository Data Models

Pydantic models for GitHub repository management, pull request data,
and repository configuration. Handles validation and serialization
for all repository-related operations.
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class RepositoryStatus(str, Enum):
    """Repository analysis status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"

class PullRequestState(str, Enum):
    """Pull request states."""
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"

class WebhookEventType(str, Enum):
    """Supported webhook event types."""
    PULL_REQUEST = "pull_request"
    PUSH = "push"
    PULL_REQUEST_REVIEW = "pull_request_review"

class GitHubUser(BaseModel):
    """GitHub user information."""
    login: str = Field(..., description="GitHub username")
    id: int = Field(..., description="GitHub user ID")
    avatar_url: HttpUrl = Field(..., description="User avatar URL")
    html_url: HttpUrl = Field(..., description="User profile URL")
    
    class Config:
        schema_extra = {
            "example": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "html_url": "https://github.com/octocat"
            }
        }

class Repository(BaseModel):
    """GitHub repository information."""
    id: int = Field(..., description="GitHub repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name (owner/repo)")
    owner: GitHubUser = Field(..., description="Repository owner")
    description: Optional[str] = Field(None, description="Repository description")
    html_url: HttpUrl = Field(..., description="Repository URL")
    clone_url: HttpUrl = Field(..., description="Git clone URL")
    default_branch: str = Field(default="main", description="Default branch name")
    language: Optional[str] = Field(None, description="Primary language")
    private: bool = Field(..., description="Whether repository is private")
    
    @validator('full_name')
    def validate_full_name_format(cls, v):
        """Ensure full_name follows owner/repo format."""
        if '/' not in v or len(v.split('/')) != 2:
            raise ValueError('full_name must be in format "owner/repo"')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1296269,
                "name": "Hello-World",
                "full_name": "octocat/Hello-World",
                "owner": {"login": "octocat", "id": 1},
                "description": "This your first repo!",
                "html_url": "https://github.com/octocat/Hello-World",
                "clone_url": "https://github.com/octocat/Hello-World.git",
                "default_branch": "main",
                "language": "Python",
                "private": False
            }
        }

class RepositoryConfig(BaseModel):
    """Repository configuration for AI-CodeReview."""
    repository_id: int = Field(..., description="GitHub repository ID")
    full_name: str = Field(..., description="Repository full name")
    status: RepositoryStatus = Field(default=RepositoryStatus.ACTIVE)
    auto_analysis: bool = Field(default=True, description="Enable automatic PR analysis")
    webhook_url: Optional[str] = Field(None, description="Webhook endpoint URL")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret for validation")
    analysis_config: Dict[str, Any] = Field(default_factory=dict, description="Custom analysis settings")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "repository_id": 1296269,
                "full_name": "octocat/Hello-World",
                "status": "active",
                "auto_analysis": True,
                "webhook_url": "https://api.ai-codereview.com/webhook",
                "analysis_config": {
                    "skip_files": ["*.md", "*.txt"],
                    "quality_threshold": 70
                }
            }
        }

class PullRequestInfo(BaseModel):
    """Pull request information from GitHub."""
    number: int = Field(..., description="PR number")
    title: str = Field(..., description="PR title")
    body: Optional[str] = Field(None, description="PR description")
    state: PullRequestState = Field(..., description="PR state")
    author: GitHubUser = Field(..., description="PR author")
    head_branch: str = Field(..., description="Source branch")
    base_branch: str = Field(..., description="Target branch")
    head_sha: str = Field(..., description="Latest commit SHA")
    html_url: HttpUrl = Field(..., description="PR URL")
    created_at: datetime = Field(..., description="PR creation time")
    updated_at: datetime = Field(..., description="Last update time")
    mergeable: Optional[bool] = Field(None, description="Whether PR is mergeable")
    
    class Config:
        schema_extra = {
            "example": {
                "number": 1,
                "title": "Add new feature",
                "body": "This PR adds a new feature to the application",
                "state": "open",
                "author": {"login": "developer", "id": 123},
                "head_branch": "feature/new-feature",
                "base_branch": "main",
                "head_sha": "abc123def456",
                "html_url": "https://github.com/octocat/Hello-World/pull/1",
                "mergeable": True
            }
        }

class FileChange(BaseModel):
    """Information about a changed file in a PR."""
    filename: str = Field(..., description="File path")
    status: str = Field(..., description="Change status (added, modified, removed)")
    additions: int = Field(..., ge=0, description="Lines added")
    deletions: int = Field(..., ge=0, description="Lines deleted")
    changes: int = Field(..., ge=0, description="Total changes")
    patch: Optional[str] = Field(None, description="File diff patch")
    
    @validator('changes')
    def changes_equals_additions_plus_deletions(cls, v, values):
        """Ensure changes equals additions plus deletions."""
        if 'additions' in values and 'deletions' in values:
            expected = values['additions'] + values['deletions']
            if v != expected:
                raise ValueError(f'Changes ({v}) must equal additions + deletions ({expected})')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "filename": "src/main.py",
                "status": "modified",
                "additions": 10,
                "deletions": 5,
                "changes": 15,
                "patch": "@@ -1,3 +1,4 @@\n def hello():\n+    print('Hello')\n     pass"
            }
        }

class PullRequestAnalysis(BaseModel):
    """Analysis results for a pull request."""
    pr_number: int = Field(..., description="PR number")
    repository: str = Field(..., description="Repository full name")
    total_files: int = Field(..., ge=0, description="Number of files analyzed")
    files_with_issues: int = Field(..., ge=0, description="Files containing issues")
    total_issues: int = Field(..., ge=0, description="Total issues found")
    average_quality_score: float = Field(..., ge=0.0, le=100.0, description="Average quality score")
    security_risk_level: str = Field(..., description="Overall security risk")
    recommendation: str = Field(..., description="Analysis recommendation")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('files_with_issues')
    def files_with_issues_not_exceed_total(cls, v, values):
        """Ensure files with issues doesn't exceed total files."""
        if 'total_files' in values and v > values['total_files']:
            raise ValueError('Files with issues cannot exceed total files')
        return v

class WebhookPayload(BaseModel):
    """GitHub webhook payload structure."""
    action: str = Field(..., description="Webhook action")
    repository: Repository = Field(..., description="Repository information")
    sender: GitHubUser = Field(..., description="Event sender")
    pull_request: Optional[PullRequestInfo] = Field(None, description="PR info for PR events")
    
    class Config:
        schema_extra = {
            "example": {
                "action": "opened",
                "repository": {"id": 1296269, "name": "Hello-World"},
                "sender": {"login": "octocat", "id": 1},
                "pull_request": {"number": 1, "title": "Add feature"}
            }
        }

class RepositoryStats(BaseModel):
    """Repository analysis statistics."""
    repository: str = Field(..., description="Repository full name")
    total_prs_analyzed: int = Field(..., ge=0, description="Total PRs analyzed")
    total_files_analyzed: int = Field(..., ge=0, description="Total files analyzed")
    total_issues_found: int = Field(..., ge=0, description="Total issues found")
    average_quality_score: float = Field(..., ge=0.0, le=100.0, description="Average quality score")
    last_analysis: Optional[datetime] = Field(None, description="Last analysis timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "repository": "octocat/Hello-World",
                "total_prs_analyzed": 25,
                "total_files_analyzed": 150,
                "total_issues_found": 12,
                "average_quality_score": 82.5,
                "last_analysis": "2025-06-01T20:20:00Z"
            }
        }

# Request/Response models for API endpoints
class AddRepositoryRequest(BaseModel):
    """Request to add a repository for analysis."""
    repository_url: HttpUrl = Field(..., description="GitHub repository URL")
    auto_analysis: bool = Field(default=True, description="Enable automatic analysis")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret")
    
    @validator('repository_url')
    def validate_github_url(cls, v):
        """Ensure URL is a valid GitHub repository URL."""
        url_str = str(v)
        if not url_str.startswith('https://github.com/'):
            raise ValueError('Must be a valid GitHub repository URL')
        return v

class RepositoryListResponse(BaseModel):
    """Response for listing repositories."""
    repositories: List[RepositoryConfig] = Field(..., description="List of configured repositories")
    total_count: int = Field(..., ge=0, description="Total number of repositories")
    
    class Config:
        schema_extra = {
            "example": {
                "repositories": [{"repository_id": 1296269, "full_name": "octocat/Hello-World"}],
                "total_count": 1
            }
        }

# Utility functions for repository operations
def extract_owner_repo(full_name: str) -> tuple[str, str]:
    """Extract owner and repository name from full_name."""
    if '/' not in full_name:
        raise ValueError("Invalid repository format. Expected 'owner/repo'")
    
    parts = full_name.split('/')
    if len(parts) != 2:
        raise ValueError("Invalid repository format. Expected 'owner/repo'")
    
    return parts[0], parts[1]

def is_analyzable_file(filename: str) -> bool:
    """Check if a file should be analyzed based on its extension."""
    analyzable_extensions = {
        '.py', '.js', '.ts', '.java', '.cpp', '.cc', '.cxx', '.c', '.h',
        '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.cs'
    }
    
    # Get file extension
    if '.' not in filename:
        return False
    
    extension = '.' + filename.split('.')[-1].lower()
    return extension in analyzable_extensions