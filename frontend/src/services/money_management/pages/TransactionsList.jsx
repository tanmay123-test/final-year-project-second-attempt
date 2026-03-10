import React, { useState, useEffect } from 'react';
import { ArrowLeft, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import styles from '../styles/TransactionsList.module.css';

const TransactionsList = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('All');

  const categories = [
    { name: 'All', color: '#6c757d' },
    { name: 'Food', color: '#007bff' },
    { name: 'Shopping', color: '#ffc107' },
    { name: 'Transport', color: '#007bff' },
    { name: 'Bills', color: '#28a745' },
    { name: 'Entertainment', color: '#dc3545' },
    { name: 'Healthcare', color: '#6610f2' },
    { name: 'Education', color: '#17a2b8' },
    { name: 'Other', color: '#6c757d' }
  ];

  const getCategoryColor = (categoryName) => {
    const category = categories.find(cat => cat.name === categoryName);
    return category ? category.color : '#6c757d';
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getTransactions();
      const transactionsData = response.data.transactions || [];
      
      // If no transactions, use sample data
      if (transactionsData.length === 0) {
        setTransactions([
          { id: 1, merchant: 'Swiggy', category: 'Food', description: 'Lunch order', date: '2026-03-09', amount: 250, type: 'expense' },
          { id: 2, merchant: 'Amazon', category: 'Shopping', description: 'Headphones', date: '2026-03-08', amount: 1200, type: 'expense' },
          { id: 3, merchant: 'Uber', category: 'Transport', description: 'Office commute', date: '2026-03-08', amount: 150, type: 'expense' },
          { id: 4, merchant: 'Jio', category: 'Bills', description: 'Phone recharge', date: '2026-03-07', amount: 500, type: 'expense' },
          { id: 5, merchant: 'Netflix', category: 'Entertainment', description: 'Monthly subscription', date: '2026-03-06', amount: 300, type: 'expense' },
          { id: 6, merchant: 'Apollo', category: 'Healthcare', description: 'Medicines', date: '2026-03-05', amount: 800, type: 'expense' },
          { id: 7, merchant: 'Coursera', category: 'Education', description: 'Course fee', date: '2026-03-04', amount: 1500, type: 'expense' },
          { id: 8, merchant: 'Metro', category: 'Transport', description: 'Daily pass', date: '2026-03-03', amount: 100, type: 'expense' }
        ]);
      } else {
        setTransactions(transactionsData);
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      // Use sample data on error
      setTransactions([
        { id: 1, merchant: 'Swiggy', category: 'Food', description: 'Lunch order', date: '2026-03-09', amount: 250, type: 'expense' },
        { id: 2, merchant: 'Amazon', category: 'Shopping', description: 'Headphones', date: '2026-03-08', amount: 1200, type: 'expense' },
        { id: 3, merchant: 'Uber', category: 'Transport', description: 'Office commute', date: '2026-03-08', amount: 150, type: 'expense' },
        { id: 4, merchant: 'Jio', category: 'Bills', description: 'Phone recharge', date: '2026-03-07', amount: 500, type: 'expense' },
        { id: 5, merchant: 'Netflix', category: 'Entertainment', description: 'Monthly subscription', date: '2026-03-06', amount: 300, type: 'expense' },
        { id: 6, merchant: 'Apollo', category: 'Healthcare', description: 'Medicines', date: '2026-03-05', amount: 800, type: 'expense' },
        { id: 7, merchant: 'Coursera', category: 'Education', description: 'Course fee', date: '2026-03-04', amount: 1500, type: 'expense' },
        { id: 8, merchant: 'Metro', category: 'Transport', description: 'Daily pass', date: '2026-03-03', amount: 100, type: 'expense' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredTransactions = transactions.filter(transaction => {
    const matchesSearch = transaction.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          transaction.merchant?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          transaction.category?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'All' || transaction.category === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className={styles.transactionsContainer}>
      {/* Mobile Header */}
      <header className={styles.transactionsHeader}>
        <button className={styles.backBtn} onClick={() => navigate('/money/dashboard')}>
          <ArrowLeft size={24} />
        </button>
        <div className={styles.headerTitle}>
          <h1>Transactions</h1>
          <p>All your transactions</p>
        </div>
        <div className={styles.headerSpacer}></div>
      </header>

      {/* Main Content */}
      <main className={styles.transactionsMainContent}>
        {/* Search and Filter */}
        <div className={styles.searchFilterContainer}>
          <div className={styles.searchBox}>
            <Search size={20} className={styles.searchIcon} />
            <input
              type="text"
              placeholder="Search merchant..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={styles.searchInput}
            />
          </div>
          <select 
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className={styles.filterDropdown}
          >
            {categories.map(cat => (
              <option key={cat.name} value={cat.name}>{cat.name}</option>
            ))}
          </select>
        </div>

        {/* Transactions List */}
        <div className={styles.transactionsList}>
          {loading ? (
            <div className={styles.loadingState}>
              <p>Loading transactions...</p>
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className={styles.noTransactions}>
              <p>No transactions found</p>
            </div>
          ) : (
            filteredTransactions.map((transaction, index) => (
              <div key={index} className={styles.transactionItem}>
                <div className={styles.transactionLeft}>
                  <div 
                    className={styles.categoryDot}
                    style={{ backgroundColor: getCategoryColor(transaction.category) }}
                  />
                  <div className={styles.transactionDetails}>
                    <div className={styles.merchantName}>
                      {transaction.merchant}
                    </div>
                    <div className={styles.categoryDate}>
                      {transaction.category} • {new Date(transaction.date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: '2-digit', 
                        year: 'numeric' 
                      })}
                    </div>
                    <div className={styles.description}>
                      {transaction.description}
                    </div>
                  </div>
                </div>
                <div className={`${styles.transactionAmount} ${styles.expense}`}>
                  -₹{transaction.amount.toLocaleString()}
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
};

export default TransactionsList;
