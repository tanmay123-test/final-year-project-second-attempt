import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import '../styles/BudgetPage.css';

const MonthlyReportPage = () => {
  const navigate = useNavigate();
  const [categoryData, setCategoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  const mockCategoryData = [
    { name: 'Transport', budget: 7500, spent: 1400 },
    { name: 'Food', budget: 10000, spent: 1122 },
    { name: 'Entertainment', budget: 4000, spent: 900 },
    { name: 'Shopping', budget: 5000, spent: 3800 },
    { name: 'Dining', budget: 3000, spent: 800 }
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

  const calculateStats = () => {
    const totalSpending = categoryData.reduce((sum, cat) => sum + cat.spent, 0);
    const transactions = 47; // Mock value, should come from transactionsApi
    const dailyAvg = Math.round(totalSpending / new Date().getDate());
    const topCategory = categoryData.reduce((max, cat) => cat.spent > max.spent ? cat : max);

    return {
      totalSpending,
      transactions,
      dailyAvg,
      topCategory: topCategory.name
    };
  };

  const generateInsights = (categories) => {
    const insights = [];
    const allUnder = categories.every(c => c.spent <= c.budget);
    if (allUnder) {
      insights.push({
        icon: '✅',
        text: 'All categories within budget'
      });
    }
    
    const highSpend = categories.filter(c => (c.spent / c.budget) > 0.75);
    if (highSpend.length > 0) {
      insights.push({
        icon: '💡',
        text: `Consider reducing ${highSpend[0].name} by 10%`
      });
    }

    insights.push({
      icon: '📊',
      text: 'Diverse spending patterns detected'
    });

    return insights;
  };

  // Custom Horizontal Bar Chart Component
  const HorizontalBarChart = ({ data }) => {
    const maxValue = Math.max(...data.map(d => d.spent));
    const chartHeight = 220;
    const barHeight = 18;
    const barGap = 12;
    const leftMargin = 60;
    const rightMargin = 16;
    const topMargin = 0;
    const bottomMargin = 0;

    const getYPosition = (index) => {
      return topMargin + index * (barHeight + barGap) + barHeight / 2;
    };

    const getBarWidth = (value) => {
      const availableWidth = 400 - leftMargin - rightMargin;
      return (value / maxValue) * availableWidth;
    };

    return (
      <div style={{ width: '100%', height: `${chartHeight}px` }}>
        <svg width="100%" height="100%" viewBox={`0 0 400 ${chartHeight}`} preserveAspectRatio="none">
          {/* Grid lines */}
          {[0, 950, 1900, 2850, 3800].map((value) => {
            const x = leftMargin + (value / maxValue) * (400 - leftMargin - rightMargin);
            return (
              <line
                key={value}
                x1={x}
                x2={x}
                y1={topMargin}
                y2={chartHeight - bottomMargin}
                stroke="#e8e8e8"
                strokeDasharray="3 3"
              />
            );
          })}

          {/* Y-axis labels */}
          {data.map((item, index) => (
            <text
              key={item.name}
              x={leftMargin - 10}
              y={getYPosition(index) + 4}
              textAnchor="end"
              fill="#555"
              fontSize="11"
            >
              {item.name}
            </text>
          ))}

          {/* X-axis labels */}
          {[0, 950, 1900, 2850, 3800].map((value) => (
            <text
              key={value}
              x={leftMargin + (value / maxValue) * (400 - leftMargin - rightMargin)}
              y={chartHeight - bottomMargin + 15}
              textAnchor="middle"
              fill="#888"
              fontSize="10"
            >
              ₹{value}
            </text>
          ))}

          {/* Bars */}
          {data.map((item, index) => (
            <rect
              key={item.name}
              x={leftMargin}
              y={getYPosition(index) - barHeight / 2}
              width={getBarWidth(item.spent)}
              height={barHeight}
              fill="#1a3a5c"
              rx={[0, 4, 4, 0]}
            />
          ))}
        </svg>
      </div>
    );
  };

  const stats = calculateStats();
  const insights = generateInsights(categoryData);

  if (loading) {
    return (
      <div className="monthly-report-page">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="monthly-report-page">
      {/* Header */}
      <div className="monthly-report-header">
        <button 
          className="back-button"
          onClick={() => navigate('/finny/budget')}
        >
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="header-title-with-icon">
          <span className="header-icon">📄</span>
          <span className="page-title">Monthly Report</span>
        </div>
      </div>

      {/* Executive Summary Card */}
      <div className="exec-summary-card">
        <div className="exec-title">Executive Summary</div>
        <div className="exec-grid">
          <div className="exec-stat-cell">
            <div className="exec-stat-label">Total Spending</div>
            <div className="exec-stat-value">{formatINR(stats.totalSpending)}</div>
          </div>
          <div className="exec-stat-cell">
            <div className="exec-stat-label">Transactions</div>
            <div className="exec-stat-value">{stats.transactions}</div>
          </div>
          <div className="exec-stat-cell">
            <div className="exec-stat-label">Daily Average</div>
            <div className="exec-stat-value">{formatINR(stats.dailyAvg)}</div>
          </div>
          <div className="exec-stat-cell">
            <div className="exec-stat-label">Top Category</div>
            <div className="exec-stat-value top-category">{stats.topCategory}</div>
          </div>
        </div>
      </div>

      {/* Category Breakdown Card */}
      <div className="category-breakdown-card">
        <div className="card-title">Category Breakdown</div>
        <HorizontalBarChart data={categoryData} />
      </div>

      {/* Budget Performance Card */}
      <div className="budget-performance-card">
        <div className="card-title">Budget Performance</div>
        {categoryData.map((category, index) => {
          const percentage = Math.round((category.spent / category.budget) * 100);
          return (
            <div key={index} className="perf-row">
              <div className="perf-row-header">
                <div className="perf-category-name">{category.name}</div>
                <div className="perf-amounts">
                  {formatINR(category.spent)} / {formatINR(category.budget)} ({percentage}%)
                </div>
              </div>
              <div className="perf-bar-track">
                <div 
                  className="perf-bar-fill"
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Insights Card */}
      <div className="insights-card">
        <div className="insights-title">Insights</div>
        {insights.map((insight, index) => (
          <div key={index} className="insight-item">
            <span className="insight-icon">{insight.icon}</span>
            <span>{insight.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MonthlyReportPage;
