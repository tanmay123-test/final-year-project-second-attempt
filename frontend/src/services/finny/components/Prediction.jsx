import React from 'react';

const Prediction = ({ prediction }) => {
  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  // Ensure we have valid prediction data
  const monthlyEstimate = prediction?.monthly_estimate || 0;

  return (
    <div className="prediction">
      <div className="prediction-header">
        <h3>Spending Prediction</h3>
        <p className="prediction-subtitle">Based on your current pace</p>
      </div>
      
      <div className="prediction-content">
        <div className="prediction-main">
          <div className="prediction-label">Estimated Monthly Spending</div>
          <div className="prediction-amount">{formatCurrency(monthlyEstimate)}</div>
        </div>
        
        <div className="prediction-details">
          <div className="detail-item">
            <div className="detail-icon">📊</div>
            <div className="detail-text">
              <div className="detail-title">Calculation Logic</div>
              <div className="detail-description">Average daily spending × 30</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prediction;
