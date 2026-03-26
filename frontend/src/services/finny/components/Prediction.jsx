import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../api/analyticsApi';
import '../styles/AnalyticsPage.css';

// Custom Line Chart Component for Prediction
const PredictionLineChart = ({ data }) => {
  const maxValue = 24000;
  const chartWidth = 400;
  const chartHeight = 260;
  const padding = { top: 10, right: 16, left: 40, bottom: 40 };
  
  const getXPosition = (index) => {
    const availableWidth = chartWidth - padding.left - padding.right;
    return padding.left + (index * availableWidth / (data.length - 1));
  };
  
  const getYPosition = (value) => {
    const availableHeight = chartHeight - padding.top - padding.bottom;
    return chartHeight - padding.bottom - ((value / maxValue) * availableHeight);
  };
  
  const createSmoothPath = () => {
    if (data.length < 2) return '';
    
    let path = `M ${getXPosition(0)} ${getYPosition(data[0].amount)}`;
    
    for (let i = 1; i < data.length; i++) {
      const x = getXPosition(i);
      const y = getYPosition(data[i].amount);
      const prevX = getXPosition(i - 1);
      const prevY = getYPosition(data[i - 1].amount);
      
      // Create smooth curve using quadratic bezier
      const cpX = (prevX + x) / 2;
      path += ` Q ${cpX} ${prevY}, ${x} ${y}`;
    }
    
    return path;
  };

  return (
    <div style={{ width: '100%', height: '260px' }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
        {/* Background */}
        <rect
          x={padding.left}
          y={padding.top}
          width={chartWidth - padding.left - padding.right}
          height={chartHeight - padding.top - padding.bottom}
          fill="#F9FAFB"
        />
        
        {/* Grid Lines */}
        {[0, 6000, 12000, 18000, 24000].map((value) => {
          const y = getYPosition(value);
          return (
            <line
              key={value}
              x1={padding.left}
              x2={chartWidth - padding.right}
              y1={y}
              y2={y}
              stroke="#e0e0e0"
              strokeDasharray="3 3"
            />
          );
        })}
        
        {/* X and Y axis lines */}
        <line
          x1={padding.left}
          x2={chartWidth - padding.right}
          y1={chartHeight - padding.bottom}
          y2={chartHeight - padding.bottom}
          stroke="#e0e0e0"
        />
        <line
          x1={padding.left}
          x2={padding.left}
          y1={padding.top}
          y2={chartHeight - padding.bottom}
          stroke="#e0e0e0"
        />
        
        {/* Y-axis labels */}
        {[0, 6000, 12000, 18000, 24000].map((value) => {
          const y = getYPosition(value);
          return (
            <text
              key={value}
              x={padding.left - 10}
              y={y + 4}
              textAnchor="end"
              fill="#888888"
              fontSize="11"
            >
              {value}
            </text>
          );
        })}
        
        {/* X-axis labels */}
        {data.map((point, index) => {
          const x = getXPosition(index);
          return (
            <text
              key={point.month}
              x={x}
              y={chartHeight - padding.bottom + 20}
              textAnchor="middle"
              fill="#888888"
              fontSize="11"
            >
              {point.month}
            </text>
          );
        })}
        
        {/* Line */}
        <path
          d={createSmoothPath()}
          fill="none"
          stroke="#1a3a5c"
          strokeWidth="2"
        />
        
        {/* Data points */}
        {data.map((point, index) => {
          const x = getXPosition(index);
          const y = getYPosition(point.amount);
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="5"
              fill="#f5a623"
              stroke="#ffffff"
              strokeWidth="2"
            />
          );
        })}
      </svg>
    </div>
  );
};

const Prediction = () => {
  const [loading, setLoading] = useState(true);
  const [predictionData, setPredictionData] = useState(null);

  // Default prediction data matching the design
  const defaultPredictionData = [
    { month: 'Oct', amount: 14000 },
    { month: 'Nov', amount: 18500 },
    { month: 'Dec', amount: 23000 },
    { month: 'Jan', amount: 18000 },
    { month: 'Feb', amount: 20000 },
    { month: 'Mar', amount: 15000 },
    { month: 'Apr', amount: 17000 },  // Predicted
    { month: 'May', amount: 16500 }   // Predicted
  ];

  useEffect(() => {
    const loadPredictionData = async () => {
      setLoading(true);
      try {
        // In a real app, fetch from analyticsApi
        const response = await analyticsApi.getAnalytics();
        if (response.success && response.data.prediction) {
          // Process prediction data from API response
          const processedData = processPredictionData(response.data.prediction);
          setPredictionData(processedData);
        } else {
          // Fall back to default data
          setPredictionData(defaultPredictionData);
        }
      } catch (error) {
        console.error('Failed to load prediction data:', error);
        // Fall back to default data
        setPredictionData(defaultPredictionData);
      } finally {
        setLoading(false);
      }
    };

    loadPredictionData();
  }, []);

  // Process prediction data from API response
  const processPredictionData = (apiData) => {
    // Convert API data format to our chart format
    // For now, return default data
    return defaultPredictionData;
  };

  // Calculate prediction statistics
  const calculatePredictionStats = (data) => {
    if (!data || data.length === 0) return { 
      nextMonthEstimate: 0, 
      trend: 'Stable', 
      savingsPotential: 0 
    };
    
    const currentMonth = data[data.length - 3].amount; // Mar
    const nextMonthEstimate = data[data.length - 1].amount; // May
    
    const trend = nextMonthEstimate < currentMonth ? 'Decreasing' : 
                 nextMonthEstimate > currentMonth ? 'Increasing' : 'Stable';
    
    const savingsPotential = currentMonth - nextMonthEstimate;
    
    return {
      nextMonthEstimate,
      trend,
      savingsPotential: Math.max(0, savingsPotential)
    };
  };

  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  if (loading) {
    return (
      <div className="predict-page">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading prediction data...</p>
        </div>
      </div>
    );
  }

  const stats = calculatePredictionStats(predictionData);

  return (
    <div className="predict-page">
      {/* Spending Prediction Chart Card */}
      <div className="prediction-chart-card">
        <h3 className="chart-title">Spending Prediction</h3>
        <PredictionLineChart data={predictionData || defaultPredictionData} />
      </div>

      {/* Prediction Summary Card */}
      <div className="prediction-summary-card">
        <div className="prediction-summary-title">
          <span>📊</span>
          <span>Prediction Summary</span>
        </div>
        
        <div className="prediction-rows">
          <div className="prediction-row">
            <span className="prediction-label">Next month estimate</span>
            <span className="prediction-value">{formatCurrency(stats.nextMonthEstimate)}</span>
          </div>
          
          <div className="prediction-row">
            <span className="prediction-label">Trend direction</span>
            <span className={`prediction-value ${stats.trend === 'Decreasing' ? 'decreasing' : 'increasing'}`}>
              {stats.trend === 'Decreasing' ? '↓ Decreasing' : '↑ Increasing'}
            </span>
          </div>
          
          <div className="prediction-row">
            <span className="prediction-label">Savings potential</span>
            <span className="prediction-value savings">{formatCurrency(stats.savingsPotential)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prediction;
