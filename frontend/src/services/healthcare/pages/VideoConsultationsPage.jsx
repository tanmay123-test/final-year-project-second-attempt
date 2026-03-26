import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import '../styles/VideoConsultations.css';
import '../styles/healthcare-shared.css';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';

const VideoConsultationsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [videoAppointments, setVideoAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  useEffect(() => {
    const fetchVideoAppointments = async () => {
      try {
        const res = await fetch('/user/appointments', { headers });
        const data = await res.json();
        
        // Filter only video appointments
        const videoOnly = (data.appointments || data || [])
          .filter(appointment => appointment.type === 'video' || appointment.appointment_type === 'video');
        
        setVideoAppointments(videoOnly);
      } catch (err) {
        console.error('Failed to fetch video appointments:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchVideoAppointments();
  }, [token]);

  const handleJoinCall = (appointmentId) => {
    // Navigate to video call room
    navigate(`/healthcare/video-call/${appointmentId}`);
  };

  return (
    <HealthcareSidebarLayout>
      <div className="page-inner-content">
        <div className="video-consultations-page">
          <div className="video-header">
            <div className="video-header-row">
              <span className="video-header-icon">🎥</span>
              <h1 className="video-header-title">Video Consultations</h1>
            </div>
            <p className="video-header-subtitle">Join live calls & view video appointments</p>
          </div>

          <div className="video-content">
            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading video appointments...</p>
              </div>
            ) : videoAppointments.length > 0 ? (
              <div className="video-appointments-list">
                {videoAppointments.map((appointment) => (
                  <div key={appointment.id} className="video-appointment-card">
                    <div className="appointment-info">
                      <div className="appointment-doctor">
                        <span className="doctor-avatar">
                          {appointment.doctor_name ? appointment.doctor_name[0].toUpperCase() : 'D'}
                        </span>
                        <div className="doctor-details">
                          <h3>{appointment.doctor_name || 'Doctor'}</h3>
                          <p>{appointment.specialization || 'Consultation'}</p>
                        </div>
                      </div>
                      <div className="appointment-time">
                        <span className="time-label">Scheduled Time</span>
                        <span className="time-value">{appointment.appointment_time || appointment.time || 'Not scheduled'}</span>
                      </div>
                      <div className="appointment-status">
                        <span className={`status-badge ${appointment.status || 'pending'}`}>{appointment.status || 'Pending'}</span>
                      </div>
                    </div>
                    <div className="appointment-actions">
                      {appointment.status === 'accepted' || appointment.status === 'confirmed' ? (
                        <button className="join-call-btn" onClick={() => handleJoinCall(appointment.id)}>
                          Join Call
                        </button>
                      ) : (
                        <button className="view-details-btn" disabled>
                          {appointment.status === 'pending' ? 'Waiting for confirmation' : 'Call ended'}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🎥</div>
                <h3>No Video Consultations</h3>
                <p>You don&apos;t have any video appointments scheduled.</p>
                <button className="book-consultation-btn" onClick={() => navigate('/healthcare/explore')}>
                  Book Video Consultation
                </button>
              </div>
            )}
          </div>

          <HealthcareBottomNav activeTab="my-care" />
        </div>
      </div>
    </HealthcareSidebarLayout>
  );
};

export default VideoConsultationsPage;
