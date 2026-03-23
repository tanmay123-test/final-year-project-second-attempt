import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Bell, Settings, User, Plus, MessageSquare, BarChart3, Home, PiggyBank, Calculator, Target, Brain } from 'lucide-react';
import { moneyService } from '../../../shared/api';
import '../styles/FinnyHomeScreen.css';

const FinnyHomeScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [monthlyData, setMonthlyData] = useState({
    totalSpending: 0,
    categories: []
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getDashboardData();
      
      // Transform backend data to match our UI structure
      const backendData = response.data;
      const categoryColors = {
        'Food': '#0F4C5C',
        'Shopping': '#F4B400',
        'Bills': '#2E8B57',
        'Transport': '#2C7DA0',
        'Entertainment': '#E67E22'
      };

      const transformedData = {
        totalSpending: backendData.total_spending || 0,
        categories: (backendData.categories || []).map(cat => ({
          name: cat.category || cat.name || 'Other',
          amount: cat.amount || 0,
          color: cat.color || categoryColors[cat.category || cat.name] || '#6B7280'
        }))
      };

      setMonthlyData(transformedData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load data');
      
      // Fallback data
      setMonthlyData({
        totalSpending: 15200,
        categories: [
          { name: 'Food', amount: 4200, color: '#0F4C5C' },
          { name: 'Shopping', amount: 3800, color: '#F4B400' },
          { name: 'Bills', amount: 3200, color: '#2E8B57' },
          { name: 'Transport', amount: 1900, color: '#2C7DA0' },
          { name: 'Entertainment', amount: 2100, color: '#E67E22' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const donutChartData = monthlyData.categories.map(cat => ({
    ...cat,
    percentage: (cat.amount / monthlyData.totalSpending) * 100
  }));

  const createDonutPath = (data, index, total) => {
    const startAngle = index === 0 ? 0 : data.slice(0, index).reduce((acc, curr) => acc + curr.percentage, 0);
    const endAngle = startAngle + data[index].percentage;
    
    const startAngleRad = (startAngle * 3.14159) / 180;
    const endAngleRad = (endAngle * 3.14159) / 180;
    
    const x1 = 50 + 40 * Math.cos(startAngleRad - 3.14159 / 2);
    const y1 = 50 + 40 * Math.sin(startAngleRad - 3.14159 / 2);
    const x2 = 50 + 40 * Math.cos(endAngleRad - 3.14159 / 2);
    const y2 = 50 + 40 * Math.sin(endAngleRad - 3.14159 / 2);
    
    const largeArcFlag = data[index].percentage > 50 ? 1 : 0;
    
    return `M ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} L 50 50 Z`;
  };

  const modeCards = [
    {
      title: 'Quick Mode',
      subtitle: 'Fast & Simple',
      description: 'Quick add transactions, view history, monthly summary & advanced analytics.',
      icon: Plus,
      iconBg: '#1F5F7A',
      buttonText: 'Open Quick Mode',
      navigation: '/finny/quick'
    },
    {
      title: 'Chat Mode',
      subtitle: 'Natural Language',
      description: 'Chat-style expense entry, natural language input & today\'s summary.',
      icon: MessageSquare,
      iconBg: '#F4B400',
      buttonText: 'Open Chat Mode',
      navigation: '/finny/chat'
    },
    {
      title: 'Analytics Mode',
      subtitle: 'Deep Insights',
      description: 'Financial dashboard, budget monitoring, predictions & health score.',
      icon: BarChart3,
      iconBg: '#2E8B57',
      buttonText: 'Open Analytics Mode',
      navigation: '/finny/analytics'
    }
  ];

  const bottomNavItems = [
    { icon: Home, label: 'Finny', path: '/finny', active: location.pathname === '/finny' },
    { icon: PiggyBank, label: 'Budget', path: '/finny/budget', active: location.pathname === '/finny/budget' },
    { icon: Calculator, label: 'Loan', path: '/finny/loan', active: location.pathname === '/finny/loan' },
    { icon: Target, label: 'Goal Jar', path: '/finny/goals', active: location.pathname === '/finny/goals' },
    { icon: Brain, label: 'AI Coach', path: '/finny/coach', active: location.pathname === '/finny/coach' }
  ];

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
            <div 
              key={index} 
              className={`sidebar-item ${item.active ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
              style={{ cursor: 'pointer' }}
            >
              <item.icon size={20} color={item.active ? '#F4B400' : '#6B7280'} />
              <span className="sidebar-label">{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      <div className="finny-page-content">
        <div className="finny-home-screen">
          {/* Header */}
          <div className="finny-header">
            <div className="header-content">
              <div className="header-text">
                <h1 className="app-title">Unified Finny</h1>
                <p className="app-subtitle">Smart Transaction Tracker</p>
              </div>
              <div className="header-icons">
                <div className="icon-button">
                  <Bell size={20} />
                </div>
                <div className="icon-button">
                  <Settings size={20} />
                </div>
                <div className="user-avatar">
                  <User size={20} />
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="main-content">
            {/* Monthly Summary Card */}
            <div className="monthly-summary-card">
              <h2 className="card-title">Monthly Summary</h2>
              {loading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading your financial data...</p>
                </div>
              ) : error ? (
                <div className="error-state">
                  <p>{error}</p>
                  <button onClick={fetchDashboardData} className="retry-button">Retry</button>
                </div>
              ) : (
                <div className="summary-content">
                  <div className="donut-chart-container">
                    <svg viewBox="0 0 100 100" className="donut-chart">
                      {donutChartData.map((segment, index) => (
                        <path
                          key={index}
                          d={createDonutPath(donutChartData, index, monthlyData.totalSpending)}
                          fill={segment.color}
                          className="chart-segment"
                        />
                      ))}
                      <circle cx="50" cy="50" r="25" fill="white" />
                    </svg>
                  </div>
                  <div className="summary-details">
                    <div className="total-spending">
                      <p className="total-label">Total Spending</p>
                      <p className="total-amount">₹{monthlyData.totalSpending.toLocaleString()}</p>
                    </div>
                    <div className="categories-list">
                      {monthlyData.categories.map((category, index) => (
                        <div key={index} className="category-item">
                          <div className="category-info">
                            <div 
                              className="category-dot" 
                              style={{ backgroundColor: category.color }}
                            ></div>
                            <span className="category-name">{category.name}</span>
                          </div>
                          <span className="category-amount">₹{category.amount.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Select Mode Section */}
            <div className="mode-section">
              <h2 className="section-title">Select Mode</h2>
              
              {/* Mode Cards */}
              <div className="mode-cards">
                {modeCards.map((mode, index) => (
                  <div key={index} className="mode-card">
                    <div className="mode-content">
                      <div className="mode-left">
                        <div 
                          className="mode-icon-circle"
                          style={{ backgroundColor: mode.iconBg }}
                        >
                          <mode.icon size={24} color="white" />
                        </div>
                        <div className="mode-text">
                          <h3 className="mode-title">{mode.title}</h3>
                          <p className="mode-subtitle">{mode.subtitle}</p>
                          <p className="mode-description">{mode.description}</p>
                        </div>
                      </div>
                    </div>
                    <button 
                      className="mode-button"
                      onClick={() => navigate(mode.navigation)}
                    >
                      {mode.buttonText}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Navigation for Mobile */}
          <div className="finny-bottom-nav">
            {bottomNavItems.map((item, index) => (
              <div 
                key={index} 
                className={`nav-item ${item.active ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
                style={{ cursor: 'pointer' }}
              >
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

export default FinnyHomeScreen;
