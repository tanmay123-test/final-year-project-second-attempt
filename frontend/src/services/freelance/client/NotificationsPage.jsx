import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, CheckCircle, MessageSquare, DollarSign, Clock, Star, Trash2, X } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const NotificationsPage = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/freelance/notifications', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(response.data.notifications || []);
    } catch (err) {
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/notifications/read', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchNotifications();
    } catch (err) {
      console.error('Error marking notifications as read:', err);
    }
  };

  const getTimeAgo = (dateString) => {
    const now = new Date();
    const past = new Date(dateString);
    const diffInMs = now - past;
    const diffInMins = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMins / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMins < 1) return 'Just now';
    if (diffInMins < 60) return `${diffInMins} mins ago`;
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    return `${diffInDays} days ago`;
  };

  const getNotifIcon = (type) => {
    switch (type) {
      case 'PROPOSAL_ACCEPTED': return { icon: CheckCircle, color: '#10b981', bg: '#f0fdf4' };
      case 'NEW_MESSAGE': return { icon: MessageSquare, color: '#3b82f6', bg: '#eff6ff' };
      case 'PAYMENT_RELEASED': return { icon: DollarSign, color: '#10b981', bg: '#f0fdf4' };
      case 'MILESTONE_SUBMITTED': return { icon: Clock, color: '#f59e0b', bg: '#fffbeb' };
      case 'NEW_REVIEW': return { icon: Star, color: '#f59e0b', bg: '#fffbeb' };
      default: return { icon: Bell, color: '#9B59B6', bg: '#f5f3ff' };
    }
  };

  if (loading && notifications.length === 0) return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Loading notifications...</p>
    </div>
  );

  return (
    <div className="project-detail-container" style={{ maxWidth: '800px' }}>
      <button className="back-btn" onClick={() => navigate(-1)}>
        <ArrowLeft size={18} /> Back
      </button>

      <header className="detail-header" style={{ marginBottom: '2rem' }}>
        <div className="header-main">
          <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>Notifications</h1>
          <p style={{ color: '#6b7280' }}>Stay updated with your latest freelance activities</p>
        </div>
        {notifications.length > 0 && (
          <button className="action-btn-outline" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }} onClick={markAsRead}>
            <CheckCircle size={16} /> Mark all read
          </button>
        )}
      </header>

      <div className="info-card" style={{ padding: 0, overflow: 'hidden' }}>
        {notifications.length === 0 ? (
          <div className="empty-state-dashboard" style={{ border: 'none', padding: '5rem 2rem' }}>
            <Bell size={60} color="#cbd5e1" style={{ marginBottom: '1.5rem' }} />
            <h3>No notifications yet</h3>
            <p style={{ color: '#9ca3af', marginTop: '0.5rem' }}>We'll notify you when something important happens.</p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map((notif, index) => {
              const config = getNotifIcon(notif.type);
              return (
                <div 
                  key={notif.id || index} 
                  className={`notification-item ${notif.is_read === 0 ? 'unread' : ''}`}
                  style={{ 
                    display: 'flex', gap: '1.2rem', padding: '1.5rem', 
                    borderBottom: index === notifications.length - 1 ? 'none' : '1px solid #f3f4f6',
                    backgroundColor: notif.is_read === 0 ? '#f5f3ff33' : 'transparent',
                    position: 'relative'
                  }}
                >
                  <div className="notif-icon-circle" style={{ 
                    backgroundColor: config.bg, color: config.color, width: '48px', height: '48px',
                    flexShrink: 0, borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <config.icon size={22} />
                  </div>
                  <div className="notif-content" style={{ flex: 1 }}>
                    <p style={{ fontSize: '1rem', fontWeight: notif.is_read === 0 ? 700 : 500, color: '#111827', marginBottom: '0.4rem', lineHeight: 1.4 }}>
                      {notif.message}
                    </p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <span style={{ fontSize: '0.85rem', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <Clock size={12} /> {getTimeAgo(notif.created_at)}
                      </span>
                      {notif.is_read === 0 && (
                        <span style={{ fontSize: '0.75rem', color: '#9B59B6', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#9B59B6' }}></div> New
                        </span>
                      )}
                    </div>
                  </div>
                  {notif.is_read === 0 && (
                    <div className="unread-dot" style={{ 
                      width: '10px', height: '10px', background: '#9B59B6', borderRadius: '50%',
                      position: 'absolute', right: '1.5rem', top: '2rem'
                    }}></div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationsPage;
