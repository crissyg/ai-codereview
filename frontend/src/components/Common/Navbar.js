/**
 * Navigation Bar Component
 * 
 * Top navigation bar with branding, user actions, and system status.
 * Provides consistent header across all pages with responsive design.
 */

import React, { useState } from 'react';
import { 
  BellIcon, 
  UserCircleIcon, 
  Cog6ToothIcon,
  ChevronDownIcon 
} from '@heroicons/react/24/outline';
import { useQuery } from 'react-query';
import { apiService } from '../../services/api';

const Navbar = () => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Fetch system health status for indicator
  const { data: healthStatus } = useQuery(
    'health-status',
    apiService.healthCheck,
    {
      refetchInterval: 30000, // Check every 30 seconds
      retry: false,
    }
  );

  const handleUserMenuToggle = () => {
    setShowUserMenu(!showUserMenu);
    setShowNotifications(false); // Close notifications when opening user menu
  };

  const handleNotificationsToggle = () => {
    setShowNotifications(!showNotifications);
    setShowUserMenu(false); // Close user menu when opening notifications
  };

  // Close dropdowns when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.dropdown-container')) {
        setShowUserMenu(false);
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Left side - Brand and system status */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900 flex items-center">
                🤖 AI-CodeReview
              </h1>
            </div>
            
            {/* System health indicator */}
            <div className="hidden sm:flex items-center">
              <div className={`w-2 h-2 rounded-full ${
                healthStatus?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="ml-2 text-xs text-gray-500">
                {healthStatus?.status === 'healthy' ? 'System Online' : 'System Issues'}
              </span>
            </div>
          </div>
          
          {/* Right side - User actions */}
          <div className="flex items-center space-x-4">
            
            {/* Notifications dropdown */}
            <div className="relative dropdown-container">
              <button
                onClick={handleNotificationsToggle}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors relative"
                aria-label="View notifications"
              >
                <BellIcon className="h-6 w-6" />
                {/* Notification badge */}
                <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-red-400"></span>
              </button>
              
              {/* Notifications dropdown menu */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  <div className="p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Recent Notifications</h3>
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900">Analysis completed for PR #123</p>
                          <p className="text-xs text-gray-500">2 minutes ago</p>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900">Security issues found in main.py</p>
                          <p className="text-xs text-gray-500">5 minutes ago</p>
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 pt-3 border-t border-gray-200">
                      <a href="#" className="text-sm text-blue-600 hover:text-blue-500">
                        View all notifications
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Settings button */}
            <button
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors"
              aria-label="Settings"
            >
              <Cog6ToothIcon className="h-6 w-6" />
            </button>
            
            {/* User menu dropdown */}
            <div className="relative dropdown-container">
              <button
                onClick={handleUserMenuToggle}
                className="flex items-center space-x-2 p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 transition-colors"
                aria-label="User menu"
              >
                <UserCircleIcon className="h-6 w-6" />
                <ChevronDownIcon className="h-4 w-4" />
              </button>
              
              {/* User dropdown menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">Developer</p>
                      <p className="text-xs text-gray-500">developer@example.com</p>
                    </div>
                    <a
                      href="#"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Profile Settings
                    </a>
                    <a
                      href="#"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      API Keys
                    </a>
                    <a
                      href="#"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Documentation
                    </a>
                    <div className="border-t border-gray-200">
                      <a
                        href="#"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Sign out
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;