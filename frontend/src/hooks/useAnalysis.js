/**
 * Analysis Custom Hook
 * 
 * Custom React hook for managing code analysis operations including
 * submitting analysis requests, managing state, and handling results.
 * Provides reusable analysis logic across components.
 */

import { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

/**
 * Custom hook for code analysis operations
 * @returns {object} Analysis state and functions
 */
export const useAnalysis = () => {
  const queryClient = useQueryClient();
  const [analysisHistory, setAnalysisHistory] = useState([]);

  /**
   * Mutation for analyzing code
   */
  const analyzeCodeMutation = useMutation(
    apiService.analyzeCode,
    {
      onSuccess: (data, variables) => {
        toast.success('Code analysis completed successfully!');
        
        // Add to local history
        const historyItem = {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          fileName: variables.file_path || 'untitled',
          language: variables.language || 'unknown',
          result: data,
        };
        
        setAnalysisHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10
        
        // Invalidate related queries
        queryClient.invalidateQueries('analysis-stats');
      },
      onError: (error) => {
        const errorMessage = error.response?.data?.detail || error.message || 'Analysis failed';
        toast.error(`Analysis failed: ${errorMessage}`);
        console.error('Analysis error:', error);
      },
    }
  );

  /**
   * Query for analysis statistics
   */
  const { data: analysisStats, isLoading: statsLoading } = useQuery(
    'analysis-stats',
    apiService.getStats,
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  );

  /**
   * Analyze code with validation
   * @param {object} codeData - Code analysis request data
   */
  const analyzeCode = useCallback(async (codeData) => {
    // Validation
    if (!codeData.code_content || !codeData.code_content.trim()) {
      toast.error('Please provide code content to analyze');
      return;
    }

    if (codeData.code_content.length > 100000) {
      toast.error('Code content is too large (max 100KB)');
      return;
    }

    // Submit analysis
    return analyzeCodeMutation.mutateAsync(codeData);
  }, [analyzeCodeMutation]);

  /**
   * Get analysis summary from result
   * @param {object} analysisResult - Analysis result data
   * @returns {object} Summary statistics
   */
  const getAnalysisSummary = useCallback((analysisResult) => {
    if (!analysisResult?.analysis) return null;

    const { analysis } = analysisResult;
    
    return {
      totalIssues: analysis.security_issues?.length || 0,
      highSeverityIssues: analysis.security_issues?.filter(
        issue => issue.severity === 'HIGH'
      ).length || 0,
      qualityScore: analysis.quality_score || 0,
      complexityRating: analysis.complexity?.complexity_rating || 'UNKNOWN',
      overallRating: analysis.overall_rating || 'N/A',
      hasSecurityIssues: (analysis.security_issues?.length || 0) > 0,
      suggestionCount: analysis.suggestions?.length || 0,
    };
  }, []);

  /**
   * Check if analysis result indicates good code quality
   * @param {object} analysisResult - Analysis result data
   * @returns {boolean} True if code quality is good
   */
  const isGoodQuality = useCallback((analysisResult) => {
    const summary = getAnalysisSummary(analysisResult);
    if (!summary) return false;

    return (
      summary.qualityScore >= 80 &&
      summary.highSeverityIssues === 0 &&
      summary.complexityRating !== 'HIGH'
    );
  }, [getAnalysisSummary]);

  /**
   * Get quality recommendations based on analysis
   * @param {object} analysisResult - Analysis result data
   * @returns {array} Array of recommendation objects
   */
  const getQualityRecommendations = useCallback((analysisResult) => {
    const summary = getAnalysisSummary(analysisResult);
    if (!summary) return [];

    const recommendations = [];

    if (summary.highSeverityIssues > 0) {
      recommendations.push({
        type: 'security',
        priority: 'high',
        message: `Address ${summary.highSeverityIssues} high-severity security issue(s)`,
        icon: '🔒',
      });
    }

    if (summary.qualityScore < 70) {
      recommendations.push({
        type: 'quality',
        priority: 'medium',
        message: 'Improve code quality score (currently below 70%)',
        icon: '📊',
      });
    }

    if (summary.complexityRating === 'HIGH') {
      recommendations.push({
        type: 'complexity',
        priority: 'medium',
        message: 'Consider refactoring to reduce code complexity',
        icon: '🔄',
      });
    }

    if (summary.suggestionCount > 0) {
      recommendations.push({
        type: 'suggestions',
        priority: 'low',
        message: `Review ${summary.suggestionCount} improvement suggestion(s)`,
        icon: '💡',
      });
    }

    return recommendations;
  }, [getAnalysisSummary]);

  /**
   * Clear analysis history
   */
  const clearHistory = useCallback(() => {
    setAnalysisHistory([]);
    toast.success('Analysis history cleared');
  }, []);

  /**
   * Export analysis result as JSON
   * @param {object} analysisResult - Analysis result to export
   * @param {string} fileName - File name for export
   */
  const exportAnalysis = useCallback((analysisResult, fileName = 'analysis-result') => {
    try {
      const dataStr = JSON.stringify(analysisResult, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      
      const link = document.createElement('a');
      link.href = URL.createObjectURL(dataBlob);
      link.download = `${fileName}-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      toast.success('Analysis result exported successfully');
    } catch (error) {
      toast.error('Failed to export analysis result');
      console.error('Export error:', error);
    }
  }, []);

  /**
   * Get supported programming languages
   */
  const supportedLanguages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'php', label: 'PHP' },
    { value: 'ruby', label: 'Ruby' },
  ];

  return {
    // State
    isAnalyzing: analyzeCodeMutation.isLoading,
    analysisError: analyzeCodeMutation.error,
    analysisResult: analyzeCodeMutation.data,
    analysisHistory,
    analysisStats,
    statsLoading,
    
    // Functions
    analyzeCode,
    getAnalysisSummary,
    isGoodQuality,
    getQualityRecommendations,
    clearHistory,
    exportAnalysis,
    
    // Configuration
    supportedLanguages,
    
    // Mutation object for advanced usage
    mutation: analyzeCodeMutation,
  };
};

/**
 * Hook for managing bulk analysis operations
 * @returns {object} Bulk analysis state and functions
 */
export const useBulkAnalysis = () => {
  const [files, setFiles] = useState([]);
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [results, setResults] = useState([]);

  const analyzeCodeMutation = useMutation(apiService.analyzeCode);

  /**
   * Add file to bulk analysis queue
   * @param {object} fileData - File data to analyze
   */
  const addFile = useCallback((fileData) => {
    setFiles(prev => [...prev, { ...fileData, id: Date.now() + Math.random() }]);
  }, []);

  /**
   * Remove file from queue
   * @param {string} fileId - File ID to remove
   */
  const removeFile = useCallback((fileId) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  }, []);

  /**
   * Start bulk analysis
   */
  const startBulkAnalysis = useCallback(async () => {
    if (files.length === 0) {
      toast.error('No files to analyze');
      return;
    }

    setCurrentFileIndex(0);
    setResults([]);

    for (let i = 0; i < files.length; i++) {
      setCurrentFileIndex(i);
      
      try {
        const result = await analyzeCodeMutation.mutateAsync(files[i]);
        setResults(prev => [...prev, { file: files[i], result, success: true }]);
      } catch (error) {
        setResults(prev => [...prev, { file: files[i], error, success: false }]);
      }
    }

    toast.success(`Bulk analysis completed! Analyzed ${files.length} files.`);
  }, [files, analyzeCodeMutation]);

  /**
   * Clear all files and results
   */
  const clearAll = useCallback(() => {
    setFiles([]);
    setResults([]);
    setCurrentFileIndex(0);
  }, []);

  return {
    files,
    currentFileIndex,
    results,
    isAnalyzing: analyzeCodeMutation.isLoading,
    addFile,
    removeFile,
    startBulkAnalysis,
    clearAll,
    progress: files.length > 0 ? (currentFileIndex / files.length) * 100 : 0,
  };
};

export default useAnalysis;