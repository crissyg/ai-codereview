"""
Analysis Data Models

Pydantic models for code analysis requests, responses, and internal data structures.
These models handle validation, serialization, and type safety for all analysis operations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class AnalysisLanguage(str, Enum):
    """Supported programming languages for analysis."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    PHP = "php"
    RUBY = "ruby"

class SecuritySeverity(str, Enum):
    """Security issue severity levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ComplexityRating(str, Enum):
    """Code complexity ratings."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class SecurityIssue(BaseModel):
    """Individual security vulnerability found in code."""
    type: str = Field(..., description="Type of security issue")
    severity: SecuritySeverity = Field(..., description="Issue severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence score")
    description: str = Field(..., description="Human-readable issue description")
    line_number: Optional[int] = Field(None, description="Line number where issue occurs")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "SQL injection vulnerabilities",
                "severity": "HIGH",
                "confidence": 0.85,
                "description": "Potential SQL injection detected in query construction",
                "line_number": 42
            }
        }

class ComplexityMetrics(BaseModel):
    """Code complexity analysis metrics."""
    total_lines: int = Field(..., ge=0, description="Total lines in file")
    code_lines: int = Field(..., ge=0, description="Lines containing code")
    comment_lines: int = Field(..., ge=0, description="Lines containing comments")
    function_count: int = Field(..., ge=0, description="Number of functions")
    class_count: int = Field(..., ge=0, description="Number of classes")
    complexity_rating: ComplexityRating = Field(..., description="Overall complexity rating")
    
    @validator('code_lines')
    def code_lines_not_exceed_total(cls, v, values):
        """Ensure code lines don't exceed total lines."""
        if 'total_lines' in values and v > values['total_lines']:
            raise ValueError('Code lines cannot exceed total lines')
        return v

class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    code_content: str = Field(..., min_length=1, description="Source code to analyze")
    file_path: Optional[str] = Field(None, description="File path for context")
    language: AnalysisLanguage = Field(AnalysisLanguage.PYTHON, description="Programming language")
    
    @validator('code_content')
    def code_content_not_empty(cls, v):
        """Ensure code content is not just whitespace."""
        if not v.strip():
            raise ValueError('Code content cannot be empty or whitespace only')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code_content": "def hello_world():\n    print('Hello, World!')",
                "file_path": "example.py",
                "language": "python"
            }
        }

class AnalysisResult(BaseModel):
    """Complete analysis results for a piece of code."""
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Code quality score (0-100)")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    documentation: str = Field(..., description="AI-generated documentation")
    complexity_analysis: ComplexityMetrics = Field(..., description="Complexity metrics")
    overall_rating: str = Field(..., description="Overall letter grade (A-F)")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "security_issues": [],
                "quality_score": 85.5,
                "suggestions": ["Consider adding type hints", "Add error handling"],
                "documentation": "This function prints a greeting message",
                "complexity_analysis": {
                    "total_lines": 10,
                    "code_lines": 8,
                    "comment_lines": 1,
                    "function_count": 1,
                    "class_count": 0,
                    "complexity_rating": "LOW"
                },
                "overall_rating": "B - Good"
            }
        }

class AnalysisResponse(BaseModel):
    """API response model for analysis requests."""
    status: str = Field(..., description="Response status")
    file_path: Optional[str] = Field(None, description="Analyzed file path")
    analysis: AnalysisResult = Field(..., description="Analysis results")
    summary: Dict[str, Any] = Field(..., description="Analysis summary")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "file_path": "example.py",
                "analysis": "...",  # AnalysisResult example
                "summary": {
                    "total_issues": 0,
                    "security_risk_level": "LOW",
                    "recommendation": "Code looks good! Ready for merge."
                }
            }
        }

class AnalysisHistory(BaseModel):
    """Historical analysis record for tracking and comparison."""
    id: str = Field(..., description="Unique analysis identifier")
    file_path: str = Field(..., description="Analyzed file path")
    repository: Optional[str] = Field(None, description="Repository name")
    branch: Optional[str] = Field(None, description="Git branch")
    commit_sha: Optional[str] = Field(None, description="Git commit hash")
    analysis_result: AnalysisResult = Field(..., description="Analysis results")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "analysis_123456",
                "file_path": "src/main.py",
                "repository": "user/repo",
                "branch": "feature/new-feature",
                "commit_sha": "abc123def456",
                "analysis_result": "...",  # AnalysisResult example
                "created_at": "2025-06-01T20:20:00Z"
            }
        }

class BulkAnalysisRequest(BaseModel):
    """Request model for analyzing multiple files."""
    files: List[AnalysisRequest] = Field(..., min_items=1, max_items=50)
    repository_context: Optional[str] = Field(None, description="Repository context")
    
    @validator('files')
    def validate_file_count(cls, v):
        """Ensure reasonable number of files for bulk analysis."""
        if len(v) > 50:
            raise ValueError('Cannot analyze more than 50 files at once')
        return v

class BulkAnalysisResponse(BaseModel):
    """Response model for bulk analysis requests."""
    status: str = Field(..., description="Overall analysis status")
    total_files: int = Field(..., description="Number of files analyzed")
    results: List[AnalysisResponse] = Field(..., description="Individual file results")
    summary: Dict[str, Any] = Field(..., description="Aggregate summary")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "completed",
                "total_files": 3,
                "results": ["..."],  # List of AnalysisResponse
                "summary": {
                    "total_issues": 5,
                    "average_quality_score": 78.5,
                    "files_with_issues": 2,
                    "overall_recommendation": "Review flagged files before merge"
                }
            }
        }

# Utility functions for model operations
def create_analysis_summary(analysis_result: AnalysisResult) -> Dict[str, Any]:
    """Create summary statistics from analysis results."""
    return {
        "total_issues": len(analysis_result.security_issues),
        "security_risk_level": _calculate_risk_level(analysis_result.security_issues),
        "recommendation": _generate_recommendation(analysis_result),
        "quality_grade": analysis_result.overall_rating.split(' - ')[0],
        "has_high_severity_issues": any(
            issue.severity == SecuritySeverity.HIGH 
            for issue in analysis_result.security_issues
        )
    }

def _calculate_risk_level(security_issues: List[SecurityIssue]) -> str:
    """Calculate overall security risk level."""
    if not security_issues:
        return "LOW"
    
    high_severity_count = sum(1 for issue in security_issues if issue.severity == SecuritySeverity.HIGH)
    
    if high_severity_count > 0:
        return "HIGH"
    elif len(security_issues) > 3:
        return "MEDIUM"
    else:
        return "LOW"

def _generate_recommendation(analysis_result: AnalysisResult) -> str:
    """Generate human-readable recommendation based on analysis."""
    if analysis_result.quality_score >= 90:
        return "Excellent code quality! Ready for merge."
    elif analysis_result.quality_score >= 80:
        return "Good code quality with minor suggestions."
    elif analysis_result.quality_score >= 70:
        return "Code quality is acceptable but could benefit from improvements."
    else:
        return "Code quality needs significant improvement before merge."