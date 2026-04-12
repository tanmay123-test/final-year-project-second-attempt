import React, { useState } from 'react';
import { ArrowLeft, TrendingDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import '../styles/LoanPage.css';

const LoanImpactPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    monthlyIncome: '50000',
    fixedExpenses: '20000',
    currentEmi: '0',
    newLoanAmount: '300000',
    interestRate: '10',
    tenure: '24'
  });

  const handleBackClick = () => {
    navigate('/finny/loan');
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
  };

  const handleSimulate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Get user_id from localStorage or context
      const user_id = localStorage.getItem('user_id') || 'demo_user';
      
      const payload = {
        user_id: user_id,
        monthly_income: Number(formData.monthlyIncome),
        monthly_fixed_expenses: Number(formData.fixedExpenses || formData.currentEmi),
        loan_amount: Number(formData.newLoanAmount),
        interest_rate: Number(formData.interestRate),
        loan_tenure: Number(formData.tenure)
      };

      console.log('Sending loan impact request:', payload);
      const response = await loanApi.simulateImpact(payload);
      console.log('Loan impact response:', response);
      
      if (response.success) {
        setResults(response.data);
        // Scroll results into view
        setTimeout(() => {
          const resultsElement = document.getElementById('results-section');
          if (resultsElement) {
            resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 100);
      } else {
        setError(response.error || 'Failed to calculate loan impact');
      }
    } catch (err) {
      console.error('Loan impact error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        const mockData = {
          emi: 13896,
          disposable_income_before: 30000,
          disposable_income_after: 16104,
          impact_percentage: 46.3,
          message: 'Loan impact within manageable range'
        };
        setResults(mockData);
        setError('Using demo data - Backend server not available');
        
        // Scroll results into view
        setTimeout(() => {
          const resultsElement = document.getElementById('results-section');
          if (resultsElement) {
            resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 100);
      } else {
        setError('Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  };

  const getBudgetWarning = () => {
    if (!results) return null;

    const disposableIncomeBefore = Number(formData.monthlyIncome) - Number(formData.fixedExpenses);
    const remaining = results.disposable_income_after;
    const impactPercentage = results.impact_percentage;

    if (remaining < 0 || impactPercentage > 90) {
      return {
        type: 'critical',
        icon: '🚨',
        title: 'Critical Budget',
        subtitle: 'EMI exceeds disposable income. High financial risk.',
        bgColor: '#FEF2F2',
        borderColor: '#FECACA',
        titleColor: '#DC2626'
      };
    } else if (impactPercentage > 60) {
      return {
        type: 'tight',
        icon: '⚠️',
        title: 'Tight Budget',
        subtitle: 'Budget will be tight. Minimize discretionary spending.',
        bgColor: '#FFFBEB',
        borderColor: '#FDE68A',
        titleColor: '#D97706'
      };
    } else if (impactPercentage > 30) {
      return {
        type: 'moderate',
        icon: '⚠️',
        title: 'Moderate Impact',
        subtitle: 'Loan is manageable but monitor expenses carefully.',
        bgColor: '#FFF7ED',
        borderColor: '#FED7AA',
        titleColor: '#EA580C'
      };
    } else {
      return {
        type: 'healthy',
        icon: '✅',
        title: 'Healthy Budget',
        subtitle: 'Loan fits comfortably within your budget.',
        bgColor: '#F0FDF4',
        borderColor: '#BBF7D0',
        titleColor: '#16A34A'
      };
    }
  };

  const budgetWarning = getBudgetWarning();

  return (
    <div className="loan-impact-page">
      {/* Header */}
      <div className="budget-status-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Loan Impact Simulation</h1>
            <p className="loan-header-subtitle">Simulate how a new loan affects your monthly disposable income.</p>
          </div>
        </div>
      </div>

      {/* Form Section */}
      <div className="impact-form-section">
        <div className="impact-form-card">
          <form onSubmit={handleSimulate}>
            <div className="loan-form-grid">
              <div className="form-field">
                <label className="field-label">Current EMI (₹)</label>
                <div className="input-wrapper">
                  <span className="input-prefix">₹</span>
                  <input
                    type="number"
                    value={formData.currentEmi}
                    onChange={(e) => handleInputChange('currentEmi', e.target.value)}
                    className="form-input with-prefix"
                    placeholder="e.g. 15000"
                  />
                </div>
              </div>

              <div className="form-field">
                <label className="field-label">Monthly Income (₹)</label>
                <div className="input-wrapper">
                  <span className="input-prefix">₹</span>
                  <input
                    type="number"
                    value={formData.monthlyIncome}
                    onChange={(e) => handleInputChange('monthlyIncome', e.target.value)}
                    className="form-input with-prefix"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label className="field-label">New Loan Amount (₹)</label>
                <div className="input-wrapper">
                  <span className="input-prefix">₹</span>
                  <input
                    type="number"
                    value={formData.newLoanAmount}
                    onChange={(e) => handleInputChange('newLoanAmount', e.target.value)}
                    className="form-input with-prefix"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label className="field-label">Interest Rate (% p.a.)</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.interestRate}
                  onChange={(e) => handleInputChange('interestRate', e.target.value)}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-field">
                <label className="field-label">Tenure (Months)</label>
                <input
                  type="number"
                  value={formData.tenure}
                  onChange={(e) => handleInputChange('tenure', e.target.value)}
                  className="form-input"
                  required
                />
              </div>
            </div>

            <button type="submit" className="simulate-button" disabled={loading}>
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Simulate Impact'
              )}
            </button>
          </form>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div id="results-section" className="results-section">
          {/* Result Card 1 - Disposable Income Hero */}
          <div className="disposable-income-hero">
            <div className="hero-label">Disposable Income After EMI</div>
            <div className="hero-value">{formatAmount(results.remaining_after_emi || results.disposable_income_after)}</div>
            <div className="hero-impact">Impact: {results.impact_percentage}% of disposable income</div>
          </div>

          {/* Result Card 2 - Breakdown Table */}
          <div className="breakdown-table">
            <div className="table-row">
              <span className="row-label">Monthly Income</span>
              <span className="row-value">{formatAmount(formData.monthlyIncome)}</span>
            </div>
            <div className="table-row">
              <span className="row-label">Fixed Expenses</span>
              <span className="row-value">{formatAmount(formData.fixedExpenses || formData.currentEmi)}</span>
            </div>
            <div className="table-row">
              <span className="row-label">Disposable Income</span>
              <span className="row-value">
                {formatAmount(results.disposable_income)}
              </span>
            </div>
            <div className="table-row">
              <span className="row-label">Loan EMI</span>
              <span className="row-value">{formatAmount(results.monthly_emi || results.emi)}</span>
            </div>
            <div className="table-row">
              <span className="row-label">Remaining</span>
              <span className="row-value">{formatAmount(results.remaining_after_emi || results.disposable_income_after)}</span>
            </div>
          </div>

          {/* Result Card 3 - Budget Warning */}
          {budgetWarning && (
            <div className="budget-warning" style={{
              backgroundColor: budgetWarning.bgColor,
              borderColor: budgetWarning.borderColor
            }}>
              <div className="warning-header">
                <span className="warning-icon">{budgetWarning.icon}</span>
                <span className="warning-title" style={{ color: budgetWarning.titleColor }}>
                  {budgetWarning.title}
                </span>
              </div>
              <div className="warning-subtitle">{budgetWarning.subtitle}</div>
            </div>
          )}
        </div>
      )}

      {/* Bottom Navigation */}
      <div className="bottom-nav">
        <div className="nav-item" onClick={() => navigate('/finny')}>
          <span className="nav-icon">🏠</span>
          <span className="nav-label">Finny</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/budget')}>
          <span className="nav-icon">📊</span>
          <span className="nav-label">Budget</span>
        </div>
        <div className="nav-item active" onClick={() => navigate('/finny/loan')}>
          <span className="nav-icon">⚖️</span>
          <span className="nav-label">Loan</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/goal-jar')}>
          <span className="nav-icon">🎯</span>
          <span className="nav-label">Goal Jar</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/finny/ai-coach')}>
          <span className="nav-icon">🧠</span>
          <span className="nav-label">AI Coach</span>
        </div>
      </div>
    </div>
  );
};

export default LoanImpactPage;
