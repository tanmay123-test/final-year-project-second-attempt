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

  const formatINR = (n) => {
    if (n === undefined || n === null || isNaN(n)) return "₹0";
    return "₹" + Math.round(n).toLocaleString('en-IN');
  };

  const calculateStats = () => {
    if (!categoryData || !Array.isArray(categoryData) || categoryData.length === 0) {
      return {
        totalSpending: 0,
        transactions: 0,
        dailyAvg: 0,
        topCategory: 'None'
      };
    }

    const totalSpending = categoryData.reduce((sum, cat) => sum + (cat.spent || 0), 0);
    const transactions = 47; // Mock value, should come from transactionsApi
    const now = new Date();
    const daysElapsed = Math.max(1, now.getDate());
    const dailyAvg = Math.round(totalSpending / daysElapsed);
    
    const topCategory = categoryData.reduce((max, cat) => (cat.spent || 0) > (max.spent || 0) ? cat : max, categoryData[0]);

    return {
      totalSpending,
      transactions,
      dailyAvg,
      topCategory: topCategory?.name || 'None'
    };
  };

  const generateInsights = (categories) => {
    if (!categories || categories.length === 0) return [{ icon: 'ℹ️', text: 'No data available for insights' }];
    
    const insights = [];
    const allUnder = categories.every(c => (c.spent || 0) <= (c.budget || 1));
    if (allUnder) {
      insights.push({
        icon: '✅',
        text: 'All categories within budget'
      });
    }
    
    const highSpend = categories.filter(c => (c.spent / (c.budget || 1)) > 0.75);
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
    if (!data || data.length === 0) return <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>No data to display</div>;
    
    const maxValue = Math.max(...data.map(d => d.spent || 0), 1);
    const chartHeight = 250;
    const barHeight = 22;
    const barGap = 16;
    const leftMargin = 100; // Increased to prevent label truncation
    const rightMargin = 40;
    const topMargin = 20;
    const bottomMargin = 40;
    const svgWidth = 500; // Fixed base width for viewBox

    const getYPosition = (index) => {
      return topMargin + index * (barHeight + barGap) + barHeight / 2;
    };

    const getBarWidth = (value) => {
      const availableWidth = svgWidth - leftMargin - rightMargin;
      return (value / maxValue) * availableWidth;
    };

    return (
      <div style={{ width: '100%', overflowX: 'auto', background: 'white', borderRadius: '12px' }}>
        <svg width="100%" height={chartHeight} viewBox={`0 0 ${svgWidth} ${chartHeight}`} preserveAspectRatio="xMinYMin meet">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const x = leftMargin + ratio * (svgWidth - leftMargin - rightMargin);
            return (
              <g key={ratio}>
                <line
                  x1={x}
                  x2={x}
                  y1={topMargin}
                  y2={chartHeight - bottomMargin}
                  stroke="#F1F5F9"
                  strokeDasharray="4 4"
                />
                <text
                  x={x}
                  y={chartHeight - bottomMargin + 20}
                  textAnchor="middle"
                  fill="#94A3B8"
                  fontSize="10"
                >
                  ₹{Math.round(ratio * maxValue)}
                </text>
              </g>
            );
          })}

          {/* Bars and Labels */}
          {data.map((item, index) => (
            <g key={item.name}>
              {/* Y-axis labels */}
              <text
                x={leftMargin - 12}
                y={getYPosition(index) + 5}
                textAnchor="end"
                fill="#475569"
                fontSize="12"
                fontWeight="500"
              >
                {item.name}
              </text>
              
              {/* Background bar (track) */}
              <rect
                x={leftMargin}
                y={getYPosition(index) - barHeight / 2}
                width={svgWidth - leftMargin - rightMargin}
                height={barHeight}
                fill="#F8FAFC"
                rx="4"
              />

              {/* Progress bar */}
              <rect
                x={leftMargin}
                y={getYPosition(index) - barHeight / 2}
                width={getBarWidth(item.spent)}
                height={barHeight}
                fill="#1E293B"
                rx="4"
              />

              {/* Value label on bar */}
              {getBarWidth(item.spent) > 40 && (
                <text
                  x={leftMargin + getBarWidth(item.spent) - 8}
                  y={getYPosition(index) + 4}
                  textAnchor="end"
                  fill="white"
                  fontSize="10"
                  fontWeight="600"
                >
                  ₹{item.spent}
                </text>
              )}
            </g>
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
      <div className="budget-status-header">
        <button 
          className="back-button"
          onClick={() => navigate('/finny/budget')}
        >
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Monthly Report</h1>
            <p className="loan-header-subtitle">Detailed breakdown of your monthly spending habits.</p>
          </div>
        </div>
      </div>

      <div className="stats-grid">
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
          <div className="insights-grid-list">
            {insights.map((insight, index) => (
              <div key={index} className="insight-item">
                <span className="insight-icon">{insight.icon}</span>
                <span>{insight.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonthlyReportPage;
