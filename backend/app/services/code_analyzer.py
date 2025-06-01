"""
Code Analysis Service - The Brain of the AI System

This service coordinates multiple AI models to analyze code as a team of expert reviewers:
- Security Expert: Finds vulnerabilities
- Documentation Writer: Generates explanations
- Code Reviewer: Suggests improvements
- Q&A Assistant: Answers questions about the code
"""

from transformers import pipeline, AutoTokenizer, AutoModel
import asyncio
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)

@dataclass
class CodeAnalysisResult:
    """
    Container for storing the results of AI analysis.
    
    This serves as a comprehensive report card for a piece of code, containing
    all the insights the AI models discovered during analysis.
    """
    security_issues: List[Dict[str, Any]]
    quality_score: float
    suggestions: List[str]
    documentation: str
    complexity_analysis: Dict[str, Any]
    overall_rating: str

class AIModelManager:
    """
    Manages all AI models - acts as a team manager for AI assistants.
    
    Each model has a specific expertise:
    - Classifier: Categorizes code issues
    - Generator: Creates documentation
    - Q&A: Answers questions about code
    - Security Scanner: Finds vulnerabilities
    """
    
    def __init__(self):
        """Initialize all AI models when the system starts."""
        logger.info("Loading AI models... This may take a moment.")
        
        try:
            # Model 1: Text Classification - Categorizes code issues
            self.classifier = pipeline(
                'text-classification',
                model='microsoft/codebert-base',
                return_all_scores=True
            )
            
            # Model 2: Text Generation - Creates documentation
            self.generator = pipeline(
                'text-generation',
                model='microsoft/DialoGPT-medium',
                max_length=150,
                num_return_sequences=1
            )
            
            # Model 3: Question Answering - Answers code-related questions
            self.qa_model = pipeline(
                'question-answering',
                model='deepset/roberta-base-squad2'
            )
            
            # Model 4: Security Analysis - Custom model for vulnerability detection
            self.security_classifier = pipeline(
                'text-classification',
                model='huggingface/CodeBERTa-small-v1'
            )
            
            # Model 5: Code Completion - Suggests improvements
            self.code_completer = pipeline(
                'fill-mask',
                model='microsoft/codebert-base-mlm'
            )
            
            logger.info("All AI models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            raise

class CodeAnalyzer:
    """
    Main code analysis orchestrator.
    
    This class acts as a project manager - it takes a piece of code,
    sends it to different AI specialists, and combines their insights
    into a comprehensive analysis report.
    """
    
    def __init__(self):
        """Initialize the code analyzer with AI models."""
        self.model_manager = AIModelManager()
        self.analysis_cache = {}  # Cache results to improve performance
        
    async def analyze_code(self, code_content: str, file_path: str = "") -> CodeAnalysisResult:
        """
        Perform comprehensive AI analysis on a piece of code.
        
        Args:
            code_content: The actual code to analyze
            file_path: Path to the file (helps with context)
            
        Returns:
            Detailed analysis results from all AI models
        """
        logger.info(f"Starting analysis for file: {file_path}")
        
        try:
            # Run different types of analysis concurrently for speed
            analysis_tasks = [
                self._analyze_security(code_content),
                self._analyze_quality(code_content),
                self._generate_documentation(code_content, file_path),
                self._analyze_complexity(code_content),
                self._generate_suggestions(code_content)
            ]
            
            # Wait for all analyses to complete
            results = await asyncio.gather(*analysis_tasks)
            
            # Combine all results into a comprehensive report
            analysis_result = CodeAnalysisResult(
                security_issues=results[0],
                quality_score=results[1],
                documentation=results[2],
                complexity_analysis=results[3],
                suggestions=results[4],
                overall_rating=self._calculate_overall_rating(results)
            )
            
            logger.info(f"Analysis completed for {file_path}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {e}")
            raise
    
    async def _analyze_security(self, code_content: str) -> List[Dict[str, Any]]:
        """
        Uses AI to scan for security vulnerabilities.
        
        Functions as a security expert reviewing the code for potential threats.
        """
        security_issues = []
        
        # Common security patterns to check
        security_patterns = [
            "SQL injection vulnerabilities",
            "Cross-site scripting (XSS) risks",
            "Authentication bypasses",
            "Data exposure risks"
        ]
        
        for pattern in security_patterns:
            try:
                # Ask the AI if this security issue exists in the code
                result = self.model_manager.security_classifier(
                    f"Does this code have {pattern}? Code: {code_content[:500]}"
                )
                
                # If AI detects a security issue, record it
                if result[0]['label'] == 'POSITIVE' and result[0]['score'] > 0.7:
                    security_issues.append({
                        'type': pattern,
                        'severity': 'HIGH' if result[0]['score'] > 0.9 else 'MEDIUM',
                        'confidence': result[0]['score'],
                        'description': f"Potential {pattern} detected"
                    })
                    
            except Exception as e:
                logger.warning(f"Security analysis failed for pattern {pattern}: {e}")
        
        return security_issues
    
    async def _analyze_quality(self, code_content: str) -> float:
        """
        Calculates a quality score for the code.
        
        Functions as a code reviewer giving the code a grade from 0-100.
        """
        try:
            # Use AI to classify code quality
            quality_result = self.model_manager.classifier(
                f"Rate the quality of this code: {code_content[:300]}"
            )
            
            # Convert AI confidence to a quality score
            base_score = quality_result[0]['score'] * 100
            
            # Adjust score based on code characteristics
            lines = code_content.split('\n')
            
            # Bonus points for good practices
            if any('def ' in line for line in lines):  # Has functions
                base_score += 5
            if any('#' in line for line in lines):     # Has comments
                base_score += 5
            if len(lines) < 100:                       # Not too long
                base_score += 5
                
            return min(base_score, 100.0)  # Cap at 100
            
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return 50.0  # Default neutral score
    
    async def _generate_documentation(self, code_content: str, file_path: str) -> str:
        """
        Generate human-readable documentation for the code.
        
        Functions as a technical writer explaining what the code does in plain English.
        """
        try:
            # Create a prompt for the AI to generate documentation
            prompt = f"Explain what this code does in simple terms: {code_content[:200]}"
            
            # Generate documentation using AI
            doc_result = self.model_manager.generator(prompt)
            generated_text = doc_result[0]['generated_text']
            
            # Clean up the generated text
            documentation = generated_text.replace(prompt, "").strip()
            
            # Add file context if available
            if file_path:
                file_name = file_path.split('/')[-1]
                documentation = f"File: {file_name}\n\n{documentation}"
            
            return documentation
            
        except Exception as e:
            logger.warning(f"Documentation generation failed: {e}")
            return "Documentation could not be generated automatically."
    
    async def _analyze_complexity(self, code_content: str) -> Dict[str, Any]:
        """
        Analyze code complexity metrics.
        
        Measures how difficult the code is to understand and maintain.
        """
        lines = code_content.split('\n')
        
        # Calculate basic complexity metrics
        complexity_metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'function_count': len(re.findall(r'def\s+\w+', code_content)),
            'class_count': len(re.findall(r'class\s+\w+', code_content)),
            'complexity_rating': 'LOW'  # Default rating
        }
        
        # Determine complexity rating
        if complexity_metrics['code_lines'] > 200:
            complexity_metrics['complexity_rating'] = 'HIGH'
        elif complexity_metrics['code_lines'] > 100:
            complexity_metrics['complexity_rating'] = 'MEDIUM'
        
        return complexity_metrics
    
    async def _generate_suggestions(self, code_content: str) -> List[str]:
        """
        Generate improvement suggestions for the code.
        
        Functions as a senior developer mentor providing helpful tips.
        """
        suggestions = []
        
        # Basic rule-based suggestions
        lines = code_content.split('\n')
        
        if not any('#' in line for line in lines):
            suggestions.append("Consider adding comments to explain complex logic")
        
        if any(len(line) > 120 for line in lines):
            suggestions.append("Some lines are very long - consider breaking them up for readability")
        
        if 'TODO' in code_content or 'FIXME' in code_content:
            suggestions.append("There are TODO/FIXME comments that should be addressed")
        
        # Add AI-generated suggestions
        try:
            # Use AI to suggest improvements
            prompt = f"Suggest improvements for this code: {code_content[:200]}"
            ai_suggestions = self.model_manager.generator(prompt)
            
            if ai_suggestions:
                suggestions.append("AI Suggestion: " + ai_suggestions[0]['generated_text'][:100])
                
        except Exception as e:
            logger.warning(f"AI suggestion generation failed: {e}")
        
        return suggestions if suggestions else ["Code looks good! No major issues found."]
    
    def _calculate_overall_rating(self, analysis_results: List) -> str:
        """
        Calculate an overall rating based on all analysis results.
        
        Provides the code with an overall grade: A, B, C, D, or F.
        """
        security_issues, quality_score, _, complexity_analysis, suggestions = analysis_results
        
        # Start with quality score
        total_score = quality_score
        
        # Deduct points for security issues
        high_severity_issues = len([issue for issue in security_issues if issue.get('severity') == 'HIGH'])
        total_score -= (high_severity_issues * 20)
        
        # Deduct points for high complexity
        if complexity_analysis.get('complexity_rating') == 'HIGH':
            total_score -= 15
        elif complexity_analysis.get('complexity_rating') == 'MEDIUM':
            total_score -= 5
        
        # Convert to letter grade
        if total_score >= 90:
            return "A - Excellent"
        elif total_score >= 80:
            return "B - Good"
        elif total_score >= 70:
            return "C - Average"
        elif total_score >= 60:
            return "D - Needs Improvement"
        else:
            return "F - Major Issues Found"
