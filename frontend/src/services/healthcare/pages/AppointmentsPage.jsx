import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import healthcareSocket from '../../healthcareSocket';
import '../styles/healthcare-shared.css';

const AppointmentsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const userId = user?.id || JSON.parse(localStorage.getItem('user'))?.id;

  const fetchAppointments = async () => {
    if (!userId) return;
    try {
      setLoading(true);
      const res = await fetch(`/user/appointments`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await res.json();
      setAppointments(data.appointments || []);
    } catch (err) {
      console.error('Failed to fetch appointments:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
    
    if (userId) {
      healthcareSocket.connect();
      healthcareSocket.joinRoom('user', userId);

      const handleUpdate = (data) => {
        console.log('🔄 Real-time appointment update:', data);
        // Refresh list
        fetchAppointments();
        
        // Show notification
        if (Notification.permission === "granted") {
          new Notification("Appointment Update", {
            body: `Your appointment status has been updated to ${data.status}`
          });
        }
      };

      healthcareSocket.on('appointment_update', handleUpdate);

      return () => {
        healthcareSocket.off('appointment_update', handleUpdate);
        healthcareSocket.leaveRoom('user', userId);
      };
    }
  }, [userId]);

  const getStatusColor = (status) => {
    switch(status?.toLowerCase()) {
      case 'accepted': 
      case 'confirmed': 
      case 'upcoming': return '#10B981';
      case 'completed': return '#6B7280';
      case 'pending': return '#F59E0B';
      case 'rejected':
      case 'cancelled': return '#EF4444';
      case 'payment_pending': return '#8E44AD';
      default: return '#6B7280';
    }
  };

  return (
    <HealthcareSidebarLayout>
      <div className="page-inner-content" style={{ width: '100%', boxSizing: 'border-box' }}>
        <div
          style={{
            minHeight: '100vh',
            backgroundColor: '#f8f8f8',
            padding: '0',
            paddingBottom: '100px',
            width: '100%',
            boxSizing: 'border-box'
          }}
        >
          <div
            style={{
              background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
              padding: '32px',
              borderRadius: '0',
              marginBottom: '32px',
              color: 'white',
              boxShadow: '0 8px 32px rgba(142, 68, 173, 0.15)'
            }}
          >
            <h1 style={{ fontSize: '28px', fontWeight: '800', margin: 0 }}>My Appointments</h1>
            <p style={{ fontSize: '15px', opacity: 0.9, margin: '8px 0 0 0' }}>Manage your healthcare appointments</p>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div>Loading appointments...</div>
            </div>
          ) : appointments.length === 0 ? (
            <div
              style={{
                background: 'white',
                padding: '40px',
                borderRadius: '16px',
                textAlign: 'center',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              }}
            >
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📅</div>
              <h3 style={{ color: '#1a1a2e', marginBottom: '8px' }}>No appointments yet</h3>
              <p style={{ color: '#666', marginBottom: '20px' }}>Book your first appointment to get started</p>
              <button
                onClick={() => navigate('/healthcare/explore')}
                style={{
                  background: '#7B2FBE',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '99px',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                Find Doctors
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {appointments.map((appointment) => (
                <div
                  key={appointment.id}
                  style={{
                    background: 'white',
                    padding: '16px',
                    borderRadius: '16px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <h3
                      style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#1a1a2e',
                        margin: '0 0 4px 0',
                      }}
                    >
                      {appointment.doctor_name || appointment.doctorName || appointment.name || 'Doctor'}
                    </h3>
                    <p style={{ fontSize: '13px', color: '#666', margin: '0 0 8px 0' }}>{appointment.specialization}</p>
                    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#888' }}>
                      <span>📅 {appointment.booking_date || appointment.date}</span>
                      <span>🕐 {appointment.time_slot || appointment.time}</span>
                      <span>₹{appointment.fee || appointment.consultation_fee || 500}</span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                      <span
                        style={{
                          background: getStatusColor(appointment.status),
                          color: 'white',
                          padding: '4px 12px',
                          borderRadius: '99px',
                          fontSize: '11px',
                          fontWeight: '600',
                          textTransform: 'uppercase',
                        }}
                      >
                        {appointment.status}
                      </span>
                      {appointment.status === 'payment_pending' && (
                        <button
                          onClick={() => navigate(`/healthcare/payment/${appointment.id}`)}
                          style={{
                            background: '#8E44AD',
                            color: 'white',
                            border: 'none',
                            padding: '6px 12px',
                            borderRadius: '8px',
                            fontSize: '11px',
                            fontWeight: '600',
                            cursor: 'pointer'
                          }}
                        >
                          Pay Now
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <HealthcareBottomNav activeTab="my-care" />
        </div>
      </div>
    </HealthcareSidebarLayout>
  );
};

export default AppointmentsPage;
