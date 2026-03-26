import React, { useState } from 'react';
import { ArrowLeft, Bell, Settings, User, Calculator, ArrowUpDown, TrendingDown, TrendingUp, CreditCard, FileText, Shield, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import '../styles/LoanPage.css';

const SmartLoanAnalyzerPage = () => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    navigate('/finny/money');
  };

  const handleCardClick = (route) => {
    navigate(route);
  };

  const loanFeatures = [
    {
      icon: Calculator,
      title: 'Analyze Single Loan',
      subtitle: 'Calculate EMI, total interest, affordability, and loan risk.',
      badge: 'Analyze Loan',
      route: '/finny/loan/analyze'
    },
    {
      icon: ArrowUpDown,
      title: 'Compare Two Loans',
      subtitle: 'Compare EMI, interest, and total repayment between two loan options.',
      badge: 'Compare Loans',
      route: '/finny/loan/compare'
    },
    {
      icon: TrendingDown,
      title: 'Loan Impact Simulation',
      subtitle: 'Understand how a loan affects your monthly finances.',
      badge: 'Simulate Impact',
      route: '/finny/loan/impact'
    },
    {
      icon: CreditCard,
      title: 'Early Repayment Simulation',
      subtitle: 'Calculate interest savings by paying extra each month.',
      badge: 'Simulate Savings',
      route: '/finny/loan/early-repayment'
    },
    {
      icon: FileText,
      title: 'Generate Repayment Schedule',
      subtitle: 'See month-by-month breakdown of loan payments.',
      badge: 'Generate Schedule',
      route: '/finny/loan/schedule'
    },
    {
      icon: Shield,
      title: 'Loan Risk Assessment',
      subtitle: 'Evaluate the risk level of a loan using financial metrics.',
      badge: 'Assess Risk',
      route: '/finny/loan/risk'
    },
    {
      icon: Clock,
      title: 'Loan Analysis History',
      subtitle: 'View past loan analyses and comparisons.',
      badge: 'View History',
      route: '/finny/loan/history'
    }
  ];

  return (
    <div className="smart-loan-analyzer-page">
      {/* Header */}
      <div className="loan-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="header-content">
          <div className="header-title-section">
            <Calculator size={22} color="white" />
            <div className="header-text">
              <h1 className="header-title">Smart Loan Analyzer</h1>
              <p className="header-subtitle">Analyze loan affordability, risks, and repayment strategies.</p>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-button">
            <Bell size={20} color="white" />
          </button>
          <button className="icon-button">
            <Settings size={20} color="white" />
          </button>
          <div className="user-avatar">
            <User size={16} color="white" />
          </div>
        </div>
      </div>

      {/* Menu Cards List */}
      <div className="loan-cards-container">
        {loanFeatures.map((feature, index) => (
          <div key={index} className="loan-card" onClick={() => handleCardClick(feature.route)}>
            <div className="card-left">
              <div className="card-icon-circle">
                <feature.icon size={24} color="#0F172A" />
              </div>
            </div>
            <div className="card-center">
              <h3 className="card-title">{feature.title}</h3>
              <p className="card-subtitle">{feature.subtitle}</p>
            </div>
            <div className="card-right">
              <div className="card-badge">{feature.badge}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Back Button (shown when header is hidden/scrolled) */}
      <div className="bottom-back-button">
        <button className="back-to-money-btn">
          🏠 Back to Money Service
        </button>
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-nav">
        <div className="nav-item" onClick={() => navigate('/finny')}>
          <span className="nav-icon">🏠</span>
          <span className="nav-label">Finny</span>
        </div>
        <div className="nav-item active" onClick={() => navigate('/finny/loan')}>
          <TrendingUp size={20} color="#F59E0B" />
          <span className="nav-label">Loan</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/goal-jar')}>
          <span className="nav-icon">🎯</span>
          <span className="nav-label">Goal Jar</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/ai-coach')}>
          <span className="nav-icon">🧠</span>
          <span className="nav-label">AI Coach</span>
        </div>
      </div>
    </div>
  );
};

export default SmartLoanAnalyzerPage;
