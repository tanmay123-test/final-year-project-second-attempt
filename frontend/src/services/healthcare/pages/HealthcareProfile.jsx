import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import '../styles/HealthcareProfile.css';
import '../styles/healthcare-shared.css';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';

const HealthcareProfile = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [userData, setUserData] = useState(null);
  const [stats, setStats] = useState({
    total: 0, completed: 0, upcoming: 0
  });
  const [notifEnabled, setNotifEnabled] = useState(true);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // Format date function
  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString(
      'en-IN', { month: 'long', year: 'numeric' }
    );
  };

  // Fetch user profile
  const fetchUserProfile = async () => {
    try {
      // First try auth context
      if (user) {
        setUserData({
          name: user.name,
          username: user.username,
          email: user.email,
          is_verified: user.is_verified
        });
        return;
      }
      
      // Fallback: fetch from API
      const res = await fetch('/user/profile', { headers });
      const data = await res.json();
      setUserData({
        name: data.name,
        username: data.username,
        email: data.email,
        is_verified: data.is_verified
      });
    } catch (err) {
      console.error('Profile fetch failed:', err);
    }
  };

  // Fetch appointment stats
  const fetchStats = async () => {
    try {
      const res = await fetch('/user/appointments', { headers });
      const data = await res.json();
      const appointments = data.appointments || data || [];
      
      setStats({
        total: appointments.length,
        completed: appointments.filter(a => a.status === 'completed').length,
        upcoming: appointments.filter(a => 
          a.status === 'pending' || 
          a.status === 'accepted' ||
          a.status === 'confirmed'
        ).length
      });
    } catch (err) {
      console.error('Stats fetch failed:', err);
      setStats({ total: 0, completed: 0, upcoming: 0 });
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await fetchUserProfile();
      await fetchStats();
      setLoading(false);
    };
    loadData();
  }, [user, token]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    if (logout) logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <HealthcareSidebarLayout>
        <div className="profile-page">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading profile...</p>
          </div>
        </div>
      </HealthcareSidebarLayout>
    );
  }

  const getUserInitial = (name) => {
    if (!name) return 'U';
    return name.charAt(0).toUpperCase();
  };

  return (
    <HealthcareSidebarLayout>
      <div className="profile-page" style={{ width: '100%', maxWidth: 'none', margin: 0, padding: '24px', boxSizing: 'border-box' }}>
        <div className="profile-header" style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)', borderRadius: '24px', padding: '32px', color: 'white', boxShadow: '0 8px 32px rgba(142, 68, 173, 0.15)', marginBottom: '32px' }}>
          <h1 className="profile-header-title" style={{ color: 'white', margin: 0 }}>My Profile</h1>
        </div>

        <div className="profile-desktop-grid">
          <div className="profile-left-col">
            <div className="user-info-card">
              <div className="user-avatar-circle">{userData?.name ? getUserInitial(userData.name) : '👤'}</div>
              <div className="user-info-content">
                <div className="user-display-name">{userData?.name || 'User'}</div>
                <div className="user-username">@{userData?.username || 'username'}</div>
                <div className="user-email-text">{userData?.email || 'email@example.com'}</div>
              </div>
              <button className="edit-icon-btn" onClick={() => navigate('/healthcare/profile/edit')}>
                ✏️
              </button>
            </div>

            <div className="stats-row-card">
              <div className="stat-col">
                <span className="stat-icon">📅</span>
                <span className="stat-number">{stats.total}</span>
                <span className="stat-label">Total</span>
              </div>
              <div className="stat-col">
                <span className="stat-icon">✅</span>
                <span className="stat-number">{stats.completed}</span>
                <span className="stat-label">Completed</span>
              </div>
              <div className="stat-col">
                <span className="stat-icon">🕐</span>
                <span className="stat-number">{stats.upcoming}</span>
                <span className="stat-label">Upcoming</span>
              </div>
            </div>
          </div>

          <div className="profile-right-col">
            <div className="profile-tabs">
              <button
                className={`profile-tab ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                Overview
              </button>
              <button
                className={`profile-tab ${activeTab === 'medical' ? 'active' : ''}`}
                onClick={() => setActiveTab('medical')}
              >
                Medical
              </button>
              <button
                className={`profile-tab ${activeTab === 'settings' ? 'active' : ''}`}
                onClick={() => setActiveTab('settings')}
              >
                Settings
              </button>
            </div>

            <div className="profile-tab-content">
              {activeTab === 'overview' && (
                <div className="overview-card">
                  <h3 className="overview-section-title">Personal Information</h3>

                  <div className="info-row">
                    <span className="info-label">Name</span>
                    <span className="info-value">{userData?.name || 'N/A'}</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">Username</span>
                    <span className="info-value">@{userData?.username || 'N/A'}</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">Email</span>
                    <span className="info-value">{userData?.email || 'N/A'}</span>
                  </div>

                  <div className="info-row">
                    <span className="info-label">Account Status</span>
                    <span className="info-value">{userData?.is_verified ? '✅ Verified' : '⏳ Not Verified'}</span>
                  </div>
                </div>
              )}

              {activeTab === 'medical' && (
                <div className="overview-card">
                  <h3 className="overview-section-title">Medical Information</h3>

                  <div className="medical-empty-state">
                    <div className="medical-empty-icon">🏥</div>
                    <p>No medical information available yet.</p>
                    <small>Medical details can be added by your doctor after consultation.</small>
                  </div>
                </div>
              )}

              {activeTab === 'settings' && (
                <div className="overview-card">
                  <h3 className="overview-section-title">Settings</h3>

                  <div className="settings-item" onClick={() => setNotifEnabled(!notifEnabled)}>
                    <div className="settings-icon-box">
                      <span>🔔</span>
                    </div>
                    <div className="settings-item-content">
                      <div className="settings-item-title">Notifications</div>
                      <div className="settings-item-subtitle">Manage alerts & reminders</div>
                    </div>
                    <div className="settings-toggle">
                      <input
                        type="checkbox"
                        checked={notifEnabled}
                        onChange={() => setNotifEnabled(!notifEnabled)}
                        className="toggle-input"
                      />
                      <span className={`toggle-slider ${notifEnabled ? 'active' : ''}`}></span>
                    </div>
                  </div>

                  <div className="settings-item">
                    <div className="settings-icon-box">
                      <span>🔒</span>
                    </div>
                    <div className="settings-item-content">
                      <div className="settings-item-title">Privacy</div>
                      <div className="settings-item-subtitle">Data & privacy settings</div>
                    </div>
                    <span className="settings-arrow">›</span>
                  </div>

                  <div className="settings-item">
                    <div className="settings-icon-box">
                      <span>❓</span>
                    </div>
                    <div className="settings-item-content">
                      <div className="settings-item-title">Help & Support</div>
                      <div className="settings-item-subtitle">FAQs & contact support</div>
                    </div>
                    <span className="settings-arrow">›</span>
                  </div>

                  <div className="settings-item" onClick={handleLogout}>
                    <div className="settings-icon-box danger">
                      <span>🚪</span>
                    </div>
                    <div className="settings-item-content">
                      <div className="settings-item-title danger">Logout</div>
                      <div className="settings-item-subtitle">Sign out of your account</div>
                    </div>
                    <span className="settings-arrow danger">›</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <HealthcareBottomNav activeTab="profile" />
      </div>
    </HealthcareSidebarLayout>
  );
};

export default HealthcareProfile;
