import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Target, Plus,
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
  const [, setSummary] = useState({});

  // Form state for new goal
  const [formData, setFormData] = useState({
    goal_name: '',
    target_amount: '',
    monthly_contribution: '',
    target_date: ''
  });

  useEffect(() => {
    fetchGoals();
    // Load Razorpay checkout script
    if (!document.getElementById('razorpay-script')) {
      const script = document.createElement('script');
      script.id = 'razorpay-script';
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      document.body.appendChild(script);
    }
  }, []);

  const fetchGoals = async () => {
    try {
      setLoading(true);
      const userId = user?.user_id || user?.id;
      const response = await moneyService.getGoals(userId);
      if (response.data?.success) {
        setGoals(response.data?.data?.goals || []);
        setSummary(response.data?.data?.summary || {});
      } else {
        setGoals([]);
        setSummary({});
      }
      setError(null);
    } catch (err) {
      console.error('Failed to fetch goals:', err);
      if (err?.response?.status === 401) {
        setError('Session expired. Please log in again.');
      } else {
        setError('Failed to load goals. Please try again.');
      }
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
      if (err?.response?.status === 401) {
        alert('Session expired. Please log in again.');
      } else {
        alert(err?.response?.data?.message || 'Failed to create goal. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddSavings = async (goalId) => {
    if (!savingsAmount || isNaN(savingsAmount) || parseFloat(savingsAmount) <= 0) return;
    const amount = parseFloat(savingsAmount);

    try {
      // 1. Create Razorpay order
      const orderRes = await moneyService.createGoalPaymentOrder({
        goal_id: goalId,
        amount,
        goal_name: goals.find(g => g.id === goalId)?.goal_name || 'Goal Jar'
      });

      const { order_id, key } = orderRes.data;

      // 2. Open Razorpay checkout
      const options = {
        key,
        amount: amount * 100,
        currency: 'INR',
        name: 'ExpertEase',
        description: 'Goal Jar Savings',
        order_id,
        handler: async (response) => {
          // 3. Verify payment and record savings
          try {
            await moneyService.verifyGoalPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              goal_id: goalId,
              amount,
            });
            setSavingsAmount('');
            setAddingSavings(null);
            fetchGoals();
          } catch (err) {
            alert('Payment received but failed to record. Please contact support.');
          }
        },
        prefill: {
          name: user?.user_name || '',
          email: user?.email || '',
        },
        theme: { color: '#1F5F7A' },
        modal: {
          ondismiss: () => setAddingSavings(goalId) // keep input open if dismissed
        }
      };

      const rzp = new window.Razorpay(options);
      rzp.open();

    } catch (err) {
      console.error('Payment error:', err);
      alert(err?.response?.data?.error || 'Failed to initiate payment. Please try again.');
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

    </div>
  );
};

export default GoalJarPage;
