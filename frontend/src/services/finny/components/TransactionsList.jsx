import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import '../styles/TransactionsList.css';

const TransactionsList = ({ transactions, loading, onSearch, onFilter, searchTerm, filterCategory }) => {
  const [localTransactions, setLocalTransactions] = useState(transactions || []);

  useEffect(() => {
    setLocalTransactions(transactions || []);
  }, [transactions]);

  const categories = ['All', 'Food', 'Shopping', 'Bills', 'Transport', 'Entertainment'];

  const getCategoryColor = (category) => {
    const colors = {
      'Food': '#0F4C5C',
      'Shopping': '#F4B400',
      'Bills': '#2E8B57',
      'Transport': '#2C7DA0',
      'Entertainment': '#E67E22'
    };
    return colors[category] || '#6B7280';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit' 
    });
  };

  const filteredTransactions = localTransactions.filter(transaction => {
    const matchesSearch = !searchTerm || 
      transaction.merchant?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'All' || 
      transaction.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="transactions-loading">
        <div className="loading-spinner"></div>
        <p>Loading transactions...</p>
      </div>
    );
  }

  return (
    <div className="transactions-list">
      {/* Search and Filter Controls */}
      <div className="transactions-controls">
        <div className="search-bar">
          <Search size={20} color="#6B7280" />
          <input
            type="text"
            placeholder="Search merchant..."
            value={searchTerm || ''}
            onChange={(e) => onSearch(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-dropdown">
          <select
            value={filterCategory || 'All'}
            onChange={(e) => onFilter(e.target.value)}
            className="filter-select"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Transactions List */}
      <div className="transactions-container">
        {filteredTransactions.length === 0 ? (
          <div className="no-transactions">
            <p>No transactions found</p>
            <p>Try adjusting your search or filter</p>
          </div>
        ) : (
          filteredTransactions.map((transaction) => (
            <div key={transaction.id} className="transaction-card">
              <div className="transaction-left">
                <div 
                  className="category-dot" 
                  style={{ backgroundColor: getCategoryColor(transaction.category) }}
                ></div>
              </div>
              
              <div className="transaction-center">
                <div className="merchant-name">{transaction.merchant}</div>
                <div className="transaction-meta">
                  <span className="category-text">{transaction.category}</span>
                  <span className="date-text">{formatDate(transaction.date)}</span>
                  {transaction.description && (
                    <span className="description-text">{transaction.description}</span>
                  )}
                </div>
              </div>
              
              <div className="transaction-right">
                <div className="amount">
                  {transaction.amount < 0 ? '-' : '+'}₹{Math.abs(transaction.amount).toLocaleString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TransactionsList;
