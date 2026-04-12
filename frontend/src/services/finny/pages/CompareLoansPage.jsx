import React, { useState } from 'react';
import { ArrowLeft, ArrowUpDown, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import '../styles/LoanPage.css';

const CompareLoansPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Form state for both loans
  const [loan1, setLoan1] = useState({
    amount: '500000',
    rate: '10',
    tenure: '24'
  });

  const [loan2, setLoan2] = useState({
    amount: '500000',
    rate: '12',
    tenure: '36'
  });

  const handleBackClick = () => {
    navigate('/finny/loan');
  };

  const handleLoan1Change = (field, value) => {
    setLoan1(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
  };

  const handleLoan2Change = (field, value) => {
    setLoan2(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
  };

  const handleCompare = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Get user_id from localStorage or context
      const user_id = localStorage.getItem('user_id') || 'demo_user';
      
      const payload = {
        user_id: user_id,
        loan1: {
          amount: Number(loan1.amount),
          rate: Number(loan1.rate),
          tenure: Number(loan1.tenure)
        },
        loan2: {
          amount: Number(loan2.amount),
          rate: Number(loan2.rate),
          tenure: Number(loan2.tenure)
        }
      };

      console.log('Sending loan comparison request:', payload);
      const response = await loanApi.compareLoans(payload);
      console.log('Loan comparison response:', response);
      
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
        setError(response.error || 'Failed to compare loans');
      }
    } catch (err) {
      console.error('Loan comparison error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        const mockData = {
          loan1: {
            emi: 22444,
            total_interest: 38656,
            total_payment: 538656
          },
          loan2: {
            emi: 16667,
            total_interest: 50012,
            total_payment: 550012
          },
          recommendation: {
            winner: 'Loan 1',
            savings: 11356,
            message: 'Loan 1 has lower total repayment despite higher monthly EMI'
          }
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

  const getBetterValue = (value1, value2) => {
    return Number(value1) < Number(value2) ? value1 : value2;
  };

  return (
    <div className="compare-loans-page">
      {/* Header */}
      <div className="loan-header-section">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Compare Two Loans</h1>
            <p className="loan-header-subtitle">Compare different loan options to find the best deal.</p>
          </div>
        </div>
      </div>

      <div className="compare-form-section">
        <div className="loans-grid">
          <div className="loan-card-form">
            <h3 className="section-title">Loan Option 1</h3>
            <div className="form-field">
              <label className="field-label">Loan Amount (₹)</label>
              <div className="input-wrapper">
                <span className="input-prefix">₹</span>
                <input
                  type="number"
                  className="form-input with-prefix"
                  placeholder="e.g. 500000"
                  value={loan1.amount}
                  onChange={(e) => setLoan1({...loan1, amount: e.target.value})}
                />
              </div>
            </div>
            <div className="form-field">
              <label className="field-label">Interest Rate (% p.a.)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 8.5"
                step="0.1"
                value={loan1.rate}
                onChange={(e) => setLoan1({...loan1, rate: e.target.value})}
              />
            </div>
            <div className="form-field">
              <label className="field-label">Tenure (Months)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 24"
                value={loan1.tenure}
                onChange={(e) => setLoan1({...loan1, tenure: e.target.value})}
              />
            </div>
          </div>

          <div className="loan-card-form">
            <h3 className="section-title">Loan Option 2</h3>
            <div className="form-field">
              <label className="field-label">Loan Amount (₹)</label>
              <div className="input-wrapper">
                <span className="input-prefix">₹</span>
                <input
                  type="number"
                  className="form-input with-prefix"
                  placeholder="e.g. 500000"
                  value={loan2.amount}
                  onChange={(e) => setLoan2({...loan2, amount: e.target.value})}
                />
              </div>
            </div>
            <div className="form-field">
              <label className="field-label">Interest Rate (% p.a.)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 9.0"
                step="0.1"
                value={loan2.rate}
                onChange={(e) => setLoan2({...loan2, rate: e.target.value})}
              />
            </div>
            <div className="form-field">
              <label className="field-label">Tenure (Months)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 36"
                value={loan2.tenure}
                onChange={(e) => setLoan2({...loan2, tenure: e.target.value})}
              />
            </div>
          </div>
        </div>

        <button
          className="compare-button"
          onClick={handleCompare}
          disabled={loading}
        >
          {loading ? <div className="loading-spinner" /> : "Compare Loans"}
        </button>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {results && results.loan1 && results.loan2 && (
        <div id="results-section" className="results-section">
          {/* Result Card 1 - Comparison Table */}
          <div className="result-card">
            <div className="comparison-table">
              <div className="table-header">
                <div className="header-cell">Metric</div>
                <div className="header-cell loan1-header">Loan 1</div>
                <div className="header-cell loan2-header">Loan 2</div>
              </div>
              
              <div className="table-row">
                <div className="metric-cell">Monthly EMI</div>
                <div className={`value-cell ${getBetterValue(results.loan1?.monthly_emi ?? results.loan1?.emi ?? 0, results.loan2?.monthly_emi ?? results.loan2?.emi ?? 0) === (results.loan1?.monthly_emi ?? results.loan1?.emi ?? 0) ? 'better-value' : ''}`}>
                  {formatAmount(results.loan1?.monthly_emi ?? results.loan1?.emi ?? 0)}
                </div>
                <div className={`value-cell ${getBetterValue(results.loan1?.monthly_emi ?? results.loan1?.emi ?? 0, results.loan2?.monthly_emi ?? results.loan2?.emi ?? 0) === (results.loan2?.monthly_emi ?? results.loan2?.emi ?? 0) ? 'better-value' : ''}`}>
                  {formatAmount(results.loan2?.monthly_emi ?? results.loan2?.emi ?? 0)}
                </div>
              </div>
              
              <div className="table-row">
                <div className="metric-cell">Total Interest</div>
                <div className={`value-cell ${getBetterValue(results.loan1?.total_interest ?? 0, results.loan2?.total_interest ?? 0) === (results.loan1?.total_interest ?? 0) ? 'better-value' : ''}`}>
                  {formatAmount(results.loan1?.total_interest ?? 0)}
                </div>
                <div className={`value-cell ${getBetterValue(results.loan1?.total_interest ?? 0, results.loan2?.total_interest ?? 0) === (results.loan2?.total_interest ?? 0) ? 'better-value' : ''}`}>
                  {formatAmount(results.loan2?.total_interest ?? 0)}
                </div>
              </div>
              
              <div className="table-row">
                <div className="metric-cell">Total Repayment</div>
                <div className={`value-cell ${getBetterValue(results.loan1?.total_repayment ?? results.loan1?.total_payment ?? 0, results.loan2?.total_repayment ?? results.loan2?.total_payment ?? 0) === (results.loan1?.total_repayment ?? results.loan1?.total_payment ?? 0) ? 'better-value' : ''}`}>
                  {formatAmount(results.loan1?.total_repayment ?? results.loan1?.total_payment ?? 0)}
                </div>
                <div className={`value-cell ${getBetterValue(results.loan1?.total_repayment ?? results.loan1?.total_payment ?? 0, results.loan2?.total_repayment ?? results.loan2?.total_payment ?? 0) === (results.loan2?.total_repayment ?? results.loan2?.total_payment ?? 0) ? 'better-value' : ''}`}>
                  {formatAmount(results.loan2?.total_repayment ?? results.loan2?.total_payment ?? 0)}
                </div>
              </div>
            </div>
          </div>

          {/* Result Card 2 - Recommendation */}
          {results.recommendation && (
            <div className="recommendation-card">
              <div className="recommendation-header">
                <Check size={18} color="#16A34A" />
                <span className="recommendation-title">Recommendation</span>
              </div>
              <div className="recommendation-body">
                <div className="winner-text" style={{ fontSize: '18px', fontWeight: '600', color: '#1E293B' }}>
                  {results.recommendation}
                </div>
                <div className="savings-text" style={{ marginTop: '8px', color: '#64748B' }}>
                  By choosing {results.cheaper_option}, you reduce your total interest burden and save significantly over the full tenure.
                </div>
              </div>
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

export default CompareLoansPage;
