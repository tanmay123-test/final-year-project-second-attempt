import React, { useState, useEffect } from 'react';
import { ArrowLeft, Plus, List, BarChart3, Brain, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import QuickAddTransactionModal from '../../../components/money/QuickAddTransactionModal';
import QuickAnalyticsSummary from '../../../components/money/QuickAnalyticsSummary';
import '../styles/QuickMode.css';

const QuickMode = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showQuickAddModal, setShowQuickAddModal] = useState(false);
  const [notification, setNotification] = useState(null);

  const handleQuickAddSuccess = (transaction) => {
    setNotification(`₹${transaction.amount} – ${transaction.category} at ${transaction.merchant}`);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
      setNotification(null);
    }, 3000);
  };

  const handleMenuOptionClick = (option) => {
    if (option.action) {
      option.action();
    } else if (option.route) {
      navigate(option.route);
    }
  };

  const menuOptions = [
    {
      id: 'quick-add',
      icon: <Plus size={32} />,
      title: 'Quick Add Transaction',
      description: 'Fast & Simple',
      color: 'blue',
      action: () => setShowQuickAddModal(true)
    },
    {
      id: 'view-transactions',
      icon: <List size={32} />,
      title: 'View Transactions',
      description: 'View & Search',
      color: 'gray',
      route: '/money/transactions'
    },
    {
      id: 'monthly-summary',
      icon: <BarChart3 size={32} />,
      title: 'Monthly Summary',
      description: 'Spending Overview',
      color: 'green',
      route: '/money/summary'
    },
    {
      id: 'analytics',
      icon: <Brain size={32} />,
      title: 'Advanced Analytics Dashboard',
      description: 'Deep Insights',
      color: 'orange',
      route: '/money/analytics'
    }
  ];

  return (
    <div className="finny-mobile-container">
      {/* Mobile Header */}
      <header className="finny-header">
        <button className="back-btn" onClick={() => navigate('/money/dashboard')}>
          <ArrowLeft size={24} />
        </button>
        <div className="header-title">
          <h1>Quick Mode</h1>
          <p>Fast & Simple tracking</p>
        </div>
        <div className="header-spacer"></div>
      </header>

      {/* Main Content - Analytics Summary and Menu Options */}
      <main className="finny-main-content">
        {/* Quick Analytics Summary */}
        <QuickAnalyticsSummary />

        {/* Menu Options */}
        <div className="menu-options-grid">
          {menuOptions.map((option) => (
            <div
              key={option.id}
              className="menu-option-card"
              onClick={() => handleMenuOptionClick(option)}
            >
              <div className={`option-icon ${option.color}`}>
                {option.icon}
              </div>
              <div className="option-content">
                <h3>{option.title}</h3>
                <p>{option.description}</p>
              </div>
              <div className="option-arrow">
                <ArrowLeft size={20} style={{ transform: 'rotate(180deg)' }} />
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Success Notification */}
      {notification && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-pulse">
          Transaction added successfully.
          <div className="text-sm opacity-90">{notification}</div>
        </div>
      )}

      {/* Quick Add Modal */}
      <QuickAddTransactionModal
        isOpen={showQuickAddModal}
        onClose={() => setShowQuickAddModal(false)}
        onSuccess={handleQuickAddSuccess}
      />

      {/* Bottom Navigation */}
      <div className="finny-bottom-nav">
        <button className="bottom-nav-item active">
          <div className="nav-icon finny-icon">F</div>
          <span>Finny</span>
        </button>
        <button className="bottom-nav-item">
          <div className="nav-icon budget-icon">B</div>
          <span>Budget</span>
        </button>
        <button className="bottom-nav-item">
          <div className="nav-icon loan-icon">L</div>
          <span>Loan</span>
        </button>
        <button className="bottom-nav-item">
          <div className="nav-icon goal-icon">G</div>
          <span>Goal Jar</span>
        </button>
        <button className="bottom-nav-item">
          <div className="nav-icon ai-icon">AI</div>
          <span>AI Coach</span>
        </button>
      </div>
    </div>
  );
};

export default QuickMode;
