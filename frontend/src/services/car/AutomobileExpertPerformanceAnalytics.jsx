import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  TrendingUp, 
  BarChart3, 
  Clock, 
  DollarSign, 
  Star,
  Users,
  Target,
  Calendar,
  AlertCircle
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertPerformanceAnalytics = () => {
  const navigate = useNavigate();
  const [analyticsData, setAnalyticsData] = useState({
    totalConsultations: 0,
    totalEarnings: 0,
    avgRating: 0,
    avgResponseTime: 0,
    avgDuration: 0,
    monthlyStats: [],
    categoryStats: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPerformanceAnalytics = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/expert-availability/performance-analytics/${workerId}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          setAnalyticsData(data.analytics || {});
        } else {
          setError(data.error || 'Failed to load performance analytics');
        }
      } else {
        setError('Failed to load performance analytics');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching performance analytics:', error);
      setError('Error loading performance analytics');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformanceAnalytics();
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
          <p style={{ color: '#8b5cf6' }}>Loading performance analytics...</p>
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
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>📈 Performance Analytics</h1>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
              Track your performance metrics and trends
            </p>
          </div>
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
            {/* Key Metrics */}
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
                    {analyticsData.totalConsultations || 0}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Total Consultations</p>
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <DollarSign size={20} style={{ color: '#16a34a' }} />
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                    ₹{(analyticsData.totalEarnings || 0).toLocaleString()}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Total Earnings</p>
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <Star size={20} style={{ color: '#f59e0b' }} />
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                    {(analyticsData.avgRating || 0).toFixed(1)}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Average Rating</p>
              </div>

              <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <Clock size={20} style={{ color: '#8b5cf6' }} />
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#111827' }}>
                    {analyticsData.avgResponseTime || 0} min
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>Avg Response Time</p>
              </div>
            </div>

            {/* Performance Trends */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Performance Trends
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '500', color: '#374151' }}>
                    Monthly Consultations
                  </h3>
                  <div style={{ 
                    backgroundColor: '#f8fafc', 
                    padding: '20px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    color: '#6b7280'
                  }}>
                    <BarChart3 size={32} style={{ margin: '0 auto 8px' }} />
                    <p>Monthly trend data will appear here</p>
                  </div>
                </div>

                <div>
                  <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '500', color: '#374151' }}>
                    Category Distribution
                  </h3>
                  <div style={{ 
                    backgroundColor: '#f8fafc', 
                    padding: '20px', 
                    borderRadius: '8px',
                    textAlign: 'center',
                    color: '#6b7280'
                  }}>
                    <Target size={32} style={{ margin: '0 auto 8px' }} />
                    <p>Category breakdown will appear here</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Detailed Stats */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Detailed Statistics
              </h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
                <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Average Session Duration</div>
                  <div style={{ fontSize: '20px', fontWeight: '600', color: '#111827' }}>
                    {analyticsData.avgDuration || 0} minutes
                  </div>
                </div>

                <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Completion Rate</div>
                  <div style={{ fontSize: '20px', fontWeight: '600', color: '#111827' }}>
                    {analyticsData.totalConsultations > 0 ? '100%' : '0%'}
                  </div>
                </div>

                <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Average Earnings per Session</div>
                  <div style={{ fontSize: '20px', fontWeight: '600', color: '#111827' }}>
                    ₹{analyticsData.totalConsultations > 0 
                      ? Math.round(analyticsData.totalEarnings / analyticsData.totalConsultations).toLocaleString()
                      : 0}
                  </div>
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

export default AutomobileExpertPerformanceAnalytics;
