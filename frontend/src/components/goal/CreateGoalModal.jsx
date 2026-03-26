import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import goalApi from '../../services/goalApi';
import '../../styles/GoalJar.css';

const CreateGoalModal = ({ isOpen, onClose, onGoalCreated }) => {
  const [formData, setFormData] = useState({
    goal_name: '',
    target_amount: '',
    monthly_contribution: '',
    target_date: ''
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setFormData({
        goal_name: '',
        target_amount: '',
        monthly_contribution: '',
        target_date: ''
      });
    }
  }, [isOpen]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const calculateMonths = () => {
    const target = Number(formData.target_amount);
    const monthly = Number(formData.monthly_contribution);
    if (!target || !monthly || monthly <= 0) return null;
    return Math.ceil(target / monthly);
  };

  const calculateYears = () => {
    const months = calculateMonths();
    if (!months) return null;
    return (months / 12).toFixed(1);
  };

  const getRequiredMonthlyFor5Years = () => {
    const target = Number(formData.target_amount);
    if (!target) return 0;
    return Math.ceil(target / 60);
  };

  const months = calculateMonths();
  const years = calculateYears();
  const requiredMonthly = getRequiredMonthlyFor5Years();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        goal_name: formData.goal_name,
        target_amount: Number(formData.target_amount),
        monthly_contribution: Number(formData.monthly_contribution)
      };

      if (formData.target_date) {
        payload.target_date = formData.target_date;
      }

      const response = await goalApi.createGoal(payload);
      const data = response.data;

      if (data.success) {
        onGoalCreated();
        onClose();
        showToast('✓ Goal created!');
      } else {
        showToast('Failed to create goal. Try again.');
      }
    } catch (error) {
      console.error('Create goal error:', error);
      if (error?.response?.status === 401) {
        showToast('Session expired. Please log in again.');
      } else {
        showToast(error?.response?.data?.message || 'Failed to create goal. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message) => {
    // Simple toast implementation
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
          <h2>Create New Goal</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} color="#64748B" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="goal-form">
          {/* Goal Name */}
          <div className="form-field">
            <label>Goal Name</label>
            <input
              type="text"
              placeholder="e.g. Buy Bike, Vacation"
              value={formData.goal_name}
              onChange={(e) => handleInputChange('goal_name', e.target.value)}
              required
            />
          </div>

          {/* Target Amount */}
          <div className="form-field">
            <label>Target Amount (₹)</label>
            <input
              type="number"
              placeholder="e.g. 50000"
              value={formData.target_amount}
              onChange={(e) => handleInputChange('target_amount', e.target.value)}
              required
            />
          </div>

          {/* Monthly Contribution */}
          <div className="form-field">
            <label>Monthly Contribution (₹)</label>
            <input
              type="number"
              placeholder="e.g. 5000"
              value={formData.monthly_contribution}
              onChange={(e) => handleInputChange('monthly_contribution', e.target.value)}
              required
            />
          </div>

          {/* Target Date */}
          <div className="form-field">
            <label>Target Date (optional)</label>
            <input
              type="date"
              value={formData.target_date}
              onChange={(e) => handleInputChange('target_date', e.target.value)}
            />
          </div>

          {/* Auto Preview */}
          {months && (
            <div className="auto-preview">
              📅 You'll reach this in {months} months ({years} yrs)
            </div>
          )}

          {/* Feasibility Warning */}
          {months && months > 60 && (
            <div className="feasibility-warning">
              ⚠️ Over 5 years. Save ₹{requiredMonthly}/mo to finish in 5 yrs.
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="submit-btn"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Goal'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateGoalModal;
