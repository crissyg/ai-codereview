/**
 * Analysis Page Component
 * 
 * Main page for code analysis functionality. Provides a tabbed interface
 * for analyzing new code and viewing analysis history. Integrates with
 * the CodeAnalyzer and AnalysisHistory components.
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  BeakerIcon, 
  ClockIcon,
  ChartBarIcon,
  DocumentTextIcon 
} from '@heroicons/react/24/outline';

// Import analysis components
import CodeAnalyzer from '../components/Analysis/CodeAnalyzer';
import AnalysisHistory from '../components/Analysis/AnalysisHistory';

// Import hooks and utilities
import { useAnalysis } from '../hooks/useAnalysis';
import { formatters } from '../utils/formatters';

const Analysis = () => {
  // Get URL search parameters for deep linking to specific tabs
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') || 'analyzer';
  
  // State for active tab management
  const [activeTab, setActiveTab] = useState(initialTab);
  
  // Get analysis data from custom hook
  const { 
    analysisHistory, 
    isAnalyzing, 
    analysisStats,
    supportedLanguages 
  } = useAnalysis();

  // Update URL when tab changes for better UX and bookmarking
  useEffect(() => {
    setSearchParams({ tab: activeTab });
  }, [activeTab, setSearchParams]);

  // Tab configuration with icons and descriptions
  const tabs = [
    { 
      id: 'analyzer', 
      name: 'Code Analyzer', 
      icon: BeakerIcon,
      description: 'Analyze new code for quality and security issues'
    },
    { 
      id: 'history', 
      name: 'Analysis History', 
      icon: ClockIcon,
      description: 'View past analysis results and trends'
    },
    { 
      id: 'bulk', 
      name: 'Bulk Analysis', 
      icon: ChartBarIcon,
      description: 'Analyze multiple files at once'
    },
    { 
      id: 'reports', 
      name: 'Reports', 
      icon: DocumentTextIcon,
      description: 'Generate and export analysis reports'
    },
  ];

  // Get the active tab component
  const getActiveComponent = () => {
    switch (activeTab) {
      case 'analyzer':
        return <CodeAnalyzer />;
      case 'history':
        return <AnalysisHistory />;
      case 'bulk':
        return <BulkAnalysisComponent />;
      case 'reports':
        return <ReportsComponent />;
      default:
        return <CodeAnalyzer />;
    }
  };

  // Calculate quick stats for the header
  const quickStats = React.useMemo(() => {
    return {
      totalAnalyses: analysisHistory.length,
      recentAnalyses: analysisHistory.filter(
        analysis => new Date(analysis.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
      ).length,
      averageQuality: analysisHistory.length > 0 
        ? analysisHistory.reduce((sum, analysis) => 
            sum + (analysis.result?.analysis?.quality_score || 0), 0
          ) / analysisHistory.length
        : 0,
    };
  }, [analysisHistory]);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Code Analysis</h1>
              <p className="mt-1 text-sm text-gray-500">
                AI-powered code review and security analysis
              </p>
            </div>
            
            {/* Quick Stats */}
            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {formatters.formatNumber(quickStats.totalAnalyses)}
                </div>
                <div className="text-xs text-gray-500">Total Analyses</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatters.formatNumber(quickStats.recentAnalyses)}
                </div>
                <div className="text-xs text-gray-500">Today</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {formatters.formatPercentage(quickStats.averageQuality, 1)}
                </div>
                <div className="text-xs text-gray-500">Avg Quality</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
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
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors duration-200`}
                title={tab.description}
              >
                <tab.icon className="h-4 w-4 mr-2" />
                {tab.name}
                
                {/* Show loading indicator on analyzer tab when analyzing */}
                {tab.id === 'analyzer' && isAnalyzing && (
                  <div className="ml-2">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                  </div>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Description */}
        <div className="px-6 py-3 bg-gray-50">
          <p className="text-sm text-gray-600">
            {tabs.find(tab => tab.id === activeTab)?.description}
          </p>
        </div>
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {getActiveComponent()}
      </div>

      {/* Analysis Tips */}
      {activeTab === 'analyzer' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-4">Analysis Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Supported Languages</h4>
              <div className="flex flex-wrap gap-2">
                {supportedLanguages.slice(0, 6).map((lang) => (
                  <span 
                    key={lang.value}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {lang.label}
                  </span>
                ))}
                {supportedLanguages.length > 6 && (
                  <span className="text-xs text-blue-600">
                    +{supportedLanguages.length - 6} more
                  </span>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Best Practices</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Include complete functions for better analysis</li>
                <li>• Add comments to help AI understand context</li>
                <li>• Keep file size under 100KB for optimal performance</li>
                <li>• Use descriptive variable and function names</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Placeholder components for additional tabs
const BulkAnalysisComponent = () => (
  <div className="bg-white shadow rounded-lg p-6">
    <div className="text-center py-12">
      <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Bulk Analysis</h3>
      <p className="text-gray-500 mb-4">
        Analyze multiple files simultaneously for comprehensive project review.
      </p>
      <p className="text-sm text-gray-400">Coming soon...</p>
    </div>
  </div>
);

const ReportsComponent = () => (
  <div className="bg-white shadow rounded-lg p-6">
    <div className="text-center py-12">
      <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Analysis Reports</h3>
      <p className="text-gray-500 mb-4">
        Generate detailed reports and export analysis data for documentation.
      </p>
      <p className="text-sm text-gray-400">Coming soon...</p>
    </div>
  </div>
);

export default Analysis;