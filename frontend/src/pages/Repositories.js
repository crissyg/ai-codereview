/**
 * Repositories Page Component
 * 
 * Repository management interface for configuring GitHub repositories
 * for automated code analysis. Provides functionality to add, configure,
 * and monitor repositories with their analysis status and metrics.
 */

import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  PlusIcon, 
  FolderIcon,
  ChartBarIcon,
  Cog6ToothIcon 
} from '@heroicons/react/24/outline';

// Import repository components
import RepositoryList from '../components/Repository/RepositoryList';
import RepositoryConfig from '../components/Repository/RepositoryConfig';

// Import services and utilities
import { apiService } from '../services/api';
import { formatters } from '../utils/formatters';

const Repositories = () => {
  // State for managing UI flow
  const [currentView, setCurrentView] = useState('list'); // 'list', 'add', 'configure'
  const [selectedRepository, setSelectedRepository] = useState(null);

  // Fetch repositories and statistics
  const { data: repositories, isLoading: repositoriesLoading } = useQuery(
    'repositories',
    apiService.getRepositories,
    {
      staleTime: 2 * 60 * 1000, // 2 minutes
      refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
    }
  );

  // Fetch repository statistics for overview
  const { data: repoStats } = useQuery(
    'repository-stats',
    () => apiService.getStats({ type: 'repositories' }),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Calculate overview metrics
  const overviewMetrics = React.useMemo(() => {
    const repoList = repositories?.data || [];
    
    return {
      totalRepositories: repoList.length,
      activeRepositories: repoList.filter(repo => repo.status === 'active').length,
      totalAnalyses: repoList.reduce((sum, repo) => sum + (repo.total_analyses || 0), 0),
      repositoriesWithWebhooks: repoList.filter(repo => repo.webhook_url).length,
      averageQuality: repoStats?.data?.average_quality_score || 0,
      recentActivity: repoList.filter(repo => {
        if (!repo.last_analysis_at) return false;
        const lastAnalysis = new Date(repo.last_analysis_at);
        const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
        return lastAnalysis > yesterday;
      }).length,
    };
  }, [repositories, repoStats]);

  // Handle navigation between views
  const handleAddRepository = () => {
    setSelectedRepository(null);
    setCurrentView('add');
  };

  const handleConfigureRepository = (repository) => {
    setSelectedRepository(repository);
    setCurrentView('configure');
  };

  const handleBackToList = () => {
    setSelectedRepository(null);
    setCurrentView('list');
  };

  const handleSaveComplete = () => {
    setCurrentView('list');
    setSelectedRepository(null);
  };

  // Render the appropriate view based on current state
  const renderCurrentView = () => {
    switch (currentView) {
      case 'add':
        return (
          <RepositoryConfig
            repository={null}
            onSave={handleSaveComplete}
            onCancel={handleBackToList}
          />
        );
      
      case 'configure':
        return (
          <RepositoryConfig
            repository={selectedRepository}
            onSave={handleSaveComplete}
            onCancel={handleBackToList}
          />
        );
      
      case 'list':
      default:
        return (
          <RepositoryList
            onAddRepository={handleAddRepository}
            onConfigureRepository={handleConfigureRepository}
          />
        );
    }
  };

  // Get page title based on current view
  const getPageTitle = () => {
    switch (currentView) {
      case 'add':
        return 'Add Repository';
      case 'configure':
        return `Configure ${selectedRepository?.full_name || 'Repository'}`;
      default:
        return 'Repositories';
    }
  };

  // Get page description based on current view
  const getPageDescription = () => {
    switch (currentView) {
      case 'add':
        return 'Add a new GitHub repository for automated code analysis';
      case 'configure':
        return 'Configure repository settings and analysis preferences';
      default:
        return 'Manage GitHub repositories for automated code analysis';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-2">
            {currentView !== 'list' && (
              <button
                onClick={handleBackToList}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}
            <h1 className="text-2xl font-bold text-gray-900">{getPageTitle()}</h1>
          </div>
          <p className="mt-1 text-sm text-gray-500">{getPageDescription()}</p>
        </div>

        {/* Quick Actions */}
        {currentView === 'list' && (
          <div className="flex items-center space-x-3">
            <button
              onClick={handleAddRepository}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Repository
            </button>
          </div>
        )}
      </div>

      {/* Overview Metrics - Only show on list view */}
      {currentView === 'list' && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Repository Overview</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {formatters.formatNumber(overviewMetrics.totalRepositories)}
                </div>
                <div className="text-xs text-gray-500">Total Repos</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatters.formatNumber(overviewMetrics.activeRepositories)}
                </div>
                <div className="text-xs text-gray-500">Active</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {formatters.formatNumber(overviewMetrics.totalAnalyses)}
                </div>
                <div className="text-xs text-gray-500">Total Analyses</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {formatters.formatNumber(overviewMetrics.repositoriesWithWebhooks)}
                </div>
                <div className="text-xs text-gray-500">With Webhooks</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {formatters.formatPercentage(overviewMetrics.averageQuality, 1)}
                </div>
                <div className="text-xs text-gray-500">Avg Quality</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-600">
                  {formatters.formatNumber(overviewMetrics.recentActivity)}
                </div>
                <div className="text-xs text-gray-500">Active Today</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="min-h-96">
        {renderCurrentView()}
      </div>

      {/* Help Section - Only show on list view when no repositories */}
      {currentView === 'list' && overviewMetrics.totalRepositories === 0 && !repositoriesLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <FolderIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-blue-900">Get Started with Repository Analysis</h3>
              <div className="mt-2 text-sm text-blue-800">
                <p className="mb-4">
                  Connect your GitHub repositories to enable automated code analysis on every pull request.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <ChartBarIcon className="h-4 w-4 mr-2" />
                    <span>Automatic analysis on pull requests</span>
                  </div>
                  <div className="flex items-center">
                    <Cog6ToothIcon className="h-4 w-4 mr-2" />
                    <span>Configurable analysis settings</span>
                  </div>
                  <div className="flex items-center">
                    <FolderIcon className="h-4 w-4 mr-2" />
                    <span>Support for multiple programming languages</span>
                  </div>
                </div>
              </div>
              <div className="mt-4">
                <button
                  onClick={handleAddRepository}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Add Your First Repository
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Repositories;