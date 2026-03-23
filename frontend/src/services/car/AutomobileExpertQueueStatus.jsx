import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Users, 
  Clock, 
  TrendingUp, 
  BarChart3,
  Activity,
  AlertCircle,
  RefreshCw,
  Calendar,
  Target
} from 'lucide-react';
import api from '../../shared/api';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertQueueStatus = () => {
  const navigate = useNavigate();
  const [queueData, setQueueData] = useState({
    waitingRequests: 0,
    activeConsultations: 0,
    demandLevel: 'LOW',
    avgWaitTime: 0,
    queueTrends: [],
    expertStatus: 'OFFLINE',
    lastUpdated: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchQueueStatus = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      const response = await api.get(`/api/expert-availability/queue-status/${workerId}`);
      
      if (response.data.success) {
        const data = response.data;
        
        if (data.success) {
          setQueueData({
            ...data.queue_status,
            lastUpdated: new Date()
          });
        } else {
          setError(data.error || 'Failed to load queue status');
        }
      } else {
        setError('Failed to load queue status');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching queue status:', error);
      setError('Error loading queue status');
      setLoading(false);
    }
  };

  const getDemandColor = (level) => {
    switch (level) {
      case 'HIGH': return '#dc2626';
      case 'MEDIUM': return '#f59e0b';
      case 'LOW': return '#16a34a';
      default: return '#6b7280';
    }
  };

  const getDemandBgColor = (level) => {
    switch (level) {
      case 'HIGH': return '#fef2f2';
      case 'MEDIUM': return '#fef3c7';
      case 'LOW': return '#f0fdf4';
      default: return '#f9fafb';
    }
  };

  useEffect(() => {
    fetchQueueStatus();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchQueueStatus, 30000);
    return () => clearInterval(interval);
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
          <p style={{ color: '#8b5cf6' }}>Loading queue status...</p>
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
              <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>📊 Queue Status</h1>
              <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
                Real-time consultation queue information
              </p>
            </div>
          </div>
          <button
            onClick={fetchQueueStatus}
            style={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              border: 'none',
              color: 'white',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '14px'
            }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        {error ? (
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
              <h3 style={{ margin: '0 0 4px 0', color: '#991b1b' }}>Error</h3>
              <p style={{ margin: 0, color: '#7f1d1d' }}>{error}</p>
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '20px' }}>
            {/* Queue Overview */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px' 
            }}>
              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <Users size={20} style={{ color: '#2563eb' }} />
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                    {queueData.waitingRequests || 0}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Waiting Requests</p>
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <Activity size={20} style={{ color: '#16a34a' }} />
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                    {queueData.activeConsultations || 0}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Active Consultations</p>
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <Clock size={20} style={{ color: '#f59e0b' }} />
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                    {queueData.avgWaitTime || 0} min
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Avg Wait Time</p>
              </div>

              <div style={{
                backgroundColor: getDemandBgColor(queueData.demandLevel),
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: `1px solid ${getDemandColor(queueData.demandLevel)}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <TrendingUp size={20} style={{ color: getDemandColor(queueData.demandLevel) }} />
                  <span style={{ 
                    fontSize: '24px', 
                    fontWeight: '700', 
                    color: getDemandColor(queueData.demandLevel) 
                  }}>
                    {queueData.demandLevel || 'LOW'}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Demand Level</p>
              </div>
            </div>

            {/* Expert Status */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Your Status
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Current Status</div>
                  <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    backgroundColor: queueData.expertStatus === 'ONLINE' ? '#f0fdf4' : '#fef2f2',
                    color: queueData.expertStatus === 'ONLINE' ? '#16a34a' : '#dc2626',
                    fontWeight: '500'
                  }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      backgroundColor: queueData.expertStatus === 'ONLINE' ? '#16a34a' : '#dc2626'
                    }}></div>
                    {queueData.expertStatus || 'OFFLINE'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Last Updated</div>
                  <div style={{ fontSize: '16px', fontWeight: '500', color: '#111827' }}>
                    {queueData.lastUpdated ? queueData.lastUpdated.toLocaleTimeString() : 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Queue Trends */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Queue Trends
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '500', color: '#374151' }}>
                    Hourly Queue Volume
                  </h3>
                  <div style={{ 
                    backgroundColor: '#f8fafc', 
                    padding: '40px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    color: '#6b7280'
                  }}>
                    <BarChart3 size={32} style={{ margin: '0 auto 8px' }} />
                    <p>Hourly trend chart will appear here</p>
                  </div>
                </div>

                <div>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '500', color: '#374151' }}>
                    Peak Hours Analysis
                  </h3>
                  <div style={{ 
                    backgroundColor: '#f8fafc', 
                    padding: '40px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    color: '#6b7280'
                  }}>
                    <Target size={32} style={{ margin: '0 auto 8px' }} />
                    <p>Peak hours data will appear here</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Recommendations
              </h2>
              
              <div style={{ display: 'grid', gap: '12px' }}>
                {queueData.demandLevel === 'HIGH' && (
                  <div style={{
                    backgroundColor: '#fef2f2',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid #fecaca'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <AlertCircle size={16} style={{ color: '#dc2626' }} />
                      <span style={{ fontWeight: '500', color: '#991b1b' }}>High Demand Alert</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '14px', color: '#7f1d1d' }}>
                      Consider staying online to help with the high volume of requests.
                    </p>
                  </div>
                )}

                {queueData.demandLevel === 'LOW' && queueData.expertStatus === 'ONLINE' && (
                  <div style={{
                    backgroundColor: '#f0fdf4',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid #bbf7d0'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <Target size={16} style={{ color: '#16a34a' }} />
                      <span style={{ fontWeight: '500', color: '#15803d' }}>Optimal Time</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '14px', color: '#166534' }}>
                      Good time to take a break or focus on other tasks. Demand is currently low.
                    </p>
                  </div>
                )}

                <div style={{
                  backgroundColor: '#eff6ff',
                  padding: '16px',
                  borderRadius: '8px',
                  border: '1px solid #bfdbfe'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <Calendar size={16} style={{ color: '#2563eb' }} />
                    <span style={{ fontWeight: '500', color: '#1d4ed8' }}>Queue Insights</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '14px', color: '#1e40af' }}>
                    Current average wait time is {queueData.avgWaitTime || 0} minutes. 
                    {queueData.waitingRequests > 5 ? ' Consider accepting more requests to reduce wait times.' : ' Wait times are within acceptable range.'}
                  </p>
                </div>
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

export default AutomobileExpertQueueStatus;
