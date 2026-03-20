import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  AlertTriangle, 
  User, 
  Calendar,
  MessageSquare,
  Send,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertReportUser = () => {
  const navigate = useNavigate();
  const [recentUsers, setRecentUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [reportData, setReportData] = useState({
    category: '',
    user_id: '',
    request_id: '',
    description: ''
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const reportCategories = [
    '👤 User Abuse',
    '🔧 Technical Issue',
    '📞 General Support'
  ];

  const fetchRecentUsers = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/expert-availability/recent-users/${workerId}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          setRecentUsers(data.users || []);
        } else {
          setError(data.error || 'Failed to load recent users');
        }
      } else {
        setError('Failed to load recent users');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching recent users:', error);
      setError('Error loading recent users');
      setLoading(false);
    }
  };

  const handleSubmitReport = async (e) => {
    e.preventDefault();
    
    if (!reportData.category || !reportData.user_id || !reportData.description) {
      setError('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;

      const response = await fetch(`http://localhost:5000/api/expert-availability/report-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          expert_id: workerId,
          user_id: reportData.user_id,
          request_id: reportData.request_id || null,
          category: reportData.category,
          description: reportData.description
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          setSuccess(true);
          setSelectedUser(null);
          setReportData({ category: '', user_id: '', request_id: '', description: '' });
        } else {
          setError(data.error || 'Failed to submit report');
        }
      } else {
        setError('Failed to submit report');
      }
      
      setSubmitting(false);
    } catch (error) {
      console.error('Error submitting report:', error);
      setError('Error submitting report');
      setSubmitting(false);
    }
  };

  useEffect(() => {
    fetchRecentUsers();
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
            borderTop: '4px solid #8b5cf6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px'
          }}></div>
          <p style={{ color: '#8b5cf6' }}>Loading recent users...</p>
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
        backgroundColor: '#8b5cf6',
        color: 'white',
        padding: '16px 20px',
        boxShadow: '0 2px 4px rgba(139, 92, 246, 0.1)'
      }}>
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
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>🚨 Report User</h1>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
              Report inappropriate or problematic user behavior
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        {success ? (
          <div style={{
            backgroundColor: '#f0fdf4',
            border: '1px solid #16a34a',
            borderRadius: '12px',
            padding: '40px',
            textAlign: 'center'
          }}>
            <CheckCircle size={48} style={{ margin: '0 auto 16px', color: '#16a34a' }} />
            <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600', color: '#16a34a' }}>
              Report Submitted Successfully
            </h2>
            <p style={{ margin: '0 0 24px 0', color: '#15803d' }}>
              Thank you for helping keep our community safe. We will review your report and take appropriate action.
            </p>
            <button
              onClick={() => setSuccess(false)}
              style={{
                backgroundColor: '#16a34a',
                border: 'none',
                color: 'white',
                padding: '12px 24px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              Report Another User
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Recent Users */}
            <div>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Recent Consultations
              </h2>
              
              {recentUsers.length === 0 ? (
                <div style={{
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  padding: '40px',
                  textAlign: 'center',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: '1px solid #e5e7eb'
                }}>
                  <User size={48} style={{ margin: '0 auto 16px', color: '#9ca3af' }} />
                  <p style={{ margin: 0, color: '#6b7280' }}>
                    No recent consultations found
                  </p>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: '12px' }}>
                  {recentUsers.map((user) => (
                    <div
                      key={user.request_id}
                      onClick={() => setSelectedUser(user)}
                      style={{
                        backgroundColor: selectedUser?.request_id === user.request_id ? '#eff6ff' : 'white',
                        border: selectedUser?.request_id === user.request_id ? '2px solid #2563eb' : '1px solid #e5e7eb',
                        borderRadius: '12px',
                        padding: '16px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '50%',
                          backgroundColor: '#f3f4f6',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <User size={20} style={{ color: '#6b7280' }} />
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                            {user.user_name}
                          </div>
                          <div style={{ fontSize: '14px', color: '#6b7280' }}>
                            {user.issue_description?.substring(0, 50)}...
                          </div>
                          <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                            {new Date(user.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Report Form */}
            <div>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Report Details
              </h2>
              
              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                {!selectedUser ? (
                  <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                    <AlertTriangle size={48} style={{ margin: '0 auto 16px', color: '#f59e0b' }} />
                    <p style={{ margin: 0, color: '#6b7280' }}>
                      Please select a user from the recent consultations to report
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmitReport}>
                    <div style={{ marginBottom: '20px' }}>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                        Selected User
                      </label>
                      <div style={{
                        backgroundColor: '#f8fafc',
                        padding: '12px',
                        borderRadius: '8px',
                        fontSize: '14px',
                        color: '#374151'
                      }}>
                        <div style={{ fontWeight: '600' }}>{selectedUser.user_name}</div>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                          Consultation: {selectedUser.issue_description?.substring(0, 100)}...
                        </div>
                      </div>
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                        Report Reason *
                      </label>
                      <select
                        value={reportData.category}
                        onChange={(e) => setReportData({ ...reportData, category: e.target.value })}
                        required
                        style={{
                          width: '100%',
                          padding: '12px',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#374151'
                        }}
                      >
                        <option value="">Select a report reason</option>
                        {reportCategories.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                        👤 Enter user ID *
                      </label>
                      <input
                        type="text"
                        value={reportData.user_id || ''}
                        onChange={(e) => setReportData({ ...reportData, user_id: e.target.value })}
                        placeholder="Enter user ID"
                        required
                        style={{
                          width: '100%',
                          padding: '12px',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#374151'
                        }}
                      />
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                        📋 Enter request ID (optional)
                      </label>
                      <input
                        type="text"
                        value={reportData.request_id || ''}
                        onChange={(e) => setReportData({ ...reportData, request_id: e.target.value })}
                        placeholder="Enter request ID (optional)"
                        style={{
                          width: '100%',
                          padding: '12px',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#374151'
                        }}
                      />
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                      <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                        📝 Enter description *
                      </label>
                      <textarea
                        value={reportData.description}
                        onChange={(e) => setReportData({ ...reportData, description: e.target.value })}
                        placeholder="Enter description"
                        required
                        rows={5}
                        style={{
                          width: '100%',
                          padding: '12px',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          fontSize: '14px',
                          color: '#374151',
                          resize: 'vertical'
                        }}
                      />
                    </div>

                    {error && (
                      <div style={{
                        backgroundColor: '#fef2f2',
                        border: '1px solid #fecaca',
                        borderRadius: '8px',
                        padding: '12px',
                        marginBottom: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <AlertCircle size={16} style={{ color: '#dc2626' }} />
                        <span style={{ fontSize: '14px', color: '#991b1b' }}>{error}</span>
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={submitting}
                      style={{
                        width: '100%',
                        backgroundColor: '#dc2626',
                        border: 'none',
                        color: 'white',
                        padding: '12px',
                        borderRadius: '8px',
                        cursor: submitting ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        fontWeight: '500',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        opacity: submitting ? 0.7 : 1
                      }}
                    >
                      {submitting ? (
                        'Submitting...'
                      ) : (
                        <>
                          <Send size={16} />
                          Submit Report
                        </>
                      )}
                    </button>
                  </form>
                )}
              </div>
            </div>
          </div>
        )}
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

export default AutomobileExpertReportUser;
