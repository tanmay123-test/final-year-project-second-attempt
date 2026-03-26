import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import '../styles/MyCareScreen.css';
import '../styles/healthcare-shared.css';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';

const MyCareScreen = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [appointmentCount, setAppointmentCount] = useState(0);
  
  // Auth headers
  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // Fetch appointment count
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const res = await fetch('/user/appointments', {
          headers: {
            'Authorization': `Bearer ${token}` 
          }
        });
        const data = await res.json();
        const upcoming = (data.appointments || data || [])
          .filter(a => 
            a.status === 'pending' || 
            a.status === 'accepted' ||
            a.status === 'confirmed'
          ).length;
        setAppointmentCount(upcoming);
      } catch (err) {
        console.error('Failed to fetch appointment count:', err);
      }
    };
    fetchCount();
  }, [token]);

  return (
    <HealthcareSidebarLayout>
      <div className="page-inner-content">
        <div className="my-care-screen my-care-page">
          <div className="my-care-header">
            <div className="my-care-header-row">
              <span className="my-care-header-icon">♡</span>
              <h1 className="my-care-header-title">My Care</h1>
            </div>
            <p className="my-care-header-subtitle">Manage your appointments & consultations</p>
          </div>

          <div className="my-care-menu-container">
            <div className="my-care-menu-item" onClick={() => navigate('/healthcare/appointments')}>
              <div className="menu-icon-box">
                <span className="menu-icon">📅</span>
                {appointmentCount > 0 && <span className="appointment-badge">{appointmentCount}</span>}
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">📅 My Appointments</div>
                <div className="menu-item-subtitle">View, manage & cancel appointments</div>
              </div>
              <span className="menu-item-arrow">›</span>
            </div>

            <div className="menu-divider"></div>

            <div className="my-care-menu-item" onClick={() => navigate('/healthcare/video-consultations')}>
              <div className="menu-icon-box">
                <span className="menu-icon">🎥</span>
              </div>
              <div className="menu-item-content">
                <div className="menu-item-title">🎥 Video Consultations</div>
                <div className="menu-item-subtitle">Join live calls & view video appointments</div>
              </div>
              <span className="menu-item-arrow">›</span>
            </div>
          </div>

          <HealthcareBottomNav activeTab="my-care" />
        </div>
      </div>
    </HealthcareSidebarLayout>
  );
};

export default MyCareScreen;
