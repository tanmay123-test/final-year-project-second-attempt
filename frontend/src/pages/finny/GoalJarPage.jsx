import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, Bell, User } from 'lucide-react';
import goalApi from '../../services/goalApi';
import GoalCard from '../../components/goal/GoalCard';
import CreateGoalModal from '../../components/goal/CreateGoalModal';
import AddSavingsModal from '../../components/goal/AddSavingsModal';
import TransferLeftoverModal from '../../components/goal/TransferLeftoverModal';
import '../../styles/GoalJar.css';

const GoalJarPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [goals, setGoals] = useState([]);
  const [summary, setSummary] = useState({
    total_goals: 0,
    total_target: 0,
    total_saved: 0,
    overall_progress: 0
  });

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAddSavingsModal, setShowAddSavingsModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    setLoading(true);
    try {
      const response = await goalApi.getGoals();
      console.log('Goals response:', response);
      
      const data = response.data;
      if (data?.success) {
        setGoals(data.data?.goals || []);
        setSummary(data.data?.summary || {
          total_goals: 0,
          total_target: 0,
          total_saved: 0,
          overall_progress: 0
        });
      } else {
        // Mock data for testing
        const mockData = generateMockData();
        setGoals(mockData.goals);
        setSummary(mockData.summary);
      }
    } catch (error) {
      console.error('Fetch goals error:', error);
      // Mock data for testing
      const mockData = generateMockData();
      setGoals(mockData.goals);
      setSummary(mockData.summary);
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const mockGoals = [
      {
        id: 1,
        goal_name: 'New MacBook Pro',
        target_amount: 250000,
        current_amount: 87500,
        monthly_contribution: 15000,
        target_date: '2026-12-31',
        progress_percentage: 35
      },
      {
        id: 2,
        goal_name: 'Vacation to Bali',
        target_amount: 150000,
        current_amount: 112500,
        monthly_contribution: 8000,
        target_date: '2026-08-15',
        progress_percentage: 75
      },
      {
        id: 3,
        goal_name: 'Emergency Fund',
        target_amount: 500000,
        current_amount: 125000,
        monthly_contribution: 20000,
        target_date: '2027-06-30',
        progress_percentage: 25
      }
    ];

    const totalTarget = mockGoals.reduce((sum, goal) => sum + goal.target_amount, 0);
    const totalSaved = mockGoals.reduce((sum, goal) => sum + goal.current_amount, 0);
    const overallProgress = totalTarget > 0 ? (totalSaved / totalTarget) * 100 : 0;

    return {
      goals: mockGoals,
      summary: {
        total_goals: mockGoals.length,
        total_target: totalTarget,
        total_saved: totalSaved,
        overall_progress: Math.round(overallProgress)
      }
    };
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  };

  const handleCreateGoal = () => {
    fetchGoals(); // Refresh goals after creating
  };

  const handleAddSavings = (goal) => {
    setSelectedGoal(goal);
    setShowAddSavingsModal(true);
  };

  const handleSavingsAdded = () => {
    fetchGoals(); // Refresh goals after adding savings
  };

  const handleTransferComplete = () => {
    fetchGoals(); // Refresh goals after transfer
  };

  const handleViewDetails = (goal) => {
    navigate(`/finny/goal-jar/${goal.id}`);
  };

  // Show loading skeletons
  if (loading) {
    return (
      <div className="goal-jar-page">
        {/* Header */}
        <div className="goal-jar-header">
          <div className="header-left">
            <Target size={32} color="#F4B400" />
            <div className="header-text">
              <h1>Goal Jar</h1>
              <p>Savings Tracker</p>
            </div>
          </div>
          <div className="header-right">
            <Bell size={22} color="white" />
            <div className="user-avatar">
              <User size={18} color="white" />
            </div>
          </div>
        </div>

        {/* Summary Card Skeleton */}
        <div className="summary-card skeleton">
          <div className="stats-row">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="stat-column skeleton-stat">
                <div className="stat-value skeleton-value"></div>
                <div className="stat-label skeleton-label"></div>
              </div>
            ))}
          </div>
        </div>

        {/* Goal Cards Skeletons */}
        <div className="goals-section">
          <div className="goals-header">
            <h2>Your Goals</h2>
          </div>
          {[1, 2].map((i) => (
            <div key={i} className="goal-card skeleton">
              <div className="skeleton-content"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="goal-jar-page">
      {/* Header */}
      <div className="goal-jar-header">
        <div className="header-left">
          <Target size={32} color="#F4B400" />
          <div className="header-text">
            <h1>Goal Jar</h1>
            <p>Savings Tracker</p>
          </div>
        </div>
        <div className="header-right">
          <Bell size={22} color="white" />
          <div className="user-avatar">
            <User size={18} color="white" />
          </div>
        </div>
      </div>

      {/* Summary Card */}
      <div className="summary-card">
        <div className="stats-row">
          <div className="stat-column">
            <div className="stat-value">{summary?.total_goals || 0}</div>
            <div className="stat-label">Goals</div>
          </div>
          <div className="stat-column">
            <div className="stat-value">{formatAmount(summary?.total_target || 0)}</div>
            <div className="stat-label">Target</div>
          </div>
          <div className="stat-column">
            <div className="stat-value">{formatAmount(summary?.total_saved || 0)}</div>
            <div className="stat-label">Saved</div>
          </div>
          <div className="stat-column">
            <div className="stat-value">{summary?.overall_progress || 0}%</div>
            <div className="stat-label">Progress</div>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="summary-progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${summary?.overall_progress || 0}%` }}
          ></div>
        </div>
      </div>

      {/* Goals Section */}
      <div className="goals-section">
        <div className="goals-header">
          <h2>Your Goals</h2>
          <button
            className="create-goal-btn"
            onClick={() => setShowCreateModal(true)}
          >
            + Create Goal
          </button>
        </div>

        <button
          className="transfer-leftover-btn"
          onClick={() => setShowTransferModal(true)}
        >
          Transfer Budget Leftover →
        </button>

        {/* Goal Cards */}
        <div className="goals-list">
          {goals.length === 0 ? (
            <div className="empty-state">
              <Target size={56} color="#CBD5E1" />
              <h3>No goals yet</h3>
              <p>Tap + Create Goal to start saving</p>
              <button
                className="create-first-goal-btn"
                onClick={() => setShowCreateModal(true)}
              >
                Create Your First Goal
              </button>
            </div>
          ) : (
            goals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onAddSavings={handleAddSavings}
                onViewDetails={handleViewDetails}
              />
            ))
          )}
        </div>
      </div>

      {/* Modals */}
      <CreateGoalModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onGoalCreated={handleCreateGoal}
      />

      <AddSavingsModal
        isOpen={showAddSavingsModal}
        onClose={() => setShowAddSavingsModal(false)}
        goal={selectedGoal}
        onSavingsAdded={handleSavingsAdded}
      />

      <TransferLeftoverModal
        isOpen={showTransferModal}
        onClose={() => setShowTransferModal(false)}
        goals={goals}
        onTransferComplete={handleTransferComplete}
      />
    </div>
  );
};

export default GoalJarPage;
