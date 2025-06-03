/**
 * StatsCards Component
 * 
 * Displays key metrics in card format for the AI-CodeReview dashboard.
 * Each card shows an icon, label, and value with appropriate styling
 * and responsive grid layout.
 */

import React from 'react';
import {
  ChartBarIcon,
  ShieldCheckIcon,
  ClockIcon,
  CheckCircleIcon,
  TrendingUpIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import { formatters } from '../../utils/formatters';

const StatsCards = ({ stats, isLoading = false }) => {
  // Configuration for each metric card
  const cards = [
    {
      name: 'Total Analyses',
      value: stats?.total_analyses || 0,
      icon: ChartBarIcon,
      color: 'blue',
      description: 'Code analyses completed',
      formatter: formatters.formatNumber,
    },
    {
      name: 'Security Issues Found',
      value: stats?.security_issues_found || 0,
      icon: ShieldCheckIcon,
      color: 'red',
      description: 'Vulnerabilities detected',
      formatter: formatters.formatNumber,
    },
    {
      name: 'Average Quality Score',
      value: stats?.average_quality_score || 0,
      icon: CheckCircleIcon,
      color: 'green',
      description: 'Overall code quality',
      formatter: (value) => formatters.formatPercentage(value, 1),
    },
    {
      name: 'Active Repositories',
      value: stats?.active_repositories || 0,
      icon: TrendingUpIcon,
      color: 'purple',
      description: 'Repositories monitored',
      formatter: formatters.formatNumber,
    },
    {
      name: 'Pull Requests Processed',
      value: stats?.pull_requests_processed || 0,
      icon: UserGroupIcon,
      color: 'indigo',
      description: 'PRs analyzed this month',
      formatter: formatters.formatNumber,
    },
    {
      name: 'System Uptime',
      value: stats?.system_uptime || '99.9%',
      icon: ClockIcon,
      color: 'emerald',
      description: 'Service availability',
      formatter: (value) => value, // Already formatted as string
    },
  ];

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="bg-white overflow-hidden shadow rounded-lg animate-pulse">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="h-6 w-6 bg-gray-300 rounded"></div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div className="h-6 bg-gray-300 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    </div>
  );

  // Get trend indicator based on card type
  const getTrendIndicator = (cardName, currentValue) => {
    // This would typically come from historical data comparison
    const trends = {
      'Total Analyses': { direction: 'up', percentage: 12 },
      'Security Issues Found': { direction: 'down', percentage: 8 },
      'Average Quality Score': { direction: 'up', percentage: 5 },
      'Active Repositories': { direction: 'up', percentage: 15 },
    };

    const trend = trends[cardName];
    if (!trend) return null;

    return (
      <div className={`flex items-center text-xs ${
        trend.direction === 'up' ? 'text-green-600' : 'text-red-600'
      }`}>
        <span className="mr-1">
          {trend.direction === 'up' ? '↗' : '↘'}
        </span>
        {trend.percentage}%
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {cards.map((card) => {
        if (isLoading) {
          return <LoadingSkeleton key={card.name} />;
        }

        const formattedValue = card.formatter(card.value);
        const trendIndicator = getTrendIndicator(card.name, card.value);

        return (
          <div 
            key={card.name} 
            className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200"
          >
            <div className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`p-2 rounded-md bg-${card.color}-50`}>
                      <card.icon
                        className={`h-5 w-5 text-${card.color}-600`}
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                  <div className="ml-4 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {card.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <span className="text-2xl font-semibold text-gray-900">
                          {formattedValue}
                        </span>
                        {trendIndicator && (
                          <span className="ml-2">
                            {trendIndicator}
                          </span>
                        )}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              
              {/* Description text */}
              <div className="mt-3">
                <p className="text-xs text-gray-500">
                  {card.description}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatsCards;