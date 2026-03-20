import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Calendar, 
  DollarSign, 
  Star, 
  Clock,
  User,
  AlertCircle
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertConsultationHistory = () => {
  const navigate = useNavigate();
  const [consultations, setConsultations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConsultationHistory = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      const response = await fetch(`http://localhost:5000/api/expert-availability/consultation-history/${workerId}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          setConsultations(data.consultations || []);
        } else {
          setError(data.error || 'Failed to load consultation history');
        }
      } else {
        setError('Failed to load consultation history');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching consultation history:', error);
      setError('Error loading consultation history');
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return 'N/A';
    const start = new Date(startTime);
    const end = new Date(endTime);
    const duration = Math.floor((end - start) / 1000 / 60); // minutes
    return `${duration} min`;
  };

  useEffect(() => {
    fetchConsultationHistory();
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
          <p style={{ color: '#8b5cf6' }}>Loading consultation history...</p>
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
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>📋 Consultation History</h1>
            <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
              View your completed consultations
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
        ) : consultations.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '60px 20px',
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <Calendar size={48} style={{ margin: '0 auto 16px', color: '#9ca3af' }} />
            <h3 style={{ margin: '0 0 8px 0', color: '#374151' }}>No Consultation History</h3>
            <p style={{ margin: 0, color: '#6b7280' }}>
              You haven't completed any consultations yet. Start accepting requests to build your history.
            </p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {consultations.map((consultation) => (
              <div key={consultation.request_id} style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb'
              }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '20px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                      <User size={16} style={{ color: '#6b7280' }} />
                      <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                        {consultation.user_name || 'Anonymous User'}
                      </span>
                      {consultation.user_rating && (
                        <span style={{
                          backgroundColor: '#fef3c7',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          fontWeight: '500',
                          color: '#92400e'
                        }}>
                          {consultation.user_rating.toFixed(1)} ⭐
                        </span>
                      )}
                    </div>
                    
                    <div style={{ marginBottom: '12px' }}>
                      <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#6b7280' }}>
                        <strong>Issue:</strong> {consultation.issue_description || 'N/A'}
                      </p>
                      <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#6b7280' }}>
                        <strong>Category:</strong> {consultation.area_of_expertise || 'N/A'}
                      </p>
                      <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#6b7280' }}>
                        <strong>Location:</strong> {consultation.user_city || 'N/A'}
                      </p>
                    </div>

                    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#6b7280' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Calendar size={14} />
                        <span>Started: {formatDate(consultation.started_at)}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={14} />
                        <span>Duration: {formatDuration(consultation.started_at, consultation.completed_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ marginBottom: '8px' }}>
                      <DollarSign size={16} style={{ color: '#16a34a' }} />
                      <span style={{ fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                        ₹{(consultation.proposed_fee || 0).toLocaleString()}
                      </span>
                    </div>
                    <div style={{
                      backgroundColor: '#dcfce7',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: '500',
                      color: '#16a34a'
                    }}>
                      Completed
                    </div>
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

export default AutomobileExpertConsultationHistory;
