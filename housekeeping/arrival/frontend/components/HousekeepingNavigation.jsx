import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Bot, Search, Calendar, User } from 'lucide-react';
import './HousekeepingNavigation.css';

const HousekeepingNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: Home, label: 'Home', path: '/housekeeping/home' },
    { icon: Bot, label: 'AI Care', path: '/housekeeping/ai-chat' },
    { icon: Search, label: 'Explore', path: '/housekeeping/explore' },
    { icon: Calendar, label: 'Bookings', path: '/housekeeping/bookings' },
    { icon: User, label: 'Profile', path: '/housekeeping/profile' },
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
          >
            <item.icon size={24} strokeWidth={isActive ? 2.5 : 2} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default HousekeepingNavigation;
