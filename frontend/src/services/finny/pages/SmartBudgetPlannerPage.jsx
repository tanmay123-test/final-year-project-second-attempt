import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, Settings, User } from 'lucide-react';
import '../styles/SmartBudgetPlannerPage.css';

const SmartBudgetPlannerPage = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate(-1); // Go back to previous page
  };

  const handleFeatureClick = (route) => {
    navigate(route);
  };

  const features = [
    {
      icon: '📋',
      title: 'Create Financial Plan (U-Plan)',
      description: 'Build a personalized financial plan based on income and expenses.',
      buttonText: 'Create Plan',
      route: '/finny/budget/create-plan'
    },
    {
      icon: '📊',
      title: 'Budget Status & Monitoring',
      description: 'Track live budget progress across all categories.',
      buttonText: 'View Status',
      route: '/finny/budget/status'
    },
    {
      icon: '🔥',
      title: 'Burn Rate Analysis',
      description: 'Analyze spending velocity and predict month-end totals.',
      buttonText: 'Analyze',
      route: '/finny/budget/burn-rate'
    },
    {
      icon: '📄',
      title: 'Monthly Spending Report',
      description: 'Generate detailed monthly financial reports.',
      buttonText: 'View Report',
      route: '/finny/budget/report'
    },
    {
      icon: '🏆',
      title: 'Budget Gamification',
      description: 'Earn rewards for smart budgeting and saving habits.',
      buttonText: 'Explore',
      route: '/finny/budget/gamification'
    },
    {
      icon: '🐷',
      title: 'Leftover Budget Management',
      description: 'Optimize remaining budget and move to goal jars.',
      buttonText: 'Manage',
      route: '/finny/budget/leftover'
    }
  ];

  return (
    <div className="smart-budget-page">
      {/* Header */}
      <div className="smart-budget-header">
        <div className="header-left">
          <button className="back-btn" onClick={handleBackClick}>
            <ArrowLeft size={20} color="white" />
          </button>
          <div className="header-title-section">
            <div className="header-title">
              <span className="header-icon">📋</span>
              Smart Budget Planner
            </div>
            <div className="header-subtitle">U-Plan Financial System</div>
          </div>
        </div>
        
        <div className="header-right">
          <button className="header-icon-btn">
            <Bell size={18} />
          </button>
          <button className="header-icon-btn">
            <Settings size={18} />
          </button>
          <button className="header-icon-btn profile">
            <User size={18} />
          </button>
        </div>
      </div>

      {/* Page Subtitle */}
      <div className="page-subtitle">
        Plan, track, and optimize your monthly budget.
      </div>

      {/* Feature Cards Grid */}
      <div className="feature-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-icon-wrap">
              <span className="feature-icon">{feature.icon}</span>
            </div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-desc">{feature.description}</p>
            <button 
              className="feature-btn"
              onClick={() => handleFeatureClick(feature.route)}
            >
              {feature.buttonText}
            </button>
          </div>
        ))}
      </div>

      {/* Bottom Navigation */}
      <div className="finny-bottom-nav">
        <div 
          className="nav-item"
          onClick={() => navigate('/finny')}
        >
          <div className="nav-icon">💰</div>
          <div className="nav-label">Finny</div>
        </div>
        <div 
          className="nav-item active"
          onClick={() => navigate('/finny/budget')}
        >
          <div className="nav-icon">📊</div>
          <div className="nav-label">Budget</div>
        </div>
        <div 
          className="nav-item"
          onClick={() => navigate('/finny/loan')}
        >
          <div className="nav-icon">📈</div>
          <div className="nav-label">Loan</div>
        </div>
        <div 
          className="nav-item"
          onClick={() => navigate('/finny/goal-jar')}
        >
          <div className="nav-icon">🎯</div>
          <div className="nav-label">Goal Jar</div>
        </div>
        <div 
          className="nav-item"
          onClick={() => navigate('/finny/ai-coach')}
        >
          <div className="nav-icon">🤖</div>
          <div className="nav-label">AI Coach</div>
        </div>
      </div>
    </div>
  );
};

export default SmartBudgetPlannerPage;
