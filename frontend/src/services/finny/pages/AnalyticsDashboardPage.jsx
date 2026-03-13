import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import '../styles/FinnyHomeScreen.css';

const AnalyticsDashboardPage = () => {
  const navigate = useNavigate();

  return (
    <div className="finny-home-screen">
      <div className="finny-header">
        <div className="header-content">
          <div className="header-text">
            <button 
              className="back-button" 
              onClick={() => navigate('/finny')}
              style={{ 
                background: 'none', 
                border: 'none', 
                color: 'white', 
                marginRight: '12px',
                cursor: 'pointer'
              }}
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="app-title">Analytics Mode</h1>
            <p className="app-subtitle">Deep Financial Insights</p>
          </div>
        </div>
      </div>
      
      <div className="main-content">
        <div className="monthly-summary-card">
          <h2 className="card-title">Analytics Dashboard</h2>
          <p>Financial analytics dashboard will be implemented here.</p>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboardPage;
