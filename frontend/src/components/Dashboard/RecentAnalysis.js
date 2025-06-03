/**
 * RecentAnalysis Component
 * 
 * Displays a list of recent code analysis results with key details.
 * Provides quick access to recent analyses and highlights important metrics.
 * Supports loading state and empty state.
 */

import React from 'react';
import { formatters } from '../../utils/formatters';
import { CheckCircleIcon, ShieldExclamationIcon, ClockIcon } from '@heroicons/react/24/outline';

const RecentAnalysis = ({ analyses = [], isLoading = false }) => {
  // Loading placeholder
  if (isLoading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-500">Loading recent analyses...</p>
      </div>
    );
  }

  // Empty state
  if (!analyses.length) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <p className="text-gray-500">No recent analyses available.</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Analyses</h2>
      <ul className="divide-y divide-gray-200">
        {analyses.map((analysis) => {
          const { id, fileName, result, timestamp } = analysis;
          const quality = result?.analysis?.quality_score || 0;
          const issuesCount = result?.analysis?.security_issues?.length || 0;
          const overallRating = result?.analysis?.overall_rating || 'N/A';

          return (
            <li key={id} className="py-3 flex justify-between items-center">
              <div className="flex flex-col">
                <span className="text-sm font-medium text-gray-900 truncate">{fileName}</span>
                <span className="text-xs text-gray-500">
                  {formatters.formatDateTime(timestamp)}
                </span>
              </div>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-1">
                  <CheckCircleIcon className="h-5 w-5 text-green-500" />
                  <span className="text-sm text-gray-700">
                    {formatters.formatQualityScore(quality).text}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <ShieldExclamationIcon className="h-5 w-5 text-red-500" />
                  <span className="text-sm text-gray-700">{issuesCount}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <ClockIcon className="h-5 w-5 text-gray-400" />
                  <span className="text-sm text-gray-700">{overallRating}</span>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default RecentAnalysis;