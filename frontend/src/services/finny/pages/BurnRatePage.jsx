import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingDown, TrendingUp } from 'lucide-react';
import '../styles/BudgetPage.css';

const BurnRatePage = () => {
  const navigate = useNavigate();
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  const mockCategoryData = [
    { name: 'Groceries', budget: 10000, spent: 4200 },
    { name: 'Transport', budget: 7500, spent: 1900 },
    { name: 'Shopping', budget: 5000, spent: 3800 },
    { name: 'Entertainment', budget: 4000, spent: 2100 },
    { name: 'Dining Out', budget: 3000, spent: 800 }
  ];

  useEffect(() => {
    // Load saved category budgets from localStorage or API
    const savedBudgets = localStorage.getItem('categoryBudgets');
    if (savedBudgets) {
      setCategoryData(JSON.parse(savedBudgets));
    } else {
      setCategoryData(mockCategoryData);
    }
    setLoading(false);
  }, []);

  const formatINR = (n) => {
    if (n === undefined || n === null || isNaN(n)) return "₹0";
    return "₹" + Math.round(n).toLocaleString('en-IN');
  };

  const calculateBurnRate = (spent, budget) => {
    if (!budget) return 0;
    return Math.round((spent / budget) * 100);
  };

  const calculateOverallBurnRate = () => {
    if (!categoryData || !Array.isArray(categoryData) || categoryData.length === 0) return 0;
    const totalSpent = categoryData.reduce((sum, cat) => sum + (cat.spent || 0), 0);
    const totalBudget = categoryData.reduce((sum, cat) => sum + (cat.budget || 0), 0);
    if (!totalBudget) return 0;
    return Math.round((totalSpent / totalBudget) * 100);
  };

  const getBurnTrend = (burnRate, daysElapsed, daysInMonth) => {
    if (!daysInMonth) return 'down';
    const expectedRate = (daysElapsed / daysInMonth) * 100;
    return burnRate > expectedRate ? 'up' : 'down';
  };

  const getProgressColor = (burnRate) => {
    if (burnRate < 75) return 'burn-fill-green';
    if (burnRate < 90) return 'burn-fill-amber';
    return 'burn-fill-red';
  };

  const getInsightMessage = (burnRate) => {
    if (burnRate < 60) {
      return { text: "Low spending rate – great job staying under budget!", class: 'insight-green' };
    }
    if (burnRate < 90) {
      return { text: "⚠ Approaching budget limit, slow down spending.", class: 'insight-amber' };
    }
    return { text: "🚨 Critical! You may exceed budget this month.", class: 'insight-red' };
  };

  const calculatePredictions = (spent, budget) => {
    const now = new Date();
    const daysElapsed = Math.max(1, now.getDate());
    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    
    const expected = Math.round(((budget || 0) / daysInMonth) * daysElapsed);
    const predicted = Math.round(((spent || 0) / daysElapsed) * daysInMonth);
    
    return { expected, predicted, daysElapsed, daysInMonth };
  };

  const overallBurnRate = calculateOverallBurnRate();
  const now = new Date();
  const daysElapsed = Math.max(1, now.getDate());
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const overallTrend = getBurnTrend(overallBurnRate, daysElapsed, daysInMonth);

  if (loading) {
    return (
      <div className="burn-rate-page">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="burn-rate-page">
      {/* Header */}
      <div className="burn-rate-header">
        <button 
          className="back-button"
          onClick={() => navigate('/finny/budget')}
        >
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="header-content">
          <div className="header-text">
            <h1 className="header-title">Burn Rate Analysis</h1>
            <p className="header-subtitle">Predict if you'll stay within budget based on current spending speed.</p>
          </div>
        </div>
      </div>

      {/* Overall Burn Rate Card */}
      <div className="overall-burn-card">
        <div className="overall-burn-label">Overall Budget Burn Rate</div>
        <div className="overall-burn-value">{overallBurnRate}%</div>
        <div className="burn-rate-bar-track">
          <div 
            className="burn-rate-bar-fill" 
            style={{ width: `${overallBurnRate}%` }}
          ></div>
        </div>
        <div className="burn-stats-row">
          <div className="burn-stat-item">Elapsed: <span>{daysElapsed}/{daysInMonth} days</span></div>
          <div className="burn-stat-item">Trend: <span className={overallTrend}>{overallTrend === 'up' ? '▲ High' : '▼ Normal'}</span></div>
        </div>
      </div>

      <div className="category-cards-container">
        {categoryData.map((category, index) => {
          const burnRate = calculateBurnRate(category.spent, category.budget);
          const { expected, predicted } = calculatePredictions(category.spent, category.budget);
          const trend = getBurnTrend(burnRate, daysElapsed, daysInMonth);
          const insight = getInsightMessage(burnRate);
          
          return (
            <div key={index} className="burn-card">
              <div className="burn-card-header">
                <span className="burn-category-name">{category.name}</span>
                <span className={`burn-rate-pct ${trend}`}>
                  {burnRate}% {trend === 'up' ? '▲' : '▼'}
                </span>
              </div>
              
              <div className="burn-stats-grid">
                <div className="burn-stat-item">Budget: <span>{formatINR(category.budget)}</span></div>
                <div className="burn-stat-item">Spent: <span>{formatINR(category.spent)}</span></div>
                <div className="burn-stat-item">Expected: <span>{formatINR(expected)}</span></div>
                <div className="burn-stat-item">Predicted: <span className={predicted > category.budget ? 'predicted-over' : ''}>{formatINR(predicted)}</span></div>
              </div>

              <div className="burn-progress-track">
                <div 
                  className={`burn-progress-fill ${getProgressColor(burnRate)}`}
                  style={{ width: `${Math.min(100, burnRate)}%` }}
                ></div>
              </div>

              <div className={`burn-insight ${insight.class}`}>
                {insight.text}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BurnRatePage;
