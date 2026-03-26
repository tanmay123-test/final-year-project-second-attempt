import React from 'react';

const WeeklyBarChart = ({ data }) => {
  const maxValue = 1000;
  const chartWidth = 400;
  const chartHeight = 280;
  const padding = { top: 10, right: 10, left: 40, bottom: 40 };
  
  const getXPosition = (index) => {
    const availableWidth = chartWidth - padding.left - padding.right;
    const barWidth = availableWidth / data.length * 0.7; // 70% of available space for bars
    const gap = availableWidth / data.length * 0.3; // 30% for gaps
    return padding.left + (index * (barWidth + gap)) + (barWidth / 2);
  };
  
  const getYPosition = (value) => {
    const availableHeight = chartHeight - padding.top - padding.bottom;
    return chartHeight - padding.bottom - ((value / maxValue) * availableHeight);
  };
  
  const getBarHeight = (value) => {
    const availableHeight = chartHeight - padding.top - padding.bottom;
    return (value / maxValue) * availableHeight;
  };

  return (
    <div style={{ width: '100%', height: '280px' }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none">
        {/* Background */}
        <rect
          x={padding.left}
          y={padding.top}
          width={chartWidth - padding.left - padding.right}
          height={chartHeight - padding.top - padding.bottom}
          fill="#F9FAFB"
        />
        
        {/* Grid Lines */}
        {[0, 250, 500, 750, 1000].map((value) => {
          const y = getYPosition(value);
          return (
            <line
              key={value}
              x1={padding.left}
              x2={chartWidth - padding.right}
              y1={y}
              y2={y}
              stroke="#e0e0e0"
              strokeDasharray="3 3"
            />
          );
        })}
        
        {/* X and Y axis lines */}
        <line
          x1={padding.left}
          x2={chartWidth - padding.right}
          y1={chartHeight - padding.bottom}
          y2={chartHeight - padding.bottom}
          stroke="#e0e0e0"
        />
        <line
          x1={padding.left}
          x2={padding.left}
          y1={padding.top}
          y2={chartHeight - padding.bottom}
          stroke="#e0e0e0"
        />
        
        {/* Y-axis labels */}
        {[0, 250, 500, 750, 1000].map((value) => {
          const y = getYPosition(value);
          return (
            <text
              key={value}
              x={padding.left - 10}
              y={y + 4}
              textAnchor="end"
              fill="#888888"
              fontSize="12"
            >
              {value}
            </text>
          );
        })}
        
        {/* X-axis labels */}
        {data.map((item, index) => {
          const x = getXPosition(index);
          return (
            <text
              key={item.day}
              x={x}
              y={chartHeight - padding.bottom + 20}
              textAnchor="middle"
              fill="#888888"
              fontSize="12"
            >
              {item.day}
            </text>
          );
        })}
        
        {/* Bars */}
        {data.map((item, index) => {
          const x = getXPosition(index);
          const height = getBarHeight(item.amount);
          const barWidth = (chartWidth - padding.left - padding.right) / data.length * 0.7;
          const y = getYPosition(item.amount);
          
          return (
            <rect
              key={index}
              x={x - barWidth / 2}
              y={y}
              width={barWidth}
              height={height}
              fill="#1a3a5c"
              rx={[4, 4, 0, 0]} // Rounded top corners only
            />
          );
        })}
      </svg>
    </div>
  );
};

export default WeeklyBarChart;
