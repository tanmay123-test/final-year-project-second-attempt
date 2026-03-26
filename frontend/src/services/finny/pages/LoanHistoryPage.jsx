import React, { useState, useEffect } from 'react';
import { ArrowLeft, Clock, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { loanApi } from '../api/loanApi';
import '../styles/LoanPage.css';

const LoanHistoryPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [allAnalyses, setAllAnalyses] = useState([]);
  const [filteredAnalyses, setFilteredAnalyses] = useState([]);
  const [searchFilter, setSearchFilter] = useState('');

  const handleBackClick = () => {
    navigate('/finny/loan');
  };

  // Fetch history on component mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Filter analyses when search term changes
  useEffect(() => {
    if (!searchFilter.trim()) {
      setFilteredAnalyses(allAnalyses);
    } else {
      const filtered = allAnalyses.filter(analysis => {
        const searchTerm = searchFilter.toLowerCase();
        const dateMatch = analysis.date.toLowerCase().includes(searchTerm);
        const amountMatch = analysis.amount.toString().includes(searchTerm);
        return dateMatch || amountMatch;
      });
      setFilteredAnalyses(filtered);
    }
  }, [searchFilter, allAnalyses]);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');

    try {
      // Get user_id from localStorage or context
      const user_id = localStorage.getItem('user_id') || 'demo_user';
      
      console.log('Fetching loan history for user:', user_id);
      const response = await loanApi.getHistory();
      console.log('Loan history response:', response);
      
      if (response.success) {
        const analyses = response.data?.loan_analyses || response.data?.analyses || [];
        const sortedAnalyses = analyses.sort((a, b) => {
          return new Date(b.created_at || b.date) - new Date(a.created_at || a.date);
        });
        setAllAnalyses(sortedAnalyses);
        setFilteredAnalyses(sortedAnalyses);
      } else {
        setError(response.error || 'Failed to load loan history');
      }
    } catch (err) {
      console.error('Loan history fetch error:', err);
      
      // Check if it's a network error and provide mock data for testing
      if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        console.log('Using mock data for testing...');
        const mockData = generateMockHistory();
        setAllAnalyses(mockData);
        setFilteredAnalyses(mockData);
        setError('Using demo data - Backend server not available');
      } else {
        setError('Failed to load history. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const generateMockHistory = () => {
    const mockAnalyses = [
      {
        id: '1',
        date: '2026-03-24',
        amount: 500000,
        interest_rate: 10,
        tenure: 24,
        emi: 22444,
        dti: 38.5,
        risk_score: 45,
        risk_level: 'Medium'
      },
      {
        id: '2',
        date: '2026-03-15',
        amount: 300000,
        interest_rate: 12,
        tenure: 36,
        emi: 9964,
        dti: 25.2,
        risk_score: 22,
        risk_level: 'Low'
      },
      {
        id: '3',
        date: '2026-03-10',
        amount: 750000,
        interest_rate: 9.5,
        tenure: 48,
        emi: 15728,
        dti: 52.8,
        risk_score: 78,
        risk_level: 'High'
      },
      {
        id: '4',
        date: '2026-03-05',
        amount: 200000,
        interest_rate: 11,
        tenure: 18,
        emi: 12167,
        dti: 18.9,
        risk_score: 15,
        risk_level: 'Low'
      },
      {
        id: '5',
        date: '2026-02-28',
        amount: 400000,
        interest_rate: 10.5,
        tenure: 30,
        emi: 13801,
        dti: 42.1,
        risk_score: 58,
        risk_level: 'Medium'
      }
    ];
    
    // Sort by date descending
    return mockAnalyses.sort((a, b) => new Date(b.date) - new Date(a.date));
  };

  const getRiskBadgeColor = (score) => {
    if (score <= 25) {
      return { bg: '#DCFCE7', text: '#16A34A' }; // Green
    } else if (score <= 50) {
      return { bg: '#FEF3C7', text: '#D97706' }; // Amber
    } else if (score <= 75) {
      return { bg: '#FEE2E2', text: '#EF4444' }; // Red
    } else {
      return { bg: '#FEE2E2', text: '#EF4444' }; // Red
    }
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
  };

  const handleRetry = () => {
    fetchHistory();
  };

  // Show loading skeletons
  if (loading) {
    return (
      <div className="loan-history-page">
        {/* Header */}
        <div className="loan-header">
          <button className="back-button" onClick={handleBackClick}>
            <ArrowLeft size={20} color="white" />
          </button>
          <div className="header-content">
            <div className="header-title-section">
              <Clock size={20} color="#F59E0B" />
              <div className="header-text">
                <h1 className="header-title">Loan Analysis History</h1>
              </div>
            </div>
          </div>
        </div>

        {/* Search Bar */}
        <div className="search-container">
          <input
            type="text"
            placeholder="Filter by date or amount..."
            className="search-input"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
          />
        </div>

        {/* Loading Skeletons */}
        <div className="history-list">
          {[1, 2, 3].map((index) => (
            <div key={index} className="history-card skeleton">
              <div className="skeleton-row">
                <div className="skeleton-date"></div>
                <div className="skeleton-badge"></div>
              </div>
              <div className="skeleton-loan-summary"></div>
              <div className="skeleton-stats">
                <div className="skeleton-stat"></div>
                <div className="skeleton-stat"></div>
                <div className="skeleton-stat"></div>
              </div>
            </div>
          ))}
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
  }

  return (
    <div className="loan-history-page">
      {/* Header */}
      <div className="loan-header">
        <button className="back-button" onClick={handleBackClick}>
          <ArrowLeft size={20} color="white" />
        </button>
        <div className="header-content">
          <div className="header-title-section">
            <Clock size={20} color="#F59E0B" />
            <div className="header-text">
              <h1 className="header-title">Loan Analysis History</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-container">
        <input
          type="text"
          placeholder="Filter by date or amount..."
          className="search-input"
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
        />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button className="retry-button" onClick={handleRetry}>
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      )}

      {/* History Cards */}
      <div className="history-list">
        {filteredAnalyses.length === 0 ? (
          <div className="empty-state">
            <Clock size={48} color="#94A3B8" />
            <div className="empty-title">
              {searchFilter ? 'No results match your filter.' : 'No loan analyses yet'}
            </div>
            <div className="empty-subtitle">
              {searchFilter 
                ? 'Try adjusting your search terms.' 
                : 'Your analyzed loans will appear here.'
              }
            </div>
          </div>
        ) : (
          filteredAnalyses.map((analysis) => {
            const riskColors = getRiskBadgeColor(analysis.risk_score);
            
            return (
              <div key={analysis.id} className="history-card">
                {/* Row 1: Date and Risk Score */}
                <div className="history-card-header">
                  <span className="history-date">{analysis.date}</span>
                  <div 
                    className="risk-badge"
                    style={{ 
                      backgroundColor: riskColors.bg, 
                      color: riskColors.text 
                    }}
                  >
                    {analysis.risk_score}/100
                  </div>
                </div>

                {/* Row 2: Loan Summary */}
                <div className="loan-summary">
                  {formatAmount(analysis.amount)} @ {analysis.interest_rate}%
                </div>

                {/* Row 3: 3-Column Stats */}
                <div className="stats-row">
                  <div className="stat-column">
                    <div className="stat-label">Tenure</div>
                    <div className="stat-value">{analysis.tenure} mo</div>
                  </div>
                  <div className="stat-column">
                    <div className="stat-label">EMI</div>
                    <div className="stat-value">{formatAmount(analysis.emi)}</div>
                  </div>
                  <div className="stat-column">
                    <div className="stat-label">DTI</div>
                    <div className="stat-value">{analysis.dti}%</div>
                  </div>
                </div>
              </div>
            );
          })
        )}
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

export default LoanHistoryPage;
