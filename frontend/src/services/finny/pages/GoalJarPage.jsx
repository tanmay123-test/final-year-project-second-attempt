import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Target, Plus, Home, PiggyBank, Calculator, Brain, 
  Calendar, TrendingUp, AlertCircle 
} from 'lucide-react';
import { moneyService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/GoalJarPage.css';

const GoalJarPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [addingSavings, setAddingSavings] = useState(null); // ID of goal being added to
  const [savingsAmount, setSavingsAmount] = useState('');

  // Form state for new goal
  const [formData, setFormData] = useState({
    goal_name: '',
    target_amount: '',
    monthly_contribution: '',
    target_date: ''
  });

  const bottomNavItems = [
    { icon: Home, label: 'Finny', path: '/finny' },
    { icon: PiggyBank, label: 'Budget', path: '/finny/budget' },
    { icon: Calculator, label: 'Loan', path: '/finny/loan' },
    { icon: Target, label: 'Goal Jar', path: '/finny/goals', active: true },
    { icon: Brain, label: 'AI Coach', path: '/finny/coach' }
  ];

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      const userId = user?.user_id || user?.id;
      const response = await moneyService.getGoals(userId);
      setGoals(response.data?.goals || response.data || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch goals:', err);
      setError('Failed to load goals. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const userId = user?.user_id || user?.id;
      await moneyService.createGoal({
        user_id: userId,
        ...formData
      });
      setShowModal(false);
      setFormData({ goal_name: '', target_amount: '', monthly_contribution: '', target_date: '' });
      fetchGoals();
    } catch (err) {
      console.error('Failed to create goal:', err);
      alert('Failed to create goal.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddSavings = async (goalId) => {
    if (!savingsAmount || isNaN(savingsAmount)) return;
    try {
      setAddingSavings(goalId);
      const userId = user?.user_id || user?.id;
      await moneyService.addGoalSavings({
        user_id: userId,
        goal_id: goalId,
        amount: parseFloat(savingsAmount)
      });
      setSavingsAmount('');
      setAddingSavings(null);
      fetchGoals();
    } catch (err) {
      console.error('Failed to add savings:', err);
      alert('Failed to add savings.');
      setAddingSavings(null);
    }
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
        <div className="goal-jar-page">
          {/* Header */}
          <div className="header">
            <div className="header-content">
              <button className="back-button" onClick={() => navigate('/finny')}>
                <ArrowLeft size={20} />
              </button>
              <div className="header-text">
                <h1 className="header-title">Goal Jars</h1>
                <p className="header-subtitle">Save for your dreams</p>
              </div>
            </div>
          </div>

          <div className="main-content">
            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading your goals...</p>
              </div>
            ) : error ? (
              <div className="error-state">
                <AlertCircle size={40} color="#DC2626" />
                <p>{error}</p>
                <button onClick={fetchGoals} className="retry-button">Retry</button>
              </div>
            ) : goals.length === 0 ? (
              <div className="empty-state">
                <Target size={60} className="empty-state-icon" />
                <h3>No Goal Jars Yet</h3>
                <p>Start saving by creating your first goal jar.</p>
                <button onClick={() => setShowModal(true)} className="retry-button">Create First Goal</button>
              </div>
            ) : (
              <div className="goal-grid">
                {goals.map((goal, index) => {
                  const current = goal.current_amount || 0;
                  const target = goal.target_amount || 1;
                  const percent = Math.min((current / target) * 100, 100).toFixed(1);

                  return (
                    <div key={index} className="goal-card">
                      <div className="goal-card-header">
                        <div className="goal-name-group">
                          <div className="goal-emoji">🎯</div>
                          <span className="goal-name">{goal.goal_name}</span>
                        </div>
                        <span className="goal-percentage">{percent}%</span>
                      </div>

                      <div className="goal-amounts">
                        <span className="current-amount">{formatCurrency(current)}</span>
                        <span className="target-amount">of {formatCurrency(target)}</span>
                      </div>

                      <div className="progress-container">
                        <div 
                          className="progress-bar" 
                          style={{ width: `${percent}%` }}
                        ></div>
                      </div>

                      <div className="goal-details">
                        <div className="goal-detail-item">
                          <span className="detail-label">Monthly Savings</span>
                          <span className="detail-value">{formatCurrency(goal.monthly_contribution)}</span>
                        </div>
                        <div className="goal-detail-item" style={{ textAlign: 'right' }}>
                          <span className="detail-label">Target Date</span>
                          <span className="detail-value">{new Date(goal.target_date).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <div className="add-money-section">
                        {addingSavings === goal.id ? (
                          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                            <input 
                              type="number" 
                              className="chat-input" 
                              placeholder="Amount"
                              style={{ padding: '8px', borderRadius: '8px', border: '1px solid #E5E7EB', flex: 1 }}
                              value={savingsAmount}
                              onChange={e => setSavingsAmount(e.target.value)}
                            />
                            <button 
                              className="btn-submit" 
                              style={{ padding: '8px 12px', fontSize: '12px' }}
                              onClick={() => handleAddSavings(goal.id)}
                            >
                              Add
                            </button>
                            <button 
                              className="btn-cancel" 
                              style={{ padding: '8px 12px', fontSize: '12px' }}
                              onClick={() => setAddingSavings(null)}
                            >
                              X
                            </button>
                          </div>
                        ) : (
                          <button 
                            className="add-money-btn"
                            onClick={() => setAddingSavings(goal.id)}
                          >
                            Add Money
                          </button>
                        )}
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

          {/* New Goal Modal */}
          {showModal && (
            <div className="modal-overlay" onClick={() => setShowModal(false)}>
              <div className="modal-content" onClick={e => e.stopPropagation()}>
                <h2 className="modal-title">New Goal Jar</h2>
                <form onSubmit={handleCreateGoal}>
                  <div className="form-group">
                    <label>Goal Name</label>
                    <input 
                      type="text" 
                      placeholder="e.g. New Car"
                      value={formData.goal_name}
                      onChange={e => setFormData({ ...formData, goal_name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Target Amount (₹)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 10,00,000"
                      value={formData.target_amount}
                      onChange={e => setFormData({ ...formData, target_amount: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Monthly Contribution (₹)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 20,000"
                      value={formData.monthly_contribution}
                      onChange={e => setFormData({ ...formData, monthly_contribution: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Target Date</label>
                    <input 
                      type="date" 
                      value={formData.target_date}
                      onChange={e => setFormData({ ...formData, target_date: e.target.value })}
                      required
                    />
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
                      {submitting ? 'Creating...' : 'Create Goal'}
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

export default GoalJarPage;
