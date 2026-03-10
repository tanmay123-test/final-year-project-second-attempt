import React, { useState, useEffect } from 'react';
import { ArrowLeft, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import styles from '../styles/AddTransactionQuick.module.css';

const AddTransactionQuick = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // Form state for adding transactions
  const [formData, setFormData] = useState({
    category: 'Food',
    amount: '',
    description: '',
    merchant: '',
    date: new Date().toISOString().split('T')[0],
    type: 'expense'
  });

  const categories = [
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
          { id: 1, merchant: 'Swiggy', category: 'Food', description: 'Lunch', date: '2026-03-09', amount: 250, type: 'expense' },
          { id: 2, merchant: 'Amazon', category: 'Shopping', description: 'Headphones', date: '2026-03-08', amount: 1200, type: 'expense' },
          { id: 3, merchant: 'Uber', category: 'Transport', description: 'Ride', date: '2026-03-08', amount: 150, type: 'expense' },
          { id: 4, merchant: 'Jio', category: 'Bills', description: 'Recharge', date: '2026-03-07', amount: 500, type: 'expense' }
        ]);
      } else {
        setTransactions(transactionsData);
      }
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      // Use sample data on error
      setTransactions([
        { id: 1, merchant: 'Swiggy', category: 'Food', description: 'Lunch', date: '2026-03-09', amount: 250, type: 'expense' },
        { id: 2, merchant: 'Amazon', category: 'Shopping', description: 'Headphones', date: '2026-03-08', amount: 1200, type: 'expense' },
        { id: 3, merchant: 'Uber', category: 'Transport', description: 'Ride', date: '2026-03-08', amount: 150, type: 'expense' },
        { id: 4, merchant: 'Jio', category: 'Bills', description: 'Recharge', date: '2026-03-07', amount: 500, type: 'expense' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount greater than 0');
      return;
    }
    
    if (!formData.merchant.trim()) {
      setError('Please enter a merchant name');
      return;
    }
    
    try {
      const transactionData = {
        ...formData,
        amount: parseFloat(formData.amount)
      };
      
      console.log('Adding transaction:', transactionData);
      
      // Try to add to backend
      try {
        await moneyService.addTransaction(transactionData);
      } catch (backendError) {
        console.warn('Backend add failed, adding locally:', backendError);
        // If backend fails, add to local state
        const newTransaction = {
          id: transactions.length + 1,
          ...transactionData,
          date: transactionData.date
        };
        setTransactions(prev => [newTransaction, ...prev]);
      }
      
      // Reset form
      setFormData({
        category: 'Food',
        amount: '',
        description: '',
        merchant: '',
        date: new Date().toISOString().split('T')[0],
        type: 'expense'
      });
      setShowAddForm(false);
      setError(null);
      
      // Refresh transactions
      fetchTransactions();
    } catch (err) {
      console.error('Failed to add transaction:', err);
      setError('Failed to add transaction: ' + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className={styles.quickAddContainer}>
      {/* Mobile Header */}
      <header className={styles.quickAddHeader}>
        <button className={styles.backBtn} onClick={() => navigate('/money/dashboard')}>
          <ArrowLeft size={24} />
        </button>
        <div className={styles.headerTitle}>
          <h1>Add Transaction</h1>
          <p>Quick Mode</p>
        </div>
        <div className={styles.headerSpacer}></div>
      </header>

      {/* Main Content */}
      <main className={styles.quickAddMainContent}>
        <div className={styles.addTransactionSection}>
          <h2>Add a new transaction</h2>
          <button 
            className={styles.largeAddBtn}
            onClick={() => setShowAddForm(true)}
          >
            <Plus size={48} />
          </button>
        </div>
        
        <div className={styles.recentSection}>
          <h3>Recent</h3>
          <div className={styles.transactionsList}>
            {loading ? (
              <div className={styles.loadingState}>
                <p>Loading transactions...</p>
              </div>
            ) : transactions.length === 0 ? (
              <div className={styles.noTransactions}>
                <p>No transactions found</p>
              </div>
            ) : (
              transactions.slice(0, 4).map((transaction, index) => (
                <div key={index} className={styles.transactionCard}>
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
                    </div>
                  </div>
                  <div className={`${styles.transactionAmount} ${styles.expense}`}>
                    -₹{transaction.amount.toLocaleString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      {/* Add Transaction Modal */}
      {showAddForm && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3>Add Transaction</h3>
              <button className={styles.closeBtn} onClick={() => setShowAddForm(false)}>
                ×
              </button>
            </div>

            {error && (
              <div className={styles.errorMessage}>
                {error}
              </div>
            )}

            <form onSubmit={handleAddTransaction} className={styles.transactionForm}>
              <div className={styles.formGroup}>
                <label>Category</label>
                <select 
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  required
                >
                  {categories.map(cat => (
                    <option key={cat.name} value={cat.name}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className={styles.formGroup}>
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

              <div className={styles.formGroup}>
                <label>Description</label>
                <input 
                  type="text"
                  placeholder="Enter description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label>Merchant</label>
                <input 
                  type="text"
                  placeholder="Enter merchant name"
                  value={formData.merchant}
                  onChange={(e) => setFormData({...formData, merchant: e.target.value})}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label>Date</label>
                <input 
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                  required
                />
              </div>

              <div className={styles.formActions}>
                <button type="button" className={styles.cancelBtn} onClick={() => setShowAddForm(false)}>
                  Cancel
                </button>
                <button type="submit" className={styles.submitBtn}>
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

export default AddTransactionQuick;
