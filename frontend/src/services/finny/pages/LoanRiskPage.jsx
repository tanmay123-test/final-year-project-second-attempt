import React, { useState } from 'react';
import { ArrowLeft, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import '../styles/LoanPage.css';

const LoanRiskPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    monthlyIncome: '50000',
    fixedExpenses: '20000',
    existingEmis: '5000',
    newLoanAmount: '400000',
    interestRate: '12',
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

  const handleAssess = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Get user_id from localStorage or context
      const user_id = localStorage.getItem('user_id') || 'demo_user';
      
      const payload = {
        user_id: user_id,
        loan_amount: Number(formData.newLoanAmount),
        interest_rate: Number(formData.interestRate),
        loan_tenure: Number(formData.tenure),
        monthly_income: Number(formData.monthlyIncome),
        monthly_fixed_expenses: Number(formData.fixedExpenses),
        existing_emi: Number(formData.existingEmis)
      };

      console.log('Sending risk assessment request:', payload);
      const response = await loanApi.assessRisk(payload);
      console.log('Risk assessment response:', response);
      
      if (response.success) {
        // Map backend nested data to flat structure expected by frontend
        const data = response.data;
        const mappedResults = {
          dti_ratio: Number(data.dti_analysis?.dti_percentage || calculateDTI(data.loan_details?.monthly_emi || 0)).toFixed(1),
          emi_pct_income: Number(data.affordability?.emi_percentage || calculateEMIPctIncome(data.loan_details?.monthly_emi || 0)).toFixed(1),
          new_emi: data.loan_details?.monthly_emi || 0,
          affordable: data.affordability?.is_affordable,
          risk_score: Math.round(data.risk_analysis?.risk_score || 0),
          risk_level: data.risk_analysis?.risk_level || 'Unknown',
          recommendation: data.recommendation || 'No recommendation available'
        };
        
        setResults(mappedResults);
        
        // Scroll results into view
        setTimeout(() => {
          const resultsElement = document.getElementById('results-section');
          if (resultsElement) {
            resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 100);
      } else {
        setError(response.error || 'Failed to assess loan risk');
      }
    } catch (err) {
      console.error('Loan risk assessment error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        
        // Generate mock risk assessment data
        const monthlyIncome = Number(formData.monthlyIncome);
        const principal = Number(formData.newLoanAmount);
        const rate = Number(formData.interestRate) / 100 / 12;
        const tenure = Number(formData.tenure);
        
        // Calculate EMI
        const emi = principal * rate * Math.pow(1 + rate, tenure) / (Math.pow(1 + rate, tenure) - 1);
        
        // Calculate risk metrics
        const existingEmis = Number(formData.existingEmis);
        const totalEmis = existingEmis + emi;
        const dtiRatio = (totalEmis / monthlyIncome) * 100;
        const emiPctIncome = (emi / monthlyIncome) * 100;
        
        // Determine risk level based on DTI and other factors
        let riskScore = 0;
        let riskLevel = 'Low';
        let recommendation = '';
        
        if (dtiRatio > 50) {
          riskScore = 85 + Math.random() * 15;
          riskLevel = 'High';
          recommendation = 'High risk. Loan not recommended at current financials.';
        } else if (dtiRatio > 40) {
          riskScore = 60 + Math.random() * 25;
          riskLevel = 'Medium';
          recommendation = 'Moderate risk. Consider reducing loan amount or increasing income.';
        } else if (dtiRatio > 30) {
          riskScore = 30 + Math.random() * 30;
          riskLevel = 'Medium';
          recommendation = 'Acceptable risk. Monitor expenses carefully.';
        } else {
          riskScore = Math.random() * 30;
          riskLevel = 'Low';
          recommendation = 'Low risk. Loan appears affordable.';
        }
        
        const mockData = {
          risk_score: Math.round(riskScore),
          risk_level: riskLevel,
          new_emi: emi,
          dti_ratio: Math.round(dtiRatio * 10) / 10,
          emi_pct_income: Math.round(emiPctIncome * 10) / 10,
          affordable: dtiRatio < 40,
          recommendation: recommendation
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

  const calculateDTI = (newEmi) => {
    const existingEmis = Number(formData.existingEmis);
    const monthlyIncome = Number(formData.monthlyIncome);
    const totalEmis = existingEmis + newEmi;
    return Math.round(((totalEmis / monthlyIncome) * 100) * 10) / 10;
  };

  const calculateEMIPctIncome = (newEmi) => {
    const monthlyIncome = Number(formData.monthlyIncome);
    return Math.round(((newEmi / monthlyIncome) * 100) * 10) / 10;
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'High': return '#EF4444';
      case 'Medium': return '#F59E0B';
      case 'Low': return '#10B981';
      default: return '#64748B';
    }
  };

  const getMetricColor = (value, type) => {
    if (type === 'dti') {
      if (value > 40) return '#EF4444';
      if (value >= 20) return '#F59E0B';
      return '#10B981';
    } else if (type === 'emi') {
      if (value > 30) return '#EF4444';
      if (value >= 20) return '#F59E0B';
      return '#10B981';
    }
    return '#1E3A5F';
  };

  const createRiskRing = () => {
    if (!results) return null;
    
    const radius = 36;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (results.risk_score / 100) * circumference;
    const riskColor = getRiskColor(results.risk_level);
    
    return (
      <svg width="90" height="90" className="risk-ring">
        {/* Background circle */}
        <circle
          cx="45"
          cy="45"
          r={radius}
          stroke="#F1F5F9"
          strokeWidth="8"
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx="45"
          cy="45"
          r={radius}
          stroke={riskColor}
          strokeWidth="8"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 45 45)"
          className="risk-ring-progress"
        />
        {/* Center text */}
        <text x="45" y="45" textAnchor="middle" dominantBaseline="middle" className="risk-score-text">
          <tspan x="45" dy="-5" fontSize="20" fontWeight="bold" fill={riskColor}>
            {results.risk_score}
          </tspan>
          <tspan x="45" dy="15" fontSize="11" fill="#64748B">
            /100
          </tspan>
        </text>
      </svg>
    );
  };

  return (
    <div className="loan-risk-page">
      {/* Header */}
      <div className="budget-status-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="loan-header-content">
          <div className="loan-header-text">
            <h1 className="loan-header-title">Loan Risk Assessment</h1>
            <p className="loan-header-subtitle">Identify potential risks based on your income and expenses.</p>
          </div>
        </div>
      </div>

      {/* Form Section */}
      <div className="loan-risk-form-section">
        <div className="loan-risk-form-card">
          <form onSubmit={handleAssess}>
            <div className="loan-form-grid">
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
                <label className="field-label">Fixed Expenses (₹)</label>
                <div className="input-wrapper">
                  <span className="input-prefix">₹</span>
                  <input
                    type="number"
                    value={formData.fixedExpenses}
                    onChange={(e) => handleInputChange('fixedExpenses', e.target.value)}
                    className="form-input with-prefix"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label className="field-label">Existing EMIs (₹)</label>
                <div className="input-wrapper">
                  <span className="input-prefix">₹</span>
                  <input
                    type="number"
                    value={formData.existingEmis}
                    onChange={(e) => handleInputChange('existingEmis', e.target.value)}
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

            <button type="submit" className="assess-button" disabled={loading}>
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Assess Risk'
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
          {/* Result Card 1 - Risk Score Ring */}
          <div className="risk-score-card">
            <div className="risk-ring-container">
              {createRiskRing()}
            </div>
            <div className="risk-details">
              <div 
                className="risk-badge"
                style={{ backgroundColor: getRiskColor(results.risk_level) }}
              >
                {results.risk_level} Risk
              </div>
              <div className="risk-recommendation">
                {results.recommendation}
              </div>
            </div>
          </div>

          {/* Result Card 2 - 4 Metric Mini Cards */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">DTI Ratio</div>
              <div 
                className="metric-value"
                style={{ color: getMetricColor(results.dti_ratio, 'dti') }}
              >
                {results.dti_ratio}%
              </div>
            </div>
            
            <div className="metric-card">
              <div className="metric-label">EMI % of Income</div>
              <div 
                className="metric-value"
                style={{ color: getMetricColor(results.emi_pct_income, 'emi') }}
              >
                {results.emi_pct_income}%
              </div>
            </div>
            
            <div className="metric-card">
              <div className="metric-label">New EMI</div>
              <div className="metric-value" style={{ color: '#1E3A5F' }}>
                {formatAmount(results.new_emi)}
              </div>
            </div>
            
            <div className="metric-card">
              <div className="metric-label">Affordable?</div>
              <div 
                className="metric-value"
                style={{ color: results.affordable ? '#10B981' : '#EF4444' }}
              >
                {results.affordable ? 'Yes ✅' : 'No ⚠️'}
              </div>
            </div>
          </div>
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

export default LoanRiskPage;
