import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './FinnyBottomNav.css';

const navItems = [
  { icon: '🏠', label: 'Finny', path: '/finny' },
  { icon: '💰', label: 'Budget', path: '/finny/budget' },
  { icon: '📊', label: 'Loan', path: '/finny/loan' },
  { icon: '🎯', label: 'Goal Jar', path: '/finny/goals' },
  { icon: '🤖', label: 'AI Coach', path: '/finny/ai-coach' },
];

const FinnyBottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(`${path}/`);

  return (
    <div className="finny-bottom-nav-shared">
      {navItems.map((item) => {
        const active = isActive(item.path);
        return (
          <div
            key={item.path}
            className={`fnav-item ${active ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="fnav-icon">{item.icon}</span>
            <span className={`fnav-label ${active ? 'active' : ''}`}>{item.label}</span>
            {active && <div className="fnav-active-dot" />}
          </div>
        );
      })}
    </div>
  );
};

export default FinnyBottomNav;

