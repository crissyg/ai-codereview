"""
Database Schemas

SQLAlchemy ORM models for all database tables.
Defines the structure and relationships for persistent data storage.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, 
    ForeignKey, JSON, Float, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

from .connection import Base

class TimestampMixin:
    """Mixin for automatic timestamp columns."""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class AnalysisRecord(Base, TimestampMixin):
    """
    Stores code analysis results and metadata.
    
    Tracks all analysis performed on files, including results,
    repository context, and timing information.
    """
    __tablename__ = 'analysis_records'
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(50), unique=True, nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=True)
    branch = Column(String(100), nullable=True)
    commit_sha = Column(String(40), nullable=True, index=True)
    
    # Analysis results stored as JSON
    analysis_result = Column(JSON, nullable=False)
    quality_score = Column(Float, nullable=True, index=True)
    security_issues_count = Column(Integer, default=0)
    overall_rating = Column(String(20), nullable=True)
    
    # Analysis metadata
    language = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)
    analysis_duration = Column(Float, nullable=True)  # seconds
    
    # Relationships
    repository = relationship("RepositoryRecord", back_populates="analyses")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_analysis_repo_created', 'repository_id', 'created_at'),
        Index('idx_analysis_quality_created', 'quality_score', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AnalysisRecord(id={self.id}, file='{self.file_path}', quality={self.quality_score})>"

class RepositoryRecord(Base, TimestampMixin):
    """
    Stores GitHub repository configuration and metadata.
    
    Tracks repositories configured for analysis including
    webhook settings and analysis preferences.
    """
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    full_name = Column(String(255), unique=True, nullable=False, index=True)
    owner = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    
    # Repository metadata
    description = Column(Text, nullable=True)
    html_url = Column(String(500), nullable=True)
    clone_url = Column(String(500), nullable=True)
    default_branch = Column(String(100), default='main')
    primary_language = Column(String(50), nullable=True)
    is_private = Column(Boolean, default=False)
    
    # Configuration
    status = Column(String(20), default='active', index=True)  # active, inactive, error
    auto_analysis = Column(Boolean, default=True)
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    analysis_config = Column(JSON, nullable=True)
    
    # Statistics
    total_analyses = Column(Integer, default=0)
    last_analysis_at = Column(DateTime, nullable=True)
    
    # Relationships
    analyses = relationship("AnalysisRecord", back_populates="repository", cascade="all, delete-orphan")
    webhook_events = relationship("WebhookEventRecord", back_populates="repository", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RepositoryRecord(id={self.id}, name='{self.full_name}', status='{self.status}')>"
    
    def update_analysis_stats(self):
        """Update analysis statistics for this repository."""
        self.total_analyses = len(self.analyses)
        if self.analyses:
            self.last_analysis_at = max(analysis.created_at for analysis in self.analyses)

class UserRecord(Base, TimestampMixin):
    """
    User accounts for authentication and authorization.
    
    Stores user credentials and preferences for the system.
    Currently placeholder for future authentication features.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User status and permissions
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # User preferences
    preferences = Column(JSON, nullable=True)
    
    # GitHub integration
    github_username = Column(String(100), nullable=True, index=True)
    github_token = Column(String(255), nullable=True)  # Encrypted in production
    
    def __repr__(self):
        return f"<UserRecord(id={self.id}, username='{self.username}', active={self.is_active})>"

class WebhookEventRecord(Base, TimestampMixin):
    """
    Stores GitHub webhook events for auditing and replay.
    
    Tracks all webhook events received from GitHub including
    payload and processing status.
    """
    __tablename__ = 'webhook_events'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    
    # Event source
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=True)
    sender = Column(String(100), nullable=True)
    
    # Event data
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    
    # Processing status
    status = Column(String(20), default='received', index=True)  # received, processing, completed, failed
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Analysis results (if applicable)
    analysis_triggered = Column(Boolean, default=False)
    analysis_id = Column(String(50), nullable=True)
    
    # Relationships
    repository = relationship("RepositoryRecord", back_populates="webhook_events")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_webhook_type_created', 'event_type', 'created_at'),
        Index('idx_webhook_status_created', 'status', 'created_at'),
        Index('idx_webhook_repo_created', 'repository_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<WebhookEventRecord(id={self.id}, type='{self.event_type}', status='{self.status}')>"
    
    def mark_processing_started(self):
        """Mark webhook event as processing started."""
        self.status = 'processing'
        self.processing_started_at = func.now()
    
    def mark_processing_completed(self, analysis_id: Optional[str] = None):
        """Mark webhook event as processing completed."""
        self.status = 'completed'
        self.processing_completed_at = func.now()
        if analysis_id:
            self.analysis_triggered = True
            self.analysis_id = analysis_id
    
    def mark_processing_failed(self, error_message: str):
        """Mark webhook event as processing failed."""
        self.status = 'failed'
        self.processing_completed_at = func.now()
        self.error_message = error_message

class SystemMetric(Base, TimestampMixin):
    """
    System metrics and performance data.
    
    Stores application metrics for monitoring and analytics.
    """
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    tags = Column(JSON, nullable=True)  # Additional metadata
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_metrics_name_created', 'metric_name', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SystemMetric(name='{self.metric_name}', value={self.metric_value})>"

# Utility functions for common database operations
def create_analysis_record(
    analysis_id: str,
    file_path: str,
    analysis_result: Dict[str, Any],
    repository_id: Optional[int] = None,
    **kwargs
) -> AnalysisRecord:
    """Create a new analysis record with validation."""
    return AnalysisRecord(
        analysis_id=analysis_id,
        file_path=file_path,
        analysis_result=analysis_result,
        repository_id=repository_id,
        quality_score=analysis_result.get('quality_score'),
        security_issues_count=len(analysis_result.get('security_issues', [])),
        overall_rating=analysis_result.get('overall_rating'),
        **kwargs
    )

def create_webhook_event(
    event_id: str,
    event_type: str,
    payload: Dict[str, Any],
    repository_id: Optional[int] = None,
    **kwargs
) -> WebhookEventRecord:
    """Create a new webhook event record."""
    return WebhookEventRecord(
        event_id=event_id,
        event_type=event_type,
        payload=payload,
        repository_id=repository_id,
        **kwargs
    )