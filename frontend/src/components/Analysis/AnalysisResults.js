/**
 * AnalysisResults Component
 * 
 * Displays comprehensive analysis results from the AI system including
 * security issues, quality metrics, suggestions, and documentation.
 * Provides export functionality and detailed breakdowns.
 */

import React, { useState } from 'react';
import {
  ShieldExclamationIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';
import { formatters } from '../../utils/formatters';
import { useAnalysis } from '../../hooks/useAnalysis';

const AnalysisResults = ({ results }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const { exportAnalysis } = useAnalysis();

  // Extract data from results
  const { analysis, summary } = results;
  
  // Get formatted values for display
  const qualityFormatted = formatters.formatQualityScore(analysis.quality_score);
  const ratingFormatted = formatters.formatOverallRating(analysis.overall_rating);
  const complexityFormatted = formatters.formatComplexity(analysis.complexity?.complexity_rating);

  // Handle export functionality
  const handleExport = () => {
    const fileName = results.file_path || 'analysis-result';
    exportAnalysis(results, fileName);
  };

  // Tab configuration
  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'security', name: 'Security', icon: ShieldExclamationIcon },
    { id: 'suggestions', name: 'Suggestions', icon: ExclamationTriangleIcon },
    { id: 'documentation', name: 'Documentation', icon: DocumentTextIcon },
  ];

  return (
    <div className="space-y-6">
      {/* Results header with export */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Analysis Results</h3>
              <p className="mt-1 text-sm text-gray-500">
                {results.file_path && `File: ${results.file_path}`}
              </p>
            </div>
            <button
              onClick={handleExport}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
              Export
            </button>
          </div>
        </div>

        {/* Overall summary cards */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${ratingFormatted.colorClass} bg-opacity-10`}>
                {ratingFormatted.grade}
              </div>
              <p className="mt-2 text-xs text-gray-500">Overall Rating</p>
              <p className="text-xs text-gray-400">{ratingFormatted.description}</p>
            </div>
            
            <div className="text-center">
              <div className={`text-2xl font-bold ${qualityFormatted.colorClass}`}>
                {qualityFormatted.text}
              </div>
              <p className="text-xs text-gray-500">Quality Score</p>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {summary.total_issues}
              </div>
              <p className="text-xs text-gray-500">Issues Found</p>
            </div>
            
            <div className="text-center">
              <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${complexityFormatted.badgeClass}`}>
                {complexityFormatted.text}
              </div>
              <p className="mt-1 text-xs text-gray-500">Complexity</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabbed content */}
      <div className="bg-white shadow rounded-lg">
        {/* Tab navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">Analysis Summary</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Quality metrics */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-3">Quality Metrics</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Overall Score:</span>
                        <span className={`text-sm font-medium ${qualityFormatted.colorClass}`}>
                          {qualityFormatted.text}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Security Issues:</span>
                        <span className="text-sm font-medium text-gray-900">
                          {summary.total_issues}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Risk Level:</span>
                        <span className="text-sm font-medium text-gray-900">
                          {summary.security_risk_level}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Complexity metrics */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-3">Code Complexity</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Total Lines:</span>
                        <span className="text-sm font-medium text-gray-900">
                          {analysis.complexity?.total_lines || 0}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Code Lines:</span>
                        <span className="text-sm font-medium text-gray-900">
                          {analysis.complexity?.code_lines || 0}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Functions:</span>
                        <span className="text-sm font-medium text-gray-900">
                          {analysis.complexity?.function_count || 0}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendation */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h5 className="font-medium text-blue-900 mb-2">Recommendation</h5>
                <p className="text-sm text-blue-800">{summary.recommendation}</p>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Security Analysis</h4>
              
              {analysis.security_issues.length > 0 ? (
                <div className="space-y-4">
                  {analysis.security_issues.map((issue, index) => {
                    const severityFormatted = formatters.formatSeverity(issue.severity);
                    
                    return (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="text-sm font-medium text-gray-900">{issue.type}</h5>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityFormatted.badgeClass}`}>
                            {severityFormatted.text}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{issue.description}</p>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Confidence: {(issue.confidence * 100).toFixed(1)}%</span>
                          {issue.line_number && (
                            <span>Line: {issue.line_number}</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h5 className="text-lg font-medium text-gray-900 mb-2">No Security Issues Found</h5>
                  <p className="text-gray-500">Your code passed all security checks!</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'suggestions' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Improvement Suggestions</h4>
              
              {analysis.suggestions.length > 0 ? (
                <ul className="space-y-3">
                  {analysis.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start">
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      </div>
                      <p className="ml-3 text-sm text-gray-700">{suggestion}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-center py-8">
                  <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h5 className="text-lg font-medium text-gray-900 mb-2">No Suggestions</h5>
                  <p className="text-gray-500">Your code looks great as is!</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'documentation' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">AI-Generated Documentation</h4>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                  {analysis.documentation || 'No documentation generated.'}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;