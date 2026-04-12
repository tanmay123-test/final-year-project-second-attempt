import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, RotateCcw } from 'lucide-react';
import '../styles/BudgetPage.css';

const LeftoverManagementPage = () => {
  const navigate = useNavigate();
  const [categoryBudgets, setCategoryBudgets] = useState([]);
  const [goalJars, setGoalJars] = useState([]);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [selectedTransfer, setSelectedTransfer] = useState(null);
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  const mockCategoryData = [
    { name: 'Dining Out', budget: 3000, spent: 500 },
    { name: 'Entertainment', budget: 4000, spent: 2100 },
    { name: 'Transport', budget: 7500, spent: 1900 },
    { name: 'Groceries', budget: 10000, spent: 4200 },
    { name: 'Shopping', budget: 5000, spent: 3800 },
    { name: 'Utilities', budget: 7500, spent: 3200 }
  ];

  const mockGoalJars = [
    { name: 'Bike Fund', current: 22000, target: 50000 },
    { name: 'Vacation', current: 8000, target: 30000 }
  ];

  useEffect(() => {
    // Load saved category budgets from localStorage or API
    const savedBudgets = localStorage.getItem('categoryBudgets');
    if (savedBudgets) {
      setCategoryBudgets(JSON.parse(savedBudgets));
    } else {
      setCategoryBudgets(mockCategoryData);
    }

    // Load goal jars data
    setGoalJars(mockGoalJars);
    setLoading(false);
  }, []);

  const formatINR = (n) => "₹" + Math.round(n).toLocaleString('en-IN');

  const calculateLeftovers = () => {
    return categoryBudgets
      .map(cat => ({
        ...cat,
        leftover: cat.budget - cat.spent
      }))
      .filter(cat => cat.leftover > 0)
      .sort((a, b) => b.leftover - a.leftover);
  };

  const calculateTotalLeftover = () => {
    const leftovers = calculateLeftovers();
    return leftovers.reduce((sum, cat) => sum + cat.leftover, 0);
  };

  const handleTransferClick = (goalJar, amount) => {
    setSelectedTransfer({ goalJar, amount });
    setShowTransferModal(true);
  };

  const confirmTransfer = () => {
    if (selectedTransfer) {
      // Update goal jar amount
      setGoalJars(prev => prev.map(jar => 
        jar.name === selectedTransfer.goalJar.name 
          ? { ...jar, current: jar.current + selectedTransfer.amount }
          : jar
      ));
      
      // Show success message (in real app, would use toast)
      alert(`${formatINR(selectedTransfer.amount)} transferred to ${selectedTransfer.goalJar.name}! 🎉`);
      
      // Close modal
      setShowTransferModal(false);
      setSelectedTransfer(null);
    }
  };

  const leftovers = calculateLeftovers();
  const totalLeftover = calculateTotalLeftover();

  if (loading) {
    return (
      <div className="leftover-management-page">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="leftover-management-page">
      {/* Header */}
      <div className="budget-status-header">
        <button 
          className="back-button"
          onClick={() => navigate('/finny/budget')}
        >
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Leftover Management</h1>
            <p className="loan-header-subtitle">Optimize remaining budget and move to goal jars.</p>
          </div>
        </div>
      </div>

      {/* Section 1 - Total Leftover Budget Card */}
      <div className="total-leftover-card">
        <div className="total-leftover-label">Total Leftover Budget</div>
        <div className="total-leftover-value">{formatINR(totalLeftover)}</div>
      </div>

      {/* Section 2 - Category Leftovers */}
      <div className="section-title">Category Leftovers</div>
      
      {leftovers.slice(0, 3).map((category, index) => (
        <div key={index} className="leftover-card">
          {/* Row 1 - Title + Leftover Amount */}
          <div className="leftover-card-header">
            <div className="leftover-category-name">{category.name}</div>
            <div className="leftover-amount">{formatINR(category.leftover)}</div>
          </div>

          {/* Row 2 - Budget Reference */}
          <div className="leftover-budget-ref">
            of {formatINR(category.budget)} budget
          </div>

          {/* Row 3 - Suggestion Pill */}
          <div className="leftover-suggestion">
            <span className="suggestion-icon">💡</span>
            <span>Consider moving {formatINR(category.leftover)} to your Goal Jar.</span>
          </div>
        </div>
      ))}

      {/* Section 3 - Goal Jars */}
      <div className="section-title">Goal Jars</div>
      
      {goalJars.map((goalJar, index) => {
        const progressPercentage = Math.round((goalJar.current / goalJar.target) * 100);
        const transferAmount = Math.min(totalLeftover, goalJar.target - goalJar.current);
        
        return (
          <div key={index} className="goal-jar-card">
            {/* Row 1 - Name + Progress Amounts */}
            <div className="goal-jar-header">
              <div className="goal-jar-name">{goalJar.name}</div>
              <div className="goal-jar-amounts">
                {formatINR(goalJar.current)} / {formatINR(goalJar.target)}
              </div>
            </div>

            {/* Row 2 - Progress Bar */}
            <div className="goal-jar-bar-track">
              <div 
                className="goal-jar-bar-fill"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>

            {/* Row 3 - Transfer Button */}
            <button 
              className="transfer-btn"
              onClick={() => handleTransferClick(goalJar, transferAmount)}
              disabled={transferAmount <= 0}
            >
              <RotateCcw size={14} />
              Transfer leftover
            </button>
          </div>
        );
      })}

      {/* Transfer Modal */}
      {showTransferModal && selectedTransfer && (
        <div className="transfer-modal-overlay">
          <div className="transfer-modal">
            <div className="modal-content">
              <h3>Transfer Confirmation</h3>
              <p>
                Transfer {formatINR(selectedTransfer.amount)} to {selectedTransfer.goalJar.name}?
              </p>
              <div className="modal-buttons">
                <button 
                  className="confirm-btn"
                  onClick={confirmTransfer}
                >
                  Confirm
                </button>
                <button 
                  className="cancel-btn"
                  onClick={() => {
                    setShowTransferModal(false);
                    setSelectedTransfer(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeftoverManagementPage;
