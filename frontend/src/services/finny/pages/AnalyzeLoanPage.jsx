import React, { useState } from 'react';
import { ArrowLeft, Calculator, Shield, TrendingUp, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import '../styles/LoanPage.css';

const AnalyzeLoanPage = () => {
  const navigate = useNavigate();
  const [view, setView] = useState('form'); // 'form' or 'results'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    loanAmount: '',
    interestRate: '',
    tenure: '',
    monthlyIncome: '',
    fixedExpenses: ''
  });

  const handleBackClick = () => {
    navigate('/finny/loan');
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Form validation
    if (!formData.loanAmount || !formData.interestRate || !formData.tenure || 
        !formData.monthlyIncome || !formData.fixedExpenses) {
      setError('Please fill in all required fields.');
      return;
    }

    if (Number(formData.loanAmount) <= 0 || Number(formData.interestRate) <= 0 || 
        Number(formData.tenure) <= 0 || Number(formData.monthlyIncome) <= 0) {
      setError('All values must be greater than 0.');
      return;
    }

    setLoading(true);

    try {
      // Get user_id from localStorage or context
      const user_id = localStorage.getItem('user_id') || 'demo_user';
      
      const payload = {
        user_id: user_id,
        loan_amount: Number(formData.loanAmount),
        interest_rate: Number(formData.interestRate),
        loan_tenure: Number(formData.tenure),
        monthly_income: Number(formData.monthlyIncome),
        monthly_fixed_expenses: Number(formData.fixedExpenses)
      };

      console.log('Sending loan analysis request:', payload);
      const response = await loanApi.analyzeLoan(payload);
      console.log('Loan analysis response:', response);
      
      if (response.success) {
        // Transform backend response to frontend format
        const transformedData = {
          emi: response.data?.loan_details?.monthly_emi ?? response.data?.loan_details?.emi ?? 0,
          total_interest: response.data?.loan_details?.total_interest ?? 0,
          total_payment: response.data?.loan_details?.total_repayment ?? response.data?.loan_details?.total_payment ?? 0,
          affordability_ratio: response.data?.affordability?.emi_percentage ?? 0,
          risk_score: response.data?.risk_analysis?.risk_score ?? 0,
          risk_level: response.data?.risk_analysis?.risk_level ?? 'Unknown',
          recommendation: response.data?.risk_analysis?.recommendation ?? response.data?.recommendation ?? ''
        };
        setResults(transformedData);
        setView('results');
      } else {
        setError(response.error || 'Failed to analyze loan');
      }
    } catch (err) {
      console.error('Loan analysis error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        const mockData = {
          emi: 22444,
          total_interest: 38656,
          total_payment: 538656,
          affordability_ratio: 44.9,
          risk_score: 65,
          risk_level: 'Medium',
          recommendation: 'Consider increasing down payment or reducing loan amount to improve affordability.'
        };
        setResults(mockData);
        setView('results');
        setError('Using demo data - Backend server not available');
      } else {
        setError('Network error. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = () => {
    setView('form');
    setResults(null);
    setError('');
  };

  const calculateDTI = () => {
    if (!results?.emi || !formData.monthlyIncome) return 0;
    return ((results.emi / Number(formData.monthlyIncome)) * 100).toFixed(1);
  };

  const calculateEMIOfDisposable = () => {
    const disposable = Number(formData.monthlyIncome) - Number(formData.fixedExpenses);
    if (!results?.emi || disposable <= 0) return 0;
    return ((results.emi / disposable) * 100).toFixed(1);
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN')}`;
  };

  // Donut Chart Component
  const DonutChart = ({ principal, interest }) => {
    const total = principal + interest;
    const principalAngle = (principal / total) * 360;
    const interestAngle = (interest / total) * 360;
    
    return (
      <div style={{ width: '120px', height: '120px', position: 'relative' }}>
        <svg width="120" height="120" viewBox="0 0 120 120">
          {/* Background circle */}
          <circle cx="60" cy="60" r="50" fill="none" stroke="#E5E7EB" strokeWidth="20"/>
          
          {/* Principal segment */}
          <circle
            cx="60"
            cy="60"
            r="50"
            fill="none"
            stroke="#1F2937"
            strokeWidth="20"
            strokeDasharray={`${principalAngle} ${360 - principalAngle}`}
            strokeDashoffset="0"
            transform="rotate(-90 60 60)"
          />
          
          {/* Interest segment */}
          <circle
            cx="60"
            cy="60"
            r="50"
            fill="none"
            stroke="#F59E0B"
            strokeWidth="20"
            strokeDasharray={`${interestAngle} ${360 - interestAngle}`}
            strokeDashoffset={`-${principalAngle}`}
            transform="rotate(-90 60 60)"
          />
          
          {/* Center text */}
          <text x="60" y="60" textAnchor="middle" dominantBaseline="middle" fill="#1F2937" fontSize="14" fontWeight="bold">
            {formatAmount(total)}
          </text>
        </svg>
      </div>
    );
  };

  // Risk Score Ring Component
  const RiskScoreRing = ({ score, level }) => {
    const getRiskColor = () => {
      if (level === 'High') return '#EF4444';
      if (level === 'Medium') return '#F59E0B';
      return '#10B981';
    };

    const circumference = 2 * Math.PI * 45;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
      <div style={{ position: 'relative', width: '100px', height: '100px' }}>
        <svg width="100" height="100" viewBox="0 0 100 100">
          {/* Background ring */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="10"
          />
          
          {/* Progress ring */}
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke={getRiskColor()}
            strokeWidth="10"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 50 50)"
            strokeLinecap="round"
          />
          
          {/* Center text */}
          <text x="50" y="50" textAnchor="middle" dominantBaseline="middle" fill="#1F2937" fontSize="24" fontWeight="bold">
            {score}
          </text>
        </svg>
      </div>
    );
  };

  // Input Form View
  if (view === 'form') {
    return (
      <div className="analyze-loan-page">
        {/* Header */}
      <div className="budget-status-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Analyze Single Loan</h1>
            <p className="loan-header-subtitle">Evaluate your loan affordability and EMI breakdown.</p>
          </div>
        </div>
      </div>

        {/* Form Card */}
        <div className="loan-form-card">
          <form onSubmit={handleSubmit}>
            <div className="loan-form-grid">
              {/* Section 1 - Loan Details */}
              <div className="form-section">
                <h3 className="section-title">Loan Details</h3>
                
                <div className="form-field">
                  <label className="field-label">Loan Amount (₹)</label>
                  <div className="input-wrapper">
                    <span className="input-prefix">₹</span>
                    <input
                      type="number"
                      placeholder="e.g. 1000000"
                      value={formData.loanAmount}
                      onChange={(e) => handleInputChange('loanAmount', e.target.value)}
                      className="form-input with-prefix"
                      required
                    />
                  </div>
                </div>

                <div className="form-field">
                  <label className="field-label">Interest Rate (% p.a.)</label>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      placeholder="e.g. 8.5"
                      step="0.1"
                      value={formData.interestRate}
                      onChange={(e) => handleInputChange('interestRate', e.target.value)}
                      className="form-input"
                      required
                    />
                  </div>
                </div>

                <div className="form-field">
                  <label className="field-label">Loan Tenure (Months)</label>
                  <div className="input-wrapper">
                    <input
                      type="number"
                      placeholder="e.g. 24"
                      value={formData.tenure}
                      onChange={(e) => handleInputChange('tenure', e.target.value)}
                      className="form-input"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Section 2 - Financial Profile */}
              <div className="form-section">
                <h3 className="section-title">Financial Profile</h3>
                
                <div className="form-field">
                  <label className="field-label">Monthly Take-home Pay (₹)</label>
                  <div className="input-wrapper">
                    <span className="input-prefix">₹</span>
                    <input
                      type="number"
                      placeholder="e.g. 75000"
                      value={formData.monthlyIncome}
                      onChange={(e) => handleInputChange('monthlyIncome', e.target.value)}
                      className="form-input with-prefix"
                      required
                    />
                  </div>
                </div>

                <div className="form-field">
                  <label className="field-label">Fixed Expenses (₹)</label>
                  <div className="input-wrapper">
                    <span className="input-prefix">₹</span>
                    <input
                      type="number"
                      placeholder="e.g. 20000"
                      value={formData.fixedExpenses}
                      onChange={(e) => handleInputChange('fixedExpenses', e.target.value)}
                      className="form-input with-prefix"
                      required
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Analyze Loan'
              )}
            </button>
          </form>
        </div>

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
            <TrendingUp size={20} color="#F59E0B" />
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
  }

  // Results View
  const dtiRatio = calculateDTI();
  const emiOfDisposable = calculateEMIOfDisposable();
  const disposableIncome = Number(formData.monthlyIncome) - Number(formData.fixedExpenses);
  const remainingBalance = disposableIncome - (results?.emi ?? 0);

  if (!results) {
    return null;
  }

  return (
    <div className="analyze-loan-page">
      {/* Header */}
      <div className="budget-status-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Loan Analysis Results</h1>
            <p className="loan-header-subtitle">Review your affordability and risk breakdown.</p>
          </div>
        </div>
      </div>

      {/* Results Container */}
      <div className="results-container">
        {/* Card 1 - EMI Summary */}
        <div className="result-card emi-summary">
          <div className="emi-label">Monthly EMI</div>
          <div className="emi-amount">{formatAmount(results?.emi ?? 0)}</div>
          <div className="emi-details">
            <div className="emi-detail">
              <span>Total Interest</span>
              <span>{formatAmount(results?.total_interest ?? 0)}</span>
            </div>
            <div className="emi-detail">
              <span>Total Repayment</span>
              <span>{formatAmount(results?.total_payment ?? 0)}</span>
            </div>
          </div>
        </div>

        {/* Card 2 - EMI Breakdown */}
        <div className="result-card">
          <h3 className="card-title">EMI Breakdown</h3>
          <div className="emi-breakdown">
            <DonutChart 
              principal={Number(formData.loanAmount)} 
              interest={results?.total_interest ?? 0} 
            />
            <div className="chart-legend">
              <div className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#1F2937' }}></span>
                <span>Principal: {formatAmount(formData.loanAmount)}</span>
              </div>
              <div className="legend-item">
                <span className="legend-dot" style={{ backgroundColor: '#F59E0B' }}></span>
                <span>Interest: {formatAmount(results?.total_interest ?? 0)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 3 - Affordability Check */}
        <div className="result-card">
          <h3 className="card-title">
            <Shield size={18} style={{ marginRight: '8px' }} />
            Affordability Check
          </h3>
          <div className="affordability-row">
            <span>EMI as % of Income</span>
            <span className={`ratio-value ${(results?.affordability_ratio ?? 0) > 30 ? 'red' : 'green'}`}>
              {results?.affordability_ratio ?? '--'}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${(results?.affordability_ratio ?? 0) > 30 ? 'red' : 'green'}`}
              style={{ width: `${Math.min(results?.affordability_ratio ?? 0, 100)}%` }}
            ></div>
          </div>
          {(results?.affordability_ratio ?? 0) > 30 && (
            <div className="warning-text">
              Safe limit: 30%. ⚠️ EMI exceeds recommended safe limit.
            </div>
          )}
        </div>

        {/* Card 4 - Debt-to-Income Analysis */}
        <div className="result-card">
          <h3 className="card-title">
            <TrendingUp size={18} style={{ marginRight: '8px' }} />
            Debt-to-Income Analysis
          </h3>
          <div className="affordability-row">
            <span>DTI Ratio</span>
            <span className={`ratio-value ${dtiRatio > 40 ? 'red' : 'green'}`}>
              {dtiRatio}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${dtiRatio > 40 ? 'red' : 'green'}`}
              style={{ width: `${Math.min(dtiRatio, 100)}%` }}
            ></div>
          </div>
          <div className="info-text">
            {dtiRatio > 40 ? 'High DTI – Risky debt level.' : 'Healthy DTI.'}
          </div>
        </div>

        {/* Card 5 - Loan Impact Simulation */}
        <div className="result-card">
          <h3 className="card-title">
            <AlertTriangle size={18} style={{ marginRight: '8px' }} />
            Loan Impact Simulation
          </h3>
          <div className="impact-table">
            <div className="impact-row">
              <span>Monthly Income</span>
              <span>{formatAmount(formData.monthlyIncome)}</span>
            </div>
            <div className="impact-row">
              <span>Fixed Expenses</span>
              <span>{formatAmount(formData.fixedExpenses)}</span>
            </div>
            <div className="impact-row">
              <span>Disposable Income</span>
              <span>{formatAmount(disposableIncome)}</span>
            </div>
            <div className="impact-row">
              <span>Loan EMI</span>
              <span>{formatAmount(results?.emi ?? 0)}</span>
            </div>
            <div className="impact-row">
              <span>Remaining Balance</span>
              <span>{formatAmount(remainingBalance)}</span>
            </div>
          </div>
          <div className="info-box">
            💡 Loan EMI consumes {emiOfDisposable}% of your disposable income.
          </div>
        </div>

        {/* Card 6 - Loan Risk Score */}
        <div className="result-card">
          <h3 className="card-title">Loan Risk Score</h3>
          <div className="risk-score-container">
            <RiskScoreRing score={results?.risk_score ?? 0} level={results?.risk_level ?? 'Low'} />
            <div className="risk-details">
              <div className={`risk-badge ${(results?.risk_level ?? 'low').toLowerCase()}`}>
                {results?.risk_level ?? '--'} Risk
              </div>
              <div className="risk-recommendation">
                {results?.recommendation ?? ''}
              </div>
            </div>
          </div>
        </div>

        {/* Recalculate Button */}
        <button className="recalculate-button" onClick={handleRecalculate}>
          ← Analyze Again
        </button>
      </div>

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
          <TrendingUp size={20} color="#F59E0B" />
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

export default AnalyzeLoanPage;
