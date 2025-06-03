/**
 * API Service Layer
 * 
 * Centralized API client for all backend communication including
 * code analysis, repository management, and system operations.
 * Handles authentication, error handling, and request/response formatting.
 */

import axios from 'axios';

// Get API configuration from environment variables
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT) || 30000;

/**
 * Create axios instance with default configuration
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor for adding authentication and logging
 */
api.interceptors.request.use(
  (config) => {
    // Add request timestamp for performance monitoring
    config.metadata = { startTime: new Date() };
    
    // Add authentication token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling and logging
 */
api.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const endTime = new Date();
    const duration = endTime.getTime() - response.config.metadata.startTime.getTime();
    
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`, {
        status: response.status,
        data: response.data,
      });
    }
    
    // Add performance metrics to response
    response.metadata = {
      duration,
      timestamp: endTime.toISOString(),
    };
    
    return response;
  },
  (error) => {
    // Calculate request duration for failed requests
    const endTime = new Date();
    const duration = error.config?.metadata ? 
      endTime.getTime() - error.config.metadata.startTime.getTime() : 0;
    
    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`, {
        status: error.response?.status,
        message: error.message,
        data: error.response?.data,
      });
    }
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    // Enhance error object with additional information
    const enhancedError = {
      ...error,
      metadata: {
        duration,
        timestamp: endTime.toISOString(),
        requestId: error.config?.headers['X-Request-ID'],
      },
    };
    
    return Promise.reject(enhancedError);
  }
);

/**
 * API service functions organized by feature
 */
export const apiService = {
  
  /**
   * System and health endpoints
   */
  
  // Basic health check
  healthCheck: () => api.get('/health'),
  
  // Detailed system statistics
  getStats: () => api.get('/stats'),
  
  /**
   * Code analysis endpoints
   */
  
  // Analyze single piece of code
  analyzeCode: (codeData) => {
    const payload = {
      code_content: codeData.code_content,
      file_path: codeData.file_path || '',
      language: codeData.language || 'python',
    };
    
    return api.post('/analyze', payload);
  },
  
  // Get analysis history
  getAnalysisHistory: (params = {}) => {
    const queryParams = {
      page: params.page || 1,
      limit: params.limit || 20,
      ...params,
    };
    
    return api.get('/analysis/history', { params: queryParams });
  },
  
  // Get specific analysis details
  getAnalysisDetails: (analysisId) => api.get(`/analysis/${analysisId}`),
  
  /**
   * Repository management endpoints
   */
  
  // Get list of configured repositories
  getRepositories: () => api.get('/repositories'),
  
  // Add new repository for analysis
  addRepository: (repositoryData) => {
    const payload = {
      repository_url: repositoryData.repository_url,
      auto_analysis: repositoryData.auto_analysis ?? true,
      webhook_secret: repositoryData.webhook_secret || null,
    };
    
    return api.post('/repositories', payload);
  },
  
  // Update repository configuration
  updateRepository: (repositoryId, updateData) => 
    api.put(`/repositories/${repositoryId}`, updateData),
  
  // Remove repository from analysis
  removeRepository: (repositoryId) => api.delete(`/repositories/${repositoryId}`),
  
  // Get repository analysis statistics
  getRepositoryStats: (repositoryId) => api.get(`/repositories/${repositoryId}/stats`),
  
  /**
   * Pull request analysis endpoints
   */
  
  // Get pull requests for a repository
  getPullRequests: (repositoryId, params = {}) => {
    const queryParams = {
      state: params.state || 'open',
      page: params.page || 1,
      limit: params.limit || 20,
    };
    
    return api.get(`/repositories/${repositoryId}/pulls`, { params: queryParams });
  },
  
  // Trigger manual analysis of a pull request
  analyzePullRequest: (repositoryId, prNumber) => 
    api.post(`/repositories/${repositoryId}/pulls/${prNumber}/analyze`),
  
  // Get pull request analysis results
  getPullRequestAnalysis: (repositoryId, prNumber) => 
    api.get(`/repositories/${repositoryId}/pulls/${prNumber}/analysis`),
  
  /**
   * Webhook management endpoints
   */
  
  // Test webhook configuration
  testWebhook: (repositoryId) => api.post(`/repositories/${repositoryId}/webhook/test`),
  
  // Get webhook events history
  getWebhookEvents: (params = {}) => {
    const queryParams = {
      page: params.page || 1,
      limit: params.limit || 50,
      event_type: params.event_type || null,
    };
    
    return api.get('/webhooks/events', { params: queryParams });
  },
  
  /**
   * User and authentication endpoints (for future use)
   */
  
  // User profile
  getUserProfile: () => api.get('/user/profile'),
  
  // Update user preferences
  updateUserPreferences: (preferences) => api.put('/user/preferences', preferences),
  
  /**
   * Utility functions
   */
  
  // Upload file for analysis
  uploadFile: (file, metadata = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        
        // Emit progress event for UI updates
        if (metadata.onProgress) {
          metadata.onProgress(percentCompleted);
        }
      },
    });
  },
  
  // Download analysis report
  downloadReport: (analysisId, format = 'json') => {
    return api.get(`/analysis/${analysisId}/report`, {
      params: { format },
      responseType: 'blob',
    });
  },
  
  // Search functionality
  search: (query, filters = {}) => {
    const params = {
      q: query,
      ...filters,
    };
    
    return api.get('/search', { params });
  },
};

/**
 * Utility functions for API handling
 */

// Check if error is a network error
export const isNetworkError = (error) => {
  return !error.response && error.request;
};

// Check if error is a client error (4xx)
export const isClientError = (error) => {
  return error.response && error.response.status >= 400 && error.response.status < 500;
};

// Check if error is a server error (5xx)
export const isServerError = (error) => {
  return error.response && error.response.status >= 500;
};

// Extract error message from API response
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

// Create cancel token for request cancellation
export const createCancelToken = () => {
  return axios.CancelToken.source();
};

// Check if request was cancelled
export const isRequestCancelled = (error) => {
  return axios.isCancel(error);
};

export default api;