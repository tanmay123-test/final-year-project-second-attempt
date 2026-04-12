import React, { useState } from 'react';
import { ArrowLeft, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import '../styles/LoanPage.css';

const RepaymentSchedulePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    loanAmount: '500000',
    interestRate: '10',
    tenure: '24',
    extraPayment: '0'
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

  const handleGenerate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Get user_id from localStorage or context
      const user_id = localStorage.getItem('user_id') || 'demo_user';
      
      const payload = {
        user_id: user_id,
        loan_amount: Number(formData.loanAmount),
        interest_rate: Number(formData.interestRate),
        loan_tenure: Number(formData.tenure),
        extra_payment: Number(formData.extraPayment)
      };

      console.log('Sending repayment schedule request:', payload);
      const response = await loanApi.generateSchedule(payload);
      console.log('Repayment schedule response:', response);
      
      if (response.success) {
        setResults(response.data);
        console.log('Schedule results:', response.data);
        // Scroll results into view
        setTimeout(() => {
          const resultsElement = document.getElementById('results-section');
          if (resultsElement) {
            resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 100);
      } else {
        setError(response.error || 'Failed to generate repayment schedule');
      }
    } catch (err) {
      console.error('Repayment schedule error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        
        // Generate mock schedule data
        const principal = Number(formData.loanAmount);
        const rate = Number(formData.interestRate) / 100 / 12;
        const tenure = Number(formData.tenure);
        const extraPayment = Number(formData.extraPayment);
        
        // Calculate EMI
        const emi = principal * rate * Math.pow(1 + rate, tenure) / (Math.pow(1 + rate, tenure) - 1);
        const actualEmi = emi + extraPayment;
        
        // Generate schedule
        const schedule = [];
        let balance = principal;
        
        for (let month = 1; month <= tenure; month++) {
          const interestPaid = balance * rate;
          const principalPaid = actualEmi - interestPaid;
          
          if (principalPaid > balance) {
            // Last month adjustment
            schedule.push({
              month,
              emi: balance + interestPaid,
              principal_paid: balance,
              interest_paid: interestPaid,
              balance: 0
            });
            break;
          }
          
          balance -= principalPaid;
          
          schedule.push({
            month,
            emi: actualEmi,
            principal_paid: principalPaid,
            interest_paid: interestPaid,
            balance: Math.max(0, balance)
          });
        }
        
        const totalPayment = schedule.reduce((sum, row) => sum + row.emi, 0);
        const totalInterest = totalPayment - principal;
        
        const mockData = {
          emi: actualEmi,
          total_interest: totalInterest,
          total_payment: totalPayment,
          schedule: schedule
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
    return `₹${Number(amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  return (
    <div className="repayment-schedule-page">
      {/* Header */}
      <div className="budget-status-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Repayment Schedule</h1>
            <p className="loan-header-subtitle">Detailed month-by-month breakdown of principal and interest.</p>
          </div>
        </div>
      </div>

      {/* Form Section */}
      <div className="repayment-schedule-form-section">
        <div className="repayment-schedule-form-card">
          <form onSubmit={handleGenerate}>
            <div className="loan-form-grid">
              <div className="form-field">
                <label className="field-label">Loan Amount (₹)</label>
                <div className="input-wrapper">
                  <span className="input-prefix">₹</span>
                  <input
                    type="number"
                    value={formData.loanAmount}
                    onChange={(e) => handleInputChange('loanAmount', e.target.value)}
                    className="form-input with-prefix"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label className="field-label">Interest Rate (%)</label>
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

            <div className="form-field">
              <label className="field-label">Extra Monthly Payment (₹)</label>
              <div className="input-wrapper">
                <span className="input-prefix">₹</span>
                <input
                  type="number"
                  value={formData.extraPayment}
                  onChange={(e) => handleInputChange('extraPayment', e.target.value)}
                  className="form-input with-prefix"
                />
              </div>
            </div>

            <button type="submit" className="generate-button" disabled={loading}>
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Generate Schedule'
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
          {/* Summary Row */}
          <div className="summary-row">
            <div className="summary-chip">
              <div className="chip-label">Monthly EMI</div>
              <div className="chip-value">{formatAmount(results.emi)}</div>
            </div>
            <div className="summary-chip">
              <div className="chip-label">Total Interest</div>
              <div className="chip-value">{formatAmount(results.total_interest)}</div>
            </div>
            <div className="summary-chip">
              <div className="chip-label">Total Payment</div>
              <div className="chip-value">{formatAmount(results.total_payment)}</div>
            </div>
          </div>

          {/* Schedule Table */}
          {!(results?.schedule?.length) ? (
            <div className="error-message">No schedule data available.</div>
          ) : (
            <div className="schedule-table-container">
              <table className="schedule-table">
                <thead>
                  <tr>
                    <th>Mo.</th>
                    <th>EMI</th>
                    <th>Principal</th>
                    <th>Interest</th>
                    <th>Balance</th>
                  </tr>
                </thead>
                <tbody>
                  {(results?.schedule ?? []).map((row, index) => (
                    <tr key={row.month} className={index % 2 === 1 ? 'alternate-row' : ''}>
                      <td className="month-cell">{row.month}</td>
                      <td className="emi-cell">{formatAmount(row.emi)}</td>
                      <td className="principal-cell">{formatAmount(row.principal_paid)}</td>
                      <td className="interest-cell">{formatAmount(row.interest_paid)}</td>
                      <td className="balance-cell">{formatAmount(row.balance)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
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

export default RepaymentSchedulePage;
