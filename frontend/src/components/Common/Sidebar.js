/**
 * Sidebar Navigation Component
 * 
 * Left sidebar navigation with main application routes and active state management.
 * Responsive design that collapses on mobile devices.
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  ChartBarIcon,
  FolderIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Navigation items configuration
  const navigation = [
    { 
      name: 'Dashboard', 
      href: '/', 
      icon: HomeIcon,
      description: 'Overview and analytics'
    },
    { 
      name: 'Code Analysis', 
      href: '/analysis', 
      icon: ChartBarIcon,
      description: 'Analyze code quality'
    },
    { 
      name: 'Repositories', 
      href: '/repositories', 
      icon: FolderIcon,
      description: 'Manage repositories'
    },
    { 
      name: 'Security', 
      href: '/security', 
      icon: ShieldCheckIcon,
      description: 'Security reports'
    },
    { 
      name: 'Documentation', 
      href: '/docs', 
      icon: DocumentTextIcon,
      description: 'API documentation'
    },
    { 
      name: 'Settings', 
      href: '/settings', 
      icon: Cog6ToothIcon,
      description: 'Application settings'
    },
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  // Check if current route is active
  const isActiveRoute = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button
          onClick={toggleMobileMenu}
          className="p-2 rounded-md bg-white shadow-md text-gray-600 hover:text-gray-900"
          aria-label="Toggle navigation menu"
        >
          {isMobileMenuOpen ? (
            <XMarkIcon className="h-6 w-6" />
          ) : (
            <Bars3Icon className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-40 bg-gray-600 bg-opacity-75"
          onClick={closeMobileMenu}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white shadow-sm border-r border-gray-200 transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        
        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 lg:hidden">
          <span className="text-lg font-semibold text-gray-900">Navigation</span>
          <button
            onClick={closeMobileMenu}
            className="p-2 rounded-md text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation menu */}
        <nav className="mt-5 px-2 lg:mt-0 lg:pt-5">
          <div className="space-y-1">
            {navigation.map((item) => {
              const isActive = isActiveRoute(item.href);
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={closeMobileMenu}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200
                    ${isActive
                      ? 'bg-blue-50 border-blue-500 text-blue-700 border-l-4'
                      : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-4'
                    }
                  `}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <item.icon
                    className={`
                      mr-3 h-6 w-6 flex-shrink-0 transition-colors duration-200
                      ${isActive 
                        ? 'text-blue-500' 
                        : 'text-gray-400 group-hover:text-gray-500'
                      }
                    `}
                    aria-hidden="true"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span>{item.name}</span>
                      {/* Active indicator */}
                      {isActive && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5 group-hover:text-gray-600">
                      {item.description}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Sidebar footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">AI</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                AI-CodeReview
              </p>
              <p className="text-xs text-gray-500">
                v1.0.0
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Spacer for desktop layout */}
      <div className="hidden lg:block w-64 flex-shrink-0" aria-hidden="true">
        {/* This div is used to push content to the right on desktop */}
      </div>
    </>
  );
};

export default Sidebar;