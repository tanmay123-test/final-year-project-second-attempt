import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import goalApi from '../../services/goalApi';
import '../../styles/GoalJar.css';

const TransferLeftoverModal = ({ isOpen, onClose, goals, onTransferComplete }) => {
  const [selectedGoalId, setSelectedGoalId] = useState('');
  const [amount, setAmount] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Food & Dining');
  const [loading, setLoading] = useState(false);

  const sourceCategories = [
    'Food & Dining',
    'Transport',
    'Shopping',
    'Entertainment',
    'Other'
  ];

  useEffect(() => {
    if (!isOpen) {
      setSelectedGoalId('');
      setAmount('');
      setSelectedCategory('Food & Dining');
    } else if (goals.length > 0) {
      setSelectedGoalId(goals[0].id.toString());
    }
  }, [isOpen, goals]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!amount || Number(amount) <= 0 || !selectedGoalId) return;

    setLoading(true);

    try {
      const response = await goalApi.transferLeftover({
        goal_id: Number(selectedGoalId),
        amount: Number(amount),
        source_category: selectedCategory
      });

      const data = response.data;

      if (data?.success) {
        onTransferComplete();
        onClose();
        showToast(`₹${Number(amount).toLocaleString('en-IN')} transferred!`);
      } else {
        showToast(data?.message || 'Failed to transfer. Try again.');
      }
    } catch (error) {
      console.error('Transfer error:', error);
      if (error?.response?.status === 401) {
        showToast('Session expired. Please log in again.');
      } else {
        showToast(error?.response?.data?.message || 'Failed to transfer. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message) => {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #1a2744;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      z-index: 9999;
      font-size: 14px;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 3000);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Drag Handle */}
        <div className="drag-handle"></div>

        {/* Header */}
        <div className="modal-header">
          <h2>Transfer Leftover Budget</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} color="#64748B" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="transfer-form">
          {/* Select Goal */}
          <div className="form-field">
            <label>Select Goal</label>
            <select
              value={selectedGoalId}
              onChange={(e) => setSelectedGoalId(e.target.value)}
              className="goal-select"
              required
            >
              {goals.map((goal) => (
                <option key={goal.id} value={goal.id}>
                  {goal.goal_name}
                </option>
              ))}
            </select>
          </div>

          {/* Amount */}
          <div className="form-field">
            <label>Amount (₹)</label>
            <input
              type="number"
              placeholder="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </div>

          {/* Source Category */}
          <div className="form-field">
            <label>Source Category</label>
            <div className="category-chips">
              {sourceCategories.map((category) => (
                <button
                  key={category}
                  type="button"
                  className={`category-chip ${selectedCategory === category ? 'selected' : ''}`}
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="submit-btn transfer-submit"
            disabled={!amount || Number(amount) <= 0 || loading}
          >
            {loading ? 'Transferring...' : 'Transfer to Goal'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default TransferLeftoverModal;
