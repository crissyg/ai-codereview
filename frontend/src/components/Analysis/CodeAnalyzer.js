/**
 * CodeAnalyzer Component
 * 
 * Main interface for submitting code for AI analysis. Provides a form
 * where users can input code, select language, and configure analysis options.
 * Handles validation, submission, and displays results.
 */

import React, { useState } from 'react';
import { useAnalysis } from '../../hooks/useAnalysis';
import { formatters } from '../../utils/formatters';
import toast from 'react-hot-toast';
import AnalysisResults from './AnalysisResults';

const CodeAnalyzer = () => {
  // Form state management
  const [code, setCode] = useState('');
  const [fileName, setFileName] = useState('');
  const [language, setLanguage] = useState('python');
  const [analysisOptions, setAnalysisOptions] = useState({
    includeDocumentation: true,
    includeSuggestions: true,
    securityFocus: false,
  });

  // Use custom hook for analysis operations
  const { 
    analyzeCode, 
    isAnalyzing, 
    analysisResult, 
    analysisError,
    supportedLanguages 
  } = useAnalysis();

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Basic validation before submission
    if (!code.trim()) {
      toast.error('Please enter some code to analyze');
      return;
    }

    if (code.length > 100000) {
      toast.error('Code is too large. Please limit to 100KB');
      return;
    }

    // Prepare analysis request
    const analysisRequest = {
      code_content: code,
      file_path: fileName || 'untitled.py',
      language: language,
      options: analysisOptions,
    };

    try {
      await analyzeCode(analysisRequest);
    } catch (error) {
      // Error handling is done in the hook, but we can add UI feedback here
      console.error('Analysis submission failed:', error);
    }
  };

  // Handle file upload for code input
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file size (max 1MB)
    if (file.size > 1024 * 1024) {
      toast.error('File too large. Please select a file under 1MB');
      return;
    }

    // Read file content
    const reader = new FileReader();
    reader.onload = (e) => {
      setCode(e.target.result);
      setFileName(file.name);
      
      // Auto-detect language from file extension
      const extension = file.name.split('.').pop().toLowerCase();
      const languageMap = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'go': 'go',
        'rs': 'rust',
        'php': 'php',
        'rb': 'ruby',
      };
      
      if (languageMap[extension]) {
        setLanguage(languageMap[extension]);
      }
    };
    
    reader.readAsText(file);
  };

  // Clear form and results
  const handleClear = () => {
    setCode('');
    setFileName('');
    setLanguage('python');
    setAnalysisOptions({
      includeDocumentation: true,
      includeSuggestions: true,
      securityFocus: false,
    });
  };

  return (
    <div className="space-y-6">
      {/* Code Input Form */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Code Analysis</h3>
          <p className="mt-1 text-sm text-gray-500">
            Submit your code for AI-powered analysis including security, quality, and suggestions
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* File upload and metadata */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                File Name (optional)
              </label>
              <input
                type="text"
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                placeholder="example.py"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Programming Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                {supportedLanguages.map((lang) => (
                  <option key={lang.value} value={lang.value}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Upload File
              </label>
              <input
                type="file"
                onChange={handleFileUpload}
                accept=".py,.js,.ts,.java,.cpp,.c,.go,.rs,.php,.rb"
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
          </div>

          {/* Analysis options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Analysis Options
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={analysisOptions.includeDocumentation}
                  onChange={(e) => setAnalysisOptions(prev => ({
                    ...prev,
                    includeDocumentation: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Generate AI documentation
                </span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={analysisOptions.includeSuggestions}
                  onChange={(e) => setAnalysisOptions(prev => ({
                    ...prev,
                    includeSuggestions: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Include improvement suggestions
                </span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={analysisOptions.securityFocus}
                  onChange={(e) => setAnalysisOptions(prev => ({
                    ...prev,
                    securityFocus: e.target.checked
                  }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Focus on security analysis
                </span>
              </label>
            </div>
          </div>

          {/* Code input textarea */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Code to Analyze
            </label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              rows={15}
              placeholder="Paste your code here or upload a file above..."
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
              required
            />
            <div className="mt-2 flex justify-between text-xs text-gray-500">
              <span>
                {code.length > 0 && `${formatters.formatFileSize(code.length)} / 100KB`}
              </span>
              <span>
                {code.split('\n').length} lines
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex justify-between">
            <button
              type="button"
              onClick={handleClear}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Clear
            </button>
            
            <button
              type="submit"
              disabled={isAnalyzing || !code.trim()}
              className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                'Analyze Code'
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Display analysis results */}
      {analysisResult && (
        <AnalysisResults results={analysisResult.data} />
      )}

      {/* Display error if analysis failed */}
      {analysisError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Analysis Failed
              </h3>
              <div className="mt-2 text-sm text-red-700">
                {analysisError.message || 'An unexpected error occurred during analysis'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeAnalyzer;