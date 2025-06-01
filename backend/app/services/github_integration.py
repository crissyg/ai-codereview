"""
GitHub Integration Service

This service handles all communication with GitHub:
- Fetching code from repositories
- Receiving webhook notifications when code changes
- Posting analysis results back to pull requests

This acts as the "messenger" that talks to GitHub on behalf of the system.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)

@dataclass
class PullRequestInfo:
    """Information about a GitHub pull request that needs to be analyzed."""
    number: int
    title: str
    author: str
    branch: str
    changed_files: List[str]
    repository: str

class GitHubIntegration:
    """
    Handles all interactions with GitHub's API.
    
    This class acts as a diplomatic ambassador - it knows how to communicate
    with GitHub in the proper format and handles all the technical details
    of fetching code and posting results.
    """
    
    def __init__(self, github_token: str):
        """
        Initialize GitHub integration with authentication.
        
        Args:
            github_token: Personal access token for GitHub API
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-CodeReview/1.0"
        }
        
        logger.info("GitHub integration initialized")
    
    async def fetch_pull_request_files(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get all files changed in a pull request.
        
        Asks GitHub: "What files were modified in this pull request?"
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            pr_number: Pull request number
            
        Returns:
            List of file information including content and changes
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        files_data = await response.json()
                        logger.info(f"Fetched {len(files_data)} files from PR #{pr_number}")
                        return files_data
                    else:
                        logger.error(f"Failed to fetch PR files: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching PR files: {e}")
            return []
    
    async def get_file_content(self, repo_owner: str, repo_name: str, file_path: str, ref: str = "main") -> Optional[str]:
        """
        Download the actual content of a file from GitHub.
        
        Asks GitHub: "Can you send me the contents of this specific file?"
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            file_path: Path to the file in the repository
            ref: Branch or commit reference
            
        Returns:
            File content as a string, or None if failed
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
        params = {"ref": ref}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        file_data = await response.json()
                        
                        # GitHub returns file content encoded in base64
                        if file_data.get("encoding") == "base64":
                            content = base64.b64decode(file_data["content"]).decode('utf-8')
                            logger.info(f"Successfully fetched content for {file_path}")
                            return content
                        else:
                            logger.warning(f"Unexpected encoding for {file_path}")
                            return None
                    else:
                        logger.error(f"Failed to fetch file content: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            return None
    
    async def post_review_comment(self, repo_owner: str, repo_name: str, pr_number: int, 
                                 comment_body: str, file_path: str = None, line_number: int = None) -> bool:
        """
        Post AI analysis results as a comment on the pull request.
        
        Leaves a helpful review comment that explains what the AI found.
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            pr_number: Pull request number
            comment_body: The analysis results to post
            file_path: Specific file to comment on (optional)
            line_number: Specific line to comment on (optional)
            
        Returns:
            True if comment was posted successfully, False otherwise
        """
        if file_path and line_number:
            # Post a review comment on a specific line
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
            data = {
                "body": comment_body,
                "event": "COMMENT",
                "comments": [{
                    "path": file_path,
                    "line": line_number,
                    "body": comment_body
                }]
            }
        else:
            # Post a general comment on the pull request
            url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
            data = {"body": comment_body}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Successfully posted comment to PR #{pr_number}")
                        return True
                    else:
                        logger.error(f"Failed to post comment: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            return False
    
    async def get_pull_request_info(self, repo_owner: str, repo_name: str, pr_number: int) -> Optional[PullRequestInfo]:
        """
        Get basic information about a pull request.
        
        Asks GitHub: "Tell me the basic details about this pull request."
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        pr_data = await response.json()
                        
                        # Extract the information needed
                        pr_info = PullRequestInfo(
                            number=pr_data["number"],
                            title=pr_data["title"],
                            author=pr_data["user"]["login"],
                            branch=pr_data["head"]["ref"],
                            changed_files=[],  # Will be filled separately
                            repository=f"{repo_owner}/{repo_name}"
                        )
                        
                        logger.info(f"Fetched PR info for #{pr_number}: {pr_info.title}")
                        return pr_info
                    else:
                        logger.error(f"Failed to fetch PR info: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching PR info: {e}")
            return None
    
    async def get_repository_info(self, repo_owner: str, repo_name: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about a repository.
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            
        Returns:
            Repository information or None if failed
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        repo_data = await response.json()
                        logger.info(f"Fetched repository info for {repo_owner}/{repo_name}")
                        return repo_data
                    else:
                        logger.error(f"Failed to fetch repository info: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching repository info: {e}")
            return None
    
    async def create_check_run(self, repo_owner: str, repo_name: str, commit_sha: str, 
                              status: str, conclusion: str = None, summary: str = "") -> bool:
        """
        Create a check run for a specific commit.
        
        This shows up as a status check on the pull request.
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            commit_sha: The commit SHA to create the check for
            status: "queued", "in_progress", or "completed"
            conclusion: "success", "failure", "neutral", "cancelled", "skipped", "timed_out", or "action_required"
            summary: Summary of the check results
            
        Returns:
            True if check run was created successfully, False otherwise
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/check-runs"
        
        data = {
            "name": "AI-CodeReview",
            "head_sha": commit_sha,
            "status": status,
            "external_id": "ai-codereview-check",
            "output": {
                "title": "AI Code Review Results",
                "summary": summary
            }
        }
        
        if conclusion:
            data["conclusion"] = conclusion
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Successfully created check run for commit {commit_sha}")
                        return True
                    else:
                        logger.error(f"Failed to create check run: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error creating check run: {e}")
            return False
    
    async def list_pull_requests(self, repo_owner: str, repo_name: str, state: str = "open") -> List[Dict[str, Any]]:
        """
        List pull requests in a repository.
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            state: "open", "closed", or "all"
            
        Returns:
            List of pull request data
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/pulls"
        params = {"state": state}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        prs_data = await response.json()
                        logger.info(f"Fetched {len(prs_data)} pull requests from {repo_owner}/{repo_name}")
                        return prs_data
                    else:
                        logger.error(f"Failed to fetch pull requests: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching pull requests: {e}")
            return []
    
    async def get_commit_info(self, repo_owner: str, repo_name: str, commit_sha: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific commit.
        
        Args:
            repo_owner: GitHub username or organization
            repo_name: Repository name
            commit_sha: The commit SHA
            
        Returns:
            Commit information or None if failed
        """
        url = f"{self.base_url}/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        commit_data = await response.json()
                        logger.info(f"Fetched commit info for {commit_sha}")
                        return commit_data
                    else:
                        logger.error(f"Failed to fetch commit info: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching commit info: {e}")
            return None
    
    def validate_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Validate GitHub webhook signature for security.
        
        Args:
            payload: Raw webhook payload
            signature: GitHub signature header
            secret: Webhook secret
            
        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib
        
        if not secret:
            logger.warning("No webhook secret configured")
            return True  # Skip validation if no secret is set
        
        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # GitHub sends signature as "sha256=<hash>"
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False