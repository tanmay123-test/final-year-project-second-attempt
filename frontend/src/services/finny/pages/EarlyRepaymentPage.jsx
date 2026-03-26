import React, { useState } from 'react';
import { ArrowLeft, CreditCard } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import '../styles/LoanPage.css';

const EarlyRepaymentPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    loanAmount: '500000',
    interestRate: '10',
    tenure: '36',
    extraPayment: '5000'
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
        loan_amount: Number(formData.loanAmount),
        interest_rate: Number(formData.interestRate),
        loan_tenure: Number(formData.tenure),
        extra_payment: Number(formData.extraPayment)
      };

      console.log('Sending early repayment request:', payload);
      const response = await loanApi.simulateEarlyRepayment(payload);
      console.log('Early repayment response:', response);
      
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
        setError(response.error || 'Failed to simulate early repayment');
      }
    } catch (err) {
      console.error('Early repayment error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        const mockData = {
          original_emi: 16134,
          months_saved: 8,
          interest_saved: 25480,
          new_tenure: 28,
          total_interest_original: 180824,
          total_interest_with_extra: 155344
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

  // Prepare data for bar chart
  const getChartData = () => {
    if (!results) return [];
    
    return [
      {
        name: 'Original',
        interest: results.total_interest_original
      },
      {
        name: 'With Extra',
        interest: results.total_interest_with_extra
      }
    ];
  };

  const chartData = getChartData();

  return (
    <div className="early-repayment-page">
      {/* Header */}
      <div className="loan-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="header-content">
          <div className="header-title-section">
            <CreditCard size={20} color="#F59E0B" />
            <div className="header-text">
              <h1 className="header-title">Early Repayment Simulation</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Form Section */}
      <div className="early-repayment-form-section">
        <div className="early-repayment-form-card">
          <form onSubmit={handleSimulate}>
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
              <label className="field-label">Original Tenure (Months)</label>
              <input
                type="number"
                value={formData.tenure}
                onChange={(e) => handleInputChange('tenure', e.target.value)}
                className="form-input"
                required
              />
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
                  required
                />
              </div>
            </div>

            <button type="submit" className="simulate-button" disabled={loading}>
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                'Simulate Savings'
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
          {/* Result Card 1 - Savings Summary */}
          <div className="savings-summary">
            <div className="savings-card">
              <div className="savings-label">Months Saved</div>
              <div className="savings-value">{results.months_saved}</div>
            </div>
            <div className="savings-card">
              <div className="savings-label">Interest Saved</div>
              <div className="savings-value amount">{formatAmount(results.interest_saved)}</div>
            </div>
          </div>

          {/* Result Card 2 - Repayment Breakdown Table */}
          <div className="repayment-breakdown">
            <div className="table-row">
              <span className="row-label">Original EMI</span>
              <span className="row-value">{formatAmount(results.original_emi)}</span>
            </div>
            <div className="table-row">
              <span className="row-label">New Monthly Payment</span>
              <span className="row-value bold">
                {formatAmount(results.original_emi + Number(formData.extraPayment))}
              </span>
            </div>
            <div className="table-row">
              <span className="row-label">Original Tenure</span>
              <span className="row-value bold">{formData.tenure} months</span>
            </div>
            <div className="table-row">
              <span className="row-label">New Tenure</span>
              <span className="row-value bold green">{results.new_tenure} months</span>
            </div>
          </div>

          {/* Result Card 3 - Interest Comparison Bar Chart */}
          <div className="interest-comparison">
            <div className="chart-title">Interest Comparison</div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fill: '#6B7280', fontSize: 12 }}
                  axisLine={false}
                />
                <YAxis 
                  tick={{ fill: '#6B7280', fontSize: 11 }}
                  axisLine={false}
                  tickFormatter={(value) => `${(value/1000).toFixed(0)}k`}
                />
                <Tooltip 
                  formatter={(value) => formatAmount(value)}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                />
                <Bar 
                  dataKey="interest" 
                  fill="#1E3A5F" 
                  barSize={60}
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
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

export default EarlyRepaymentPage;
