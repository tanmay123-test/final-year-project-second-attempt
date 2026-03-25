import React from 'react';
import { User, CreditCard, Bell, Shield, CircleHelp, LogOut, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';

const UserProfile = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { icon: <User size={20} />, label: 'Personal Information' },
    { icon: <CreditCard size={20} />, label: 'Payment Methods' },
    { icon: <Bell size={20} />, label: 'Notifications' },
    { icon: <Shield size={20} />, label: 'Security & Privacy' },
    { icon: <CircleHelp size={20} />, label: 'Help Center' },
  ];

  return (
    <div className="hk-page-container" style={{ backgroundColor: '#F9FAFB', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#8E44AD', padding: '40px 20px 80px 20px', color: 'white' }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Profile</h1>
      </div>

      <div style={{ padding: '0 20px', marginTop: '-60px' }}>
        {/* Profile Card */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '20px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: '#F3E5F5', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8E44AD', fontSize: '24px', fontWeight: 'bold' }}>
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div>
            <h2 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 'bold', color: '#1F2937' }}>{user?.username || 'User'}</h2>
            <p style={{ margin: 0, fontSize: '14px', color: '#6B7280' }}>{user?.email || '+91 98765 43210'}</p>
          </div>
        </div>

        {/* Menu Items */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '8px 0', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
          {menuItems.map((item, index) => (
            <div 
              key={index} 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between', 
                padding: '16px 20px', 
                borderBottom: index < menuItems.length - 1 ? '1px solid #F3F4F6' : 'none',
                cursor: 'pointer'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: '#374151' }}>
                <div style={{ color: '#8E44AD' }}>{item.icon}</div>
                <span style={{ fontSize: '14px', fontWeight: '500' }}>{item.label}</span>
              </div>
              <ChevronRight size={16} color="#9CA3AF" />
            </div>
          ))}
        </div>

        {/* Logout */}
        <button 
          onClick={handleLogout}
          style={{ 
            marginTop: '24px', 
            width: '100%', 
            padding: '16px', 
            borderRadius: '16px', 
            backgroundColor: '#FEE2E2', 
            color: '#DC2626', 
            border: 'none', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: '8px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          <LogOut size={20} />
          Log Out
        </button>
      </div>
    </div>
  );
};

export default UserProfile;
