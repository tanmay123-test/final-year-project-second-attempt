import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Clock, 
  MessageCircle, 
  Phone, 
  PhoneOff, 
  AlertCircle,
  ArrowLeft,
  Wrench,
  MapPin,
  Calendar,
  DollarSign
} from 'lucide-react';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const ActiveConsultation = () => {
  const navigate = useNavigate();
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionDuration, setSessionDuration] = useState(0);
  const [startTime] = useState(new Date());

  // Format time display
  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Fetch active consultation data
  const fetchActiveConsultation = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!workerId) {
        navigate('/worker/car/automobile-expert/login');
        return;
      }

      // Fetch real active consultation from backend
      const response = await fetch(`http://localhost:5000/api/expert-availability/dashboard/${workerId}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.current_consultation) {
          // Transform backend data to match our component structure
          const consultationData = {
            request_id: data.current_consultation.request_id,
            user_name: data.current_consultation.user_name,
            user_city: data.current_consultation.user_city,
            user_phone: data.current_consultation.user_phone || 'Not provided',
            issue_description: data.current_consultation.issue_description,
            area_of_expertise: data.current_consultation.area_of_expertise,
            vehicle_details: data.current_consultation.vehicle_details || 'Not specified',
            proposed_fee: data.current_consultation.proposed_fee || 200,
            started_at: data.current_consultation.started_at || new Date(),
            status: data.current_consultation.status || 'IN_PROGRESS'
          };
          
          setSessionData(consultationData);
        } else {
          // No active consultation
          setSessionData(null);
        }
      } else {
        console.error('Failed to fetch active consultation');
        setSessionData(null);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching active consultation:', error);
      setLoading(false);
      setSessionData(null);
    }
  };

  // End consultation
  const handleEndConsultation = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (!sessionData?.request_id) {
        console.error('No active consultation to end');
        return;
      }

      // Call backend to complete consultation
      const response = await fetch(`http://localhost:5000/api/expert-availability/consultation-requests/${sessionData.request_id}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          expert_id: workerId,
          user_rating: null // Will be provided by user later
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Consultation ended successfully
          console.log('Consultation ended:', data.message);
          // Navigate back to homepage or requests
          navigate('/worker/car/automobile-expert/homepage');
        } else {
          console.error('Failed to end consultation:', data.error);
          // Show error message to user
          alert('Failed to end consultation: ' + (data.error || 'Unknown error'));
        }
      } else {
        console.error('Failed to end consultation');
        alert('Failed to end consultation. Please try again.');
      }
    } catch (error) {
      console.error('Error ending consultation:', error);
      alert('Error ending consultation. Please try again.');
    }
  };

  // Update session timer
  useEffect(() => {
    const timer = setInterval(() => {
      if (sessionData && sessionData.started_at) {
        const now = new Date();
        const started = new Date(sessionData.started_at);
        const duration = Math.floor((now - started) / 1000);
        setSessionDuration(duration);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [sessionData]);

  useEffect(() => {
    fetchActiveConsultation();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchActiveConsultation, 10000); // Poll every 10 seconds
    
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
          <p style={{ color: '#8b5cf6' }}>Loading active consultation...</p>
        </div>
      </div>
    );
  }

  if (!sessionData) {
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
          <AlertCircle size={48} style={{ color: '#d1d5db', margin: '0 auto 16px' }} />
          <h3 style={{ margin: '0 0 8px 0', color: '#374151' }}>No Active Consultation</h3>
          <p style={{ margin: '0 0 24px 0', color: '#6b7280' }}>
            You don't have any active consultations at the moment
          </p>
          <button
            onClick={() => navigate('/worker/car/automobile-expert/requests')}
            style={{
              backgroundColor: '#8b5cf6',
              border: 'none',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#7c3aed';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = '#8b5cf6';
            }}
          >
            View Requests Queue
          </button>
        </div>
      </div>
    );
  }

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
                padding: '4px',
                fontSize: '16px'
              }}
            >
              ← Back
            </button>
            <div>
              <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Active Consultation</h1>
              <p style={{ margin: 0, fontSize: '14px', opacity: 0.9 }}>
                Session in progress
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ 
              backgroundColor: 'rgba(255,255,255,0.2)', 
              padding: '8px 16px', 
              borderRadius: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Clock size={16} />
              <span style={{ fontSize: '14px', fontWeight: '500' }}>
                {formatTime(sessionDuration)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '20px', paddingBottom: '100px', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* Left Column - Customer Info & Issue */}
          <div>
            {/* Customer Information */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Customer Information
              </h2>
              <div style={{ display: 'grid', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
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
                    <p style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                      {sessionData.user_name}
                    </p>
                    <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                      {sessionData.user_phone}
                    </p>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                  <MapPin size={16} style={{ color: '#6b7280' }} />
                  <span style={{ color: '#6b7280' }}>Location:</span>
                  <span style={{ color: '#111827', fontWeight: '500' }}>{sessionData.user_city}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                  <Calendar size={16} style={{ color: '#6b7280' }} />
                  <span style={{ color: '#6b7280' }}>Started:</span>
                  <span style={{ color: '#111827', fontWeight: '500' }}>
                    {new Date(sessionData.started_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Vehicle Issue */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '20px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Vehicle Issue Details
              </h2>
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Wrench size={16} style={{ color: '#8b5cf6' }} />
                  <span style={{ 
                    fontSize: '12px', 
                    fontWeight: '500', 
                    color: '#8b5cf6',
                    backgroundColor: '#f3e8ff',
                    padding: '2px 8px',
                    borderRadius: '4px'
                  }}>
                    {sessionData.area_of_expertise}
                  </span>
                </div>
                <p style={{ 
                  margin: '0 0 12px 0', 
                  fontSize: '14px', 
                  color: '#6b7280',
                  lineHeight: '1.5'
                }}>
                  <strong>Issue:</strong> {sessionData.issue_description}
                </p>
                <p style={{ 
                  margin: 0, 
                  fontSize: '14px', 
                  color: '#6b7280',
                  lineHeight: '1.5'
                }}>
                  <strong>Vehicle:</strong> {sessionData.vehicle_details}
                </p>
              </div>
              <div style={{ 
                backgroundColor: '#f9fafb', 
                padding: '12px', 
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <DollarSign size={16} style={{ color: '#8b5cf6' }} />
                <span style={{ fontSize: '14px', color: '#6b7280' }}>Consultation Fee:</span>
                <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                  ₹{sessionData.proposed_fee}
                </span>
              </div>
            </div>
          </div>

          {/* Right Column - Actions */}
          <div>
            {/* Consultation Actions */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '20px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Consultation Actions
              </h2>
              <div style={{ display: 'grid', gap: '12px' }}>
                <button
                  style={{
                    backgroundColor: '#8b5cf6',
                    border: 'none',
                    color: 'white',
                    padding: '16px',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = '#7c3aed';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = '#8b5cf6';
                  }}
                >
                  <MessageCircle size={20} />
                  Open Chat
                </button>
                
                <button
                  style={{
                    backgroundColor: '#10b981',
                    border: 'none',
                    color: 'white',
                    padding: '16px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                    fontSize: '16px',
                    fontWeight: '500',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = '#059669';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = '#10b981';
                  }}
                >
                  <Phone size={20} />
                  Start Call
                </button>
              </div>
            </div>

            {/* Session Controls */}
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '20px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <h2 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#111827' }}>
                Session Controls
              </h2>
              <button
                onClick={handleEndConsultation}
                style={{
                  backgroundColor: '#dc2626',
                  border: 'none',
                  color: 'white',
                  padding: '16px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px',
                  fontSize: '16px',
                  fontWeight: '500',
                  width: '100%',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => {
                  e.target.style.backgroundColor = '#b91c1c';
                }}
                onMouseOut={(e) => {
                  e.target.style.backgroundColor = '#dc2626';
                }}
              >
                <PhoneOff size={20} />
                End Consultation
              </button>
              
              <div style={{ 
                marginTop: '16px', 
                padding: '12px', 
                backgroundColor: '#fef2f2',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#7f1d1d',
                textAlign: 'center'
              }}>
                <strong>Note:</strong> Ending the consultation will finalize the session and process payment
              </div>
            </div>
          </div>
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

export default ActiveConsultation;
