/**
 * AI-CodeReview Frontend Entry Point
 * 
 * Main entry file that initializes the React application with all necessary
 * providers, routing, and global configuration. Sets up the foundation
 * for the entire frontend application.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';

// Import main App component and global styles
import App from './App';
import './styles/index.css';

// Performance monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

// Error boundary for catching React errors
import ErrorBoundary from './components/Common/ErrorBoundary';

/**
 * Configure React Query client for server state management
 * Handles caching, background updates, and error handling for API calls
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes by default
      staleTime: 5 * 60 * 1000,
      // Keep data in cache for 10 minutes
      cacheTime: 10 * 60 * 1000,
      // Don't refetch on window focus in development
      refetchOnWindowFocus: process.env.NODE_ENV === 'production',
      // Retry failed requests up to 2 times
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
    mutations: {
      // Show error notifications for failed mutations
      onError: (error) => {
        console.error('Mutation error:', error);
        // Error handling will be done by individual components
      },
    },
  },
});

/**
 * Global error handler for unhandled promise rejections
 */
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  
  // Report to error tracking service in production
  if (process.env.NODE_ENV === 'production' && window.Sentry) {
    window.Sentry.captureException(event.reason);
  }
});

/**
 * Global error handler for JavaScript errors
 */
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  
  // Report to error tracking service in production
  if (process.env.NODE_ENV === 'production' && window.Sentry) {
    window.Sentry.captureException(event.error);
  }
});

/**
 * Performance monitoring using Web Vitals
 * Tracks Core Web Vitals metrics for performance optimization
 */
function reportWebVitals(metric) {
  // Log metrics in development
  if (process.env.NODE_ENV === 'development') {
    console.log('Web Vital:', metric);
  }
  
  // Send metrics to analytics in production
  if (process.env.NODE_ENV === 'production') {
    // Send to Google Analytics, DataDog, or other analytics service
    if (window.gtag) {
      window.gtag('event', metric.name, {
        custom_parameter_1: metric.value,
        custom_parameter_2: metric.id,
        custom_parameter_3: metric.name,
      });
    }
  }
}

/**
 * Initialize performance monitoring
 */
if (typeof window !== 'undefined') {
  // Measure Core Web Vitals
  getCLS(reportWebVitals);  // Cumulative Layout Shift
  getFID(reportWebVitals);  // First Input Delay
  getFCP(reportWebVitals);  // First Contentful Paint
  getLCP(reportWebVitals);  // Largest Contentful Paint
  getTTFB(reportWebVitals); // Time to First Byte
}

/**
 * Application configuration based on environment
 */
const isDevelopment = process.env.NODE_ENV === 'development';
const isProduction = process.env.NODE_ENV === 'production';

// Log application startup information
if (isDevelopment) {
  console.log('🚀 AI-CodeReview Frontend starting in development mode');
  console.log('📊 React Query DevTools enabled');
  console.log('🔧 Debug mode:', process.env.REACT_APP_DEBUG === 'true');
}

/**
 * Main Application Component with all providers
 */
const AppWithProviders = () => {
  return (
    <React.StrictMode>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <App />
            
            {/* Toast notifications for user feedback */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                  borderRadius: '8px',
                  fontSize: '14px',
                },
                success: {
                  iconTheme: {
                    primary: '#22c55e',
                    secondary: '#fff',
                  },
                },
                error: {
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
            
            {/* React Query DevTools - only in development */}
            {isDevelopment && (
              <ReactQueryDevtools
                initialIsOpen={false}
                position="bottom-left"
              />
            )}
          </BrowserRouter>
        </QueryClientProvider>
      </ErrorBoundary>
    </React.StrictMode>
  );
};

/**
 * Render the application to the DOM
 */
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render with error handling
try {
  root.render(<AppWithProviders />);
  
  // Mark app as loaded for loading screen
  setTimeout(() => {
    document.body.classList.add('app-loaded');
  }, 100);
  
  // Performance mark for measuring app initialization
  if (window.performance && window.performance.mark) {
    window.performance.mark('app-rendered');
    
    // Measure time from start to render
    if (window.performance.getEntriesByName('app-start').length > 0) {
      window.performance.measure('app-initialization', 'app-start', 'app-rendered');
    }
  }
  
} catch (error) {
  console.error('Failed to render React application:', error);
  
  // Fallback error display
  document.getElementById('root').innerHTML = `
    <div style="
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 100vh;
      font-family: Inter, sans-serif;
      text-align: center;
      padding: 20px;
    ">
      <h1 style="color: #ef4444; margin-bottom: 16px;">Application Error</h1>
      <p style="color: #6b7280; max-width: 400px; margin-bottom: 20px;">
        Sorry, there was an error loading the AI-CodeReview application. 
        Please refresh the page or contact support if the problem persists.
      </p>
      <button 
        onclick="window.location.reload()" 
        style="
          background: #3b82f6;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        "
      >
        Reload Page
      </button>
    </div>
  `;
}

/**
 * Hot Module Replacement (HMR) for development
 * Enables hot reloading without losing application state
 */
if (isDevelopment && module.hot) {
  module.hot.accept('./App', () => {
    console.log('🔄 Hot reloading App component');
  });
}

/**
 * Service Worker registration for PWA features
 * Enables offline functionality and caching
 */
if (isProduction && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

/**
 * Cleanup function for development
 */
if (isDevelopment) {
  window.addEventListener('beforeunload', () => {
    console.log('🛑 Application unloading');
  });
}