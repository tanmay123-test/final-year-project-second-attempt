import React from 'react';

const StatisticsCards = ({ totalSpent, dailyAverage, daysInPeriod = 30 }) => {
  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  return (
    <div className="statistics-cards">
      {/* Total Spent Card */}
      <div className="stat-card">
        <div className="stat-content">
          <h3 className="stat-title">Total Spent</h3>
          <p className="stat-value">{formatCurrency(totalSpent)}</p>
        </div>
      </div>

      {/* Daily Average Card */}
      <div className="stat-card">
        <div className="stat-content">
          <h3 className="stat-title">Daily Avg</h3>
          <p className="stat-value">{formatCurrency(dailyAverage)}</p>
        </div>
      </div>
    </div>
  );
};

export default StatisticsCards;
