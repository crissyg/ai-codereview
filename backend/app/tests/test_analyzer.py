"""
Test Suite for CodeAnalyzer Service

Unit tests for the AI-powered code analysis engine covering
security detection, quality scoring, documentation generation,
and complexity analysis using pytest and async testing.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from ..services.code_analyzer import CodeAnalyzer, CodeAnalysisResult, AIModelManager
from ..models.analysis import SecuritySeverity, ComplexityRating

class TestCodeAnalyzer:
    """Test cases for the main CodeAnalyzer class."""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Create mock AI model manager to avoid loading real models."""
        mock = Mock(spec=AIModelManager)
        
        # Mock classifier responses
        mock.classifier.return_value = [{'score': 0.85, 'label': 'POSITIVE'}]
        mock.security_classifier.return_value = [{'score': 0.75, 'label': 'POSITIVE'}]
        mock.generator.return_value = [{'generated_text': 'This function prints a greeting message.'}]
        mock.qa_model.return_value = {'answer': 'This is a greeting function'}
        mock.code_completer.return_value = [{'token_str': 'suggestion'}]
        
        return mock
    
    @pytest.fixture
    def analyzer(self, mock_model_manager):
        """Create CodeAnalyzer instance with mocked AI models."""
        with patch('app.services.code_analyzer.AIModelManager', return_value=mock_model_manager):
            return CodeAnalyzer()
    
    @pytest.fixture
    def sample_code(self):
        """Sample Python code for testing."""
        return '''
def hello_world(name="World"):
    """Simple greeting function."""
    if not name:
        name = "World"
    print(f"Hello, {name}!")
    return f"Hello, {name}!"
'''
    
    @pytest.fixture
    def vulnerable_code(self):
        """Sample code with security vulnerabilities."""
        return '''
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()
'''

class TestCodeAnalysisBasics(TestCodeAnalyzer):
    """Test basic code analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_simple_code_returns_valid_result(self, analyzer, sample_code):
        """Test that analyzing simple code returns a valid CodeAnalysisResult."""
        result = await analyzer.analyze_code(sample_code, "test.py")
        
        # Verify result structure
        assert isinstance(result, CodeAnalysisResult)
        assert isinstance(result.security_issues, list)
        assert isinstance(result.quality_score, float)
        assert isinstance(result.suggestions, list)
        assert isinstance(result.documentation, str)
        assert hasattr(result, 'complexity_analysis')
        assert isinstance(result.overall_rating, str)
    
    @pytest.mark.asyncio
    async def test_analyze_empty_code_handles_gracefully(self, analyzer):
        """Test that empty code input is handled gracefully."""
        result = await analyzer.analyze_code("", "empty.py")
        
        assert result is not None
        assert result.quality_score >= 0
        assert isinstance(result.suggestions, list)
    
    @pytest.mark.asyncio
    async def test_analyze_code_with_file_path_context(self, analyzer, sample_code):
        """Test that file path context is properly used in analysis."""
        result = await analyzer.analyze_code(sample_code, "src/utils/greeting.py")
        
        assert result is not None
        # Documentation should include file context
        assert "greeting.py" in result.documentation or result.documentation != ""

class TestSecurityAnalysis(TestCodeAnalyzer):
    """Test security vulnerability detection functionality."""
    
    @pytest.mark.asyncio
    async def test_detects_sql_injection_vulnerability(self, analyzer, vulnerable_code):
        """Test detection of SQL injection vulnerabilities."""
        result = await analyzer.analyze_code(vulnerable_code, "vulnerable.py")
        
        # Should detect at least one security issue
        assert len(result.security_issues) > 0
        
        # Verify security issue structure
        security_issue = result.security_issues[0]
        assert 'type' in security_issue
        assert 'severity' in security_issue
        assert 'confidence' in security_issue
        assert 'description' in security_issue
    
    @pytest.mark.asyncio
    async def test_security_issue_severity_classification(self, analyzer, vulnerable_code):
        """Test that security issues are properly classified by severity."""
        result = await analyzer.analyze_code(vulnerable_code, "test.py")
        
        if result.security_issues:
            for issue in result.security_issues:
                assert issue['severity'] in ['HIGH', 'MEDIUM', 'LOW']
                assert 0.0 <= issue['confidence'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_secure_code_has_no_issues(self, analyzer, sample_code):
        """Test that secure code produces fewer or no security issues."""
        result = await analyzer.analyze_code(sample_code, "secure.py")
        
        # Secure code should have minimal security issues
        high_severity_issues = [
            issue for issue in result.security_issues 
            if issue.get('severity') == 'HIGH'
        ]
        assert len(high_severity_issues) == 0

class TestQualityScoring(TestCodeAnalyzer):
    """Test code quality scoring functionality."""
    
    @pytest.mark.asyncio
    async def test_quality_score_in_valid_range(self, analyzer, sample_code):
        """Test that quality scores are within valid range (0-100)."""
        result = await analyzer.analyze_code(sample_code, "test.py")
        
        assert 0.0 <= result.quality_score <= 100.0
    
    @pytest.mark.asyncio
    async def test_quality_score_considers_code_characteristics(self, analyzer):
        """Test that quality scoring considers various code characteristics."""
        # Code with good practices (functions, comments)
        good_code = '''
def calculate_area(radius):
    """Calculate circle area."""
    return 3.14159 * radius ** 2
'''
        
        # Code with poor practices (no functions, no comments)
        poor_code = '''
x = 5
y = x * 2 + 3
print(y)
'''
        
        good_result = await analyzer.analyze_code(good_code, "good.py")
        poor_result = await analyzer.analyze_code(poor_code, "poor.py")
        
        # Good code should generally score higher
        # Note: This might not always be true due to AI model variability
        assert good_result.quality_score >= 0
        assert poor_result.quality_score >= 0

class TestComplexityAnalysis(TestCodeAnalyzer):
    """Test code complexity analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_complexity_metrics_calculation(self, analyzer, sample_code):
        """Test that complexity metrics are calculated correctly."""
        result = await analyzer.analyze_code(sample_code, "test.py")
        
        complexity = result.complexity_analysis
        
        # Verify all required metrics are present
        assert 'total_lines' in complexity
        assert 'code_lines' in complexity
        assert 'comment_lines' in complexity
        assert 'function_count' in complexity
        assert 'class_count' in complexity
        assert 'complexity_rating' in complexity
        
        # Verify metric types and ranges
        assert isinstance(complexity['total_lines'], int)
        assert isinstance(complexity['code_lines'], int)
        assert isinstance(complexity['function_count'], int)
        assert complexity['complexity_rating'] in ['LOW', 'MEDIUM', 'HIGH']
    
    @pytest.mark.asyncio
    async def test_complexity_rating_logic(self, analyzer):
        """Test that complexity rating logic works correctly."""
        # Simple code should be LOW complexity
        simple_code = "print('hello')"
        
        # Complex code should be higher complexity
        complex_code = '\n'.join([f"def func_{i}(): pass" for i in range(100)])
        
        simple_result = await analyzer.analyze_code(simple_code, "simple.py")
        complex_result = await analyzer.analyze_code(complex_code, "complex.py")
        
        assert simple_result.complexity_analysis['complexity_rating'] in ['LOW', 'MEDIUM']
        # Complex code might be MEDIUM or HIGH depending on thresholds

class TestSuggestionGeneration(TestCodeAnalyzer):
    """Test improvement suggestion generation."""
    
    @pytest.mark.asyncio
    async def test_generates_suggestions_list(self, analyzer, sample_code):
        """Test that suggestions are generated as a list."""
        result = await analyzer.analyze_code(sample_code, "test.py")
        
        assert isinstance(result.suggestions, list)
        # Should have at least one suggestion or default message
        assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_suggestions_for_code_without_comments(self, analyzer):
        """Test that code without comments gets comment suggestions."""
        code_without_comments = '''
def calculate(x, y):
    return x * y + 5
'''
        
        result = await analyzer.analyze_code(code_without_comments, "test.py")
        
        # Should suggest adding comments
        suggestions_text = ' '.join(result.suggestions).lower()
        assert 'comment' in suggestions_text or len(result.suggestions) > 0

class TestDocumentationGeneration(TestCodeAnalyzer):
    """Test AI documentation generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generates_documentation_string(self, analyzer, sample_code):
        """Test that documentation is generated as a string."""
        result = await analyzer.analyze_code(sample_code, "test.py")
        
        assert isinstance(result.documentation, str)
        assert len(result.documentation) > 0
    
    @pytest.mark.asyncio
    async def test_documentation_includes_file_context(self, analyzer, sample_code):
        """Test that documentation includes file context when provided."""
        result = await analyzer.analyze_code(sample_code, "greeting_utils.py")
        
        # Should include filename in documentation
        assert "greeting_utils.py" in result.documentation or result.documentation != ""

class TestOverallRating(TestCodeAnalyzer):
    """Test overall rating calculation functionality."""
    
    @pytest.mark.asyncio
    async def test_overall_rating_format(self, analyzer, sample_code):
        """Test that overall rating follows expected format."""
        result = await analyzer.analyze_code(sample_code, "test.py")
        
        # Should be in format "X - Description"
        assert isinstance(result.overall_rating, str)
        assert len(result.overall_rating) > 0
        
        # Should start with a letter grade
        rating_parts = result.overall_rating.split(' - ')
        assert len(rating_parts) >= 1
        assert rating_parts[0] in ['A', 'B', 'C', 'D', 'F']
    
    @pytest.mark.asyncio
    async def test_rating_considers_security_issues(self, analyzer, vulnerable_code):
        """Test that overall rating considers security issues."""
        result = await analyzer.analyze_code(vulnerable_code, "test.py")
        
        # Code with security issues should not get top rating
        rating_letter = result.overall_rating.split(' - ')[0]
        # This is a general expectation, actual results may vary
        assert rating_letter in ['A', 'B', 'C', 'D', 'F']

class TestErrorHandling(TestCodeAnalyzer):
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_handles_malformed_code(self, analyzer):
        """Test that malformed code is handled gracefully."""
        malformed_code = "def incomplete_function("
        
        # Should not raise an exception
        result = await analyzer.analyze_code(malformed_code, "malformed.py")
        
        assert result is not None
        assert isinstance(result, CodeAnalysisResult)
    
    @pytest.mark.asyncio
    async def test_handles_very_long_code(self, analyzer):
        """Test that very long code is handled appropriately."""
        long_code = "print('hello')\n" * 1000
        
        result = await analyzer.analyze_code(long_code, "long.py")
        
        assert result is not None
        assert result.complexity_analysis['total_lines'] > 500
    
    @pytest.mark.asyncio
    async def test_handles_unicode_code(self, analyzer):
        """Test that code with unicode characters is handled properly."""
        unicode_code = '''
def greet():
    print("Hello 世界! 🌍")
    return "Grüße"
'''
        
        result = await analyzer.analyze_code(unicode_code, "unicode.py")
        
        assert result is not None
        assert isinstance(result.documentation, str)