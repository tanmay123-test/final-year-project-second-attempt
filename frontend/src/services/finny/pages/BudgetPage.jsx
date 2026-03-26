import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../api/analyticsApi';
import '../styles/BudgetPage.css';

const BudgetPage = () => {
  const [loading, setLoading] = useState(true);
  const [budgetData, setBudgetData] = useState(null);

  // Default budget data matching the design
  const defaultBudgetData = [
    {
      category: 'Food',
      spent: 4200,
      total: 5000,
      percentage: 84,
      status: 'safe'
    },
    {
      category: 'Transport',
      spent: 1900,
      total: 3000,
      percentage: 63,
      status: 'safe'
    },
    {
      category: 'Shopping',
      spent: 3800,
      total: 4000,
      percentage: 95,
      status: 'danger'
    },
    {
      category: 'Bills',
      spent: 3200,
      total: 4000,
      percentage: 80,
      status: 'safe'
    },
    {
      category: 'Entertainment',
      spent: 2100,
      total: 2500,
      percentage: 84,
      status: 'safe'
    }
  ];

  useEffect(() => {
    const loadBudgetData = async () => {
      setLoading(true);
      try {
        // In a real app, fetch from budgetApi or analyticsApi
        const response = await analyticsApi.getAnalytics();
        if (response.success) {
          // Process budget data from API response
          const processedData = processBudgetData(response.data);
          setBudgetData(processedData);
        } else {
          // Fall back to default data
          setBudgetData(defaultBudgetData);
        }
      } catch (error) {
        console.error('Failed to load budget data:', error);
        // Fall back to default data
        setBudgetData(defaultBudgetData);
      } finally {
        setLoading(false);
      }
    };

    loadBudgetData();
  }, []);

  // Process budget data from API response
  const processBudgetData = (data) => {
    // This would process real API data into budget format
    // For now, return default data
    return defaultBudgetData;
  };

  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  const getProgressBarClass = (percentage) => {
    if (percentage >= 90) return 'danger';
    return 'safe';
  };

  const getProgressTextColor = (percentage) => {
    if (percentage >= 90) return '#F44336';
    return '#666666';
  };

  if (loading) {
    return (
      <div className="budget-page">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading budget data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="budget-page">
      <h2 className="section-title">Budget Monitoring</h2>
      
      <div className="budget-cards">
        {budgetData?.map((budget, index) => (
          <div key={index} className={`budget-card ${budget.status === 'danger' ? 'danger-card' : ''}`}>
            <div className="budget-header">
              <span className="category-name">{budget.category}</span>
              <span className="budget-amount">
                {formatCurrency(budget.spent)} / {formatCurrency(budget.total)}
              </span>
            </div>
            
            <div className="progress-track">
              <div 
                className={`progress-bar ${getProgressBarClass(budget.percentage)}`}
                style={{ width: `${budget.percentage}%` }}
              ></div>
            </div>
            
            <div 
              className="progress-text"
              style={{ color: getProgressTextColor(budget.percentage) }}
            >
              {budget.percentage}% used
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BudgetPage;
