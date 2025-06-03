/**
 * Dashboard Page Component
 * 
 * Main dashboard that provides an overview of the AI-CodeReview system.
 * Displays key metrics, recent activity, and visual analytics to give
 * users a quick understanding of their code analysis status and trends.
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon, 
  ShieldCheckIcon, 
  ClockIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

// Import dashboard components
import StatsCards from '../components/Dashboard/StatsCards';
import QualityChart from '../components/Dashboard/QualityChart';
import SecurityChart from '../components/Dashboard/SecurityChart';
import RecentAnalysis from '../components/Dashboard/RecentAnalysis';

// Import services and utilities
import { apiService } from '../services/api';
import { useAnalysis } from '../hooks/useAnalysis';
import { formatters } from '../utils/formatters';

const Dashboard = () => {
  // State for managing dashboard data refresh
  const [refreshKey, setRefreshKey] = useState(0);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Get analysis history from custom hook
  const { analysisHistory, analysisStats } = useAnalysis();

  // Fetch system statistics with auto-refresh
  const { 
    data: systemStats, 
    isLoading: statsLoading, 
    error: statsError,
    refetch: refetchStats 
  } = useQuery(
    ['dashboard-stats', refreshKey, selectedTimeRange],
    () => apiService.getStats({ timeRange: selectedTimeRange }),
    {
      staleTime: 2 * 60 * 1000, // Consider data fresh for 2 minutes
      cacheTime: 5 * 60 * 1000, // Keep in cache for 5 minutes
      refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
      refetchOnWindowFocus: true, // Refresh when user returns to tab
    }
  );

  // Fetch recent analyses for the activity feed
  const { 
    data: recentAnalyses, 
    isLoading: analysesLoading 
  } = useQuery(
    ['recent-analyses', refreshKey],
    () => apiService.getAnalysisHistory({ limit: 10, sortBy: 'created_at' }),
    {
      staleTime: 1 * 60 * 1000, // Fresh for 1 minute
      refetchInterval: 60 * 1000, // Refresh every minute
    }
  );

  // Set up auto-refresh interval for real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1);
    }, 5 * 60 * 1000); // Refresh every 5 minutes

    return () => clearInterval(interval);
  }, []);

  // Handle manual refresh of dashboard data
  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    refetchStats();
  };

  // Time range options for filtering data
  const timeRangeOptions = [
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
  ];

  // Prepare data for charts
  const chartData = React.useMemo(() => {
    if (!systemStats?.data) return { quality: [], security: {} };

    return {
      quality: systemStats.data.quality_trends || [],
      security: {
        highCount: systemStats.data.security_issues_high || 0,
        mediumCount: systemStats.data.security_issues_medium || 0,
        lowCount: systemStats.data.security_issues_low || 0,
      }
    };
  }, [systemStats]);

  // Calculate dashboard insights
  const insights = React.useMemo(() => {
    if (!systemStats?.data) return [];

    const stats = systemStats.data;
    const insights = [];

    // Quality trend insight
    if (stats.quality_trend_direction === 'up') {
      insights.push({
        type: 'positive',
        icon: ChartBarIcon,
        message: `Code quality improved by ${stats.quality_trend_percentage}% this week`,
      });
    } else if (stats.quality_trend_direction === 'down') {
      insights.push({
        type: 'warning',
        icon: ExclamationTriangleIcon,
        message: `Code quality decreased by ${stats.quality_trend_percentage}% this week`,
      });
    }

    // Security insight
    if (stats.security_issues_found === 0) {
      insights.push({
        type: 'positive',
        icon: ShieldCheckIcon,
        message: 'No security issues found in recent analyses',
      });
    } else if (stats.security_issues_high > 0) {
      insights.push({
        type: 'critical',
        icon: ShieldCheckIcon,
        message: `${stats.security_issues_high} high-severity security issues need attention`,
      });
    }

    // Activity insight
    if (stats.analyses_today > stats.analyses_yesterday) {
      insights.push({
        type: 'info',
        icon: ClockIcon,
        message: `${stats.analyses_today} analyses completed today`,
      });
    }

    return insights;
  }, [systemStats]);

  // Error state
  if (statsError) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-medium text-gray-900 mb-2">
            Unable to Load Dashboard
          </h2>
          <p className="text-gray-500 mb-4">
            There was an error loading the dashboard data.
          </p>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Overview of your AI-powered code analysis system
          </p>
        </div>
        
        {/* Dashboard Controls */}
        <div className="flex items-center space-x-4">
          {/* Time Range Selector */}
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="block w-40 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            {timeRangeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          
          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      {/* Key Insights Banner */}
      {insights.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Key Insights</h3>
          <div className="space-y-2">
            {insights.map((insight, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className={`p-1 rounded-full ${
                  insight.type === 'positive' ? 'bg-green-100' :
                  insight.type === 'warning' ? 'bg-yellow-100' :
                  insight.type === 'critical' ? 'bg-red-100' : 'bg-blue-100'
                }`}>
                  <insight.icon className={`h-4 w-4 ${
                    insight.type === 'positive' ? 'text-green-600' :
                    insight.type === 'warning' ? 'text-yellow-600' :
                    insight.type === 'critical' ? 'text-red-600' : 'text-blue-600'
                  }`} />
                </div>
                <span className="text-sm text-gray-700">{insight.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics Cards */}
      <StatsCards 
        stats={systemStats?.data} 
        isLoading={statsLoading} 
      />

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Trends Chart */}
        <QualityChart 
          dataPoints={chartData.quality.map(point => point.score)}
          labels={chartData.quality.map(point => formatters.formatDate(point.date, 'MMM dd'))}
        />
        
        {/* Security Issues Chart */}
        <SecurityChart 
          highCount={chartData.security.highCount}
          mediumCount={chartData.security.mediumCount}
          lowCount={chartData.security.lowCount}
        />
      </div>

      {/* Recent Activity Section */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Recent Analyses */}
        <div className="xl:col-span-2">
          <RecentAnalysis 
            analyses={recentAnalyses?.data?.results || analysisHistory}
            isLoading={analysesLoading}
          />
        </div>
        
        {/* Quick Actions Panel */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <a
              href="/analysis"
              className="block w-full px-4 py-2 text-center text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
            >
              Analyze New Code
            </a>
            
            <a
              href="/repositories"
              className="block w-full px-4 py-2 text-center text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
            >
              Manage Repositories
            </a>
            
            <a
              href="/analysis?tab=history"
              className="block w-full px-4 py-2 text-center text-sm font-medium text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
            >
              View Analysis History
            </a>
          </div>
          
          {/* System Status */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">System Status</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">API Status</span>
                <span className="flex items-center text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Online
                </span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">AI Models</span>
                <span className="flex items-center text-green-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Ready
                </span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Last Updated</span>
                <span className="text-gray-500">
                  {formatters.formatRelativeTime(new Date())}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;