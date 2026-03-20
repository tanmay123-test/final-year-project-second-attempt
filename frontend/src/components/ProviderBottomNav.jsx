import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { LayoutGrid, Calendar, Clock, Wallet, User } from 'lucide-react';
import './HousekeepingNavigation.css'; // Reuse existing CSS

const ProviderBottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: LayoutGrid, label: 'Dashboard', path: '/worker/housekeeping/dashboard' },
    { icon: Calendar, label: 'Schedule', path: '/worker/housekeeping/schedule' },
    { icon: Clock, label: 'Availability', path: '/worker/housekeeping/availability' },
    { icon: Wallet, label: 'Earnings', path: '/worker/housekeeping/earnings' },
    { icon: User, label: 'Profile', path: '/worker/housekeeping/profile' },
  ];

  return (
    <div className="hk-bottom-nav">
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        return (
          <button 
            key={item.label} 
            className={`hk-nav-item ${isActive ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
            style={{
                color: isActive ? '#8E44AD' : '#6B7280', // Purple for active
                fontWeight: isActive ? '600' : '400'
            }}
          >
            <item.icon size={24} strokeWidth={isActive ? 2.5 : 2} color={isActive ? '#8E44AD' : '#6B7280'} />
            <span style={{ fontSize: '10px', marginTop: '4px' }}>{item.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default ProviderBottomNav;
