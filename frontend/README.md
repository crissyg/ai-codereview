# AI-CodeReview Frontend

React.js dashboard for the AI-CodeReview system.

## Features

- 📊 Real-time analytics dashboard
- 🔍 Interactive code analyzer
- 📈 Quality and security metrics visualization
- 📋 Analysis history and repository management
- 🎨 Modern, responsive UI with Tailwind CSS

## Quick Start

```
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Update the API URL to match your backend
3. Configure any additional environment variables

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Technology Stack

- React 18 with Hooks
- React Router for navigation
- React Query for data fetching
- Tailwind CSS for styling
- Chart.js for data visualization
- Axios for API communication
- React Hot Toast for notifications

## API Integration

The frontend communicates with the FastAPI backend through the API service layer. All API calls are centralized in `src/services/api.js`.