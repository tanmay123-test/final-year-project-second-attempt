import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, List, PieChart, BarChart3, Home, PiggyBank, Calculator, Target, Brain } from 'lucide-react';
import { analyticsApi } from '../api/analyticsApi';
import WeeklyChart from '../components/WeeklyChart';
import FinancialHealth from '../components/FinancialHealth';
import Prediction from '../components/Prediction';
import '../styles/AnalyticsPage.css';

const AnalyticsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyticsData, setAnalyticsData] = useState({
    weekly_spending: {},
    financial_health_score: 0,
    health_status: 'Poor',
    health_description: '',
    prediction: { monthly_estimate: 0 }
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const result = await analyticsApi.getAnalytics();
      
      if (result.success) {
        setAnalyticsData(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Failed to fetch analytics data:', err);
      setError('Failed to load analytics data');
      
      // Set fallback data for testing
      setAnalyticsData({
        weekly_spending: {
          'Mon': 450,
          'Tue': 320,
          'Wed': 680,
          'Thu': 200,
          'Fri': 520,
          'Sat': 890,
          'Sun': 340
        },
        financial_health_score: 72,
        health_status: 'Good',
        health_description: 'Your spending is reasonably balanced. Consider reducing dining out expenses.',
        prediction: { monthly_estimate: 8200 }
      });
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'quick-add', label: 'Quick Add', icon: Plus },
    { id: 'transactions', label: 'Transactions', icon: List },
    { id: 'summary', label: 'Summary', icon: PieChart },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

  const bottomNavItems = [
    { icon: Home, label: 'Finny', active: false },
    { icon: PiggyBank, label: 'Budget', active: false },
    { icon: Calculator, label: 'Loan', active: false },
    { icon: Target, label: 'Goal Jar', active: false },
    { icon: Brain, label: 'AI Coach', active: false }
  ];

  if (loading) {
    return (
      <div className="analytics-page">
        {/* Header */}
        <div className="header">
          <div className="header-content">
            <button 
              className="back-button" 
              onClick={() => navigate('/finny')}
            >
              <ArrowLeft size={20} />
            </button>
            <div className="header-text">
              <h1 className="header-title">Quick Mode</h1>
              <p className="header-subtitle">Fast & Simple tracking</p>
            </div>
          </div>
        </div>

        {/* Loading State */}
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-page">
        {/* Header */}
        <div className="header">
          <div className="header-content">
            <button 
              className="back-button" 
              onClick={() => navigate('/finny')}
            >
              <ArrowLeft size={20} />
            </button>
            <div className="header-text">
              <h1 className="header-title">Quick Mode</h1>
              <p className="header-subtitle">Fast & Simple tracking</p>
            </div>
          </div>
        </div>

        {/* Error State */}
        <div className="error-state">
          <p>{error}</p>
          <button onClick={fetchAnalyticsData} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="finny-page-layout">
      {/* Sidebar for Desktop */}
      <aside className="finny-sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">Finny</h1>
          <p className="sidebar-subtitle">Smart Tracker</p>
        </div>
        <nav className="sidebar-nav">
          {bottomNavItems.map((item, index) => (
            <div key={index} className={`sidebar-item ${item.label === 'Finny' ? 'active' : ''}`}>
              <item.icon size={20} color={item.label === 'Finny' ? '#F4B400' : '#6B7280'} />
              <span className="sidebar-label">{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      <div className="finny-page-content">
        <div className="analytics-page">
          {/* Header */}
          <div className="header">
            <div className="header-content">
              <button 
                className="back-button" 
                onClick={() => navigate('/finny')}
              >
                <ArrowLeft size={20} />
              </button>
              <div className="header-text">
                <h1 className="header-title">Quick Mode</h1>
                <p className="header-subtitle">Fast & Simple tracking</p>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="mode-switch-bar">
            <div className="tabs-container">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`tab ${tab.id === 'analytics' ? 'active' : ''}`}
                  onClick={() => {/* Tab switching handled by parent */}}
                >
                  <tab.icon size={16} />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="main-section">
            {/* Weekly Spending Chart */}
            <div className="analytics-card">
              <WeeklyChart weeklySpending={analyticsData.weekly_spending} />
            </div>

            {/* Financial Health Score */}
            <div className="analytics-card">
              <FinancialHealth 
                healthScore={analyticsData.financial_health_score}
                healthStatus={analyticsData.health_status}
                healthDescription={analyticsData.health_description}
              />
            </div>

            {/* Spending Prediction */}
            <div className="analytics-card">
              <Prediction prediction={analyticsData.prediction} />
            </div>
          </div>

          {/* Bottom Navigation for Mobile */}
          <div className="finny-bottom-nav">
            {bottomNavItems.map((item, index) => (
              <div key={index} className={`nav-item ${item.active ? 'active' : ''}`}>
                <item.icon 
                  size={20} 
                  color={item.active ? '#F4B400' : '#6B7280'} 
                />
                <span className={`nav-label ${item.active ? 'active' : ''}`}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
