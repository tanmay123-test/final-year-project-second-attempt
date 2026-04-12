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

  const formatINR = (n) => {
    if (n === undefined || n === null || isNaN(n)) return "₹0";
    return "₹" + Math.round(n).toLocaleString('en-IN');
  };

  const getStatus = (spent, budget) => {
    if (!budget) return 'Safe';
    const pct = (spent / budget) * 100;
    if (pct >= 90) return 'Danger';
    if (pct >= 75) return 'Warning';
    return 'Safe';
  };

  const getBarColor = (status) => ({
    'Safe': '#4CAF50',
    'Warning': '#f5a623',
    'Danger': '#F44336'
  }[status] || '#4CAF50');

  const getLeftAmountColor = (left, budget) => {
    if (left < 0) return 'left-red';
    if (!budget || left < budget * 0.2) return 'left-amber';
    return 'left-green';
  };

  const calculateStats = () => {
    if (!categoryBudgets || !Array.isArray(categoryBudgets)) {
      return {
        dailyAverage: 0,
        recommendedPerDay: 0,
        totalSpent: 0,
        totalBudget: 0,
        daysElapsed: 1,
        daysInMonth: 30
      };
    }

    const totalSpent = categoryBudgets.reduce((sum, cat) => sum + (cat.spent || 0), 0);
    const totalBudget = categoryBudgets.reduce((sum, cat) => sum + (cat.budget || 0), 0);
    const now = new Date();
    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    const daysElapsed = Math.max(1, now.getDate());
    
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
        <div className="header-content">
          <div className="header-text">
            <h1 className="header-title">Budget Monitoring</h1>
            <p className="header-subtitle">Track your category-wise spending against monthly targets.</p>
          </div>
        </div>
      </div>

      <div className="budget-stats-row">
        <div className="budget-stat-card">
          <div className="stat-label">Total Spent</div>
          <div className="stat-value">{formatINR(stats.totalSpent)}</div>
        </div>
        <div className="budget-stat-card">
          <div className="stat-label">Daily Average</div>
          <div className="stat-value">{formatINR(stats.dailyAverage)}</div>
        </div>
        <div className="budget-stat-card">
          <div className="stat-label">Budget Left</div>
          <div className="stat-value">{formatINR(stats.totalBudget - stats.totalSpent)}</div>
        </div>
      </div>

      <div className="category-cards-container">
        {categoryBudgets.map((category, index) => {
          const status = getStatus(category.spent, category.budget);
          const left = category.budget - category.spent;
          const pct = Math.min(100, (category.spent / (category.budget || 1)) * 100);
          
          return (
            <div key={index} className="budget-status-card">
              <div className="card-top-row">
                <span className="category-title">{category.name}</span>
                <span className={`status-badge badge-${status.toLowerCase()}`}>
                  {status}
                </span>
              </div>
              
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
                  <div className={`stat-col-value ${getLeftAmountColor(left, category.budget)}`}>
                    {formatINR(left)}
                  </div>
                </div>
              </div>

              <div className="category-progress-track">
                <div 
                  className="category-progress-fill" 
                  style={{ 
                    width: `${pct}%`,
                    backgroundColor: getBarColor(status)
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BudgetStatusPage;
