/**
 * RepositoryConfig Component
 * 
 * Configuration form for repository settings including webhook setup,
 * auto-analysis preferences, and analysis options. Handles both adding
 * new repositories and updating existing repository configurations.
 */

import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  LinkIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import { formatters } from '../../utils/formatters';
import toast from 'react-hot-toast';

const RepositoryConfig = ({ repository = null, onSave, onCancel }) => {
  // Form state
  const [formData, setFormData] = useState({
    repository_url: '',
    auto_analysis: true,
    webhook_secret: '',
    analysis_config: {
      skip_files: [],
      quality_threshold: 70,
      security_focus: false,
      include_documentation: true,
    },
  });

  const [urlValidation, setUrlValidation] = useState({ isValid: false, message: '' });
  const [isTestingWebhook, setIsTestingWebhook] = useState(false);

  const queryClient = useQueryClient();

  // Initialize form with existing repository data
  useEffect(() => {
    if (repository) {
      setFormData({
        repository_url: repository.html_url || '',
        auto_analysis: repository.auto_analysis ?? true,
        webhook_secret: repository.webhook_secret || '',
        analysis_config: {
          skip_files: repository.analysis_config?.skip_files || [],
          quality_threshold: repository.analysis_config?.quality_threshold || 70,
          security_focus: repository.analysis_config?.security_focus || false,
          include_documentation: repository.analysis_config?.include_documentation ?? true,
        },
      });
    }
  }, [repository]);

  // Mutation for saving repository configuration
  const saveRepositoryMutation = useMutation(
    (data) => {
      if (repository) {
        return apiService.updateRepository(repository.id, data);
      } else {
        return apiService.addRepository(data);
      }
    },
    {
      onSuccess: () => {
        toast.success(repository ? 'Repository updated successfully' : 'Repository added successfully');
        queryClient.invalidateQueries('repositories');
        onSave?.();
      },
      onError: (error) => {
        toast.error(`Failed to save repository: ${error.message}`);
      },
    }
  );

  // Validate GitHub URL
  const validateRepositoryUrl = (url) => {
    if (!url) {
      setUrlValidation({ isValid: false, message: '' });
      return;
    }

    if (formatters.validateGitHubUrl && formatters.validateGitHubUrl(url)) {
      setUrlValidation({ isValid: true, message: 'Valid GitHub repository URL' });
    } else {
      setUrlValidation({ 
        isValid: false, 
        message: 'Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)' 
      });
    }
  };

  // Handle form field changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));

    // Validate URL on change
    if (field === 'repository_url') {
      validateRepositoryUrl(value);
    }
  };

  // Handle analysis config changes
  const handleAnalysisConfigChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      analysis_config: {
        ...prev.analysis_config,
        [field]: value,
      },
    }));
  };

  // Handle skip files list changes
  const handleSkipFilesChange = (value) => {
    const files = value.split(',').map(file => file.trim()).filter(file => file);
    handleAnalysisConfigChange('skip_files', files);
  };

  // Test webhook configuration
  const handleTestWebhook = async () => {
    if (!repository?.id) {
      toast.error('Save the repository first to test webhook');
      return;
    }

    setIsTestingWebhook(true);
    try {
      await apiService.testWebhook(repository.id);
      toast.success('Webhook test successful!');
    } catch (error) {
      toast.error(`Webhook test failed: ${error.message}`);
    } finally {
      setIsTestingWebhook(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!urlValidation.isValid && !repository) {
      toast.error('Please enter a valid GitHub repository URL');
      return;
    }

    saveRepositoryMutation.mutate(formData);
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">
          {repository ? 'Configure Repository' : 'Add Repository'}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          {repository 
            ? 'Update repository settings and analysis preferences'
            : 'Add a new GitHub repository for automated code analysis'
          }
        </p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Repository URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            GitHub Repository URL
          </label>
          <div className="mt-1 relative">
            <input
              type="url"
              value={formData.repository_url}
              onChange={(e) => handleInputChange('repository_url', e.target.value)}
              placeholder="https://github.com/owner/repository"
              className={`block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-1 sm:text-sm ${
                urlValidation.message
                  ? urlValidation.isValid
                    ? 'border-green-300 focus:ring-green-500 focus:border-green-500'
                    : 'border-red-300 focus:ring-red-500 focus:border-red-500'
                  : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
              }`}
              disabled={!!repository} // Disable URL editing for existing repos
              required={!repository}
            />
            {urlValidation.message && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                {urlValidation.isValid ? (
                  <CheckCircleIcon className="h-5 w-5 text-green-500" />
                ) : (
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
                )}
              </div>
            )}
          </div>
          {urlValidation.message && (
            <p className={`mt-2 text-sm ${urlValidation.isValid ? 'text-green-600' : 'text-red-600'}`}>
              {urlValidation.message}
            </p>
          )}
        </div>

        {/* Auto Analysis Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700">
              Automatic Analysis
            </label>
            <p className="text-sm text-gray-500">
              Automatically analyze pull requests when they are created or updated
            </p>
          </div>
          <button
            type="button"
            onClick={() => handleInputChange('auto_analysis', !formData.auto_analysis)}
            className={`${
              formData.auto_analysis ? 'bg-blue-600' : 'bg-gray-200'
            } relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
          >
            <span
              className={`${
                formData.auto_analysis ? 'translate-x-5' : 'translate-x-0'
              } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
            />
          </button>
        </div>

        {/* Webhook Configuration */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Webhook Secret (Optional)
            </label>
            <input
              type="password"
              value={formData.webhook_secret}
              onChange={(e) => handleInputChange('webhook_secret', e.target.value)}
              placeholder="Enter webhook secret for security"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
            <p className="mt-2 text-sm text-gray-500">
              Optional secret to verify webhook authenticity. Recommended for production use.
            </p>
          </div>

          {repository && (
            <div className="flex items-center space-x-3">
              <button
                type="button"
                onClick={handleTestWebhook}
                disabled={isTestingWebhook}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <LinkIcon className="h-4 w-4 mr-2" />
                {isTestingWebhook ? 'Testing...' : 'Test Webhook'}
              </button>
              
              <div className="flex items-center text-sm text-gray-500">
                <InformationCircleIcon className="h-4 w-4 mr-1" />
                Configure webhook URL in GitHub repository settings
              </div>
            </div>
          )}
        </div>

        {/* Analysis Configuration */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-900">Analysis Configuration</h4>
          
          {/* Quality Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Quality Threshold ({formData.analysis_config.quality_threshold}%)
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={formData.analysis_config.quality_threshold}
              onChange={(e) => handleAnalysisConfigChange('quality_threshold', parseInt(e.target.value))}
              className="mt-1 block w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
            <p className="mt-2 text-sm text-gray-500">
              Minimum quality score required to pass analysis
            </p>
          </div>

          {/* Skip Files */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Skip Files (Optional)
            </label>
            <input
              type="text"
              value={formData.analysis_config.skip_files.join(', ')}
              onChange={(e) => handleSkipFilesChange(e.target.value)}
              placeholder="*.md, *.txt, test_*.py"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
            <p className="mt-2 text-sm text-gray-500">
              Comma-separated list of file patterns to skip during analysis
            </p>
          </div>

          {/* Analysis Options */}
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.analysis_config.security_focus}
                onChange={(e) => handleAnalysisConfigChange('security_focus', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Focus on security analysis
              </span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.analysis_config.include_documentation}
                onChange={(e) => handleAnalysisConfigChange('include_documentation', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                Generate AI documentation
              </span>
            </label>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          
          <button
            type="submit"
            disabled={saveRepositoryMutation.isLoading || (!urlValidation.isValid && !repository)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saveRepositoryMutation.isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {repository ? 'Updating...' : 'Adding...'}
              </>
            ) : (
              repository ? 'Update Repository' : 'Add Repository'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RepositoryConfig;