import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calculator, Home, PiggyBank, Target, Brain, AlertCircle, TrendingDown, BarChart2, CheckCircle } from 'lucide-react';
import { loanService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';
import '../styles/LoanPage.css';

const LoanPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Section 1: EMI Calculator State
  const [calcData, setCalcData] = useState({
    loan_amount: '',
    interest_rate: '',
    loan_tenure: ''
  });
  const [calcResults, setCalcResults] = useState(null);
  const [loadingCalc, setLoadingCalc] = useState(false);
  
  // Section 2: EMI Schedule State
  const [schedule, setSchedule] = useState(null);
  const [loadingSchedule, setLoadingSchedule] = useState(false);
  const [showSchedule, setShowSchedule] = useState(false);
  
  // Section 3: Compare State
  const [compareData, setCompareData] = useState({
    loan1: { loan_amount: '', interest_rate: '', loan_tenure: '' },
    loan2: { loan_amount: '', interest_rate: '', loan_tenure: '' }
  });
  const [compareResult, setCompareResult] = useState(null);
  const [loadingCompare, setLoadingCompare] = useState(false);

  const bottomNavItems = [
    { icon: Home, label: 'Finny', path: '/finny' },
    { icon: PiggyBank, label: 'Budget', path: '/finny/budget' },
    { icon: Calculator, label: 'Loan', path: '/finny/loan', active: true },
    { icon: Target, label: 'Goal Jar', path: '/finny/goals' },
    { icon: Brain, label: 'AI Coach', path: '/finny/coach' }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    if (!calcData.loan_amount || !calcData.interest_rate || !calcData.loan_tenure) return;

    try {
      setLoadingCalc(true);
      const response = await loanService.analyze({
        user_id: user?.user_id || user?.id,
        ...calcData
      });
      setCalcResults(response.data);
      setSchedule(null);
      setShowSchedule(false);
    } catch (err) {
      console.error('Failed to analyze loan:', err);
      alert('Failed to calculate. Please check inputs.');
    } finally {
      setLoadingCalc(false);
    }
  };

  const handleViewSchedule = async () => {
    try {
      setLoadingSchedule(true);
      const response = await loanService.getSchedule({
        user_id: user?.user_id || user?.id,
        ...calcData
      });
      setSchedule(response.data);
      setShowSchedule(true);
    } catch (err) {
      console.error('Failed to get schedule:', err);
      alert('Failed to load schedule.');
    } finally {
      setLoadingSchedule(false);
    }
  };

  const handleCompare = async (e) => {
    e.preventDefault();
    try {
      setLoadingCompare(true);
      const response = await loanService.compare({
        user_id: user?.user_id || user?.id,
        loan1: compareData.loan1,
        loan2: compareData.loan2
      });
      setCompareResult(response.data);
    } catch (err) {
      console.error('Failed to compare loans:', err);
      alert('Failed to compare. Please check all inputs.');
    } finally {
      setLoadingCompare(false);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 7) return 'high';
    if (score >= 4) return 'medium';
    return 'low';
  };

  return (
    <div className="finny-page-layout">
      {/* Sidebar for Desktop */}
      <aside className="finny-sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">Finny</h1>
          <p className="sidebar-subtitle">Smart Tracker</p>
        </div>
        <nav className="sidebar-nav">
          {bottomNavItems.map((item, index) => (
            <div 
              key={index} 
              className={`sidebar-item ${item.active ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <item.icon size={20} color={item.active ? '#F4B400' : '#6B7280'} />
              <span className="sidebar-label">{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      <div className="finny-page-content">
        <div className="loan-page">
          {/* Header */}
          <div className="header">
            <div className="header-content">
              <button className="back-button" onClick={() => navigate('/finny')}>
                <ArrowLeft size={20} />
              </button>
              <div className="header-text">
                <h1 className="header-title">Loan Analyzer</h1>
                <p className="header-subtitle">Plan your debt wisely</p>
              </div>
            </div>
          </div>

          <div className="main-content">
            {/* Section 1: EMI Calculator */}
            <div className="section-card">
              <h2 className="section-title">
                <Calculator size={20} color="#1F5F7A" />
                EMI Calculator
              </h2>
              <form onSubmit={handleCalculate} className="calculator-form">
                <div className="form-group">
                  <label>Loan Amount (₹)</label>
                  <input 
                    type="number" 
                    placeholder="e.g. 5,00,000"
                    value={calcData.loan_amount}
                    onChange={e => setCalcData({ ...calcData, loan_amount: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Interest Rate (%)</label>
                  <input 
                    type="number" 
                    step="0.1"
                    placeholder="e.g. 10.5"
                    value={calcData.interest_rate}
                    onChange={e => setCalcData({ ...calcData, interest_rate: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Tenure (Months)</label>
                  <input 
                    type="number" 
                    placeholder="e.g. 60"
                    value={calcData.loan_tenure}
                    onChange={e => setCalcData({ ...calcData, loan_tenure: e.target.value })}
                    required
                  />
                </div>
                <button type="submit" className="btn-calculate" disabled={loadingCalc}>
                  {loadingCalc ? 'Calculating...' : 'Analyze Loan'}
                </button>
              </form>

              {calcResults && (
                <div className="results-grid">
                  <div className="result-card">
                    <span className="result-label">Monthly EMI</span>
                    <span className="result-value">{formatCurrency(calcResults.emi)}</span>
                  </div>
                  <div className="result-card">
                    <span className="result-label">Total Interest</span>
                    <span className="result-value">{formatCurrency(calcResults.total_interest)}</span>
                  </div>
                  <div className="result-card">
                    <span className="result-label">Total Repayment</span>
                    <span className="result-value">{formatCurrency(calcResults.total_payment)}</span>
                  </div>
                  <div className="result-card">
                    <span className="result-label">Affordability</span>
                    <span className={`score-badge ${getScoreClass(calcResults.affordability_score)}`}>
                      {calcResults.affordability_score}/10
                    </span>
                  </div>
                  <div className="result-card">
                    <span className="result-label">Risk Level</span>
                    <span className={`score-badge ${getScoreClass(10 - calcResults.risk_score)}`}>
                      {calcResults.risk_score}/10
                    </span>
                  </div>
                </div>
              )}

              {calcResults && !showSchedule && (
                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                  <button onClick={handleViewSchedule} className="retry-button" disabled={loadingSchedule}>
                    {loadingSchedule ? 'Loading...' : 'View Full Schedule'}
                  </button>
                </div>
              )}
            </div>

            {/* Section 2: EMI Schedule */}
            {showSchedule && schedule && (
              <div className="section-card">
                <h2 className="section-title">
                  <Info size={20} color="#1F5F7A" />
                  Repayment Schedule
                </h2>
                <div className="table-container">
                  <table className="schedule-table">
                    <thead>
                      <tr>
                        <th>Month</th>
                        <th>EMI</th>
                        <th>Principal</th>
                        <th>Interest</th>
                        <th>Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {schedule.map((row, idx) => (
                        <tr key={idx}>
                          <td>{row.month}</td>
                          <td>{formatCurrency(row.emi)}</td>
                          <td>{formatCurrency(row.principal)}</td>
                          <td>{formatCurrency(row.interest)}</td>
                          <td>{formatCurrency(row.remaining_balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Section 3: Compare Loans */}
            <div className="section-card">
              <h2 className="section-title">
                <Scale size={20} color="#1F5F7A" />
                Compare Two Loans
              </h2>
              <form onSubmit={handleCompare}>
                <div className="compare-grid">
                  <div className="compare-col">
                    <h3>Loan Option 1</h3>
                    <div className="form-group">
                      <label>Amount (₹)</label>
                      <input 
                        type="number" 
                        value={compareData.loan1.loan_amount}
                        onChange={e => setCompareData({
                          ...compareData,
                          loan1: { ...compareData.loan1, loan_amount: e.target.value }
                        })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Interest (%)</label>
                      <input 
                        type="number" 
                        step="0.1"
                        value={compareData.loan1.interest_rate}
                        onChange={e => setCompareData({
                          ...compareData,
                          loan1: { ...compareData.loan1, interest_rate: e.target.value }
                        })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Tenure (Mos)</label>
                      <input 
                        type="number" 
                        value={compareData.loan1.loan_tenure}
                        onChange={e => setCompareData({
                          ...compareData,
                          loan1: { ...compareData.loan1, loan_tenure: e.target.value }
                        })}
                        required
                      />
                    </div>
                  </div>
                  <div className="compare-col">
                    <h3>Loan Option 2</h3>
                    <div className="form-group">
                      <label>Amount (₹)</label>
                      <input 
                        type="number" 
                        value={compareData.loan2.loan_amount}
                        onChange={e => setCompareData({
                          ...compareData,
                          loan2: { ...compareData.loan2, loan_amount: e.target.value }
                        })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Interest (%)</label>
                      <input 
                        type="number" 
                        step="0.1"
                        value={compareData.loan2.interest_rate}
                        onChange={e => setCompareData({
                          ...compareData,
                          loan2: { ...compareData.loan2, interest_rate: e.target.value }
                        })}
                        required
                      />
                    </div>
                    <div className="form-group">
                      <label>Tenure (Mos)</label>
                      <input 
                        type="number" 
                        value={compareData.loan2.loan_tenure}
                        onChange={e => setCompareData({
                          ...compareData,
                          loan2: { ...compareData.loan2, loan_tenure: e.target.value }
                        })}
                        required
                      />
                    </div>
                  </div>
                </div>
                <div style={{ textAlign: 'center', marginTop: '24px' }}>
                  <button type="submit" className="btn-calculate" disabled={loadingCompare}>
                    {loadingCompare ? 'Comparing...' : 'Compare Options'}
                  </button>
                </div>
              </form>

              {compareResult && (
                <div className="comparison-result">
                  <div className="comparison-text">
                    <CheckCircle size={20} color="#059669" style={{ verticalAlign: 'middle', marginRight: '8px' }} />
                    {compareResult.recommendation}
                  </div>
                  <p style={{ marginTop: '8px', color: '#6B7280' }}>
                    Savings: <strong>{formatCurrency(compareResult.savings)}</strong>
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Navigation for Mobile */}
          <div className="finny-bottom-nav">
            {bottomNavItems.map((item, index) => (
              <div 
                key={index} 
                className={`nav-item ${item.active ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
                <item.icon 
                  size={20} 
                  color={item.active ? '#F4B400' : '#6B7280'} 
                />
                <span className={`nav-label ${item.active ? 'active' : ''}`}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoanPage;
