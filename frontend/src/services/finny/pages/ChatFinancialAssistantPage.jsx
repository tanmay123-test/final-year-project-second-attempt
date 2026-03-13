import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import '../styles/FinnyHomeScreen.css';

const ChatFinancialAssistantPage = () => {
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
            <h1 className="app-title">Chat Mode</h1>
            <p className="app-subtitle">Natural Language Assistant</p>
          </div>
        </div>
      </div>
      
      <div className="main-content">
        <div className="monthly-summary-card">
          <h2 className="card-title">Chat Interface</h2>
          <p>Chat-style expense entry will be implemented here.</p>
        </div>
      </div>
    </div>
  );
};

export default ChatFinancialAssistantPage;
