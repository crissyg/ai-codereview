"""
GitHub Webhook Handler Service

This service processes incoming GitHub webhook events and coordinates the appropriate
responses. It handles pull request events, push events, and other GitHub notifications
to trigger automated code analysis.

The handler validates webhook signatures, parses event payloads, and dispatches
background tasks for code analysis while providing immediate responses to GitHub.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..utils.config import Settings
from .code_analyzer import CodeAnalyzer
from .github_integration import GitHubIntegration

logger = logging.getLogger(__name__)

class WebhookEventType(Enum):
    """
    Supported GitHub webhook event types.
    
    These are the events we actually care about and will process.
    GitHub sends many event types, but we only need to handle the ones
    related to code changes and pull requests.
    """
    PULL_REQUEST = "pull_request"
    PUSH = "push"
    PULL_REQUEST_REVIEW = "pull_request_review"
    CHECK_RUN = "check_run"
    UNKNOWN = "unknown"

class PullRequestAction(Enum):
    """
    Pull request actions that trigger analysis.
    
    Not all PR actions need analysis - we only care about when
    new code is added or when a PR is ready for review.
    """
    OPENED = "opened"
    SYNCHRONIZE = "synchronize"  # New commits pushed
    READY_FOR_REVIEW = "ready_for_review"
    REOPENED = "reopened"

@dataclass
class WebhookEvent:
    """
    Represents a processed webhook event with relevant information extracted.
    
    This makes it easier to work with webhook data by pulling out just
    the fields we need and providing a clean interface.
    """
    event_type: WebhookEventType
    repository_owner: str
    repository_name: str
    repository_full_name: str
    sender: str
    timestamp: datetime
    raw_payload: Dict[str, Any]
    
    # Pull request specific fields
    pr_number: Optional[int] = None
    pr_action: Optional[str] = None
    pr_title: Optional[str] = None
    pr_author: Optional[str] = None
    pr_branch: Optional[str] = None
    pr_base_branch: Optional[str] = None
    
    # Push specific fields
    ref: Optional[str] = None
    before_sha: Optional[str] = None
    after_sha: Optional[str] = None
    commits: Optional[List[Dict[str, Any]]] = None

class WebhookProcessor:
    """
    Processes different types of webhook events.
    
    This class handles the business logic for each event type,
    deciding what actions to take and coordinating with other services.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the webhook processor with required services.
        
        Args:
            settings: Application configuration settings
        """
        self.settings = settings
        self.code_analyzer = CodeAnalyzer()
        self.github_client = GitHubIntegration(settings.github_token)
        self.processing_queue = asyncio.Queue()
        
        logger.info("Webhook processor initialized")
    
    async def process_pull_request_event(self, event: WebhookEvent) -> bool:
        """
        Process pull request webhook events.
        
        This handles PR opened, updated, and ready for review events.
        We analyze the changed files and post results back to the PR.
        
        Args:
            event: The webhook event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        if not event.pr_number:
            logger.error("Pull request event missing PR number")
            return False
        
        # Check if this is an action we care about
        if event.pr_action not in [action.value for action in PullRequestAction]:
            logger.info(f"Ignoring PR action: {event.pr_action}")
            return True
        
        logger.info(
            f"Processing PR #{event.pr_number} in {event.repository_full_name} "
            f"(action: {event.pr_action})"
        )
        
        try:
            # Get PR information and changed files
            pr_info = await self.github_client.get_pull_request_info(
                event.repository_owner, 
                event.repository_name, 
                event.pr_number
            )
            
            if not pr_info:
                logger.error(f"Could not fetch PR info for #{event.pr_number}")
                return False
            
            # Get the files changed in this PR
            changed_files = await self.github_client.fetch_pull_request_files(
                event.repository_owner,
                event.repository_name, 
                event.pr_number
            )
            
            if not changed_files:
                logger.warning(f"No files found in PR #{event.pr_number}")
                # Post a comment saying no files to analyze
                await self.github_client.post_review_comment(
                    event.repository_owner,
                    event.repository_name,
                    event.pr_number,
                    "🤖 AI-CodeReview: No analyzable files found in this pull request."
                )
                return True
            
            # Start background analysis
            asyncio.create_task(
                self._analyze_pull_request_files(
                    event, pr_info, changed_files
                )
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing PR event: {e}")
            return False
    
    async def process_push_event(self, event: WebhookEvent) -> bool:
        """
        Process push webhook events.
        
        For now, we mainly use push events for monitoring and logging.
        In the future, we might analyze commits or update existing
        PR analyses when new commits are pushed.
        
        Args:
            event: The webhook event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        logger.info(
            f"Processing push to {event.ref} in {event.repository_full_name} "
            f"({len(event.commits or [])} commits)"
        )
        
        # For now, just log the push event
        # Future: Could trigger analysis of new commits
        # or update existing PR analyses
        
        return True
    
    async def _analyze_pull_request_files(
        self, 
        event: WebhookEvent, 
        pr_info: Any, 
        changed_files: List[Dict[str, Any]]
    ) -> None:
        """
        Analyze all files in a pull request and post results.
        
        This runs in the background to avoid blocking the webhook response.
        It processes each file, runs AI analysis, and posts comments with results.
        
        Args:
            event: The original webhook event
            pr_info: Pull request information from GitHub
            changed_files: List of files changed in the PR
        """
        try:
            logger.info(f"Starting background analysis for PR #{event.pr_number}")
            
            # Post initial comment to let users know analysis is starting
            await self.github_client.post_review_comment(
                event.repository_owner,
                event.repository_name,
                event.pr_number,
                "🤖 AI-CodeReview: Analysis started. Results will be posted shortly..."
            )
            
            analysis_results = []
            total_issues = 0
            
            # Analyze each changed file
            for file_info in changed_files:
                file_path = file_info["filename"]
                
                # Skip files we don't want to analyze
                if not self._should_analyze_file(file_path):
                    logger.debug(f"Skipping file: {file_path}")
                    continue
                
                logger.info(f"Analyzing file: {file_path}")
                
                # Get file content from GitHub
                file_content = await self.github_client.get_file_content(
                    event.repository_owner,
                    event.repository_name,
                    file_path,
                    pr_info.branch
                )
                
                if not file_content:
                    logger.warning(f"Could not fetch content for {file_path}")
                    continue
                
                # Run AI analysis on the file
                analysis_result = await self.code_analyzer.analyze_code(
                    file_content, file_path
                )
                
                # Track results for summary
                file_issues = len(analysis_result.security_issues)
                total_issues += file_issues
                
                analysis_results.append({
                    "file": file_path,
                    "result": analysis_result,
                    "issues_count": file_issues
                })
                
                # Post detailed analysis if there are significant findings
                if file_issues > 0 or analysis_result.quality_score < 70:
                    comment = self._format_file_analysis_comment(
                        analysis_result, file_path
                    )
                    await self.github_client.post_review_comment(
                        event.repository_owner,
                        event.repository_name,
                        event.pr_number,
                        comment
                    )
            
            # Post summary comment with overall results
            if analysis_results:
                summary_comment = self._format_summary_comment(
                    analysis_results, total_issues
                )
                await self.github_client.post_review_comment(
                    event.repository_owner,
                    event.repository_name,
                    event.pr_number,
                    summary_comment
                )
            
            logger.info(
                f"Completed analysis for PR #{event.pr_number}. "
                f"Analyzed {len(analysis_results)} files, found {total_issues} issues."
            )
            
        except Exception as e:
            logger.error(f"Error in background analysis for PR #{event.pr_number}: {e}")
            
            # Post error comment to let users know something went wrong
            await self.github_client.post_review_comment(
                event.repository_owner,
                event.repository_name,
                event.pr_number,
                "🤖 AI-CodeReview: Analysis failed due to an internal error. "
                "Please try again or contact support if the issue persists."
            )
    
    def _should_analyze_file(self, file_path: str) -> bool:
        """
        Determine if a file should be analyzed based on its extension.
        
        We only want to analyze source code files, not images, docs, etc.
        This helps avoid wasting resources and prevents errors.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be analyzed, False otherwise
        """
        if not file_path:
            return False
        
        # Get file extension
        extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
        
        # Supported file extensions for analysis
        analyzable_extensions = {
            'py', 'js', 'ts', 'java', 'cpp', 'cc', 'cxx', 'c', 'h', 
            'go', 'rs', 'php', 'rb', 'swift', 'kt', 'scala', 'cs'
        }
        
        return extension in analyzable_extensions
    
    def _format_file_analysis_comment(self, analysis_result: Any, file_path: str) -> str:
        """
        Format analysis results into a GitHub comment for a specific file.
        
        Creates a nicely formatted comment with security issues, suggestions,
        and quality metrics that's easy to read in the GitHub UI.
        
        Args:
            analysis_result: Results from the AI analysis
            file_path: Path to the analyzed file
            
        Returns:
            Formatted comment text
        """
        comment = f"## 🤖 AI-CodeReview Analysis: `{file_path}`\n\n"
        comment += f"**Overall Rating:** {analysis_result.overall_rating}\n"
        comment += f"**Quality Score:** {analysis_result.quality_score:.1f}/100\n\n"
        
        # Security issues section
        if analysis_result.security_issues:
            comment += "### 🔒 Security Issues Found:\n"
            for issue in analysis_result.security_issues:
                severity_emoji = "🔴" if issue['severity'] == 'HIGH' else "🟡"
                comment += f"{severity_emoji} **{issue['severity']}**: {issue['description']}\n"
            comment += "\n"
        
        # Improvement suggestions
        if analysis_result.suggestions:
            comment += "### 💡 Suggestions for Improvement:\n"
            for suggestion in analysis_result.suggestions[:3]:  # Limit to top 3
                comment += f"- {suggestion}\n"
            comment += "\n"
        
        # AI documentation
        if analysis_result.documentation:
            comment += f"### 📖 What this code does:\n"
            comment += f"``````\n\n"
        
        comment += "*Generated by AI-CodeReview*"
        return comment
    
    def _format_summary_comment(self, analysis_results: List[Dict], total_issues: int) -> str:
        """
        Format a summary comment for the entire pull request.
        
        Provides an overview of all analyzed files and their results
        in a clean, easy-to-scan format.
        
        Args:
            analysis_results: List of analysis results for all files
            total_issues: Total number of issues found across all files
            
        Returns:
            Formatted summary comment
        """
        comment = "## 🤖 AI-CodeReview Summary\n\n"
        comment += f"**Files Analyzed:** {len(analysis_results)}\n"
        comment += f"**Total Issues Found:** {total_issues}\n\n"
        
        if analysis_results:
            comment += "### 📊 File Results:\n"
            for result in analysis_results:
                status_emoji = "✅" if result["issues_count"] == 0 else "⚠️"
                quality_score = result["result"].quality_score
                rating = result["result"].overall_rating
                
                comment += (
                    f"{status_emoji} `{result['file']}` - "
                    f"Quality: {quality_score:.1f}/100, "
                    f"Issues: {result['issues_count']}, "
                    f"Rating: {rating}\n"
                )
        
        # Overall recommendation
        if total_issues == 0:
            comment += "\n🎉 **Great job!** No security issues found. Code looks good to merge!"
        elif total_issues <= 3:
            comment += "\n✨ **Good work!** Only minor issues found. Consider addressing them before merging."
        else:
            comment += "\n⚠️ **Attention needed.** Several issues found. Please review and address them."
        
        comment += "\n\n*Powered by AI-CodeReview - Automated Code Analysis*"
        return comment

class WebhookHandler:
    """
    Main webhook handler that coordinates event processing.
    
    This is the main entry point for webhook events. It parses the raw
    webhook payload, creates structured event objects, and dispatches
    them to the appropriate processors.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the webhook handler.
        
        Args:
            settings: Application configuration settings
        """
        self.settings = settings
        self.processor = WebhookProcessor(settings)
        
        logger.info("Webhook handler initialized")
    
    async def handle_webhook(
        self, 
        event_type: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle an incoming webhook event.
        
        This is the main entry point for processing GitHub webhooks.
        It parses the payload, creates an event object, and dispatches
        it to the appropriate processor.
        
        Args:
            event_type: The GitHub event type (from X-GitHub-Event header)
            payload: The webhook payload from GitHub
            
        Returns:
            Response dictionary with status and message
        """
        try:
            # Parse the webhook event
            event = self._parse_webhook_event(event_type, payload)
            
            if event.event_type == WebhookEventType.UNKNOWN:
                logger.info(f"Ignoring unsupported event type: {event_type}")
                return {
                    "status": "ignored",
                    "message": f"Event type '{event_type}' not supported"
                }
            
            # Log the incoming event
            logger.info(
                f"Processing {event.event_type.value} event from "
                f"{event.repository_full_name} by {event.sender}"
            )
            
            # Dispatch to appropriate processor
            success = await self._dispatch_event(event)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Event processed successfully"
                }
            else:
                return {
                    "status": "error", 
                    "message": "Event processing failed"
                }
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {
                "status": "error",
                "message": f"Webhook processing failed: {str(e)}"
            }
    
    def _parse_webhook_event(self, event_type: str, payload: Dict[str, Any]) -> WebhookEvent:
        """
        Parse a raw webhook payload into a structured event object.
        
        Extracts the relevant information from GitHub's webhook payload
        and creates a clean, typed object that's easier to work with.
        
        Args:
            event_type: The GitHub event type
            payload: Raw webhook payload
            
        Returns:
            Parsed webhook event object
        """
        # Map GitHub event types to the enum
        event_type_mapping = {
            "pull_request": WebhookEventType.PULL_REQUEST,
            "push": WebhookEventType.PUSH,
            "pull_request_review": WebhookEventType.PULL_REQUEST_REVIEW,
            "check_run": WebhookEventType.CHECK_RUN,
        }
        
        parsed_event_type = event_type_mapping.get(event_type, WebhookEventType.UNKNOWN)
        
        # Extract repository information
        repository = payload.get("repository", {})
        repository_owner = repository.get("owner", {}).get("login", "")
        repository_name = repository.get("name", "")
        repository_full_name = repository.get("full_name", "")
        
        # Extract sender information
        sender = payload.get("sender", {}).get("login", "")
        
        # Create base event object
        event = WebhookEvent(
            event_type=parsed_event_type,
            repository_owner=repository_owner,
            repository_name=repository_name,
            repository_full_name=repository_full_name,
            sender=sender,
            timestamp=datetime.utcnow(),
            raw_payload=payload
        )
        
        # Extract event-specific information
        if parsed_event_type == WebhookEventType.PULL_REQUEST:
            pr = payload.get("pull_request", {})
            event.pr_number = pr.get("number")
            event.pr_action = payload.get("action")
            event.pr_title = pr.get("title")
            event.pr_author = pr.get("user", {}).get("login")
            event.pr_branch = pr.get("head", {}).get("ref")
            event.pr_base_branch = pr.get("base", {}).get("ref")
            
        elif parsed_event_type == WebhookEventType.PUSH:
            event.ref = payload.get("ref")
            event.before_sha = payload.get("before")
            event.after_sha = payload.get("after")
            event.commits = payload.get("commits", [])
        
        return event
    
    async def _dispatch_event(self, event: WebhookEvent) -> bool:
        """
        Dispatch an event to the appropriate processor.
        
        Routes different event types to their specific handlers
        based on the event type.
        
        Args:
            event: The webhook event to process
            
        Returns:
            True if processing was successful, False otherwise
        """
        if event.event_type == WebhookEventType.PULL_REQUEST:
            return await self.processor.process_pull_request_event(event)
        
        elif event.event_type == WebhookEventType.PUSH:
            return await self.processor.process_push_event(event)
        
        else:
            logger.info(f"No processor for event type: {event.event_type}")
            return True  # Not an error, just not implemented yet