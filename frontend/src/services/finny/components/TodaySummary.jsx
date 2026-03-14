import React from 'react';

const TodaySummary = ({ todayData }) => {
  const categoryColors = {
    'Food': '#0F4C5C',
    'Transport': '#2C7DA0',
    'Shopping': '#F4B400',
    'Bills': '#2E8B57',
    'Entertainment': '#E67E22'
  };

  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  const categories = todayData?.categories || {};
  const total = todayData?.total || 0;

  if (Object.keys(categories).length === 0) {
    return (
      <div className="today-summary">
        <div className="summary-header">
          <h3>Today's Summary</h3>
        </div>
        <div className="summary-content">
          <div className="summary-total">
            <span className="total-amount">{formatCurrency(0)}</span>
          </div>
          <div className="summary-empty">
            <p>No expenses today</p>
            <p>Start tracking with natural language!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="today-summary">
      <div className="summary-header">
        <h3>Today's Summary</h3>
      </div>
      <div className="summary-content">
        <div className="summary-total">
          <span className="total-amount">{formatCurrency(total)}</span>
        </div>
        <div className="category-breakdown">
          {Object.entries(categories).map(([category, amount]) => (
            <div key={category} className="category-item">
              <div className="category-info">
                <div 
                  className="category-dot" 
                  style={{ backgroundColor: categoryColors[category] || '#6B7280' }}
                ></div>
                <span className="category-name">{category}</span>
              </div>
              <div className="category-amount">{formatCurrency(amount)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TodaySummary;
