"""
Tests Package

Comprehensive test suite for the AI-CodeReview application including
unit tests, integration tests, and test utilities.

Test Modules:
- test_analyzer: AI code analysis functionality
- test_github: GitHub integration and API calls  
- test_api: REST API endpoints and responses
- test_models: Data model validation and serialization
- test_webhook: Webhook processing and event handling
"""

import pytest
import asyncio
from typing import Generator, Any
from unittest.mock import Mock, AsyncMock

# Test configuration
TEST_CONFIG = {
    "test_database_url": "sqlite:///:memory:",
    "mock_github_token": "test_token_123",
    "test_timeout": 30,
    "async_test_timeout": 10,
}

# Common test fixtures and utilities
class TestFixtures:
    """Common test fixtures and mock data."""
    
    @staticmethod
    def sample_code() -> str:
        """Sample Python code for testing analysis."""
        return '''
def hello_world(name="World"):
    """Simple greeting function."""
    if not name:
        name = "World"
    print(f"Hello, {name}!")
    return f"Hello, {name}!"
'''
    
    @staticmethod
    def sample_repository_data() -> dict:
        """Sample GitHub repository data."""
        return {
            "id": 123456,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {"login": "testuser", "id": 789},
            "html_url": "https://github.com/testuser/test-repo",
            "clone_url": "https://github.com/testuser/test-repo.git",
            "default_branch": "main",
            "private": False
        }
    
    @staticmethod
    def sample_pull_request_data() -> dict:
        """Sample pull request data."""
        return {
            "number": 1,
            "title": "Test PR",
            "state": "open",
            "user": {"login": "developer", "id": 456},
            "head": {"ref": "feature-branch", "sha": "abc123"},
            "base": {"ref": "main"},
            "html_url": "https://github.com/testuser/test-repo/pull/1"
        }

class MockServices:
    """Mock implementations of external services for testing."""
    
    @staticmethod
    def mock_github_client() -> Mock:
        """Create mock GitHub client."""
        mock = Mock()
        mock.get_pull_request_info = AsyncMock()
        mock.fetch_pull_request_files = AsyncMock()
        mock.post_review_comment = AsyncMock()
        mock.get_file_content = AsyncMock()
        return mock
    
    @staticmethod
    def mock_code_analyzer() -> Mock:
        """Create mock code analyzer."""
        mock = Mock()
        mock.analyze_code = AsyncMock()
        return mock

# Pytest configuration and fixtures
@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config() -> dict:
    """Test configuration fixture."""
    return TEST_CONFIG.copy()

@pytest.fixture
def sample_code() -> str:
    """Sample code fixture."""
    return TestFixtures.sample_code()

@pytest.fixture
def mock_github_client() -> Mock:
    """Mock GitHub client fixture."""
    return MockServices.mock_github_client()

@pytest.fixture
def mock_code_analyzer() -> Mock:
    """Mock code analyzer fixture."""
    return MockServices.mock_code_analyzer()

# Test utilities
def assert_analysis_result_valid(result: dict) -> None:
    """Assert that analysis result has required fields."""
    required_fields = [
        "security_issues", "quality_score", "suggestions",
        "documentation", "complexity_analysis", "overall_rating"
    ]
    
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    assert 0 <= result["quality_score"] <= 100, "Quality score must be 0-100"
    assert isinstance(result["security_issues"], list), "Security issues must be a list"
    assert isinstance(result["suggestions"], list), "Suggestions must be a list"

def create_test_database() -> str:
    """Create in-memory test database."""
    return TEST_CONFIG["test_database_url"]

async def cleanup_test_data() -> None:
    """Clean up test data after tests."""
    # Implementation would clean up any test artifacts
    pass

# Export test utilities
__all__ = [
    "TEST_CONFIG",
    "TestFixtures", 
    "MockServices",
    "assert_analysis_result_valid",
    "create_test_database",
    "cleanup_test_data",
]