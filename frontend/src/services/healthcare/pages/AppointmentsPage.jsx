import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import '../styles/healthcare-shared.css';

const AppointmentsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data for now
    const mockAppointments = [
      {
        id: 1,
        doctorName: 'Dr. Sarah Johnson',
        specialization: 'Cardiology',
        date: '2024-03-28',
        time: '10:00 AM',
        status: 'upcoming',
        fee: 800
      },
      {
        id: 2,
        doctorName: 'Dr. Michael Chen',
        specialization: 'Dermatology',
        date: '2024-03-25',
        time: '2:00 PM',
        status: 'completed',
        fee: 600
      }
    ];
    
    setTimeout(() => {
      setAppointments(mockAppointments);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'upcoming': return '#10B981';
      case 'completed': return '#6B7280';
      case 'cancelled': return '#EF4444';
      default: return '#6B7280';
    }
  };

  return (
    <HealthcareSidebarLayout>
      <div className="page-inner-content">
        <div
          style={{
            minHeight: '100vh',
            backgroundColor: '#f8f8f8',
            padding: '20px',
            paddingBottom: '80px',
            maxWidth: '900px',
            margin: '0 auto',
          }}
        >
          <div
            style={{
              background: 'linear-gradient(135deg, #7B2FBE 0%, #9B59B6 100%)',
              padding: '20px',
              borderRadius: '16px',
              marginBottom: '20px',
              color: 'white',
            }}
          >
            <h1 style={{ fontSize: '24px', fontWeight: '700', margin: 0 }}>My Appointments</h1>
            <p style={{ fontSize: '14px', opacity: 0.9, margin: '4px 0 0 0' }}>Manage your healthcare appointments</p>
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
                      {appointment.doctorName}
                    </h3>
                    <p style={{ fontSize: '13px', color: '#666', margin: '0 0 8px 0' }}>{appointment.specialization}</p>
                    <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#888' }}>
                      <span>📅 {appointment.date}</span>
                      <span>🕐 {appointment.time}</span>
                      <span>₹{appointment.fee}</span>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
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
