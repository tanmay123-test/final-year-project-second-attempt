import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, PiggyBank, ShoppingBag, Car, Zap, Heart, BookOpen, DollarSign, MoreHorizontal, Home, Calculator, Target, Brain, AlertCircle } from 'lucide-react';import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/BudgetPage.css';

const BudgetPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    category: 'Food',
    amount: '',
    period: 'Monthly'
  });

  const categories = [
    { name: 'Food', icon: ShoppingBag, color: '#0F4C5C' },
    { name: 'Transport', icon: Car, color: '#2C7DA0' },
    { name: 'Shopping', icon: ShoppingBag, color: '#F4B400' },
    { name: 'Entertainment', icon: Zap, color: '#E67E22' },
    { name: 'Health', icon: Heart, color: '#EF4444' },
    { name: 'Education', icon: BookOpen, color: '#8B5CF6' },
    { name: 'Bills', icon: DollarSign, color: '#2E8B57' },
    { name: 'Other', icon: MoreHorizontal, color: '#6B7280' }
  ];

  const bottomNavItems = [
    { icon: Home, label: 'Finny', path: '/finny' },
    { icon: PiggyBank, label: 'Budget', path: '/finny/budget', active: true },
    { icon: Calculator, label: 'Loan', path: '/finny/loan' },
    { icon: Target, label: 'Goal Jar', path: '/finny/goals' },
    { icon: Brain, label: 'AI Coach', path: '/finny/coach' }
  ];

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      const response = await moneyService.getBudgets();
      setBudgets(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch budgets:', err);
      setError('Failed to load budgets. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.amount || isNaN(formData.amount)) return;

    try {
      setSubmitting(true);
      await moneyService.setBudget({
        category: formData.category,
        amount: parseFloat(formData.amount),
        period: formData.period
      });
      setShowModal(false);
      setFormData({ category: 'Food', amount: '', period: 'Monthly' });
      fetchBudgets();
    } catch (err) {
      console.error('Failed to set budget:', err);
      alert('Failed to set budget. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getCategoryIcon = (categoryName) => {
    const cat = categories.find(c => c.name === categoryName) || categories[categories.length - 1];
    return cat;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="finny-page-layout">
      {/* Sidebar for Desktop */}
      <aside className="finny-sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">Finny</h1>
          <p className="sidebar-subtitle">Smart Tracker</p>
        </div>
        <nav className="sidebar-nav">
          {bottomNavItems.map((item, index) => (
            <div 
              key={index} 
              className={`sidebar-item ${item.active ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <item.icon size={20} color={item.active ? '#F4B400' : '#6B7280'} />
              <span className="sidebar-label">{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      <div className="finny-page-content">
        <div className="budget-page">
          {/* Header */}
          <div className="header">
            <div className="header-content">
              <button className="back-button" onClick={() => navigate('/finny')}>
                <ArrowLeft size={20} />
              </button>
              <div className="header-text">
                <h1 className="header-title">Monthly Budgets</h1>
                <p className="header-subtitle">Plan your spending</p>
              </div>
            </div>
          </div>

          <div className="main-content">
            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Fetching your budgets...</p>
              </div>
            ) : error ? (
              <div className="error-state">
                <AlertCircle size={40} color="#DC2626" />
                <p>{error}</p>
                <button onClick={fetchBudgets} className="retry-button">Retry</button>
              </div>
            ) : budgets.length === 0 ? (
              <div className="empty-state">
                <PiggyBank size={60} className="empty-state-icon" />
                <h3>No Budgets Set</h3>
                <p>Start by setting a budget for a category.</p>
                <button onClick={() => setShowModal(true)} className="retry-button">Set First Budget</button>
              </div>
            ) : (
              <div className="budget-grid">
                {budgets.map((budget, index) => {
                  const cat = getCategoryIcon(budget.category);
                  const spent = budget.current_spending || 0;
                  const limit = budget.amount || 0;
                  const percent = Math.min((spent / limit) * 100, 100);
                  const isOver = spent > limit;
                  const remaining = limit - spent;

                  return (
                    <div key={index} className="budget-card">
                      <div className="budget-card-header">
                        <div className="category-info">
                          <div 
                            className="category-icon-wrapper" 
                            style={{ backgroundColor: `${cat.color}15` }}
                          >
                            <cat.icon size={24} color={cat.color} />
                          </div>
                          <span className="category-name">{budget.category}</span>
                        </div>
                        <span className="amount-limit">{formatCurrency(limit)}</span>
                      </div>

                      <div className="budget-amounts">
                        <span className="amount-spent">{formatCurrency(spent)}</span>
                        <span className={`remaining-text ${isOver ? 'over' : 'under'}`}>
                          {isOver ? 'Over by ' : 'Remaining: '}
                          {formatCurrency(Math.abs(remaining))}
                        </span>
                      </div>

                      <div className="progress-container">
                        <div 
                          className="progress-bar" 
                          style={{ 
                            width: `${percent}%`,
                            backgroundColor: isOver ? '#DC2626' : '#059669'
                          }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Floating Action Button */}
          <button className="fab" onClick={() => setShowModal(true)}>
            <Plus size={24} />
          </button>

          {/* Set Budget Modal */}
          {showModal && (
            <div className="modal-overlay" onClick={() => setShowModal(false)}>
              <div className="modal-content" onClick={e => e.stopPropagation()}>
                <h2 className="modal-title">Set Budget</h2>
                <form onSubmit={handleSubmit}>
                  <div className="form-group">
                    <label>Category</label>
                    <select 
                      value={formData.category}
                      onChange={e => setFormData({ ...formData, category: e.target.value })}
                    >
                      {categories.map(cat => (
                        <option key={cat.name} value={cat.name}>{cat.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Monthly Limit (₹)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 5000"
                      value={formData.amount}
                      onChange={e => setFormData({ ...formData, amount: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Period</label>
                    <select 
                      value={formData.period}
                      onChange={e => setFormData({ ...formData, period: e.target.value })}
                    >
                      <option value="Monthly">Monthly</option>
                    </select>
                  </div>
                  <div className="modal-actions">
                    <button 
                      type="button" 
                      className="btn-cancel"
                      onClick={() => setShowModal(false)}
                    >
                      Cancel
                    </button>
                    <button 
                      type="submit" 
                      className="btn-submit"
                      disabled={submitting}
                    >
                      {submitting ? 'Setting...' : 'Set Budget'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Bottom Navigation for Mobile */}
          <div className="finny-bottom-nav">
            {bottomNavItems.map((item, index) => (
              <div 
                key={index} 
                className={`nav-item ${item.active ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
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
      </div>
    </div>
  );
};

export default BudgetPage;
