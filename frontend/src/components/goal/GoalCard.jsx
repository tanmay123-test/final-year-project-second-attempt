import React from 'react';
import { Calendar, Clock, TrendingUp } from 'lucide-react';
import '../../styles/GoalJar.css';

const GoalCard = ({ goal, onAddSavings, onViewDetails }) => {
  const getStatusBadge = (progress) => {
    if (progress >= 100) {
      return { bg: '#DCFCE7', text: '#16A34A', label: 'Completed' };
    } else if (progress >= 75) {
      return { bg: '#DCFCE7', text: '#16A34A', label: 'On Track' };
    } else if (progress >= 50) {
      return { bg: '#EFF6FF', text: '#2563EB', label: 'Halfway' };
    } else if (progress >= 25) {
      return { bg: '#FEF3C7', text: '#D97706', label: 'Started' };
    } else {
      return { bg: '#F1F5F9', text: '#64748B', label: 'Just Started' };
    }
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  };

  const calculateMonthsRemaining = (targetDate) => {
    if (!targetDate) return null;
    const today = new Date();
    const target = new Date(targetDate);
    const diffTime = target - today;
    const diffMonths = Math.ceil(diffTime / (1000 * 60 * 60 * 24 * 30));
    return Math.max(0, diffMonths);
  };

  const createDonutChart = (progress) => {
    const radius = 34;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference * (1 - progress / 100);

    return (
      <svg width="80" height="80" viewBox="0 0 80 80">
        {/* Track circle */}
        <circle
          cx="40"
          cy="40"
          r={radius}
          stroke="#E2E8F0"
          strokeWidth="7"
          fill="none"
        />
        {/* Progress arc */}
        <circle
          cx="40"
          cy="40"
          r={radius}
          stroke="#F4B400"
          strokeWidth="7"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(-90 40 40)"
        />
        {/* Center text */}
        <text
          x="40"
          y="40"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="14"
          fontWeight="700"
          fill="#1a2744"
          dy=".35em"
        >
          {Math.round(progress)}%
        </text>
      </svg>
    );
  };

  const status = getStatusBadge(goal.progress_percentage);
  const monthsRemaining = calculateMonthsRemaining(goal.target_date);

  return (
    <div className="goal-card">
      {/* Top Row */}
      <div className="goal-card-header">
        <h3 className="goal-name">{goal.goal_name}</h3>
        <div
          className="status-badge"
          style={{ backgroundColor: status.bg, color: status.text }}
        >
          {status.label}
        </div>
      </div>

      {/* Middle Row */}
      <div className="goal-card-middle">
        {/* Donut Chart */}
        <div className="donut-chart">
          {createDonutChart(goal.progress_percentage)}
        </div>

        {/* Amount Info */}
        <div className="amount-info">
          <div className="current-amount">{formatAmount(goal.current_amount)}</div>
          <div className="target-amount">of {formatAmount(goal.target_amount)}</div>
          <div className="monthly-contribution">
            <TrendingUp size={14} color="#1F5F7A" />
            <span>{formatAmount(goal.monthly_contribution)}/mo</span>
          </div>
        </div>
      </div>

      {/* Bottom Info Row */}
      <div className="goal-card-info">
        <div className="info-item">
          <Calendar size={14} color="#94A3B8" />
          <span>{goal.target_date || 'No date set'}</span>
        </div>
        <div className="info-item">
          <Clock size={14} color="#94A3B8" />
          <span>{monthsRemaining !== null ? `${monthsRemaining} months left` : 'No deadline'}</span>
        </div>
      </div>

      {/* Button Row */}
      <div className="goal-card-actions">
        <button
          className="add-savings-btn"
          onClick={() => onAddSavings(goal)}
        >
          Add Savings
        </button>
        <button
          className="view-details-btn"
          onClick={() => onViewDetails(goal)}
        >
          View Details
        </button>
      </div>
    </div>
  );
};

export default GoalCard;
