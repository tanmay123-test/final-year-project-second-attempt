import React from 'react';

const FinancialHealth = ({ healthScore, healthStatus, healthDescription }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return '#2E8B57'; // Green
    if (score >= 60) return '#F4B400'; // Yellow
    if (score >= 40) return '#E67E22'; // Orange
    return '#DC2626'; // Red
  };

  const getScoreText = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  // Ensure we have valid values
  const score = healthScore || 0;
  const status = healthStatus || getScoreText(score);
  const description = healthDescription || 'Unable to calculate financial health';

  const circumference = 2 * Math.PI * 35; // radius = 35
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="financial-health">
      <div className="health-header">
        <h3>Financial Health Score</h3>
      </div>
      
      <div className="health-content">
        <div className="health-circle-container">
          <div className="health-circle">
            <svg width="120" height="120" viewBox="0 0 120 120">
              {/* Background circle */}
              <circle
                cx="60"
                cy="60"
                r="35"
                fill="none"
                stroke="#E5E7EB"
                strokeWidth="8"
              />
              
              {/* Progress circle */}
              <circle
                cx="60"
                cy="60"
                r="35"
                fill="none"
                stroke={getScoreColor(score)}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                transform="rotate(-90 60 60)"
              />
              
              {/* Score text */}
              <text
                x="60"
                y="60"
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="18"
                fontWeight="bold"
                fill="#1F2937"
              >
                {score}
              </text>
            </svg>
          </div>
          
          <div className="health-info">
            <div className="score-text" style={{ color: getScoreColor(score) }}>
              {status}
            </div>
            <div className="score-description">
              {description}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialHealth;
