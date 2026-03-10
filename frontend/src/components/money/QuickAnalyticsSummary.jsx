import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Calendar, DollarSign, PieChart, Target } from 'lucide-react';
import { moneyService } from '../../shared/api';
import './QuickAnalyticsSummary.css';

const QuickAnalyticsSummary = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

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
      
      // Get current month data
      const currentMonth = new Date().toISOString().slice(0, 7);
      const currentMonthTransactions = transactions.filter(t => 
        t.date.startsWith(currentMonth)
      );
      
      // Get previous month data for comparison
      const previousMonth = new Date();
      previousMonth.setMonth(previousMonth.getMonth() - 1);
      const previousMonthString = previousMonth.toISOString().slice(0, 7);
      const previousMonthTransactions = transactions.filter(t => 
        t.date.startsWith(previousMonthString)
      );
      
      // Calculate metrics
      const currentMonthSpending = currentMonthTransactions.reduce((sum, t) => sum + t.amount, 0);
      const previousMonthSpending = previousMonthTransactions.reduce((sum, t) => sum + t.amount, 0);
      const monthOverMonthChange = previousMonthSpending > 0 
        ? ((currentMonthSpending - previousMonthSpending) / previousMonthSpending * 100).toFixed(1)
        : 0;
      
      // Calculate daily average
      const daysInMonth = new Date().getDate();
      const dailyAverage = currentMonthSpending / daysInMonth;
      
      // Category breakdown for current month
      const categorySpending = {};
      currentMonthTransactions.forEach(transaction => {
        if (!categorySpending[transaction.category]) {
          categorySpending[transaction.category] = 0;
        }
        categorySpending[transaction.category] += transaction.amount;
      });
      
      const topCategories = Object.entries(categorySpending)
        .map(([category, amount]) => ({
          category,
          amount,
          percentage: ((amount / currentMonthSpending) * 100).toFixed(1),
          color: categories.find(c => c.name === category)?.color || '#A0A0A0',
          icon: categories.find(c => c.name === category)?.icon || '📦'
        }))
        .sort((a, b) => b.amount - a.amount)
        .slice(0, 3);

      // Financial health score
      const healthScore = calculateHealthScore(currentMonthSpending, dailyAverage, topCategories);

      setAnalyticsData({
        currentMonthSpending,
        previousMonthSpending,
        monthOverMonthChange,
        dailyAverage,
        transactionCount: currentMonthTransactions.length,
        topCategories,
        healthScore,
        currentMonthName: new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
      });
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateHealthScore = (spending, dailyAvg, categories) => {
    let score = 100;
    
    // Deduct points for high spending (arbitrary thresholds)
    if (spending > 10000) score -= 20;
    else if (spending > 5000) score -= 10;
    
    // Deduct points for high daily average
    if (dailyAvg > 500) score -= 15;
    else if (dailyAvg > 300) score -= 8;
    
    // Bonus for diversified spending
    if (categories.length >= 4) score += 10;
    else if (categories.length >= 3) score += 5;
    
    return Math.min(100, Math.max(0, score));
  };

  if (loading) {
    return (
      <div className="analytics-summary-card">
        <div className="loading-spinner">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return null;
  }

  return (
    <div className="analytics-summary-card">
      {/* Header */}
      <div className="analytics-header">
        <div className="analytics-title">
          <PieChart size={20} className="text-blue-500" />
          <h3>Quick Analytics</h3>
        </div>
        <div className="analytics-period">
          <Calendar size={16} className="text-gray-500" />
          <span>{analyticsData.currentMonthName}</span>
        </div>
      </div>

      {/* Main Metrics */}
      <div className="metrics-grid">
        <div className="metric-card primary">
          <div className="metric-icon">
            <DollarSign size={18} />
          </div>
          <div className="metric-content">
            <div className="metric-value">₹{analyticsData.currentMonthSpending.toLocaleString()}</div>
            <div className="metric-label">Total Spent</div>
            <div className={`metric-change ${analyticsData.monthOverMonthChange >= 0 ? 'negative' : 'positive'}`}>
              {analyticsData.monthOverMonthChange >= 0 ? (
                <TrendingUp size={12} />
              ) : (
                <TrendingDown size={12} />
              )}
              {Math.abs(analyticsData.monthOverMonthChange)}% vs last month
            </div>
          </div>
        </div>

        <div className="metric-card secondary">
          <div className="metric-icon">
            <Calendar size={18} />
          </div>
          <div className="metric-content">
            <div className="metric-value">₹{Math.round(analyticsData.dailyAverage).toLocaleString()}</div>
            <div className="metric-label">Daily Average</div>
            <div className="metric-sublabel">{analyticsData.transactionCount} transactions</div>
          </div>
        </div>

        <div className="metric-card health">
          <div className="metric-icon">
            <Target size={18} />
          </div>
          <div className="metric-content">
            <div className="metric-value">{analyticsData.healthScore}</div>
            <div className="metric-label">Health Score</div>
            <div className={`health-status ${analyticsData.healthScore >= 80 ? 'excellent' : analyticsData.healthScore >= 60 ? 'good' : 'fair'}`}>
              {analyticsData.healthScore >= 80 ? 'Excellent' : analyticsData.healthScore >= 60 ? 'Good' : 'Fair'}
            </div>
          </div>
        </div>
      </div>

      {/* Top Categories */}
      <div className="categories-section">
        <h4 className="section-title">Top Categories</h4>
        <div className="categories-list">
          {analyticsData.topCategories.map((category, index) => (
            <div key={category.category} className="category-item">
              <div className="category-info">
                <div 
                  className="category-dot" 
                  style={{ backgroundColor: category.color }}
                />
                <div className="category-details">
                  <div className="category-name">{category.icon} {category.category}</div>
                  <div className="category-amount">₹{category.amount.toLocaleString()}</div>
                </div>
              </div>
              <div className="category-percentage">{category.percentage}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Insights */}
      <div className="insights-section">
        <h4 className="section-title">Quick Insights</h4>
        <div className="insights-list">
          {analyticsData.monthOverMonthChange > 10 && (
            <div className="insight-item warning">
              <TrendingUp size={14} />
              <span>Spending increased by {analyticsData.monthOverMonthChange}% this month</span>
            </div>
          )}
          {analyticsData.dailyAverage > 300 && (
            <div className="insight-item info">
              <DollarSign size={14} />
              <span>Daily spending is higher than usual</span>
            </div>
          )}
          {analyticsData.healthScore >= 80 && (
            <div className="insight-item success">
              <Target size={14} />
              <span>Great financial health! Keep it up!</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuickAnalyticsSummary;
