import React from 'react';

const CategoryBreakdown = ({ categories }) => {
  const categoryColors = {
    'Food': '#0F4C5C',
    'Transport': '#2C7DA0',
    'Shopping': '#F4B400',
    'Bills': '#2E8B57',
    'Entertainment': '#E67E22'
  };

  const formatCurrency = (amount) => {
    return `₹${amount.toLocaleString()}`;
  };

  // Handle different data formats
  const processedCategories = (categories || []).map(cat => ({
    name: cat.name || cat.category || 'Unknown',
    amount: cat.amount || 0
  }));

  if (!categories || categories.length === 0) {
    return (
      <div className="category-breakdown-empty">
        <p>No categories to display</p>
      </div>
    );
  }

  return (
    <div className="category-breakdown">
      {processedCategories.map((category, index) => (
        <div key={`${category.name}-${index}`} className="category-item">
          <div className="category-info">
            <div 
              className="category-dot" 
              style={{ backgroundColor: categoryColors[category.name] || '#6B7280' }}
            ></div>
            <span className="category-name">{category.name}</span>
          </div>
          <div className="category-amount">{formatCurrency(category.amount)}</div>
        </div>
      ))}
    </div>
  );
};

export default CategoryBreakdown;
