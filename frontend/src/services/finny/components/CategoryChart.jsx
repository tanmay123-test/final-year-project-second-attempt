import React from 'react';

const CategoryChart = ({ categories, totalSpending }) => {
  const categoryColors = {
    'Food': '#0F4C5C',
    'Transport': '#2C7DA0',
    'Shopping': '#F4B400',
    'Bills': '#2E8B57',
    'Entertainment': '#E67E22'
  };

  const calculatePercentage = (amount) => {
    return totalSpending > 0 ? ((amount / totalSpending) * 100).toFixed(1) : 0;
  };

  const createPieSlice = (data, index, total) => {
    const startAngle = index === 0 ? 0 : data.slice(0, index).reduce((acc, curr) => acc + curr.percentage, 0);
    const endAngle = startAngle + parseFloat(data[index].percentage);
    
    const largeRadius = 40;
    const smallRadius = 0; // Full pie chart (not donut)
    
    // Convert angles to radians
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;
    
    // Calculate path for pie slice
    const x1 = 50 + largeRadius * Math.cos(startAngleRad);
    const y1 = 50 + largeRadius * Math.sin(startAngleRad);
    const x2 = 50 + largeRadius * Math.cos(endAngleRad);
    const y2 = 50 + largeRadius * Math.sin(endAngleRad);
    
    const largeArcFlag = endAngle - startAngle > 180 ? 1 : 0;
    
    return `
      M 50 50
      L ${x1} ${y1}
      A ${largeRadius} ${largeRadius} 0 ${largeArcFlag} 1
      L ${x2} ${y2}
      Z
    `;
  };

  // Handle different data formats
  const chartData = (categories || []).map(cat => ({
    name: cat.name || cat.category || 'Unknown',
    amount: cat.amount || 0,
    color: categoryColors[cat.name || cat.category] || '#6B7280',
    percentage: calculatePercentage(cat.amount || 0)
  }));

  if (!categories || categories.length === 0 || totalSpending === 0) {
    return (
      <div className="category-chart-empty">
        <div className="empty-chart-message">
          <p>No spending data available</p>
          <p>Add transactions to see your breakdown</p>
        </div>
      </div>
    );
  }

  return (
    <div className="category-chart">
      <svg viewBox="0 0 100 100" className="pie-chart">
        {chartData.map((segment, index) => (
          <path
            key={`${segment.name}-${index}`}
            d={createPieSlice(chartData, index, totalSpending)}
            fill={segment.color}
            className="chart-segment"
            title={`${segment.name}: ₹${segment.amount.toLocaleString()} (${segment.percentage}%)`}
          />
        ))}
      </svg>
      
      {/* Legend */}
      <div className="chart-legend">
        {chartData.map((segment, index) => (
          <div key={`${segment.name}-legend-${index}`} className="legend-item">
            <div 
              className="legend-color" 
              style={{ backgroundColor: segment.color }}
            ></div>
            <span className="legend-text">
              {segment.name} ({segment.percentage}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryChart;
