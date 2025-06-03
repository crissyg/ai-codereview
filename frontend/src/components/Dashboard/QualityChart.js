/**
 * QualityChart Component
 * 
 * Displays a line chart showing code quality trends over time.
 * Utilizes Chart.js and react-chartjs-2 for rendering.
 * Responsive and accessible with clear labels and tooltips.
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const QualityChart = ({ dataPoints = [], labels = [] }) => {
  // Default data if none provided
  const defaultLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  const defaultData = [65, 72, 68, 75, 82, 78];

  const chartData = {
    labels: labels.length ? labels : defaultLabels,
    datasets: [
      {
        label: 'Average Quality Score',
        data: dataPoints.length ? dataPoints : defaultData,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14,
            weight: 'bold',
          },
          color: '#1e3a8a',
        },
      },
      title: {
        display: true,
        text: 'Code Quality Trends',
        font: {
          size: 18,
          weight: 'bold',
        },
        color: '#1e3a8a',
      },
      tooltip: {
        enabled: true,
        mode: 'nearest',
        intersect: false,
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
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
          text: 'Month',
          font: {
            size: 14,
            weight: 'bold',
          },
          color: '#4b5563',
        },
        grid: {
          display: false,
        },
        ticks: {
          color: '#4b5563',
          font: {
            size: 12,
          },
        },
      },
      y: {
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Quality Score (%)',
          font: {
            size: 14,
            weight: 'bold',
          },
          color: '#4b5563',
        },
        grid: {
          color: '#e5e7eb',
          borderDash: [5, 5],
        },
        ticks: {
          stepSize: 10,
          color: '#4b5563',
          font: {
            size: 12,
          },
          callback: function(value) {
            return value + '%';
          },
        },
      },
    },
    interaction: {
      mode: 'nearest',
      intersect: false,
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart',
    },
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow h-96">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default QualityChart;