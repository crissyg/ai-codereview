/**
 * RepositoryList Component
 * 
 * Displays a list of configured repositories with their analysis status,
 * recent activity, and management actions. Provides functionality to add,
 * remove, and configure repositories for automated code analysis.
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  PlusIcon,
  TrashIcon,
  Cog6ToothIcon,
  EyeIcon,
  ShieldCheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import { formatters } from '../../utils/formatters';
import toast from 'react-hot-toast';

const RepositoryList = ({ onConfigureRepository, onAddRepository }) => {
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  
  const queryClient = useQueryClient();

  // Fetch repositories from API
  const { data: repositories, isLoading, error } = useQuery(
    'repositories',
    apiService.getRepositories,
    {
      staleTime: 2 * 60 * 1000, // 2 minutes
      cacheTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Mutation for removing repositories
  const removeRepositoryMutation = useMutation(
    apiService.removeRepository,
    {
      onSuccess: () => {
        toast.success('Repository removed successfully');
        queryClient.invalidateQueries('repositories');
        setShowDeleteConfirm(null);
      },
      onError: (error) => {
        toast.error(`Failed to remove repository: ${error.message}`);
      },
    }
  );

  // Handle repository removal
  const handleRemoveRepository = (repositoryId) => {
    removeRepositoryMutation.mutate(repositoryId);
  };

  // Get status indicator for repository
  const getStatusIndicator = (status) => {
    const statusConfig = {
      active: {
        color: 'text-green-500',
        bgColor: 'bg-green-100',
        icon: ShieldCheckIcon,
        label: 'Active',
      },
      inactive: {
        color: 'text-gray-500',
        bgColor: 'bg-gray-100',
        icon: ClockIcon,
        label: 'Inactive',
      },
      error: {
        color: 'text-red-500',
        bgColor: 'bg-red-100',
        icon: ExclamationTriangleIcon,
        label: 'Error',
      },
    };

    return statusConfig[status] || statusConfig.inactive;
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-300 rounded w-1/4"></div>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-300 rounded"></div>
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
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Repositories</h3>
          <p className="text-gray-500">{error.message}</p>
        </div>
      </div>
    );
  }

  const repositoryList = repositories?.data || [];

  return (
    <div className="space-y-6">
      {/* Header with add button */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Repositories</h3>
              <p className="mt-1 text-sm text-gray-500">
                {repositoryList.length} repositories configured for analysis
              </p>
            </div>
            <button
              onClick={onAddRepository}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Add Repository
            </button>
          </div>
        </div>
      </div>

      {/* Repository list */}
      <div className="bg-white shadow rounded-lg">
        {repositoryList.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {repositoryList.map((repo) => {
              const statusConfig = getStatusIndicator(repo.status);
              const repoInfo = formatters.formatRepositoryName(repo.full_name);

              return (
                <li key={repo.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    {/* Repository info */}
                    <div className="flex items-center space-x-4">
                      <div className={`flex-shrink-0 p-2 rounded-full ${statusConfig.bgColor}`}>
                        <statusConfig.icon className={`h-5 w-5 ${statusConfig.color}`} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {repoInfo.display}
                          </p>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusConfig.bgColor} ${statusConfig.color}`}>
                            {statusConfig.label}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-4 mt-1">
                          <p className="text-sm text-gray-500">
                            Language: {formatters.formatLanguage(repo.primary_language)}
                          </p>
                          {repo.last_analysis_at && (
                            <p className="text-sm text-gray-500">
                              Last analysis: {formatters.formatRelativeTime(repo.last_analysis_at)}
                            </p>
                          )}
                          <p className="text-sm text-gray-500">
                            {repo.total_analyses} analyses
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Repository metrics */}
                    <div className="flex items-center space-x-6">
                      {repo.auto_analysis && (
                        <div className="text-center">
                          <div className="text-sm font-medium text-green-600">
                            Auto
                          </div>
                          <div className="text-xs text-gray-500">Analysis</div>
                        </div>
                      )}
                      
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {repo.webhook_url ? 'Yes' : 'No'}
                        </div>
                        <div className="text-xs text-gray-500">Webhook</div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setSelectedRepo(repo)}
                          className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
                          title="View details"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        
                        <button
                          onClick={() => onConfigureRepository(repo)}
                          className="p-2 text-blue-400 hover:text-blue-600 rounded-full hover:bg-blue-50"
                          title="Configure repository"
                        >
                          <Cog6ToothIcon className="h-4 w-4" />
                        </button>
                        
                        <button
                          onClick={() => setShowDeleteConfirm(repo.id)}
                          className="p-2 text-red-400 hover:text-red-600 rounded-full hover:bg-red-50"
                          title="Remove repository"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          // Empty state
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <svg fill="none" stroke="currentColor" viewBox="0 0 48 48">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 20h8m-4-4v8m-8-4h16" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No repositories</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by adding a repository to analyze.
            </p>
            <div className="mt-6">
              <button
                onClick={onAddRepository}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Repository
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Repository details modal */}
      {selectedRepo && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    Repository Details
                  </h3>
                  <button
                    onClick={() => setSelectedRepo(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Repository</label>
                    <p className="text-sm text-gray-900">{selectedRepo.full_name}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Description</label>
                    <p className="text-sm text-gray-900">{selectedRepo.description || 'No description'}</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Status</label>
                      <p className="text-sm text-gray-900">{selectedRepo.status}</p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Language</label>
                      <p className="text-sm text-gray-900">{formatters.formatLanguage(selectedRepo.primary_language)}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Auto Analysis</label>
                      <p className="text-sm text-gray-900">{selectedRepo.auto_analysis ? 'Enabled' : 'Disabled'}</p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Total Analyses</label>
                      <p className="text-sm text-gray-900">{selectedRepo.total_analyses}</p>
                    </div>
                  </div>
                  
                  {selectedRepo.last_analysis_at && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Last Analysis</label>
                      <p className="text-sm text-gray-900">
                        {formatters.formatDateTime(selectedRepo.last_analysis_at)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Remove Repository
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Are you sure you want to remove this repository? This action cannot be undone
                        and will delete all analysis history.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  onClick={() => handleRemoveRepository(showDeleteConfirm)}
                  disabled={removeRepositoryMutation.isLoading}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                >
                  {removeRepositoryMutation.isLoading ? 'Removing...' : 'Remove'}
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(null)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RepositoryList;