import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Target, TrendingUp, Calendar, Clock } from 'lucide-react';
import goalApi from '../../services/goalApi';
import '../../styles/GoalJar.css';

const GoalJarDetailPage = () => {
  const { goalId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [goal, setGoal] = useState(null);
  const [projection, setProjection] = useState([]);

  useEffect(() => {
    if (goalId) {
      fetchGoalDetails();
      fetchProjection();
    }
  }, [goalId]);

  const fetchGoalDetails = async () => {
    try {
      const response = await goalApi.getProgress(goalId);
      console.log('Goal detail response:', response);
      
      const data = response.data;
      if (data?.success) {
        setGoal(data.data);
      } else {
        // Mock data for testing
        setGoal(generateMockGoal());
      }
    } catch (error) {
      console.error('Fetch goal details error:', error);
      // Mock data for testing
      setGoal(generateMockGoal());
    } finally {
      setLoading(false);
    }
  };

  const fetchProjection = async () => {
    try {
      const response = await goalApi.getProjection(goalId);
      console.log('Projection response:', response);
      
      const data = response.data;
      if (data?.success) {
        setProjection(data.data?.projections || []);
      } else {
        // Mock projection data
        setProjection(generateMockProjection());
      }
    } catch (error) {
      console.error('Fetch projection error:', error);
      // Mock projection data
      setProjection(generateMockProjection());
    }
  };

  const generateMockGoal = () => {
    return {
      id: Number(goalId),
      goal_name: 'New MacBook Pro',
      target_amount: 250000,
      current_amount: 87500,
      monthly_contribution: 15000,
      target_date: '2026-12-31',
      progress_percentage: 35,
      created_date: '2026-01-15',
      total_contributions: 87500,
      months_remaining: 9,
      estimated_completion: '2027-03-15'
    };
  };

  const generateMockProjection = () => {
    const projection = [];
    const currentAmount = 87500;
    const monthlyContribution = 15000;
    const targetAmount = 250000;
    
    for (let month = 1; month <= 24; month++) {
      const projectedAmount = Math.min(currentAmount + (monthlyContribution * month), targetAmount);
      projection.push({
        month,
        projected_amount: projectedAmount,
        monthly_contribution: monthlyContribution,
        cumulative_amount: projectedAmount
      });
    }
    
    return projection;
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  };

  const handleBackClick = () => {
    navigate('/finny/goal-jar');
  };

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

  const createDonutChart = (progress) => {
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference * (1 - progress / 100);

    return (
      <svg width="140" height="140" viewBox="0 0 140 140">
        {/* Track circle */}
        <circle
          cx="70"
          cy="70"
          r={radius}
          stroke="#E2E8F0"
          strokeWidth="12"
          fill="none"
        />
        {/* Progress arc */}
        <circle
          cx="70"
          cy="70"
          r={radius}
          stroke="#F4B400"
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(-90 70 70)"
        />
        {/* Center text */}
        <text
          x="70"
          y="70"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="24"
          fontWeight="700"
          fill="#1a2744"
          dy=".35em"
        >
          {Math.round(progress)}%
        </text>
      </svg>
    );
  };

  if (loading) {
    return (
      <div className="goal-detail-page">
        <div className="detail-header">
          <button className="back-btn" onClick={handleBackClick}>
            <ArrowLeft size={20} color="white" />
          </button>
          <h1>Loading...</h1>
        </div>
        <div className="loading-skeleton">
          <div className="skeleton-donut"></div>
          <div className="skeleton-info"></div>
        </div>
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="goal-detail-page">
        <div className="detail-header">
          <button className="back-btn" onClick={handleBackClick}>
            <ArrowLeft size={20} color="white" />
          </button>
          <h1>Goal Not Found</h1>
        </div>
        <div className="error-state">
          <p>The goal you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  const status = getStatusBadge(goal.progress_percentage);

  return (
    <div className="goal-detail-page">
      {/* Header */}
      <div className="detail-header">
        <button className="back-btn" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <h1>{goal.goal_name}</h1>
      </div>

      {/* Main Content */}
      <div className="detail-content">
        {/* Progress Section */}
        <div className="progress-section">
          <div className="donut-container">
            {createDonutChart(goal.progress_percentage)}
          </div>
          
          <div className="progress-info">
            <div
              className="status-badge"
              style={{ backgroundColor: status.bg, color: status.text }}
            >
              {status.label}
            </div>
            
            <div className="amount-info">
              <div className="current-amount">{formatAmount(goal.current_amount)}</div>
              <div className="target-amount">of {formatAmount(goal.target_amount)}</div>
              <div className="monthly-info">
                <TrendingUp size={16} color="#1F5F7A" />
                <span>{formatAmount(goal.monthly_contribution)}/mo</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <Calendar size={20} color="#64748B" />
            <div>
              <div className="stat-label">Target Date</div>
              <div className="stat-value">{goal.target_date}</div>
            </div>
          </div>
          
          <div className="stat-card">
            <Clock size={20} color="#64748B" />
            <div>
              <div className="stat-label">Time Left</div>
              <div className="stat-value">{goal.months_remaining} months</div>
            </div>
          </div>
          
          <div className="stat-card">
            <Target size={20} color="#64748B" />
            <div>
              <div className="stat-label">Est. Completion</div>
              <div className="stat-value">{goal.estimated_completion}</div>
            </div>
          </div>
        </div>

        {/* Projection Chart */}
        <div className="projection-section">
          <h3>24-Month Projection</h3>
          <div className="projection-chart">
            {projection.slice(0, 12).map((item, index) => (
              <div key={item.month} className="projection-bar">
                <div
                  className="bar-fill"
                  style={{
                    height: `${(item.projected_amount / goal.target_amount) * 100}%`
                  }}
                ></div>
                <div className="bar-label">M{item.month}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="action-btn primary">
            Add Savings
          </button>
          <button className="action-btn secondary">
            Edit Goal
          </button>
        </div>
      </div>
    </div>
  );
};

export default GoalJarDetailPage;
