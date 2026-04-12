import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import '../styles/BudgetPage.css';

const BudgetGamificationPage = () => {
  const navigate = useNavigate();

  const [rewards] = useState([
    {
      id: 1,
      icon: '🏆',
      iconBg: 'gray',
      title: 'Budget Master',
      subtitle: 'Stay within budget for a full month',
      progress: 75,
      status: 'in-progress'
    },
    {
      id: 2,
      icon: '🛡️',
      iconBg: 'gray',
      title: 'Savings Hero',
      subtitle: 'Save more than target for 3 months',
      progress: 40,
      status: 'in-progress'
    },
    {
      id: 3,
      icon: '🔥',
      iconBg: 'gold',
      title: 'Discipline Streak',
      subtitle: '7-day streak of logging expenses',
      progress: 100,
      status: 'unlocked'
    },
    {
      id: 4,
      icon: '🎯',
      iconBg: 'gray',
      title: 'Consistency Champion',
      subtitle: 'Consistent spending across categories',
      progress: 60,
      status: 'in-progress'
    },
  ]);

  const [earnedRewards] = useState([
    {
      title: 'Budget Master – March 2026',
      subtitle: 'Stayed within all budgets'
    },
    {
      title: 'Savings Hero – February 2026',
      subtitle: 'Saved ₹7,800 above target'
    },
  ]);

  const handleBackClick = () => {
    navigate('/finny/budget');
  };

  return (
    <div className="budget-gamification-page">
      {/* Header */}
      <div className="budget-status-header">
        <button 
          className="back-button"
          onClick={handleBackClick}
        >
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Budget Gamification</h1>
            <p className="loan-header-subtitle">Earn rewards for smart budgeting and saving habits.</p>
          </div>
        </div>
      </div>

      {/* Section 1 - Potential Rewards */}
      <div className="section-title">Potential Rewards</div>
      
      {rewards.map((reward) => (
        <div 
          key={reward.id} 
          className={`reward-card ${reward.status === 'unlocked' ? 'unlocked' : ''}`}
        >
          {/* Row 1 */}
          <div className="reward-card-row1">
            <div className="reward-left">
              <div className={`reward-icon-circle ${reward.iconBg === 'gold' ? 'gold-bg' : ''}`}>
                {reward.icon}
              </div>
              <div>
                <div className="reward-title">{reward.title}</div>
                <div className="reward-subtitle">{reward.subtitle}</div>
              </div>
            </div>
            <div className="reward-right">
              {reward.status === 'unlocked' ? (
                <div className="unlocked-badge">Unlocked</div>
              ) : (
                <div className="reward-progress-pct">{reward.progress}%</div>
              )}
            </div>
          </div>

          {/* Row 2 - Progress Bar */}
          <div className="reward-bar-track">
            <div 
              className={`reward-bar-fill ${reward.status === 'unlocked' ? 'fill-gold' : 'fill-navy'}`}
              style={{ width: `${reward.progress}%` }}
            ></div>
          </div>
        </div>
      ))}

      {/* Section 2 - Earned Rewards */}
      <div className="section-title">Earned Rewards</div>
      
      {earnedRewards.map((earned, index) => (
        <div key={index} className="earned-card">
          <div className="earned-trophy-icon">🏆</div>
          <div>
            <div className="earned-title">{earned.title}</div>
            <div className="earned-subtitle">{earned.subtitle}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default BudgetGamificationPage;
