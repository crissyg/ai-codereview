/**
 * AnalysisHistory Component
 * 
 * Displays a paginated list of previous code analyses with filtering
 * and search capabilities. Allows users to view past results and
 * track analysis trends over time.
 */

import React, { useState, useMemo } from 'react';
import { useQuery } from 'react-query';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  TrashIcon,
  EyeIcon,
  CalendarIcon 
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import { formatters } from '../../utils/formatters';
import { useAnalysis } from '../../hooks/useAnalysis';

const AnalysisHistory = () => {
  // State for filtering and pagination
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  const [selectedRating, setSelectedRating] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  const { analysisHistory, clearHistory } = useAnalysis();

  // Fetch analysis history from API
  const { data: historyData, isLoading, error } = useQuery(
    ['analysis-history', currentPage],
    () => apiService.getAnalysisHistory({ page: currentPage, limit: 20 }),
    {
      keepPreviousData: true,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Combine local and remote history
  const allHistory = useMemo(() => {
    const remoteHistory = historyData?.data?.results || [];
    return [...analysisHistory, ...remoteHistory];
  }, [analysisHistory, historyData]);

  // Filter history based on search and filters
  const filteredHistory = useMemo(() => {
    return allHistory.filter((item) => {
      const matchesSearch = !searchTerm || 
        item.fileName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.language.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesLanguage = selectedLanguage === 'all' || 
        item.language === selectedLanguage;

      const matchesRating = selectedRating === 'all' || 
        item.result?.analysis?.overall_rating?.startsWith(selectedRating);

      return matchesSearch && matchesLanguage && matchesRating;
    });
  }, [allHistory, searchTerm, selectedLanguage, selectedRating]);

  // Get unique languages for filter dropdown
  const availableLanguages = useMemo(() => {
    const languages = [...new Set(allHistory.map(item => item.language))];
    return languages.sort();
  }, [allHistory]);

  // Handle viewing analysis details
  const handleViewAnalysis = (analysis) => {
    setSelectedAnalysis(analysis);
  };

  // Handle clearing all history
  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all analysis history?')) {
      clearHistory();
    }
  };

  // Loading state
  if (isLoading && !historyData) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-300 rounded w-1/4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading History</h3>
          <p className="text-gray-500">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with search and filters */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Analysis History</h3>
              <p className="mt-1 text-sm text-gray-500">
                {filteredHistory.length} analyses found
              </p>
            </div>
            
            {allHistory.length > 0 && (
              <button
                onClick={handleClearHistory}
                className="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <TrashIcon className="h-4 w-4 mr-2" />
                Clear History
              </button>
            )}
          </div>
        </div>

        {/* Search and filters */}
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search input */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by filename or language..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Language filter */}
            <div>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Languages</option>
                {availableLanguages.map((lang) => (
                  <option key={lang} value={lang}>
                    {formatters.formatLanguage(lang)}
                  </option>
                ))}
              </select>
            </div>

            {/* Rating filter */}
            <div>
              <select
                value={selectedRating}
                onChange={(e) => setSelectedRating(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md leading-5 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Ratings</option>
                <option value="A">A - Excellent</option>
                <option value="B">B - Good</option>
                <option value="C">C - Average</option>
                <option value="D">D - Needs Improvement</option>
                <option value="F">F - Major Issues</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* History list */}
      <div className="bg-white shadow rounded-lg">
        {filteredHistory.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {filteredHistory.map((analysis) => {
              const qualityScore = analysis.result?.analysis?.quality_score || 0;
              const securityIssues = analysis.result?.analysis?.security_issues?.length || 0;
              const overallRating = analysis.result?.analysis?.overall_rating || 'N/A';
              const qualityFormatted = formatters.formatQualityScore(qualityScore);
              const ratingFormatted = formatters.formatOverallRating(overallRating);

              return (
                <li key={analysis.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <CalendarIcon className="h-5 w-5 text-gray-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {analysis.fileName}
                          </p>
                          <p className="text-sm text-gray-500">
                            {formatters.formatLanguage(analysis.language)} • {' '}
                            {formatters.formatRelativeTime(analysis.timestamp)}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Analysis metrics */}
                    <div className="flex items-center space-x-6">
                      <div className="text-center">
                        <div className={`text-sm font-medium ${qualityFormatted.colorClass}`}>
                          {qualityFormatted.text}
                        </div>
                        <div className="text-xs text-gray-500">Quality</div>
                      </div>

                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {securityIssues}
                        </div>
                        <div className="text-xs text-gray-500">Issues</div>
                      </div>

                      <div className="text-center">
                        <div className={`text-sm font-medium ${ratingFormatted.colorClass}`}>
                          {ratingFormatted.grade}
                        </div>
                        <div className="text-xs text-gray-500">Rating</div>
                      </div>

                      <button
                        onClick={() => handleViewAnalysis(analysis)}
                        className="inline-flex items-center p-2 border border-transparent rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <div className="text-center py-12">
            <CalendarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis History</h3>
            <p className="text-gray-500">
              {searchTerm || selectedLanguage !== 'all' || selectedRating !== 'all'
                ? 'No analyses match your current filters.'
                : 'Start analyzing code to see your history here.'}
            </p>
          </div>
        )}
      </div>

      {/* Analysis details modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Analysis Details: {selectedAnalysis.fileName}
                  </h3>
                  <button
                    onClick={() => setSelectedAnalysis(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                {/* Display analysis results */}
                <div className="max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(selectedAnalysis.result, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisHistory;