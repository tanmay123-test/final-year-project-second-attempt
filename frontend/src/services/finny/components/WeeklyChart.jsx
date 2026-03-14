import React from 'react';

const WeeklyChart = ({ weeklySpending }) => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  // Handle different data formats and ensure we have values for all days
  const processedData = days.reduce((acc, day) => {
    acc[day] = weeklySpending?.[day] || 0;
    return acc;
  }, {});

  const maxValue = Math.max(...Object.values(processedData), 1); // Ensure at least 1 to avoid division by zero

  const getBarHeight = (value) => {
    return maxValue > 0 ? (value / maxValue) * 100 : 0;
  };

  if (!weeklySpending || Object.keys(weeklySpending).length === 0) {
    return (
      <div className="weekly-chart-empty">
        <div className="empty-chart-message">
          <p>No weekly spending data available</p>
          <p>Add transactions to see your weekly analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="weekly-chart">
      <div className="chart-header">
        <h3>Weekly Spending</h3>
      </div>
      
      <div className="chart-container">
        <div className="chart-bars">
          {days.map((day, index) => {
            const amount = processedData[day] || 0;
            const height = getBarHeight(amount);
            
            return (
              <div key={day} className="chart-bar-container">
                <div className="chart-bar" style={{ height: `${height}%` }}></div>
                <div className="chart-label">{day}</div>
                <div className="chart-value">{formatCurrency(amount)}</div>
                <div className="chart-tooltip">
                  <div className="tooltip-content">
                    <div className="tooltip-day">{day}</div>
                    <div className="tooltip-amount">Amount: {formatCurrency(amount)}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default WeeklyChart;
