import React, { useState, useEffect } from 'react';
import { ArrowLeft, Brain, TrendingUp, TrendingDown, BarChart3, PieChart, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/QuickMode.css';

const AnalyticsDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const categories = [
    { name: 'Food', color: '#FF6B6B', icon: '🍔' },
    { name: 'Shopping', color: '#4ECDC4', icon: '🛍️' },
    { name: 'Bills', color: '#45B7D1', icon: '📄' },
    { name: 'Transport', color: '#96CEB4', icon: '🚗' },
    { name: 'Entertainment', color: '#FFEAA7', icon: '🎬' },
    { name: 'Healthcare', color: '#DDA0DD', icon: '🏥' },
    { name: 'Education', color: '#87CEEB', icon: '📚' },
    { name: 'Other', color: '#A0A0A0', icon: '📦' }
  ];

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getTransactions();
      const transactions = response.data.transactions || [];
      
      // Get last 6 months of data
      const currentMonth = new Date();
      const monthlyData = [];
      
      for (let i = 0; i < 6; i++) {
        const monthDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - i, 1);
        const monthString = monthDate.toISOString().slice(0, 7);
        
        const monthTransactions = transactions.filter(t => 
          t.date.startsWith(monthString)
        );
        
        const monthSpending = monthTransactions.reduce((sum, t) => sum + t.amount, 0);
        
        monthlyData.push({
          month: monthString,
          monthName: monthDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
          spending: monthSpending,
          transactionCount: monthTransactions.length
        });
      }
      
      // Category trends
      const categoryTrends = {};
      transactions.forEach(transaction => {
        const month = transaction.date.slice(0, 7);
        if (!categoryTrends[transaction.category]) {
          categoryTrends[transaction.category] = {};
        }
        if (!categoryTrends[transaction.category][month]) {
          categoryTrends[transaction.category][month] = 0;
        }
        categoryTrends[transaction.category][month] += transaction.amount;
      });
      
      // Calculate insights
      const totalSpending = transactions.reduce((sum, t) => sum + t.amount, 0);
      const avgMonthlySpending = totalSpending / 6;
      
      // Find top categories
      const categoryTotals = {};
      transactions.forEach(transaction => {
        if (!categoryTotals[transaction.category]) {
          categoryTotals[transaction.category] = 0;
        }
        categoryTotals[transaction.category] += transaction.amount;
      });
      
      const topCategories = Object.entries(categoryTotals)
        .map(([category, amount]) => ({
          category,
          amount,
          percentage: ((amount / totalSpending) * 100).toFixed(1),
          color: categories.find(c => c.name === category)?.color || '#A0A0A0',
          icon: categories.find(c => c.name === category)?.icon || '📦'
        }))
        .sort((a, b) => b.amount - a.amount)
        .slice(0, 5);

      setAnalyticsData({
        monthlyData: monthlyData.reverse(),
        categoryTrends,
        totalSpending,
        avgMonthlySpending,
        topCategories,
        insights: generateInsights(monthlyData, topCategories)
      });
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const generateInsights = (monthlyData, topCategories) => {
    const insights = [];
    
    if (monthlyData.length >= 2) {
      const currentMonth = monthlyData[monthlyData.length - 1];
      const previousMonth = monthlyData[monthlyData.length - 2];
      
      if (currentMonth.spending > previousMonth.spending) {
        const increase = ((currentMonth.spending - previousMonth.spending) / previousMonth.spending * 100).toFixed(1);
        insights.push({
          type: 'warning',
          icon: <TrendingUp size={16} color="#dc3545" />,
          text: `Spending increased by ${increase}% this month`
        });
      } else {
        const decrease = ((previousMonth.spending - currentMonth.spending) / previousMonth.spending * 100).toFixed(1);
        insights.push({
          type: 'success',
          icon: <TrendingDown size={16} color="#28a745" />,
          text: `Spending decreased by ${decrease}% this month`
        });
      }
    }
    
    if (topCategories.length > 0) {
      insights.push({
        type: 'info',
        icon: <Target size={16} color="#4a90e2" />,
        text: `${topCategories[0].category} is your highest expense category`
      });
    }
    
    return insights;
  };

  if (loading) {
    return (
      <div className="finny-mobile-container">
        <header className="finny-header">
          <button className="back-btn" onClick={() => navigate('/money/quick')}>
            <ArrowLeft size={24} />
          </button>
          <div className="header-title">
            <h1>Analytics Dashboard</h1>
            <p>Deep Insights</p>
          </div>
          <div className="header-spacer"></div>
        </header>
        <div className="finny-main-content">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="loading-state">
              <p>Loading analytics...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="finny-mobile-container">
        <header className="finny-header">
          <button className="back-btn" onClick={() => navigate('/money/quick')}>
            <ArrowLeft size={24} />
          </button>
          <div className="header-title">
            <h1>Analytics Dashboard</h1>
            <p>Deep Insights</p>
          </div>
          <div className="header-spacer"></div>
        </header>
        <div className="finny-main-content">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="error-state">
              <p>{error}</p>
              <button onClick={fetchAnalyticsData}>Retry</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="finny-mobile-container">
      <header className="finny-header">
        <button className="back-btn" onClick={() => navigate('/money/quick')}>
          <ArrowLeft size={24} />
        </button>
        <div className="header-title">
          <h1>Analytics Dashboard</h1>
          <p>Deep Insights</p>
        </div>
        <div className="header-spacer"></div>
      </header>

      <main className="finny-main-content">
        {/* AI Insights */}
        <div style={{ padding: '20px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6f42c1, #5a32a3)',
            color: 'white',
            padding: '20px',
            borderRadius: '16px',
            boxShadow: '0 4px 16px rgba(111, 66, 193, 0.3)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <Brain size={24} />
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>
                AI Financial Insights
              </h3>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {analyticsData.insights.map((insight, index) => (
                <div key={index} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px'
                }}>
                  {insight.icon}
                  <span style={{ fontSize: '14px' }}>{insight.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Monthly Trend */}
        <div style={{ padding: '0 20px 20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            6-Month Spending Trend
          </h3>
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                Average Monthly Spending
              </div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4a90e2' }}>
                ₹{Math.round(analyticsData.avgMonthlySpending).toLocaleString()}
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {analyticsData.monthlyData.map((month, index) => (
                <div key={month.month} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 0',
                  borderBottom: index < analyticsData.monthlyData.length - 1 ? '1px solid #f0f0f0' : 'none'
                }}>
                  <span style={{ fontSize: '14px', color: '#666' }}>{month.monthName}</span>
                  <span style={{ fontSize: '16px', fontWeight: '600' }}>
                    ₹{month.spending.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Categories */}
        <div style={{ padding: '0 20px 20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Top Spending Categories
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {analyticsData.topCategories.map((category, index) => (
              <div key={category.category} style={{
                background: 'white',
                padding: '16px',
                borderRadius: '12px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                display: 'flex',
                alignItems: 'center',
                gap: '16px'
              }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '12px',
                  background: category.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '20px'
                }}>
                  {category.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '4px'
                  }}>
                    <h4 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>
                      {category.category}
                    </h4>
                    <span style={{ fontSize: '16px', fontWeight: '600', color: category.color }}>
                      ₹{category.amount.toLocaleString()}
                    </span>
                  </div>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div style={{
                      fontSize: '14px',
                      color: '#666'
                    }}>
                      {category.percentage}% of total
                    </div>
                    <div style={{
                      width: '80px',
                      height: '6px',
                      background: '#f0f0f0',
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${category.percentage}%`,
                        height: '100%',
                        background: category.color,
                        borderRadius: '3px'
                      }}></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Financial Health Score */}
        <div style={{ padding: '0 20px 20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Financial Health Score
          </h3>
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{
              width: '120px',
              height: '120px',
              margin: '0 auto 16px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #28a745, #20c997)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '36px',
              fontWeight: 'bold'
            }}>
              85
            </div>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '600' }}>
              Excellent
            </h4>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              Your spending habits are well-controlled and diversified
            </p>
          </div>
        </div>
      </main>

      {/* Bottom Navigation */}
      <div className="finny-bottom-nav">
        <button className="bottom-nav-item" onClick={() => navigate('/money/quick')}>
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

export default AnalyticsDashboard;
