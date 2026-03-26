import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import goalApi from '../../services/goalApi';
import '../../styles/GoalJar.css';

const AddSavingsModal = ({ isOpen, onClose, goal, onSavingsAdded }) => {
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Online');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const paymentMethods = ['Online', 'Cash', 'Bank Transfer'];

  useEffect(() => {
    if (!isOpen) {
      setAmount('');
      setPaymentMethod('Online');
      setNotes('');
    }
  }, [isOpen]);

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!amount || Number(amount) <= 0) return;

    setLoading(true);

    try {
      const response = await goalApi.addSavings({
        goal_id: Number(goal.id),
        amount: Number(amount),
        payment_method: paymentMethod,
        notes: notes
      });

      const data = response.data;

      if (data?.success) {
        onSavingsAdded();
        onClose();
        showToast(`₹${Number(amount).toLocaleString('en-IN')} added!`);
      } else {
        showToast(data?.message || 'Failed to add savings. Try again.');
      }
    } catch (error) {
      console.error('Add savings error:', error);
      if (error?.response?.status === 401) {
        showToast('Session expired. Please log in again.');
      } else {
        showToast(error?.response?.data?.message || 'Failed to add savings. Please try again.');
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

  const getProgressPercentage = () => {
    if (!goal || !goal.target_amount) return 0;
    return (goal.current_amount / goal.target_amount) * 100;
  };

  if (!isOpen || !goal) return null;

  const progressPercentage = getProgressPercentage();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Drag Handle */}
        <div className="drag-handle"></div>

        {/* Header */}
        <div className="modal-header">
          <h2>Add Savings</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} color="#64748B" />
          </button>
        </div>

        {/* Goal Info */}
        <div className="goal-info">
          <div className="goal-name">{goal.goal_name}</div>
          <div className="progress-info">
            {formatAmount(goal.current_amount)} saved of {formatAmount(goal.target_amount)}
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${Math.min(progressPercentage, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="savings-form">
          {/* Amount Input */}
          <div className="amount-field">
            <input
              type="number"
              placeholder="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="amount-input"
              required
            />
          </div>

          {/* Payment Method */}
          <div className="payment-methods">
            {paymentMethods.map((method) => (
              <button
                key={method}
                type="button"
                className={`method-chip ${paymentMethod === method ? 'selected' : ''}`}
                onClick={() => setPaymentMethod(method)}
              >
                {method}
              </button>
            ))}
          </div>

          {/* Notes */}
          <div className="form-field">
            <label>Notes (optional)</label>
            <input
              type="text"
              placeholder="e.g. Monthly deposit"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="submit-btn savings-submit"
            disabled={!amount || Number(amount) <= 0 || loading}
          >
            {loading ? 'Adding...' : `Add ${formatAmount(amount)} to ${goal.goal_name}`}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AddSavingsModal;
