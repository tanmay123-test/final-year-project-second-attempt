import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const DoctorNavbar = ({ activeTab = 'dashboard' }) => {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);
  const location = useLocation();

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const navItems = [
    { id: 'dashboard', icon: '🏠', label: 'Dashboard', path: '/doctor/dashboard' },
    { id: 'availability', icon: '📅', label: 'Availability', path: '/doctor/availability' },
    { id: 'requests', icon: '📋', label: 'Requests', path: '/doctor/requests' },
    { id: 'appointments', icon: '🗓️', label: 'Appointments', path: '/doctor/appointments' },
    { id: 'profile', icon: '👤', label: 'Profile', path: '/doctor/profile' }
  ];

  if (isMobile) {
    // Mobile Bottom Navigation
    return (
      <div 
        className="doctor-bottom-nav"
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          background: 'white',
          borderTop: '1px solid #e5e7eb',
          display: 'flex',
          height: '65px',
          zIndex: 9999,
          boxShadow: '0 -2px 8px rgba(0,0,0,0.08)'
        }}
      >
        {navItems.map((item) => (
          <Link
            key={item.id}
            to={item.path}
            className={`nav-tab ${activeTab === item.id ? 'active' : ''}`}
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              textDecoration: 'none',
              fontSize: '10px',
              color: activeTab === item.id ? '#7C3AED' : '#9ca3af',
              border: 'none',
              background: 'none',
              transition: 'color 0.2s ease',
              cursor: 'pointer'
            }}
          >
            <span className="nav-tab-icon" style={{ fontSize: '20px' }}>
              {item.icon}
            </span>
            <span className="nav-tab-label">
              {item.label}
            </span>
          </Link>
        ))}
      </div>
    );
  }

  // Desktop Sidebar Navigation
  return (
    <div 
      className="doctor-sidebar"
      style={{
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        width: '260px',
        background: 'white',
        borderRight: '1px solid #e5e7eb',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 9999,
        boxShadow: '2px 0 8px rgba(0,0,0,0.06)'
      }}
    >
      {/* Logo/Brand */}
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid #f0f0f0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #7C3AED, #9333EA)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: '700',
            fontSize: '18px'
          }}>
            E
          </div>
          <div>
            <div style={{
              fontSize: '16px',
              fontWeight: '700',
              color: '#1a1a2e'
            }}>
              Expertease
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6b7280'
            }}>
              Doctor Portal
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Items */}
      <div style={{ flex: 1, padding: '20px 0' }}>
        {navItems.map((item) => (
          <Link
            key={item.id}
            to={item.path}
            className={`sidebar-nav-item ${activeTab === item.id ? 'active' : ''}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '12px 20px',
              textDecoration: 'none',
              color: activeTab === item.id ? '#7C3AED' : '#6b7280',
              background: activeTab === item.id ? '#EDE9FE' : 'transparent',
              borderLeft: activeTab === item.id ? '3px solid #7C3AED' : '3px solid transparent',
              transition: 'all 0.2s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== item.id) {
                e.currentTarget.style.background = '#f9fafb';
                e.currentTarget.style.color = '#374151';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== item.id) {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = '#6b7280';
              }
            }}
          >
            <span style={{ fontSize: '20px' }}>
              {item.icon}
            </span>
            <span style={{
              fontSize: '14px',
              fontWeight: '500'
            }}>
              {item.label}
            </span>
          </Link>
        ))}
      </div>

      {/* User Info Footer */}
      <div style={{
        padding: '20px',
        borderTop: '1px solid #f0f0f0'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: '#EDE9FE',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#7C3AED',
            fontWeight: '600',
            fontSize: '14px'
          }}>
            D
          </div>
          <div style={{ flex: 1 }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#1a1a2e'
            }}>
              Dr. User
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6b7280'
            }}>
              Online
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorNavbar;
