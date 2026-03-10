import React, { useState, useEffect } from 'react';
import { ArrowLeft, TrendingUp, TrendingDown, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/QuickMode.css';

const MonthlySummary = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));

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
    fetchSummaryData();
  }, [selectedMonth]);

  const fetchSummaryData = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getTransactions();
      const transactions = response.data.transactions || [];
      
      // Filter transactions for selected month
      const monthTransactions = transactions.filter(transaction => 
        transaction.date.startsWith(selectedMonth)
      );
      
      // Calculate summary
      const totalSpending = monthTransactions.reduce((sum, t) => sum + t.amount, 0);
      
      // Group by category
      const categorySpending = {};
      monthTransactions.forEach(transaction => {
        if (!categorySpending[transaction.category]) {
          categorySpending[transaction.category] = 0;
        }
        categorySpending[transaction.category] += transaction.amount;
      });
      
      // Convert to array with percentages
      const categoryData = Object.entries(categorySpending).map(([category, amount]) => ({
        category,
        amount,
        percentage: ((amount / totalSpending) * 100).toFixed(1),
        color: categories.find(c => c.name === category)?.color || '#A0A0A0',
        icon: categories.find(c => c.name === category)?.icon || '📦'
      })).sort((a, b) => b.amount - a.amount);

      setSummaryData({
        totalSpending,
        transactionCount: monthTransactions.length,
        categories: categoryData,
        month: selectedMonth
      });
    } catch (err) {
      console.error('Failed to fetch summary:', err);
      setError('Failed to load summary data');
    } finally {
      setLoading(false);
    }
  };

  const formatMonth = (monthString) => {
    const date = new Date(monthString + '-01');
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="finny-mobile-container">
        <header className="finny-header">
          <button className="back-btn" onClick={() => navigate('/money/quick')}>
            <ArrowLeft size={24} />
          </button>
          <div className="header-title">
            <h1>Monthly Summary</h1>
            <p>Spending Overview</p>
          </div>
          <div className="header-spacer"></div>
        </header>
        <div className="finny-main-content">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="loading-state">
              <p>Loading summary...</p>
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
            <h1>Monthly Summary</h1>
            <p>Spending Overview</p>
          </div>
          <div className="header-spacer"></div>
        </header>
        <div className="finny-main-content">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="error-state">
              <p>{error}</p>
              <button onClick={fetchSummaryData}>Retry</button>
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
          <h1>Monthly Summary</h1>
          <p>Spending Overview</p>
        </div>
        <div className="header-spacer"></div>
      </header>

      <main className="finny-main-content">
        {/* Month Selector */}
        <div style={{ padding: '20px 20px 0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <Calendar size={20} color="#4a90e2" />
            <input
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '16px'
              }}
            />
          </div>
        </div>

        {/* Total Spending Card */}
        <div style={{ padding: '0 20px 20px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #4a90e2, #357abd)',
            color: 'white',
            padding: '24px',
            borderRadius: '16px',
            textAlign: 'center',
            boxShadow: '0 4px 16px rgba(74, 144, 226, 0.3)'
          }}>
            <h3 style={{ fontSize: '14px', opacity: 0.9, margin: '0 0 8px 0' }}>
              Total Spending
            </h3>
            <div style={{ fontSize: '32px', fontWeight: 'bold', margin: '0 0 8px 0' }}>
              ₹{summaryData.totalSpending.toLocaleString()}
            </div>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>
              {summaryData.transactionCount} transactions
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        <div style={{ padding: '0 20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Category Breakdown
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {summaryData.categories.map((category, index) => (
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
                      width: '100px',
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

        {/* Insights */}
        <div style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Quick Insights
          </h3>
          <div style={{
            background: 'white',
            padding: '20px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
          }}>
            {summaryData.categories.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <TrendingUp size={16} color="#28a745" />
                  <span style={{ fontSize: '14px', fontWeight: '500' }}>Highest Spending</span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
                  {summaryData.categories[0].category}: ₹{summaryData.categories[0].amount.toLocaleString()}
                </p>
              </div>
            )}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <TrendingDown size={16} color="#dc3545" />
                <span style={{ fontSize: '14px', fontWeight: '500' }}>Average per Transaction</span>
              </div>
              <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
                ₹{Math.round(summaryData.totalSpending / summaryData.transactionCount).toLocaleString()}
              </p>
            </div>
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

export default MonthlySummary;
