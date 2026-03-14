import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import '../styles/FinnyHomeScreen.css';

const QuickTransactionsPage = () => {
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
            <h1 className="app-title">Quick Mode</h1>
            <p className="app-subtitle">Fast & Simple Transactions</p>
          </div>
        </div>
      </div>
      
      <div className="main-content">
        <div className="monthly-summary-card">
          <h2 className="card-title">Quick Transactions</h2>
          <p>Quick transaction interface will be implemented here.</p>
        </div>
      </div>
    </div>
  );
};

export default QuickTransactionsPage;
