/**
 * SecurityChart Component
 * 
 * Displays a bar chart showing security issue counts by severity.
 * Uses Chart.js and react-chartjs-2 for rendering.
 * Provides clear visual cues for security risk levels.
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const SecurityChart = ({ highCount = 0, mediumCount = 0, lowCount = 0 }) => {
  const data = {
    labels: ['High', 'Medium', 'Low'],
    datasets: [
      {
        label: 'Security Issues',
        data: [highCount, mediumCount, lowCount],
        backgroundColor: [
          'rgba(239, 68, 68, 0.7)',    // Red for High
          'rgba(234, 179, 8, 0.7)',    // Yellow for Medium
          'rgba(34, 197, 94, 0.7)',    // Green for Low
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(234, 179, 8, 1)',
          'rgba(34, 197, 94, 1)',
        ],
        borderWidth: 1,
        borderRadius: 4,
        maxBarThickness: 40,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Security Issues by Severity',
        font: {
          size: 18,
          weight: 'bold',
        },
        color: '#b91c1c',
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 12,
        },
        cornerRadius: 6,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Severity Level',
          font: {
            size: 14,
            weight: 'bold',
          },
          color: '#6b21a8',
        },
        grid: {
          display: false,
        },
        ticks: {
          color: '#6b21a8',
          font: {
            size: 12,
          },
        },
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Issues',
          font: {
            size: 14,
            weight: 'bold',
          },
          color: '#6b21a8',
        },
        grid: {
          color: '#e0e7ff',
          borderDash: [5, 5],
        },
        ticks: {
          stepSize: 1,
          color: '#6b21a8',
          font: {
            size: 12,
          },
        },
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart',
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow h-96">
      <Bar data={data} options={options} />
    </div>
  );
};

export default SecurityChart;