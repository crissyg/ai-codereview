/** @type {import('tailwindcss').Config} */
module.exports = {
  // Specifies which files Tailwind should scan for class names
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  
  theme: {
    extend: {
      // Custom color palette for the AI-CodeReview application
      colors: {
        // Primary brand colors
        primary: {
          50: '#eff6ff',
          100: '#dbeafe', 
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a'
        },
        
        // Status colors for code analysis results
        success: {
          50: '#f0fdf4',
          500: '#22c55e',
          600: '#16a34a'
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706'
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626'
        },
        
        // Neutral grays for UI elements
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827'
        }
      },
      
      // Custom font family for better readability
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Monaco', 'Menlo', 'monospace']
      },
      
      // Custom spacing for consistent layout
      spacing: {
        '18': '4.5rem',
        '88': '22rem'
      },
      
      // Animation for loading states and transitions
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out'
      },
      
      // Custom keyframes for animations
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      },
      
      // Box shadows for depth and elevation
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
      },
      
      // Custom border radius for modern UI
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem'
      }
    },
  },
  
  plugins: [
    // Official Tailwind plugins for enhanced functionality
    require('@tailwindcss/forms'),      // Better form styling
    require('@tailwindcss/typography'), // Rich text content styling
    require('@tailwindcss/aspect-ratio') // Aspect ratio utilities
  ],
  
  // Dark mode configuration (class-based for manual toggle)
  darkMode: 'class'
}