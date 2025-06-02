"""
Test Suite for API Endpoints

Integration tests for FastAPI endpoints covering code analysis,
webhook processing, repository management, and error handling.
Uses FastAPI's test client for realistic HTTP testing.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
import json
from typing import Dict, Any

from ..main import app
from ..models.analysis import AnalysisRequest, AnalysisResult
from ..models.repository import WebhookPayload
from ..services.code_analyzer import CodeAnalysisResult

class TestAPIClient:
    """Base test class with common fixtures and utilities."""
    
    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_analysis_request(self):
        """Sample analysis request payload."""
        return {
            "code_content": "def hello():\n    print('Hello, World!')",
            "file_path": "test.py",
            "language": "python"
        }
    
    @pytest.fixture
    def sample_webhook_payload(self):
        """Sample GitHub webhook payload."""
        return {
            "action": "opened",
            "pull_request": {
                "number": 1,
                "title": "Test PR",
                "user": {"login": "testuser"},
                "head": {"ref": "feature-branch", "sha": "abc123"},
                "base": {"ref": "main"}
            },
            "repository": {
                "id": 123456,
                "name": "test-repo",
                "full_name": "testuser/test-repo",
                "owner": {"login": "testuser"}
            },
            "sender": {"login": "testuser"}
        }
    
    @pytest.fixture
    def mock_analysis_result(self):
        """Mock analysis result for testing."""
        return CodeAnalysisResult(
            security_issues=[],
            quality_score=85.5,
            suggestions=["Consider adding type hints"],
            documentation="This function prints a greeting message",
            complexity_analysis={
                "total_lines": 2,
                "code_lines": 2,
                "comment_lines": 0,
                "function_count": 1,
                "class_count": 0,
                "complexity_rating": "LOW"
            },
            overall_rating="B - Good"
        )

class TestHealthEndpoints(TestAPIClient):
    """Test health check and system status endpoints."""
    
    def test_health_check_endpoint(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AI-CodeReview"
    
    def test_api_health_check_endpoint(self, client):
        """Test API-specific health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data

class TestCodeAnalysisEndpoints(TestAPIClient):
    """Test code analysis API endpoints."""
    
    @patch('app.services.code_analyzer.CodeAnalyzer.analyze_code')
    def test_analyze_code_endpoint_success(self, mock_analyze, client, sample_analysis_request, mock_analysis_result):
        """Test successful code analysis request."""
        mock_analyze.return_value = mock_analysis_result
        
        response = client.post("/api/v1/analyze", json=sample_analysis_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["file_path"] == "test.py"
        assert "analysis" in data
        assert "summary" in data
        
        # Verify analysis structure
        analysis = data["analysis"]
        assert "security_issues" in analysis
        assert "quality_score" in analysis
        assert "suggestions" in analysis
        assert "documentation" in analysis
        assert "complexity" in analysis
        assert "overall_rating" in analysis
    
    def test_analyze_code_endpoint_validation_error(self, client):
        """Test validation error handling for invalid request."""
        invalid_request = {
            "code_content": "",  # Empty code should fail validation
            "file_path": "test.py"
        }
        
        response = client.post("/api/v1/analyze", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_analyze_code_endpoint_missing_fields(self, client):
        """Test handling of requests with missing required fields."""
        incomplete_request = {
            "file_path": "test.py"
            # Missing code_content
        }
        
        response = client.post("/api/v1/analyze", json=incomplete_request)
        
        assert response.status_code == 422
    
    @patch('app.services.code_analyzer.CodeAnalyzer.analyze_code')
    def test_analyze_code_endpoint_internal_error(self, mock_analyze, client, sample_analysis_request):
        """Test handling of internal analysis errors."""
        mock_analyze.side_effect = Exception("Analysis failed")
        
        response = client.post("/api/v1/analyze", json=sample_analysis_request)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Analysis failed" in data["detail"]
    
    def test_analyze_code_endpoint_with_different_languages(self, client):
        """Test analysis endpoint with different programming languages."""
        languages = ["python", "javascript", "java", "cpp"]
        
        for language in languages:
            request_data = {
                "code_content": f"// {language} code\nfunction test() {{ return true; }}",
                "file_path": f"test.{language}",
                "language": language
            }
            
            with patch('app.services.code_analyzer.CodeAnalyzer.analyze_code') as mock_analyze:
                mock_analyze.return_value = Mock(
                    security_issues=[],
                    quality_score=80.0,
                    suggestions=[],
                    documentation="Test function",
                    complexity_analysis={},
                    overall_rating="B - Good"
                )
                
                response = client.post("/api/v1/analyze", json=request_data)
                assert response.status_code == 200

class TestWebhookEndpoints(TestAPIClient):
    """Test GitHub webhook processing endpoints."""
    
    @patch('app.services.webhook_handler.WebhookHandler.handle_webhook')
    def test_github_webhook_endpoint_success(self, mock_handler, client, sample_webhook_payload):
        """Test successful webhook processing."""
        mock_handler.return_value = {
            "status": "success",
            "message": "Event processed successfully"
        }
        
        headers = {
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": "sha256=test_signature"
        }
        
        response = client.post(
            "/api/v1/webhook/github",
            json=sample_webhook_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_github_webhook_endpoint_missing_headers(self, client, sample_webhook_payload):
        """Test webhook endpoint with missing required headers."""
        response = client.post("/api/v1/webhook/github", json=sample_webhook_payload)
        
        # Should handle missing headers gracefully
        assert response.status_code in [200, 400]
    
    @patch('app.services.webhook_handler.WebhookHandler.handle_webhook')
    def test_github_webhook_endpoint_unsupported_event(self, mock_handler, client):
        """Test webhook endpoint with unsupported event type."""
        mock_handler.return_value = {
            "status": "ignored",
            "message": "Event type 'issues' not supported"
        }
        
        payload = {
            "action": "opened",
            "issue": {"number": 1},
            "repository": {"name": "test-repo"},
            "sender": {"login": "testuser"}
        }
        
        headers = {"X-GitHub-Event": "issues"}
        
        response = client.post(
            "/api/v1/webhook/github",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
    
    @patch('app.services.webhook_handler.WebhookHandler.handle_webhook')
    def test_github_webhook_endpoint_processing_error(self, mock_handler, client, sample_webhook_payload):
        """Test webhook endpoint error handling."""
        mock_handler.side_effect = Exception("Webhook processing failed")
        
        headers = {"X-GitHub-Event": "pull_request"}
        
        response = client.post(
            "/api/v1/webhook/github",
            json=sample_webhook_payload,
            headers=headers
        )
        
        assert response.status_code == 500

class TestSystemStatsEndpoints(TestAPIClient):
    """Test system statistics and monitoring endpoints."""
    
    def test_stats_endpoint_success(self, client):
        """Test system statistics endpoint."""
        response = client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify expected statistics fields
        expected_fields = [
            "total_analyses",
            "pull_requests_processed", 
            "security_issues_found",
            "average_quality_score",
            "system_uptime",
            "active_repositories"
        ]
        
        for field in expected_fields:
            assert field in data
            assert isinstance(data[field], (int, float, str))
    
    def test_stats_endpoint_data_types(self, client):
        """Test that statistics endpoint returns correct data types."""
        response = client.get("/api/v1/stats")
        data = response.json()
        
        # Verify data types
        assert isinstance(data["total_analyses"], int)
        assert isinstance(data["security_issues_found"], int)
        assert isinstance(data["average_quality_score"], (int, float))
        assert isinstance(data["system_uptime"], str)

class TestErrorHandling(TestAPIClient):
    """Test API error handling and edge cases."""
    
    def test_404_endpoint_not_found(self, client):
        """Test handling of non-existent endpoints."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test handling of unsupported HTTP methods."""
        response = client.delete("/api/v1/analyze")
        
        assert response.status_code == 405
    
    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON requests."""
        response = client.post(
            "/api/v1/analyze",
            data="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_large_request_payload(self, client):
        """Test handling of very large request payloads."""
        large_code = "print('hello')\n" * 10000  # Very large code
        
        request_data = {
            "code_content": large_code,
            "file_path": "large.py",
            "language": "python"
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        
        # Should either process successfully or return appropriate error
        assert response.status_code in [200, 413, 422, 500]

class TestRequestValidation(TestAPIClient):
    """Test request validation and data sanitization."""
    
    def test_code_content_validation(self, client):
        """Test validation of code content field."""
        test_cases = [
            {"code_content": "", "expected_status": 422},  # Empty
            {"code_content": "   ", "expected_status": 422},  # Whitespace only
            {"code_content": "print('hello')", "expected_status": 200},  # Valid
        ]
        
        for case in test_cases:
            request_data = {
                "code_content": case["code_content"],
                "file_path": "test.py"
            }
            
            with patch('app.services.code_analyzer.CodeAnalyzer.analyze_code') as mock_analyze:
                mock_analyze.return_value = Mock(
                    security_issues=[], quality_score=80.0, suggestions=[],
                    documentation="", complexity_analysis={}, overall_rating="B"
                )
                
                response = client.post("/api/v1/analyze", json=request_data)
                assert response.status_code == case["expected_status"]
    
    def test_language_validation(self, client):
        """Test validation of programming language field."""
        valid_languages = ["python", "javascript", "java", "cpp"]
        
        for language in valid_languages:
            request_data = {
                "code_content": "test code",
                "file_path": "test.py",
                "language": language
            }
            
            with patch('app.services.code_analyzer.CodeAnalyzer.analyze_code') as mock_analyze:
                mock_analyze.return_value = Mock(
                    security_issues=[], quality_score=80.0, suggestions=[],
                    documentation="", complexity_analysis={}, overall_rating="B"
                )
                
                response = client.post("/api/v1/analyze", json=request_data)
                assert response.status_code == 200

class TestResponseFormat(TestAPIClient):
    """Test API response format consistency."""
    
    @patch('app.services.code_analyzer.CodeAnalyzer.analyze_code')
    def test_analysis_response_format(self, mock_analyze, client, sample_analysis_request, mock_analysis_result):
        """Test that analysis responses follow consistent format."""
        mock_analyze.return_value = mock_analysis_result
        
        response = client.post("/api/v1/analyze", json=sample_analysis_request)
        data = response.json()
        
        # Verify top-level structure
        assert "status" in data
        assert "file_path" in data
        assert "analysis" in data
        assert "summary" in data
        
        # Verify analysis structure
        analysis = data["analysis"]
        required_analysis_fields = [
            "security_issues", "quality_score", "suggestions",
            "documentation", "complexity", "overall_rating"
        ]
        for field in required_analysis_fields:
            assert field in analysis
        
        # Verify summary structure
        summary = data["summary"]
        required_summary_fields = [
            "total_issues", "security_risk_level", "recommendation"
        ]
        for field in required_summary_fields:
            assert field in summary
    
    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        response = client.post("/api/v1/analyze", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data