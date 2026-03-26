import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DoctorNavbar from '../components/DoctorNavbar';
import DoctorStatsCard from '../components/DoctorStatsCard';
import AppointmentCard from '../components/AppointmentCard';
import useDoctorAuth from '../hooks/useDoctorAuth';
import '../styles/DoctorDashboard.css';

const DoctorDashboard = () => {
  const { doctorToken, doctorInfo, loading: authLoading } = useDoctorAuth();
  const [stats, setStats] = useState({
    todays_patients: 0,
    pending_requests: 0,
    this_week: 0,
    revenue: 0
  });
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    if (doctorToken) {
      fetchDashboardData();
    }
  }, [doctorToken]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch dashboard stats
      const statsResponse = await fetch(`${import.meta.env.VITE_API_URL}/doctor/dashboard-stats`, {
        headers: {
          'Authorization': `Bearer ${doctorToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch today's schedule
      const scheduleResponse = await fetch(`${import.meta.env.VITE_API_URL}/doctor/todays-schedule`, {
        headers: {
          'Authorization': `Bearer ${doctorToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (scheduleResponse.ok) {
        const scheduleData = await scheduleResponse.json();
        setAppointments(scheduleData || []);
      }

      // Set online status from doctor info
      if (doctorInfo?.is_online !== undefined) {
        setIsOnline(doctorInfo.is_online);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleOnlineStatus = async () => {
    if (!doctorToken) return;

    try {
      const newStatus = !isOnline;
      
      // Optimistic update
      setIsOnline(newStatus);

      const response = await fetch(`${import.meta.env.VITE_API_URL}/doctor/toggle-online`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${doctorToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_online: newStatus })
      });

      if (!response.ok) {
        // Revert on error
        setIsOnline(!newStatus);
        console.error('Failed to update online status');
      }
    } catch (error) {
      // Revert on error
      setIsOnline(!isOnline);
      console.error('Error toggling online status:', error);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const getInitials = (name) => {
    return name ? name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'D';
  };

  const formatRevenue = (amount) => {
    if (amount >= 1000) {
      return `₹${(amount / 1000).toFixed(1)}K`;
    }
    return `₹${amount}`;
  };

  if (authLoading || loading) {
    return (
      <div className="doctor-dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="doctor-dashboard-container">
      <DoctorNavbar activeTab="dashboard" />
      
      <div className="doctor-dashboard-content">
        {/* Header Section with Purple Gradient */}
        <div 
          className="doctor-header"
          style={{
            background: 'linear-gradient(135deg, #7C3AED, #9333EA)',
            borderRadius: '20px',
            padding: '32px',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            marginBottom: '24px'
          }}
        >
          {/* Top Stats Cards (overlap with header) */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            marginBottom: '24px'
          }}>
            <DoctorStatsCard 
              icon="👥" 
              number={stats.todays_patients} 
              label="Today's Patients"
              isTopCard={true}
            />
            <DoctorStatsCard 
              icon="🕐" 
              number={stats.pending_requests} 
              label="Pending Requests"
              isTopCard={true}
            />
          </div>

          {/* Header Content */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: '16px'
          }}>
            <div>
              <div style={{
                fontSize: '14px',
                opacity: 0.9,
                marginBottom: '8px'
              }}>
                {getGreeting()} 👋
              </div>
              <div style={{
                fontSize: '32px',
                fontWeight: '700',
                marginBottom: '8px'
              }}>
                Dr. {doctorInfo?.name || 'User'}
              </div>
              <div style={{
                fontSize: '16px',
                opacity: 0.8
              }}>
                {doctorInfo?.specialization || 'General Practitioner'}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              {/* Online Toggle */}
              <button
                onClick={toggleOnlineStatus}
                className="online-toggle"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  borderRadius: '20px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                }}
              >
                <span style={{ fontSize: '16px' }}>
                  {isOnline ? '🟢' : '⚫'}
                </span>
                {isOnline ? 'Online' : 'Offline'}
              </button>

              {/* Avatar */}
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.2)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                {getInitials(doctorInfo?.name)}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Stats Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '16px',
          marginBottom: '32px',
          marginTop: '-40px', // Overlap with header
          position: 'relative',
          zIndex: 2
        }}>
          <DoctorStatsCard 
            icon="📅" 
            number={stats.this_week} 
            label="This Week"
            isTopCard={false}
          />
          <DoctorStatsCard 
            icon="📈" 
            number={formatRevenue(stats.revenue)} 
            label="Revenue"
            isTopCard={false}
          />
        </div>

        {/* Today's Schedule Section */}
        <div className="schedule-section" style={{
          background: 'white',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          border: '1px solid #f0f0f0'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#1a1a2e',
              margin: 0
            }}>
              Today's Schedule
            </h2>
            <Link 
              to="/doctor/appointments"
              style={{
                color: '#7C3AED',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              View All ›
            </Link>
          </div>

          {appointments.length > 0 ? (
            <div>
              {appointments.map((appointment) => (
                <AppointmentCard 
                  key={appointment.id} 
                  appointment={appointment}
                />
              ))}
            </div>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '40px 20px',
              color: '#6b7280'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📅</div>
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                No appointments today
              </h3>
              <p style={{ fontSize: '14px', margin: 0 }}>
                Enjoy your free time! Check back for new appointments.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DoctorDashboard;
