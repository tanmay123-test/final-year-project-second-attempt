import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Clock, 
  DollarSign, 
  MessageCircle, 
  X, 
  Check, 
  AlertCircle,
  RefreshCw,
  Bell
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertRequests = () => {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Fetch consultation requests
  const fetchRequests = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/expert-availability/consultation-queue/${workerId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setRequests(data.consultation_requests || []);
          setLastUpdated(new Date());
        } else {
          setError(data.error || 'Failed to fetch requests');
        }
      } else {
        setError('Failed to connect to server');
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
      setError('Error fetching requests');
    } finally {
      setLoading(false);
    }
  };

  // Accept request
  const handleAccept = async (requestId) => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;

      const response = await fetch(`http://localhost:5000/api/expert-availability/consultation-requests/${requestId}/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          expert_id: workerId
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Navigate to active consultation
          navigate('/worker/car/automobile-expert/active');
        } else {
          setError(data.error || 'Failed to accept request');
        }
      } else {
        setError('Failed to accept request');
      }
    } catch (error) {
      console.error('Error accepting request:', error);
      setError('Error accepting request');
    }
  };

  // Reject request
  const handleReject = async (requestId) => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;

      const response = await fetch(`http://localhost:5000/api/expert-availability/consultation-requests/${requestId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          expert_id: workerId,
          rejection_reason: 'Expert declined the request'
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Remove the rejected request from the list
          setRequests(requests.filter(req => req.request_id !== requestId));
        } else {
          setError(data.error || 'Failed to reject request');
        }
      } else {
        setError('Failed to reject request');
      }
    } catch (error) {
      console.error('Error rejecting request:', error);
      setError('Error rejecting request');
    }
  };

  // Format time ago
  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const requestTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - requestTime) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} mins ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`;
    return `${Math.floor(diffInMinutes / 1440)} days ago`;
  };

  // Real-time polling effect
  useEffect(() => {
    fetchRequests();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchRequests, 10000); // Poll every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#8b5cf6',
        color: 'white',
        padding: '16px 20px',
        boxShadow: '0 2px 4px rgba(139, 92, 246, 0.1)'
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
                padding: '4px'
              }}
            >
              ← Back
            </button>
            <div>
              <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Consultation Requests Queue</h1>
              <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
                {requests.length} pending request{requests.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
              <RefreshCw size={14} />
              Last updated: {formatTimeAgo(lastUpdated)}
            </div>
            <button
              onClick={fetchRequests}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: 'none',
                color: 'white',
                padding: '8px 12px',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', paddingBottom: '100px', maxWidth: '1200px', margin: '0 auto' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <RefreshCw size={32} style={{ animation: 'spin 1s linear infinite', color: '#8b5cf6' }} />
            <p style={{ marginTop: '16px', color: '#8b5cf6' }}>Loading requests...</p>
          </div>
        ) : error ? (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <AlertCircle size={20} style={{ color: '#dc2626' }} />
            <div>
              <p style={{ margin: 0, fontWeight: '500', color: '#dc2626' }}>Error</p>
              <p style={{ margin: 0, fontSize: '14px', color: '#7f1d1d' }}>{error}</p>
            </div>
          </div>
        ) : requests.length === 0 ? (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '40px',
            textAlign: 'center',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <Bell size={48} style={{ color: '#d1d5db', margin: '0 auto 16px' }} />
            <h3 style={{ margin: '0 0 8px 0', color: '#374151' }}>No pending requests</h3>
            <p style={{ margin: 0, color: '#6b7280' }}>
              New consultation requests will appear here automatically
            </p>
            <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#9ca3af' }}>
              This page refreshes automatically every 10 seconds
            </p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {requests.map((request) => (
              <div
                key={request.request_id}
                style={{
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  padding: '20px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  border: '1px solid #e5e7eb',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                      <div style={{
                        backgroundColor: '#f3f4f6',
                        borderRadius: '50%',
                        padding: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <User size={20} style={{ color: '#6b7280' }} />
                      </div>
                      <div>
                        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                          {request.user_name || 'Anonymous User'}
                        </h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#6b7280' }}>
                          <Clock size={12} />
                          {formatTimeAgo(request.created_at)}
                          {request.user_city && (
                            <>
                              <span>•</span>
                              <span>{request.user_city}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: '500', color: '#374151' }}>
                        Issue:
                      </h4>
                      <p style={{ 
                        margin: 0, 
                        fontSize: '14px', 
                        color: '#6b7280', 
                        lineHeight: '1.5',
                        backgroundColor: '#f9fafb',
                        padding: '12px',
                        borderRadius: '6px'
                      }}>
                        {request.issue_description}
                      </p>
                    </div>

                    <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontSize: '12px', color: '#6b7280' }}>Category:</span>
                        <span style={{ 
                          fontSize: '12px', 
                          fontWeight: '500', 
                          color: '#8b5cf6',
                          backgroundColor: '#f3e8ff',
                          padding: '2px 8px',
                          borderRadius: '4px'
                        }}>
                          {request.area_of_expertise}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <DollarSign size={14} style={{ color: '#6b7280' }} />
                        <span style={{ fontSize: '12px', color: '#6b7280' }}>Consultation Fee:</span>
                        <span style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                          ₹{request.proposed_fee || '200'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => handleReject(request.request_id)}
                      style={{
                        backgroundColor: '#fef2f2',
                        border: '1px solid #fecaca',
                        color: '#dc2626',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '14px',
                        fontWeight: '500',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseOver={(e) => {
                        e.target.style.backgroundColor = '#fee2e2';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.backgroundColor = '#fef2f2';
                      }}
                    >
                      <X size={16} />
                      Decline
                    </button>
                    <button
                      onClick={() => handleAccept(request.request_id)}
                      style={{
                        backgroundColor: '#8b5cf6',
                        border: 'none',
                        color: 'white',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: '500',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseOver={(e) => {
                        e.target.style.backgroundColor = '#7c3aed';
                      }}
                      onMouseOut={(e) => {
                        e.target.style.backgroundColor = '#8b5cf6';
                      }}
                    >
                      <Check size={16} />
                      Accept
                    </button>
                  </div>
                </div>
              </div>
            ))}
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

export default AutomobileExpertRequests;
