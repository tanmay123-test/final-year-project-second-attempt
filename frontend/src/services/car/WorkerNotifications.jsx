import React, { useState, useEffect, useRef } from 'react';
import { Bell, CheckCircle, AlertCircle, X, Pause, Play } from 'lucide-react';

const WorkerNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    // Fetch notifications for the logged-in worker
    const fetchNotifications = async () => {
      try {
        const token = localStorage.getItem('workerToken');
        if (!token) return;

        const response = await fetch('http://127.0.0.1:5000/api/worker/notifications', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setNotifications(data.notifications || []);
        }
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      }
    };

    fetchNotifications();

    // Set up real-time notifications (polling every 30 seconds)
    const interval = setInterval(fetchNotifications, 30000);

    return () => clearInterval(interval);
  }, []);

  const markAsRead = async (notificationId) => {
    try {
      const token = localStorage.getItem('workerToken');
      const response = await fetch(`http://127.0.0.1:5000/api/worker/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, read: true }
              : notif
          )
        );
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'approval':
        return <CheckCircle size={20} className="approval-icon" />;
      case 'task_assigned':
        return <Bell size={20} className="task-icon" />;
      case 'payment':
        return <CheckCircle size={20} className="payment-icon" />;
      default:
        return <AlertCircle size={20} className="default-icon" />;
    }
  };

  const getNotificationStyle = (type) => {
    switch (type) {
      case 'approval':
        return 'notification approval';
      case 'task_assigned':
        return 'notification task';
      case 'payment':
        return 'notification payment';
      default:
        return 'notification default';
    }
  };

  return (
    <div className="worker-notifications">
      {/* Notification Bell Icon */}
      <div className="notification-bell" onClick={() => setShowNotifications(!showNotifications)}>
        <Bell size={24} />
        {notifications.filter(n => !n.read).length > 0 && (
          <span className="notification-badge">{notifications.filter(n => !n.read).length}</span>
        )}
      </div>

      {/* Notifications Panel */}
      {showNotifications && (
        <div className="notifications-overlay">
          <div className="notifications-panel">
            <div className="notifications-header">
              <h3>🔔 Notifications</h3>
              <button 
                className="close-notifications"
                onClick={() => setShowNotifications(false)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="notifications-list">
              {notifications.length === 0 ? (
                <div className="no-notifications">
                  <p>No notifications yet</p>
                </div>
              ) : (
                notifications.map(notification => (
                  <div 
                    key={notification.id} 
                    className={`notification-item ${getNotificationStyle(notification.type)} ${notification.read ? 'read' : 'unread'}`}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                  >
                    <div className="notification-content">
                      <div className="notification-icon-wrapper">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="notification-text">
                        <h4>{notification.title}</h4>
                        <p>{notification.message}</p>
                        <span className="notification-time">
                          {new Date(notification.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    {!notification.read && (
                      <div className="unread-indicator"></div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .worker-notifications {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 1000;
        }

        .notification-bell {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
          transition: all 0.2s;
          position: relative;
        }

        .notification-bell:hover {
          transform: scale(1.1);
        }

        .notification-badge {
          position: absolute;
          top: -5px;
          right: -5px;
          background: #ff4757;
          color: white;
          border-radius: 50%;
          width: 20px;
          height: 20px;
          font-size: 0.75rem;
          font-weight: bold;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .notifications-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1001;
        }

        .notifications-panel {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          max-width: 400px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
          animation: slideIn 0.3s ease-out;
        }

        .notifications-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #e1e5e9;
        }

        .notifications-header h3 {
          margin: 0;
          color: #1a1a1a;
          font-size: 1.2rem;
          font-weight: 600;
        }

        .close-notifications {
          background: none;
          border: none;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 8px;
          color: #666;
          transition: all 0.2s;
        }

        .close-notifications:hover {
          background: #f1f5f5;
        }

        .notifications-list {
          max-height: 60vh;
          overflow-y: auto;
        }

        .no-notifications {
          text-align: center;
          padding: 2rem;
          color: #666;
        }

        .notification-item {
          display: flex;
          align-items: flex-start;
          padding: 1rem;
          border-radius: 12px;
          margin-bottom: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
          position: relative;
        }

        .notification-item:hover {
          background: #f8f9fa;
          transform: translateX(-5px);
        }

        .notification-item.unread {
          background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
          border-left: 4px solid #667eea;
        }

        .notification-item.read {
          background: #f8f9fa;
          border-left: 4px solid transparent;
        }

        .notification-content {
          flex: 1;
          margin-left: 1rem;
        }

        .notification-icon-wrapper {
          flex-shrink: 0;
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 8px;
        }

        .notification-icon.approval {
          color: #10b981;
          background: #d4edda;
        }

        .notification-icon.task {
          color: #3b82f6;
          background: #dbeafe;
        }

        .notification-icon.payment {
          color: #059669;
          background: #d4edda;
        }

        .notification-icon.default {
          color: #666;
          background: #e1e5e9;
        }

        .notification-text h4 {
          margin: 0 0 0.5rem;
          color: #1a1a1a;
          font-size: 1rem;
          font-weight: 600;
        }

        .notification-text p {
          margin: 0 0 0.5rem;
          color: #666;
          font-size: 0.9rem;
          line-height: 1.4;
        }

        .notification-time {
          font-size: 0.8rem;
          color: #999;
          margin-top: 0.5rem;
        }

        .unread-indicator {
          position: absolute;
          top: 20px;
          left: 20px;
          width: 8px;
          height: 8px;
          background: #ff4757;
          border-radius: 50%;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default WorkerNotifications;
