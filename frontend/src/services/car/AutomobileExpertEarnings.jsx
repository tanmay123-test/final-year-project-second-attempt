import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  DollarSign, 
  Calendar, 
  Star, 
  TrendingUp, 
  ArrowLeft,
  CreditCard
} from 'lucide-react';
import api from '../../shared/api';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertEarnings = () => {
  const navigate = useNavigate();
  const [earningsData, setEarningsData] = useState({
    totalEarnings: 0,
    totalConsultations: 0,
    avgRating: 0,
    consultationHistory: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch earnings and consultation history
  const fetchEarningsData = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      // Fetch consultation history from backend
      const response = await api.get(`/api/expert-availability/consultation-history/${workerId}`);
      
      if (response.data?.success) {
        const data = response.data;
        // Calculate totals from consultation history
        const totalEarnings = data.consultations.reduce((sum, consultation) => 
          sum + (consultation.proposed_fee || 0), 0
        );
        
        const totalConsultations = data.consultations.length;
        
        const avgRating = data.consultations.length > 0 
          ? data.consultations.reduce((sum, consultation) => 
              sum + (consultation.user_rating || 0), 0
            ) / data.consultations.length
          : 0;

        setEarningsData({
          totalEarnings,
          totalConsultations,
          avgRating,
          consultationHistory: data.consultations
        });
      } else {
        console.error('Failed to fetch earnings data');
        setError('Failed to load earnings data');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching earnings data:', error);
      setError('Error loading earnings data');
      setLoading(false);
    }
  };

  // Handle withdrawal
  const handleWithdrawal = () => {
    const amount = earningsData.totalEarnings;
    if (amount > 0) {
      alert(`Withdrawal request for ₹${amount.toLocaleString()} has been submitted. You will receive the amount within 2-3 business days.`);
    } else {
      alert('No earnings available for withdrawal.');
    }
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Format issue description
  const formatIssue = (description) => {
    if (!description) return 'N/A';
    return description.length > 30 ? description.substring(0, 30) + '...' : description;
  };

  useEffect(() => {
    fetchEarningsData();
  }, []);

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid #e5e7eb',
            borderTop: '4px solid #2563eb',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#6b7280' }}>Loading earnings data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div style={{ 
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <div style={{ 
            backgroundColor: '#fef2f2',
            borderRadius: '50%',
            width: '60px',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <TrendingUp size={30} style={{ color: '#dc2626' }} />
          </div>
          <h3 style={{ margin: '0 0 8px 0', color: '#374151' }}>Error Loading Data</h3>
          <p style={{ margin: '0 0 24px 0', color: '#6b7280' }}>
            {error}
          </p>
          <button
            onClick={fetchEarningsData}
            style={{
              backgroundColor: '#2563eb',
              border: 'none',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      paddingBottom: '80px'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#2563eb',
        color: 'white',
        padding: '16px 20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => navigate('/worker/car/automobile-expert/homepage')}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                padding: '4px',
                fontSize: '16px'
              }}
            >
              ← Back
            </button>
            <div>
              <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Consultation History & Earnings</h1>
              <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
                Track your consultation history and earnings
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Stats Cards */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px', 
          marginBottom: '30px' 
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Earnings</div>
                <div style={{ fontSize: '32px', fontWeight: '700', color: '#111827' }}>
                  ₹{earningsData.totalEarnings.toLocaleString()}
                </div>
              </div>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '10px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <DollarSign style={{ width: '24px', height: '24px', color: '#16a34a' }} />
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Consultations</div>
                <div style={{ fontSize: '32px', fontWeight: '700', color: '#111827' }}>
                  {earningsData.totalConsultations}
                </div>
              </div>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '10px', 
                background: '#dbeafe', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <TrendingUp style={{ width: '24px', height: '24px', color: '#2563eb' }} />
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Avg Rating</div>
                <div style={{ fontSize: '32px', fontWeight: '700', color: '#111827' }}>
                  {earningsData.avgRating.toFixed(1)} ⭐
                </div>
              </div>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '10px', 
                background: '#fef3c7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Star style={{ width: '24px', height: '24px', color: '#f59e0b' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Withdrawal Button */}
        <div style={{ marginBottom: '30px' }}>
          <button
            onClick={handleWithdrawal}
            style={{
              backgroundColor: '#16a34a',
              border: 'none',
              color: 'white',
              padding: '16px 32px',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              fontSize: '16px',
              fontWeight: '500',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#15803d';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = '#16a34a';
            }}
          >
            <CreditCard size={20} />
            Withdraw ₹{earningsData.totalEarnings.toLocaleString()}
          </button>
        </div>

        {/* Consultation History Table */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
            Consultation History
          </h2>
          
          {earningsData.consultationHistory.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px', 
              color: '#6b7280' 
            }}>
              <Calendar size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
              <p>No consultation history available yet.</p>
              <p style={{ fontSize: '14px' }}>Start accepting consultation requests to build your history.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                    <th style={{ 
                      padding: '12px', 
                      textAlign: 'left', 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      color: '#374151' 
                    }}>
                      Date
                    </th>
                    <th style={{ 
                      padding: '12px', 
                      textAlign: 'left', 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      color: '#374151' 
                    }}>
                      Issue
                    </th>
                    <th style={{ 
                      padding: '12px', 
                      textAlign: 'left', 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      color: '#374151' 
                    }}>
                      Amount
                    </th>
                    <th style={{ 
                      padding: '12px', 
                      textAlign: 'left', 
                      fontSize: '14px', 
                      fontWeight: '600', 
                      color: '#374151' 
                    }}>
                      Rating
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {earningsData.consultationHistory.map((consultation, index) => (
                    <tr key={consultation.request_id || index} style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '12px', fontSize: '14px', color: '#374151' }}>
                        {formatDate(consultation.completed_at || consultation.created_at)}
                      </td>
                      <td style={{ padding: '12px', fontSize: '14px', color: '#374151' }}>
                        {formatIssue(consultation.issue_description)}
                      </td>
                      <td style={{ padding: '12px', fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                        ₹{(consultation.proposed_fee || 0).toLocaleString()}
                      </td>
                      <td style={{ padding: '12px', fontSize: '14px', color: '#374151' }}>
                        {consultation.user_rating ? (
                          <span style={{ 
                            backgroundColor: '#fef3c7', 
                            padding: '2px 8px', 
                            borderRadius: '4px',
                            fontWeight: '500'
                          }}>
                            {consultation.user_rating.toFixed(1)} ⭐
                          </span>
                        ) : (
                          <span style={{ color: '#9ca3af' }}>Not rated</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <AutomobileExpertBottomNav />

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default AutomobileExpertEarnings;
