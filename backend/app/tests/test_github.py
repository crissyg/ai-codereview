"""
Test Suite for GitHub Integration Service

Unit tests for GitHub API interactions including repository data fetching,
pull request management, webhook signature validation, and error handling.
Uses mocking to avoid actual API calls during testing.
"""

import pytest
import aiohttp
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
import base64

from ..services.github_integration import GitHubIntegration, PullRequestInfo
from ..models.repository import GitHubUser, Repository

class TestGitHubIntegration:
    """Test cases for the main GitHubIntegration class."""
    
    @pytest.fixture
    def github_token(self):
        """Mock GitHub token for testing."""
        return "ghp_test_token_123456789"
    
    @pytest.fixture
    def github_client(self, github_token):
        """Create GitHubIntegration instance with test token."""
        return GitHubIntegration(github_token)
    
    @pytest.fixture
    def mock_session_response(self):
        """Create mock aiohttp session response."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock()
        return mock_response
    
    @pytest.fixture
    def sample_repository_data(self):
        """Sample GitHub repository API response data."""
        return {
            "id": 123456,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {
                "login": "testuser",
                "id": 789,
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "html_url": "https://github.com/testuser"
            },
            "description": "A test repository",
            "html_url": "https://github.com/testuser/test-repo",
            "clone_url": "https://github.com/testuser/test-repo.git",
            "default_branch": "main",
            "language": "Python",
            "private": False
        }
    
    @pytest.fixture
    def sample_pull_request_data(self):
        """Sample GitHub pull request API response data."""
        return {
            "number": 1,
            "title": "Add new feature",
            "body": "This PR adds a new feature",
            "state": "open",
            "user": {
                "login": "developer",
                "id": 456,
                "avatar_url": "https://github.com/images/error/octocat_happy.gif",
                "html_url": "https://github.com/developer"
            },
            "head": {
                "ref": "feature-branch",
                "sha": "abc123def456"
            },
            "base": {
                "ref": "main"
            },
            "html_url": "https://github.com/testuser/test-repo/pull/1",
            "created_at": "2025-06-01T10:00:00Z",
            "updated_at": "2025-06-01T12:00:00Z",
            "mergeable": True
        }

class TestGitHubClientInitialization(TestGitHubIntegration):
    """Test GitHub client initialization and configuration."""
    
    def test_client_initialization_with_token(self, github_token):
        """Test that client initializes correctly with token."""
        client = GitHubIntegration(github_token)
        
        assert client.github_token == github_token
        assert client.base_url == "https://api.github.com"
        assert "Authorization" in client.headers
        assert f"token {github_token}" in client.headers["Authorization"]
    
    def test_client_headers_configuration(self, github_client):
        """Test that client headers are configured correctly."""
        headers = github_client.headers
        
        assert "Authorization" in headers
        assert "Accept" in headers
        assert "User-Agent" in headers
        assert headers["Accept"] == "application/vnd.github.v3+json"
        assert "AI-CodeReview" in headers["User-Agent"]

class TestPullRequestOperations(TestGitHubIntegration):
    """Test pull request related operations."""
    
    @pytest.mark.asyncio
    async def test_fetch_pull_request_files_success(self, github_client, mock_session_response):
        """Test successful fetching of pull request files."""
        # Mock response data
        files_data = [
            {
                "filename": "src/main.py",
                "status": "modified",
                "additions": 10,
                "deletions": 5,
                "changes": 15
            },
            {
                "filename": "tests/test_main.py",
                "status": "added",
                "additions": 20,
                "deletions": 0,
                "changes": 20
            }
        ]
        mock_session_response.json.return_value = files_data
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_session_response
            
            result = await github_client.fetch_pull_request_files("testuser", "test-repo", 1)
            
            assert len(result) == 2
            assert result[0]["filename"] == "src/main.py"
            assert result[1]["filename"] == "tests/test_main.py"
    
    @pytest.mark.asyncio
    async def test_fetch_pull_request_files_api_error(self, github_client):
        """Test handling of API errors when fetching PR files."""
        mock_response = Mock()
        mock_response.status = 404
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.fetch_pull_request_files("testuser", "nonexistent-repo", 1)
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_pull_request_info_success(self, github_client, sample_pull_request_data, mock_session_response):
        """Test successful retrieval of pull request information."""
        mock_session_response.json.return_value = sample_pull_request_data
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_session_response
            
            result = await github_client.get_pull_request_info("testuser", "test-repo", 1)
            
            assert isinstance(result, PullRequestInfo)
            assert result.number == 1
            assert result.title == "Add new feature"
            assert result.author == "developer"
            assert result.head_branch == "feature-branch"
            assert result.base_branch == "main"
    
    @pytest.mark.asyncio
    async def test_get_pull_request_info_not_found(self, github_client):
        """Test handling of non-existent pull request."""
        mock_response = Mock()
        mock_response.status = 404
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.get_pull_request_info("testuser", "test-repo", 999)
            
            assert result is None

class TestFileContentOperations(TestGitHubIntegration):
    """Test file content retrieval operations."""
    
    @pytest.mark.asyncio
    async def test_get_file_content_success(self, github_client, mock_session_response):
        """Test successful file content retrieval."""
        # Mock file content (base64 encoded)
        file_content = "def hello():\n    print('Hello, World!')"
        encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        
        file_data = {
            "content": encoded_content,
            "encoding": "base64"
        }
        mock_session_response.json.return_value = file_data
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_session_response
            
            result = await github_client.get_file_content("testuser", "test-repo", "src/main.py")
            
            assert result == file_content
    
    @pytest.mark.asyncio
    async def test_get_file_content_file_not_found(self, github_client):
        """Test handling of non-existent file."""
        mock_response = Mock()
        mock_response.status = 404
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.get_file_content("testuser", "test-repo", "nonexistent.py")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_file_content_unexpected_encoding(self, github_client, mock_session_response):
        """Test handling of unexpected file encoding."""
        file_data = {
            "content": "some content",
            "encoding": "unknown"
        }
        mock_session_response.json.return_value = file_data
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_session_response
            
            result = await github_client.get_file_content("testuser", "test-repo", "file.txt")
            
            assert result is None

class TestCommentOperations(TestGitHubIntegration):
    """Test comment posting operations."""
    
    @pytest.mark.asyncio
    async def test_post_review_comment_success(self, github_client):
        """Test successful posting of review comment."""
        mock_response = Mock()
        mock_response.status = 201
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.post_review_comment(
                "testuser", "test-repo", 1, "Great work on this PR!"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_post_review_comment_with_file_and_line(self, github_client):
        """Test posting comment on specific file and line."""
        mock_response = Mock()
        mock_response.status = 201
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.post_review_comment(
                "testuser", "test-repo", 1, 
                "Consider using a more descriptive variable name",
                file_path="src/main.py",
                line_number=42
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_post_review_comment_api_error(self, github_client):
        """Test handling of API errors when posting comments."""
        mock_response = Mock()
        mock_response.status = 403  # Forbidden
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.post_review_comment(
                "testuser", "test-repo", 1, "Comment"
            )
            
            assert result is False

class TestRepositoryOperations(TestGitHubIntegration):
    """Test repository information retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_repository_info_success(self, github_client, sample_repository_data, mock_session_response):
        """Test successful repository information retrieval."""
        mock_session_response.json.return_value = sample_repository_data
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_session_response
            
            result = await github_client.get_repository_info("testuser", "test-repo")
            
            assert result is not None
            assert result["id"] == 123456
            assert result["name"] == "test-repo"
            assert result["full_name"] == "testuser/test-repo"
    
    @pytest.mark.asyncio
    async def test_list_pull_requests_success(self, github_client, sample_pull_request_data, mock_session_response):
        """Test successful listing of pull requests."""
        mock_session_response.json.return_value = [sample_pull_request_data]
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_session_response
            
            result = await github_client.list_pull_requests("testuser", "test-repo")
            
            assert len(result) == 1
            assert result[0]["number"] == 1
            assert result[0]["title"] == "Add new feature"

class TestWebhookValidation(TestGitHubIntegration):
    """Test webhook signature validation."""
    
    def test_validate_webhook_signature_valid(self, github_client):
        """Test validation of correct webhook signature."""
        payload = b'{"action": "opened", "number": 1}'
        secret = "webhook_secret_123"
        
        # Calculate expected signature
        import hmac
        import hashlib
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        result = github_client.validate_webhook_signature(
            payload, f"sha256={expected_signature}", secret
        )
        
        assert result is True
    
    def test_validate_webhook_signature_invalid(self, github_client):
        """Test validation of incorrect webhook signature."""
        payload = b'{"action": "opened", "number": 1}'
        secret = "webhook_secret_123"
        invalid_signature = "sha256=invalid_signature_here"
        
        result = github_client.validate_webhook_signature(
            payload, invalid_signature, secret
        )
        
        assert result is False
    
    def test_validate_webhook_signature_no_secret(self, github_client):
        """Test validation when no secret is configured."""
        payload = b'{"action": "opened", "number": 1}'
        signature = "sha256=some_signature"
        
        result = github_client.validate_webhook_signature(
            payload, signature, None
        )
        
        # Should return True when no secret is configured (skip validation)
        assert result is True

class TestCheckRunOperations(TestGitHubIntegration):
    """Test GitHub check run operations."""
    
    @pytest.mark.asyncio
    async def test_create_check_run_success(self, github_client):
        """Test successful creation of check run."""
        mock_response = Mock()
        mock_response.status = 201
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.create_check_run(
                "testuser", "test-repo", "abc123def456",
                "completed", "success", "All checks passed!"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_create_check_run_in_progress(self, github_client):
        """Test creation of in-progress check run."""
        mock_response = Mock()
        mock_response.status = 201
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.create_check_run(
                "testuser", "test-repo", "abc123def456",
                "in_progress", summary="Analysis in progress..."
            )
            
            assert result is True

class TestErrorHandling(TestGitHubIntegration):
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, github_client):
        """Test handling of network errors."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = aiohttp.ClientError("Network error")
            
            result = await github_client.get_repository_info("testuser", "test-repo")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, github_client):
        """Test handling of request timeouts."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.side_effect = asyncio.TimeoutError()
            
            result = await github_client.fetch_pull_request_files("testuser", "test-repo", 1)
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_invalid_json_response_handling(self, github_client):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            result = await github_client.get_repository_info("testuser", "test-repo")
            
            assert result is None