import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, List, PieChart, BarChart3, Home, PiggyBank, Calculator, Target, Brain } from 'lucide-react';
import { summaryApi } from '../api/summaryApi';
import CategoryChart from '../components/CategoryChart';
import CategoryBreakdown from '../components/CategoryBreakdown';
import StatisticsCards from '../components/StatisticsCards';
import '../styles/SummaryPage.css';

const SummaryPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summaryData, setSummaryData] = useState({
    categories: [],
    totalSpent: 0,
    dailyAverage: 0,
    month: '',
    daysInPeriod: 30
  });

  useEffect(() => {
    fetchSummaryData();
  }, []);

  const fetchSummaryData = async () => {
    try {
      setLoading(true);
      const result = await summaryApi.getMonthlySummary();
      
      if (result.success) {
        setSummaryData(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Failed to fetch summary data:', err);
      setError('Failed to load summary data');
      
      // Set fallback data for testing
      setSummaryData({
        categories: [
          { name: 'Transport', amount: 1400 },
          { name: 'Food', amount: 1122 },
          { name: 'Entertainment', amount: 900 },
          { name: 'Shopping', amount: 500 },
          { name: 'Other', amount: 200 }
        ],
        totalSpent: 6789,
        dailyAverage: 226,
        month: '2026-03',
        daysInPeriod: 30
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
      <div className="summary-page">
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
          <p>Loading summary data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="summary-page">
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
          <button onClick={fetchSummaryData} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="summary-page">
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
              className={`tab ${tab.id === 'summary' ? 'active' : ''}`}
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
        {/* Category Breakdown Card */}
        <div className="category-breakdown-card">
          <h2 className="card-title">Category Breakdown</h2>
          <div className="breakdown-content">
            <div className="chart-container">
              <CategoryChart 
                categories={summaryData.categories} 
                totalSpending={summaryData.totalSpent}
              />
            </div>
            <div className="breakdown-list">
              <CategoryBreakdown categories={summaryData.categories} />
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        <StatisticsCards 
          totalSpent={summaryData.totalSpent}
          dailyAverage={summaryData.dailyAverage}
          daysInPeriod={summaryData.daysInPeriod}
        />
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
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
  );
};

export default SummaryPage;
