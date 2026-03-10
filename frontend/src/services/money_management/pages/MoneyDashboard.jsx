import React, { useState, useEffect } from 'react';
import { Bell, Settings, User, TrendingUp, MessageCircle, PieChart, BarChart3, Brain, List, Target, CreditCard, PiggyBank } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/MoneyDashboard.css';

const MoneyDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('home');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getDashboardData();
      setDashboardData(response.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fallback data for initial display
  const fallbackSpendingData = [
    { category: 'Food', amount: 4500, color: '#FF6B6B' },
    { category: 'Shopping', amount: 3200, color: '#4ECDC4' },
    { category: 'Bills', amount: 2800, color: '#45B7D1' },
    { category: 'Transport', amount: 2200, color: '#96CEB4' },
    { category: 'Entertainment', amount: 2500, color: '#FFEAA7' }
  ];

  const spendingData = dashboardData?.monthly_summary?.categories || fallbackSpendingData;
  const totalSpending = dashboardData?.monthly_summary?.total_spending || 
                       spendingData.reduce((sum, item) => sum + item.amount, 0);

  const createDonutPath = (data, index, total) => {
    const percentage = data[index].amount / total;
    const startAngle = index === 0 ? 0 : data.slice(0, index).reduce((sum, item) => sum + (item.amount / total) * 360, 0);
    const endAngle = startAngle + (percentage * 360);
    
    const startAngleRad = (startAngle - 90) * Math.PI / 180;
    const endAngleRad = (endAngle - 90) * Math.PI / 180;
    
    const x1 = 50 + 40 * Math.cos(startAngleRad);
    const y1 = 50 + 40 * Math.sin(startAngleRad);
    const x2 = 50 + 40 * Math.cos(endAngleRad);
    const y2 = 50 + 40 * Math.sin(endAngleRad);
    
    const largeArcFlag = percentage > 0.5 ? 1 : 0;
    
    return `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your financial dashboard...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="error-container">
          <div className="error-card">
            <p>{error}</p>
            <button className="retry-btn" onClick={fetchDashboardData}>
              Try Again
            </button>
          </div>
        </div>
      );
    }

    switch (activeTab) {
      case 'home':
        return (
          <>
            {/* Header */}
            <header className="money-header">
              <div className="header-content">
                <h1>Unified Finny</h1>
                <p>Manage your finances smartly</p>
              </div>
              <div className="header-actions">
                <button className="header-action-btn">
                  <Bell size={20} />
                </button>
                <button className="header-action-btn">
                  <Settings size={20} />
                </button>
                <button className="header-action-btn">
                  <User size={20} />
                </button>
              </div>
            </header>

            {/* Monthly Summary */}
            <section className="monthly-summary-section">
              <h2>Monthly Summary</h2>
              <div className="summary-card">
                <div className="chart-container">
                  <div className="donut-chart">
                    <svg width="200" height="200" className="transform -rotate-90">
                      {spendingData.map((item, index) => (
                        <path
                          key={index}
                          d={createDonutPath(spendingData, index, totalSpending)}
                          fill={item.color}
                          className="hover:opacity-80 transition-opacity"
                        />
                      ))}
                      <circle cx="100" cy="100" r="60" fill="white" />
                    </svg>
                    <div className="chart-center-text">
                      <div className="total-amount">₹{totalSpending.toLocaleString()}</div>
                      <div className="total-label">Total Spending</div>
                    </div>
                  </div>
                  <div className="categories-list">
                    {spendingData.map((item, index) => (
                      <div key={index} className="category-item">
                        <div className="category-left">
                          <div 
                            className="category-color"
                            style={{ backgroundColor: item.color }}
                          />
                          <span className="category-name">{item.category}</span>
                        </div>
                        <span className="category-amount">₹{item.amount.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Recent Transactions */}
            {dashboardData?.recent_transactions && dashboardData.recent_transactions.length > 0 && (
              <section className="recent-transactions-section">
                <h2>Recent Transactions</h2>
                <div className="transactions-list">
                  {dashboardData.recent_transactions.slice(0, 5).map((transaction, index) => (
                    <div key={index} className="transaction-item">
                      <div className="transaction-info">
                        <h4>{transaction.description || transaction.category}</h4>
                        <p>{transaction.category} • {new Date(transaction.date).toLocaleDateString()}</p>
                      </div>
                      <span className="transaction-amount">₹{transaction.amount.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Mode Selection */}
            <section className="mode-selection-section">
              <div className="mode-cards">
                <div className="mode-card">
                  <div className="mode-header">
                    <div className="mode-icon quick">
                      <TrendingUp size={24} />
                    </div>
                    <div className="mode-info">
                      <h3>Add Transaction</h3>
                      <p>Quick Mode</p>
                    </div>
                  </div>
                  <button 
                    className="mode-btn quick"
                    onClick={() => navigate('/money/add-exact')}
                  >
                    Add Transaction
                  </button>
                </div>

                <div className="mode-card">
                  <div className="mode-header">
                    <div className="mode-icon transactions">
                      <List size={24} />
                    </div>
                    <div className="mode-info">
                      <h3>All Transactions</h3>
                      <p>View & Search</p>
                    </div>
                  </div>
                  <button 
                    className="mode-btn transactions"
                    onClick={() => navigate('/money/transactions')}
                  >
                    View Transactions
                  </button>
                </div>

                <div className="mode-card">
                  <div className="mode-header">
                    <div className="mode-icon chat">
                      <MessageCircle size={24} />
                    </div>
                    <div className="mode-info">
                      <h3>Chat Mode</h3>
                      <p>Natural Language</p>
                    </div>
                  </div>
                  <button 
                    className="mode-btn chat"
                    onClick={() => setActiveTab('chat')}
                  >
                    Open Chat Mode
                  </button>
                </div>

                <div className="mode-card">
                  <div className="mode-header">
                    <div className="mode-icon analytics">
                      <TrendingUp size={24} />
                    </div>
                    <div className="mode-info">
                      <h3>Analytics Mode</h3>
                      <p>Deep Insights</p>
                    </div>
                  </div>
                  <button 
                    className="mode-btn analytics"
                    onClick={() => setActiveTab('analytics')}
                  >
                    Open Analytics Mode
                  </button>
                </div>
              </div>
            </section>
          </>
        );
      
      case 'budget':
        return (
          <div className="error-container">
            <div className="error-card">
              <Target size={48} color="#10b981" />
              <h3>Budget Management</h3>
              <p>Set and track your budgets. Coming soon!</p>
            </div>
          </div>
        );
      
      case 'loan':
        return (
          <div className="error-container">
            <div className="error-card">
              <CreditCard size={48} color="#10b981" />
              <h3>Loan Calculator</h3>
              <p>Calculate and manage your loans. Coming soon!</p>
            </div>
          </div>
        );
      
      case 'goals':
        return (
          <div className="error-container">
            <div className="error-card">
              <PiggyBank size={48} color="#10b981" />
              <h3>Goal Jar</h3>
              <p>Track your savings goals. Coming soon!</p>
            </div>
          </div>
        );
      
      case 'ai':
        return (
          <div className="error-container">
            <div className="error-card">
              <Brain size={48} color="#10b981" />
              <h3>AI Coach</h3>
              <p>Get personalized financial advice. Coming soon!</p>
            </div>
          </div>
        );
      
      case 'quick':
        return (
          <div className="error-container">
            <div className="error-card">
              <TrendingUp size={48} color="#3b82f6" />
              <h3>Quick Mode</h3>
              <p>Fast transaction entry and analytics.</p>
              <button 
                className="retry-btn"
                onClick={() => navigate('/money/quick')}
              >
                Open Quick Mode
              </button>
            </div>
          </div>
        );
      
      case 'analytics':
        return (
          <div className="error-container">
            <div className="error-card">
              <TrendingUp size={48} color="#3b82f6" />
              <h3>Analytics Mode</h3>
              <p>Deep insights and financial analytics. Coming soon!</p>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="money-dashboard-container">
      {renderContent()}

      {/* Bottom Navigation */}
      <nav className="money-bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <div className="w-6 h-6 bg-green-600 rounded flex items-center justify-center">
            <span className="text-white text-xs font-bold">F</span>
          </div>
          <span>Finny</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'budget' ? 'active' : ''}`}
          onClick={() => setActiveTab('budget')}
        >
          <Target size={24} />
          <span>Budget</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'loan' ? 'active' : ''}`}
          onClick={() => setActiveTab('loan')}
        >
          <CreditCard size={24} />
          <span>Loan</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'goals' ? 'active' : ''}`}
          onClick={() => setActiveTab('goals')}
        >
          <PiggyBank size={24} />
          <span>Goal Jar</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <Brain size={24} />
          <span>AI Coach</span>
        </button>
      </nav>
    </div>
  );
};

export default MoneyDashboard;
