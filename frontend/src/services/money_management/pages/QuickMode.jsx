import React, { useState, useEffect } from 'react';
import { ArrowLeft, Plus, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/QuickMode.css';

const QuickMode = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Debug state
  console.log('showAddForm:', showAddForm);

  // Form state
  const [formData, setFormData] = useState({
    category: 'Food',
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    type: 'expense' // Always expense, no income option
  });

  const categories = [
    'Food', 'Shopping', 'Bills', 'Transport', 'Entertainment', 
    'Healthcare', 'Education', 'Other'
  ];

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getTransactions();
      setTransactions(response.data.transactions || []);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      setError('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    try {
      await moneyService.addTransaction({
        ...formData,
        amount: parseFloat(formData.amount)
      });
      
      // Reset form
      setFormData({
        category: 'Food',
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        type: 'expense' // Always expense
      });
      setShowAddForm(false);
      
      // Refresh transactions
      fetchTransactions();
    } catch (err) {
      console.error('Failed to add transaction:', err);
      setError('Failed to add transaction');
    }
  };

  const filteredTransactions = transactions.filter(transaction => 
    transaction.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    transaction.category?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="quick-mode-container">
      {/* ExpertEase Header */}
      <header className="experthease-header">
        <div className="header-left">
          <div className="logo">
            <span className="expert-text">Expert</span>
            <span className="ease-text">Ease</span>
          </div>
        </div>
        
        <nav className="header-nav">
          <a href="#" className="nav-link">Dashboard</a>
          <a href="#" className="nav-link">Find Housekeeping Worker</a>
        </nav>
        
        <div className="header-right">
          <div className="user-info">
            <span>Hi, {user?.name || 'Sarthak Surendra Sawant'}</span>
          </div>
          <button className="logout-btn">Logout</button>
        </div>
      </header>

      {/* Quick Mode Banner */}
      <div className="quick-mode-banner">
        <button className="back-arrow" onClick={() => navigate('/money/dashboard')}>
          <ArrowLeft size={24} />
        </button>
        <h1>Quick Mode</h1>
        <div className="banner-spacer"></div>
      </div>

      {/* Main Content */}
      <main className="quick-main-content">
        <div className="transactions-section">
          <div className="transactions-header">
            <h2>Recent Transactions</h2>
            <button 
              className="quick-add-btn"
              onClick={() => {
                console.log('Quick Add button clicked!');
                setShowAddForm(true);
              }}
            >
              <Plus size={20} />
              Quick Add
            </button>
          </div>

          <div className="search-container">
            <Search size={20} className="search-icon" />
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="transactions-list">
            {loading ? (
              <div className="loading-state">
                <p>Loading transactions...</p>
              </div>
            ) : error ? (
              <div className="error-state">
                <p>{error}</p>
                <button onClick={fetchTransactions}>Retry</button>
              </div>
            ) : filteredTransactions.length === 0 ? (
              <div className="no-transactions">
                <p>No transactions found</p>
              </div>
            ) : (
              filteredTransactions.map((transaction, index) => (
                <div key={index} className="transaction-item">
                  <div className="transaction-info">
                    <div className="transaction-category">{transaction.category}</div>
                    <div className="transaction-description">{transaction.description || 'No description'}</div>
                    <div className="transaction-date">
                      {new Date(transaction.date).toLocaleDateString()}
                    </div>
                  </div>
                  <div className={`transaction-amount ${transaction.type}`}>
                    {transaction.type === 'expense' ? '-' : '+'}₹{transaction.amount.toLocaleString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        <button className="nav-item active">
          Transactions
        </button>
        <button className="nav-item">
          Summary
        </button>
        <button className="nav-item">
          Analytics
        </button>
      </div>

      {/* Add Transaction Modal */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Add Transaction</h3>
              <button className="close-btn" onClick={() => setShowAddForm(false)}>
                ×
              </button>
            </div>

            <form onSubmit={handleAddTransaction} className="transaction-form">
              <div className="form-group">
                <label>Category</label>
                <select 
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  required
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Amount</label>
                <input 
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={formData.amount}
                  onChange={(e) => setFormData({...formData, amount: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <input 
                  type="text"
                  placeholder="Enter description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label>Date</label>
                <input 
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                  required
                />
              </div>

              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowAddForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn">
                  Add Transaction
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickMode;
