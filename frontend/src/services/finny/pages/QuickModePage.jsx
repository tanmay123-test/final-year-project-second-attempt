import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, List, PieChart, BarChart3, Home, PiggyBank, Calculator, Target, Brain } from 'lucide-react';
import { moneyService } from '../../../shared/api';
import { transactionsApi } from '../api/transactionsApi';
import TransactionsList from '../components/TransactionsList';
import '../styles/QuickModePage.css';

const QuickModePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('quick-add');
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [allTransactions, setAllTransactions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [transactionForm, setTransactionForm] = useState({
    amount: '',
    merchant: '',
    category: 'Food',
    date: new Date().toISOString().split('T')[0],
    description: ''
  });

  useEffect(() => {
    fetchTransactions();
  }, []);

  useEffect(() => {
    if (activeTab === 'transactions') {
      fetchAllTransactions();
    }
  }, [activeTab]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getTransactions({ limit: 10 });
      
      // Transform backend data to match our UI structure
      const backendTransactions = response.data.transactions || [];
      const categoryColors = {
        'Food': '#0F4C5C',
        'Shopping': '#F4B400',
        'Bills': '#2E8B57',
        'Transport': '#2C7DA0',
        'Entertainment': '#E67E22'
      };

      const transformedTransactions = backendTransactions.map(tx => ({
        id: tx.id,
        merchant: tx.merchant || 'Unknown',
        category: tx.category || 'Other',
        date: tx.date || new Date().toISOString().split('T')[0],
        amount: tx.amount || 0,
        description: tx.description || '',
        categoryColor: categoryColors[tx.category] || '#6B7280'
      }));

      setRecentTransactions(transformedTransactions);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      setError('Failed to load transactions');
      
      // Fallback data
      setRecentTransactions([
        {
          id: 1,
          merchant: 'Swiggy',
          category: 'Food',
          date: '2026-03-09',
          amount: -250,
          categoryColor: '#0F4C5C'
        },
        {
          id: 2,
          merchant: 'Amazon',
          category: 'Shopping',
          date: '2026-03-08',
          amount: -1200,
          categoryColor: '#F4B400'
        },
        {
          id: 3,
          merchant: 'Uber',
          category: 'Transport',
          date: '2026-03-08',
          amount: -150,
          categoryColor: '#2C7DA0'
        },
        {
          id: 4,
          merchant: 'Jio',
          category: 'Bills',
          date: '2026-03-07',
          amount: -500,
          categoryColor: '#2E8B57'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAllTransactions = async () => {
    try {
      setTransactionsLoading(true);
      const result = await transactionsApi.getTransactions();
      
      if (result.success) {
        const categoryColors = {
          'Food': '#0F4C5C',
          'Shopping': '#F4B400',
          'Bills': '#2E8B57',
          'Transport': '#2C7DA0',
          'Entertainment': '#E67E22'
        };

        const transformedTransactions = result.data.map(tx => ({
          id: tx.id,
          merchant: tx.merchant || 'Unknown',
          category: tx.category || 'Other',
          date: tx.date || new Date().toISOString().split('T')[0],
          amount: tx.amount || 0,
          description: tx.description || '',
          categoryColor: categoryColors[tx.category] || '#6B7280'
        }));

        setAllTransactions(transformedTransactions);
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Failed to fetch all transactions:', err);
      setError('Failed to load transactions');
    } finally {
      setTransactionsLoading(false);
    }
  };

  const handleFormChange = (field, value) => {
    setTransactionForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveTransaction = async () => {
    try {
      const transactionData = {
        amount: parseFloat(transactionForm.amount),
        merchant: transactionForm.merchant,
        category: transactionForm.category,
        date: transactionForm.date,
        description: transactionForm.description,
        type: 'expense'
      };

      console.log('Sending transaction data:', transactionData);
      const response = await moneyService.addTransaction(transactionData);
      console.log('Transaction response:', response);

      // Reset form and close modal
      setTransactionForm({
        amount: '',
        merchant: '',
        category: 'Food',
        date: new Date().toISOString().split('T')[0],
        description: ''
      });
      setShowModal(false);
      
      // Refresh transactions
      fetchTransactions();
      
      // If we're on transactions tab, also refresh all transactions
      if (activeTab === 'transactions') {
        fetchAllTransactions();
      }
    } catch (err) {
      console.error('Failed to save transaction:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Failed to save transaction. Please try again.';
      alert(`Error: ${errorMessage}`);
    }
  };

  const tabs = [
    { id: 'quick-add', label: 'Quick Add', icon: Plus },
    { id: 'transactions', label: 'Transactions', icon: List },
    { id: 'summary', label: 'Summary', icon: PieChart },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

  const bottomNavItems = [
    { icon: Home, label: 'Finny', active: true },
    { icon: PiggyBank, label: 'Budget', active: false },
    { icon: Calculator, label: 'Loan', active: false },
    { icon: Target, label: 'Goal Jar', active: false },
    { icon: Brain, label: 'AI Coach', active: false }
  ];

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    // Remove navigation - just switch tabs within the same page
    // switch(tabId) {
    //   case 'transactions':
    //     navigate('/finny/transactions');
    //     break;
    //   case 'summary':
    //     navigate('/finny/summary');
    //     break;
    //   case 'analytics':
    //     navigate('/finny/analytics');
    //     break;
    // }
  };

  return (
    <div className="quick-mode-page">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <button 
            className="back-button" 
            onClick={() => navigate('/finny')}
          >
            <ArrowLeft size={20} />
          </button>
          <div className="header-text">
            <h1 className="header-title">Quick Mode</h1>
            <p className="header-subtitle">Fast & Simple tracking</p>
          </div>
        </div>
      </div>

      {/* Mode Switch Bar */}
      <div className="mode-switch-bar">
        <div className="tabs-container">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => handleTabClick(tab.id)}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Section */}
      <div className="main-section">
        {activeTab === 'quick-add' && (
          <>
            <div className="center-text">
              Add a new transaction
            </div>

            {/* Recent Transactions */}
            <div className="recent-transactions">
              <h2 className="section-title">Recent</h2>
              
              {loading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading transactions...</p>
                </div>
              ) : error ? (
                <div className="error-state">
                  <p>{error}</p>
                  <button onClick={fetchTransactions} className="retry-button">Retry</button>
                </div>
              ) : (
                <div className="transaction-list">
                  {recentTransactions.map((transaction) => (
                    <div key={transaction.id} className="transaction-card">
                      <div className="transaction-left">
                        <div 
                          className="category-dot" 
                          style={{ backgroundColor: transaction.categoryColor }}
                        ></div>
                      </div>
                      <div className="transaction-middle">
                        <div className="merchant-name">{transaction.merchant}</div>
                        <div className="transaction-meta">
                          <span className="category-text">{transaction.category}</span>
                          <span className="date-text">{transaction.date}</span>
                        </div>
                      </div>
                      <div className="transaction-right">
                        <div className="amount">
                          ₹{Math.abs(transaction.amount).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'transactions' && (
          <TransactionsList
            transactions={allTransactions}
            loading={transactionsLoading}
            onSearch={setSearchTerm}
            onFilter={setFilterCategory}
            searchTerm={searchTerm}
            filterCategory={filterCategory}
          />
        )}

        {activeTab === 'summary' && (
          <div className="center-text">
            <h3>Summary View</h3>
            <p>Monthly spending analysis and insights coming soon...</p>
            <button 
              className="navigate-button"
              onClick={() => navigate('/finny/summary')}
            >
              Open Full Summary
            </button>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="center-text">
            <h3>Analytics View</h3>
            <p>Advanced financial analytics coming soon...</p>
            <button 
              className="navigate-button"
              onClick={() => navigate('/finny/analytics')}
            >
              Open Full Analytics
            </button>
          </div>
        )}
      </div>

      {/* Add Transaction Button */}
      <button 
        className="add-transaction-button"
        onClick={() => setShowModal(true)}
      >
        <Plus size={32} color="#3A2A00" />
      </button>

      {/* Transaction Input Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Transaction</h3>
              <button 
                className="close-button"
                onClick={() => setShowModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Amount</label>
                <input 
                  type="number" 
                  placeholder="Enter amount" 
                  value={transactionForm.amount}
                  onChange={(e) => handleFormChange('amount', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Merchant</label>
                <input 
                  type="text" 
                  placeholder="Enter merchant name" 
                  value={transactionForm.merchant}
                  onChange={(e) => handleFormChange('merchant', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select 
                  value={transactionForm.category}
                  onChange={(e) => handleFormChange('category', e.target.value)}
                >
                  <option value="Food">Food</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Transport">Transport</option>
                  <option value="Bills">Bills</option>
                  <option value="Entertainment">Entertainment</option>
                </select>
              </div>
              <div className="form-group">
                <label>Date</label>
                <input 
                  type="date" 
                  value={transactionForm.date}
                  onChange={(e) => handleFormChange('date', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  placeholder="Add description (optional)"
                  value={transactionForm.description}
                  onChange={(e) => handleFormChange('description', e.target.value)}
                ></textarea>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="cancel-button"
                onClick={() => setShowModal(false)}
              >
                Cancel
              </button>
              <button 
                className="save-button"
                onClick={handleSaveTransaction}
                disabled={!transactionForm.amount || !transactionForm.merchant}
              >
                Save Transaction
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        {bottomNavItems.map((item, index) => (
          <div key={index} className={`nav-item ${item.active ? 'active' : ''}`}>
            <item.icon 
              size={20} 
              color={item.active ? '#F4B400' : '#6B7280'} 
            />
            <span className={`nav-label ${item.active ? 'active' : ''}`}>
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuickModePage;
