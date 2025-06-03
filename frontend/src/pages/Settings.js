/**
 * Settings Page Component
 * 
 * Application settings and configuration page. Allows users to manage
 * their preferences, API keys, notification settings, and system configuration.
 * Organized into logical sections with proper validation and persistence.
 */

import React, { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  KeyIcon,
  PaintBrushIcon,
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Settings = () => {
  // State for active settings section
  const [activeSection, setActiveSection] = useState('profile');
  
  // State for form data
  const [settings, setSettings] = useState({
    profile: {
      name: '',
      email: '',
      company: '',
      role: '',
    },
    notifications: {
      emailNotifications: true,
      analysisComplete: true,
      securityAlerts: true,
      weeklyReports: false,
      systemUpdates: true,
    },
    analysis: {
      defaultLanguage: 'python',
      qualityThreshold: 70,
      autoAnalysis: true,
      includeDocumentation: true,
      securityFocus: false,
    },
    appearance: {
      theme: 'light',
      compactMode: false,
      showLineNumbers: true,
      fontSize: 'medium',
    },
    api: {
      githubToken: '',
      webhookSecret: '',
      rateLimitWarnings: true,
    },
  });

  const queryClient = useQueryClient();

  // Fetch current user settings
  const { data: userSettings, isLoading } = useQuery(
    'user-settings',
    apiService.getUserProfile,
    {
      onSuccess: (data) => {
        if (data?.preferences) {
          setSettings(prev => ({ ...prev, ...data.preferences }));
        }
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Mutation for saving settings
  const saveSettingsMutation = useMutation(
    (settingsData) => apiService.updateUserPreferences(settingsData),
    {
      onSuccess: () => {
        toast.success('Settings saved successfully');
        queryClient.invalidateQueries('user-settings');
      },
      onError: (error) => {
        toast.error(`Failed to save settings: ${error.message}`);
      },
    }
  );

  // Settings sections configuration
  const sections = [
    {
      id: 'profile',
      name: 'Profile',
      icon: UserCircleIcon,
      description: 'Personal information and account details',
    },
    {
      id: 'notifications',
      name: 'Notifications',
      icon: BellIcon,
      description: 'Email and system notification preferences',
    },
    {
      id: 'analysis',
      name: 'Analysis',
      icon: ShieldCheckIcon,
      description: 'Default analysis settings and preferences',
    },
    {
      id: 'appearance',
      name: 'Appearance',
      icon: PaintBrushIcon,
      description: 'Theme and display preferences',
    },
    {
      id: 'api',
      name: 'API & Security',
      icon: KeyIcon,
      description: 'API keys and security configuration',
    },
    {
      id: 'system',
      name: 'System',
      icon: Cog6ToothIcon,
      description: 'Advanced system settings',
    },
  ];

  // Handle form field changes
  const handleSettingChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  // Handle form submission
  const handleSaveSettings = () => {
    saveSettingsMutation.mutate(settings);
  };

  // Reset settings to defaults
  const handleResetSettings = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      // Reset to default values
      setSettings({
        profile: { name: '', email: '', company: '', role: '' },
        notifications: {
          emailNotifications: true,
          analysisComplete: true,
          securityAlerts: true,
          weeklyReports: false,
          systemUpdates: true,
        },
        analysis: {
          defaultLanguage: 'python',
          qualityThreshold: 70,
          autoAnalysis: true,
          includeDocumentation: true,
          securityFocus: false,
        },
        appearance: {
          theme: 'light',
          compactMode: false,
          showLineNumbers: true,
          fontSize: 'medium',
        },
        api: { githubToken: '', webhookSecret: '', rateLimitWarnings: true },
      });
      toast.success('Settings reset to defaults');
    }
  };

  // Render settings section content
  const renderSectionContent = () => {
    switch (activeSection) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <input
                    type="text"
                    value={settings.profile.name}
                    onChange={(e) => handleSettingChange('profile', 'name', e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    value={settings.profile.email}
                    onChange={(e) => handleSettingChange('profile', 'email', e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Company</label>
                  <input
                    type="text"
                    value={settings.profile.company}
                    onChange={(e) => handleSettingChange('profile', 'company', e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <select
                    value={settings.profile.role}
                    onChange={(e) => handleSettingChange('profile', 'role', e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select role</option>
                    <option value="developer">Developer</option>
                    <option value="team-lead">Team Lead</option>
                    <option value="architect">Software Architect</option>
                    <option value="manager">Engineering Manager</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
              <div className="space-y-4">
                {Object.entries(settings.notifications).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700">
                        {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      </label>
                      <p className="text-sm text-gray-500">
                        {getNotificationDescription(key)}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleSettingChange('notifications', key, !value)}
                      className={`${
                        value ? 'bg-blue-600' : 'bg-gray-200'
                      } relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
                    >
                      <span
                        className={`${
                          value ? 'translate-x-5' : 'translate-x-0'
                        } pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out`}
                      />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'analysis':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Analysis Defaults</h3>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Default Language</label>
                  <select
                    value={settings.analysis.defaultLanguage}
                    onChange={(e) => handleSettingChange('analysis', 'defaultLanguage', e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="typescript">TypeScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="go">Go</option>
                    <option value="rust">Rust</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Quality Threshold ({settings.analysis.qualityThreshold}%)
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={settings.analysis.qualityThreshold}
                    onChange={(e) => handleSettingChange('analysis', 'qualityThreshold', parseInt(e.target.value))}
                    className="mt-1 block w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0%</span>
                    <span>50%</span>
                    <span>100%</span>
                  </div>
                </div>
                
                <div className="space-y-3">
                  {['autoAnalysis', 'includeDocumentation', 'securityFocus'].map((key) => (
                    <label key={key} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.analysis[key]}
                        onChange={(e) => handleSettingChange('analysis', key, e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 'appearance':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Appearance Settings</h3>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Theme</label>
                  <div className="mt-2 space-y-2">
                    {['light', 'dark', 'auto'].map((theme) => (
                      <label key={theme} className="flex items-center">
                        <input
                          type="radio"
                          name="theme"
                          value={theme}
                          checked={settings.appearance.theme === theme}
                          onChange={(e) => handleSettingChange('appearance', 'theme', e.target.value)}
                          className="text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700 capitalize">{theme}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Font Size</label>
                  <select
                    value={settings.appearance.fontSize}
                    onChange={(e) => handleSettingChange('appearance', 'fontSize', e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                  </select>
                </div>
                
                <div className="space-y-3">
                  {['compactMode', 'showLineNumbers'].map((key) => (
                    <label key={key} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={settings.appearance[key]}
                        onChange={(e) => handleSettingChange('appearance', key, e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 'api':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">API Configuration</h3>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">GitHub Token</label>
                  <input
                    type="password"
                    value={settings.api.githubToken}
                    onChange={(e) => handleSettingChange('api', 'githubToken', e.target.value)}
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Personal access token for GitHub integration
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Webhook Secret</label>
                  <input
                    type="password"
                    value={settings.api.webhookSecret}
                    onChange={(e) => handleSettingChange('api', 'webhookSecret', e.target.value)}
                    placeholder="Enter webhook secret"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Secret for validating GitHub webhook requests
                  </p>
                </div>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.api.rateLimitWarnings}
                    onChange={(e) => handleSettingChange('api', 'rateLimitWarnings', e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Show rate limit warnings
                  </span>
                </label>
              </div>
            </div>
          </div>
        );

      case 'system':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">System Settings</h3>
              <div className="space-y-4">
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-yellow-800">Advanced Settings</h3>
                      <div className="mt-2 text-sm text-yellow-700">
                        <p>These settings affect system behavior and should only be modified by administrators.</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={handleResetSettings}
                  className="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Reset All Settings
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Helper function for notification descriptions
  const getNotificationDescription = (key) => {
    const descriptions = {
      emailNotifications: 'Receive email notifications for important events',
      analysisComplete: 'Notify when code analysis is complete',
      securityAlerts: 'Alert for high-severity security issues',
      weeklyReports: 'Weekly summary of analysis activity',
      systemUpdates: 'Notifications about system updates and maintenance',
    };
    return descriptions[key] || '';
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`${
                  activeSection === section.id
                    ? 'bg-blue-50 border-blue-500 text-blue-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                } group flex items-center px-3 py-2 text-sm font-medium border-l-4 rounded-md w-full text-left`}
              >
                <section.icon
                  className={`${
                    activeSection === section.id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                  } mr-3 h-6 w-6 flex-shrink-0`}
                />
                <div>
                  <div>{section.name}</div>
                  <div className="text-xs text-gray-500">{section.description}</div>
                </div>
              </button>
            ))}
          </nav>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                {sections.find(s => s.id === activeSection)?.name}
              </h3>
            </div>
            
            <div className="px-6 py-6">
              {renderSectionContent()}
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={handleSaveSettings}
                disabled={saveSettingsMutation.isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {saveSettingsMutation.isLoading ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;