/**
 * Data Formatting Utilities
 * 
 * Collection of utility functions for formatting data display including
 * dates, numbers, file sizes, and analysis results for consistent UI presentation.
 */

import { format, formatDistanceToNow, isValid, parseISO } from 'date-fns';

/**
 * Format date/time values for display
 */
export const formatters = {
  
  /**
   * Format date to human-readable string
   * @param {string|Date} date - Date to format
   * @param {string} formatString - Format pattern (default: 'MMM dd, yyyy')
   * @returns {string} Formatted date string
   */
  formatDate: (date, formatString = 'MMM dd, yyyy') => {
    if (!date) return 'N/A';
    
    try {
      const dateObj = typeof date === 'string' ? parseISO(date) : date;
      return isValid(dateObj) ? format(dateObj, formatString) : 'Invalid date';
    } catch (error) {
      console.warn('Date formatting error:', error);
      return 'Invalid date';
    }
  },

  /**
   * Format date to relative time (e.g., "2 hours ago")
   * @param {string|Date} date - Date to format
   * @returns {string} Relative time string
   */
  formatRelativeTime: (date) => {
    if (!date) return 'N/A';
    
    try {
      const dateObj = typeof date === 'string' ? parseISO(date) : date;
      return isValid(dateObj) ? formatDistanceToNow(dateObj, { addSuffix: true }) : 'Invalid date';
    } catch (error) {
      console.warn('Relative time formatting error:', error);
      return 'Invalid date';
    }
  },

  /**
   * Format date and time with timezone
   * @param {string|Date} date - Date to format
   * @returns {string} Formatted datetime string
   */
  formatDateTime: (date) => {
    if (!date) return 'N/A';
    
    try {
      const dateObj = typeof date === 'string' ? parseISO(date) : date;
      return isValid(dateObj) ? format(dateObj, 'MMM dd, yyyy HH:mm') : 'Invalid date';
    } catch (error) {
      console.warn('DateTime formatting error:', error);
      return 'Invalid date';
    }
  },

  /**
   * Format numbers for display
   */
  
  /**
   * Format number with thousands separators
   * @param {number} num - Number to format
   * @returns {string} Formatted number string
   */
  formatNumber: (num) => {
    if (typeof num !== 'number' || isNaN(num)) return '0';
    return new Intl.NumberFormat().format(num);
  },

  /**
   * Format percentage values
   * @param {number} value - Percentage value (0-100)
   * @param {number} decimals - Number of decimal places (default: 1)
   * @returns {string} Formatted percentage string
   */
  formatPercentage: (value, decimals = 1) => {
    if (typeof value !== 'number' || isNaN(value)) return '0%';
    return `${value.toFixed(decimals)}%`;
  },

  /**
   * Format file sizes in human-readable format
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size string
   */
  formatFileSize: (bytes) => {
    if (typeof bytes !== 'number' || bytes === 0) return '0 B';
    
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = bytes / Math.pow(1024, i);
    
    return `${size.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
  },

  /**
   * Format duration in milliseconds to human-readable format
   * @param {number} ms - Duration in milliseconds
   * @returns {string} Formatted duration string
   */
  formatDuration: (ms) => {
    if (typeof ms !== 'number' || ms < 0) return '0ms';
    
    if (ms < 1000) return `${Math.round(ms)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    if (ms < 3600000) return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
    
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    return `${hours}h ${minutes}m`;
  },

  /**
   * Analysis-specific formatters
   */
  
  /**
   * Format quality score with color coding
   * @param {number} score - Quality score (0-100)
   * @returns {object} Object with formatted score and color class
   */
  formatQualityScore: (score) => {
    if (typeof score !== 'number' || isNaN(score)) {
      return { text: 'N/A', colorClass: 'text-gray-500' };
    }
    
    const formattedScore = `${score.toFixed(1)}%`;
    let colorClass = 'text-gray-500';
    
    if (score >= 90) colorClass = 'text-green-600';
    else if (score >= 80) colorClass = 'text-blue-600';
    else if (score >= 70) colorClass = 'text-yellow-600';
    else if (score >= 60) colorClass = 'text-orange-600';
    else colorClass = 'text-red-600';
    
    return { text: formattedScore, colorClass };
  },

  /**
   * Format security severity with appropriate styling
   * @param {string} severity - Security severity level
   * @returns {object} Object with formatted text and styling classes
   */
  formatSeverity: (severity) => {
    const severityMap = {
      HIGH: {
        text: 'High',
        badgeClass: 'bg-red-100 text-red-800',
        iconClass: 'text-red-500'
      },
      MEDIUM: {
        text: 'Medium',
        badgeClass: 'bg-yellow-100 text-yellow-800',
        iconClass: 'text-yellow-500'
      },
      LOW: {
        text: 'Low',
        badgeClass: 'bg-green-100 text-green-800',
        iconClass: 'text-green-500'
      }
    };
    
    return severityMap[severity] || {
      text: severity || 'Unknown',
      badgeClass: 'bg-gray-100 text-gray-800',
      iconClass: 'text-gray-500'
    };
  },

  /**
   * Format overall rating with letter grade styling
   * @param {string} rating - Overall rating (e.g., "A - Excellent")
   * @returns {object} Object with grade, description, and styling
   */
  formatOverallRating: (rating) => {
    if (!rating) return { grade: 'N/A', description: '', colorClass: 'text-gray-500' };
    
    const [grade, ...descriptionParts] = rating.split(' - ');
    const description = descriptionParts.join(' - ');
    
    const gradeColors = {
      A: 'text-green-600',
      B: 'text-blue-600',
      C: 'text-yellow-600',
      D: 'text-orange-600',
      F: 'text-red-600'
    };
    
    return {
      grade: grade || 'N/A',
      description: description || '',
      colorClass: gradeColors[grade] || 'text-gray-500'
    };
  },

  /**
   * Format complexity rating with appropriate styling
   * @param {string} complexity - Complexity rating (LOW, MEDIUM, HIGH)
   * @returns {object} Object with formatted text and styling
   */
  formatComplexity: (complexity) => {
    const complexityMap = {
      LOW: {
        text: 'Low',
        badgeClass: 'bg-green-100 text-green-800',
        description: 'Easy to understand and maintain'
      },
      MEDIUM: {
        text: 'Medium',
        badgeClass: 'bg-yellow-100 text-yellow-800',
        description: 'Moderately complex'
      },
      HIGH: {
        text: 'High',
        badgeClass: 'bg-red-100 text-red-800',
        description: 'Complex, may need refactoring'
      }
    };
    
    return complexityMap[complexity] || {
      text: complexity || 'Unknown',
      badgeClass: 'bg-gray-100 text-gray-800',
      description: 'Complexity not determined'
    };
  },

  /**
   * Utility functions
   */
  
  /**
   * Truncate text to specified length with ellipsis
   * @param {string} text - Text to truncate
   * @param {number} maxLength - Maximum length (default: 50)
   * @returns {string} Truncated text
   */
  truncateText: (text, maxLength = 50) => {
    if (!text || typeof text !== 'string') return '';
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength)}...`;
  },

  /**
   * Format programming language name for display
   * @param {string} language - Programming language
   * @returns {string} Formatted language name
   */
  formatLanguage: (language) => {
    const languageMap = {
      javascript: 'JavaScript',
      typescript: 'TypeScript',
      python: 'Python',
      java: 'Java',
      cpp: 'C++',
      c: 'C',
      go: 'Go',
      rust: 'Rust',
      php: 'PHP',
      ruby: 'Ruby'
    };
    
    return languageMap[language?.toLowerCase()] || language || 'Unknown';
  },

  /**
   * Format repository name for display
   * @param {string} fullName - Full repository name (owner/repo)
   * @returns {object} Object with owner and repo separated
   */
  formatRepositoryName: (fullName) => {
    if (!fullName || typeof fullName !== 'string') {
      return { owner: '', repo: '', display: 'Unknown Repository' };
    }
    
    const [owner, repo] = fullName.split('/');
    return {
      owner: owner || '',
      repo: repo || '',
      display: fullName
    };
  }
};

export default formatters;