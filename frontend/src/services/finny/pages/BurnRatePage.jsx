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

  const formatINR = (n) => "₹" + Math.round(n).toLocaleString('en-IN');

  const calculateBurnRate = (spent, budget) => {
    return Math.round((spent / budget) * 100);
  };

  const calculateOverallBurnRate = () => {
    const totalSpent = categoryData.reduce((sum, cat) => sum + cat.spent, 0);
    const totalBudget = categoryData.reduce((sum, cat) => sum + cat.budget, 0);
    return Math.round((totalSpent / totalBudget) * 100);
  };

  const getBurnTrend = (burnRate, daysElapsed, daysInMonth) => {
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
    const daysElapsed = new Date().getDate();
    const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate();
    
    const expected = Math.round((budget / daysInMonth) * daysElapsed);
    const predicted = Math.round((spent / daysElapsed) * daysInMonth);
    
    return { expected, predicted, daysElapsed, daysInMonth };
  };

  const overallBurnRate = calculateOverallBurnRate();

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
        <h1 className="page-title">Burn Rate Analysis</h1>
      </div>

      {/* Overall Burn Rate Card */}
      <div className="overall-burn-card">
        <div className="overall-burn-label">Overall Burn Rate</div>
        <div className="overall-burn-value">{overallBurnRate}%</div>
        <div className="burn-rate-bar-track">
          <div 
            className="burn-rate-bar-fill"
            style={{ width: `${overallBurnRate}%` }}
          ></div>
        </div>
      </div>

      {/* Category Burn Rate Cards */}
      <div className="category-cards-container">
        {categoryData.map((category, index) => {
          const burnRate = calculateBurnRate(category.spent, category.budget);
          const { expected, predicted, daysElapsed, daysInMonth } = calculatePredictions(category.spent, category.budget);
          const trend = getBurnTrend(burnRate, daysElapsed, daysInMonth);
          const progressColor = getProgressColor(burnRate);
          const insight = getInsightMessage(burnRate);

          return (
            <div key={index} className="burn-card">
              {/* Title + Burn Rate % */}
              <div className="burn-card-header">
                <div className="burn-category-name">{category.name}</div>
                <div className={`burn-rate-pct ${trend}`}>
                  {trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  {burnRate}%
                </div>
              </div>

              {/* 2x2 Stats Grid */}
              <div className="burn-stats-grid">
                <div className="burn-stat-item">
                  Budget: <span>{formatINR(category.budget)}</span>
                </div>
                <div className="burn-stat-item">
                  Expected: <span>{formatINR(expected)}</span>
                </div>
                <div className="burn-stat-item">
                  Spent: <span>{formatINR(category.spent)}</span>
                </div>
                <div className="burn-stat-item">
                  Predicted: 
                  <span className={predicted > category.budget ? 'predicted-over' : ''}>
                    {formatINR(predicted)}
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="burn-progress-track">
                <div 
                  className={`burn-progress-fill ${progressColor}`}
                  style={{ width: `${burnRate}%` }}
                ></div>
              </div>

              {/* Insight Message */}
              {burnRate < 60 && (
                <div className={`burn-insight ${insight.class}`}>
                  {insight.text}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BurnRatePage;
