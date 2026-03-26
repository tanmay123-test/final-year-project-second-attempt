import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import '../styles/BudgetPage.css';

const BudgetStatusPage = () => {
  const navigate = useNavigate();
  const [categoryBudgets, setCategoryBudgets] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  const mockCategoryData = [
    { name: 'Groceries', budget: 10000, spent: 4200 },
    { name: 'Transport', budget: 7500, spent: 1900 },
    { name: 'Utilities', budget: 7500, spent: 3200 },
    { name: 'Shopping', budget: 5000, spent: 3800 },
    { name: 'Entertainment', budget: 4000, spent: 2100 },
    { name: 'Dining Out', budget: 3000, spent: 0 }
  ];

  useEffect(() => {
    // Load saved category budgets from localStorage or API
    const savedBudgets = localStorage.getItem('categoryBudgets');
    if (savedBudgets) {
      setCategoryBudgets(JSON.parse(savedBudgets));
    } else {
      setCategoryBudgets(mockCategoryData);
    }
    setLoading(false);
  }, []);

  const formatINR = (n) => "₹" + Math.round(n).toLocaleString('en-IN');

  const getStatus = (spent, budget) => {
    const pct = (spent / budget) * 100;
    if (pct >= 90) return 'Danger';
    if (pct >= 75) return 'Warning';
    return 'Safe';
  };

  const getBarColor = (status) => ({
    'Safe': '#4CAF50',
    'Warning': '#f5a623',
    'Danger': '#F44336'
  }[status]);

  const getLeftAmountColor = (left, budget) => {
    if (left < 0) return 'left-red';
    if (left < budget * 0.2) return 'left-amber';
    return 'left-green';
  };

  const calculateStats = () => {
    const totalSpent = categoryBudgets.reduce((sum, cat) => sum + cat.spent, 0);
    const totalBudget = categoryBudgets.reduce((sum, cat) => sum + cat.budget, 0);
    const daysInMonth = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate();
    const daysElapsed = new Date().getDate();
    
    const dailyAverage = totalSpent / daysElapsed;
    const disposableIncome = 50000; // Mock value, should come from saved plan
    const recommendedPerDay = disposableIncome / daysInMonth;

    return {
      dailyAverage,
      recommendedPerDay,
      totalSpent,
      totalBudget,
      daysElapsed,
      daysInMonth
    };
  };

  const stats = calculateStats();

  if (loading) {
    return (
      <div className="budget-status-page">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="budget-status-page">
      {/* Header */}
      <div className="budget-status-header">
        <button 
          className="back-button"
          onClick={() => navigate('/finny/budget')}
        >
          <ArrowLeft size={20} color="white" />
        </button>
        <h1 className="page-title">Budget Status & Monitoring</h1>
      </div>

      {/* Top Stats Row */}
      <div className="budget-stats-row">
        <div className="budget-stat-card">
          <div className="stat-label">Daily Average</div>
          <div className="stat-value">{formatINR(stats.dailyAverage)}</div>
        </div>
        <div className="budget-stat-card">
          <div className="stat-label">Recommended/day</div>
          <div className="stat-value">{formatINR(stats.recommendedPerDay)}</div>
        </div>
      </div>

      {/* Category Budget Cards */}
      <div className="category-cards-container">
        {categoryBudgets.map((category, index) => {
          const left = category.budget - category.spent;
          const percentage = Math.round((category.spent / category.budget) * 100);
          const status = getStatus(category.spent, category.budget);
          const barColor = getBarColor(status);
          const leftColorClass = getLeftAmountColor(left, category.budget);

          return (
            <div key={index} className="budget-status-card">
              {/* Top Row */}
              <div className="card-top-row">
                <div className="category-title">{category.name}</div>
                <div className={`status-badge badge-${status.toLowerCase()}`}>
                  {status}
                </div>
              </div>

              {/* Stats Row */}
              <div className="card-stats-row">
                <div className="stat-col">
                  <div className="stat-col-label">Budget</div>
                  <div className="stat-col-value">{formatINR(category.budget)}</div>
                </div>
                <div className="stat-col">
                  <div className="stat-col-label">Spent</div>
                  <div className="stat-col-value">{formatINR(category.spent)}</div>
                </div>
                <div className="stat-col">
                  <div className="stat-col-label">Left</div>
                  <div className={`stat-col-value ${leftColorClass}`}>
                    {formatINR(left)}
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="category-progress-track">
                <div 
                  className="category-progress-fill"
                  style={{ 
                    width: `${percentage}%`,
                    backgroundColor: barColor
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BudgetStatusPage;
