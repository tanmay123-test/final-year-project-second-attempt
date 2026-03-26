import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './HealthcareSidebarLayout.css';

const HealthcareSidebarLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { id: 'home', icon: '🏠', label: 'Home', path: '/healthcare/home' },
    { id: 'ai-care', icon: '🤖', label: 'AI Care', path: '/healthcare/ai-care' },
    { id: 'explore', icon: '🔍', label: 'Explore', path: '/healthcare/explore' },
    { id: 'my-care', icon: '❤️', label: 'My Care', path: '/healthcare/my-care' },
    { id: 'profile', icon: '👤', label: 'Profile', path: '/healthcare/profile' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="hc-layout">
      <aside className="hc-sidebar">
        <div className="hc-sidebar-brand">
          <span className="hc-brand-icon">🏥</span>
          <span className="hc-brand-text">HealthCare</span>
        </div>

        <nav className="hc-sidebar-nav">
          {navItems.map((item) => (
            <div
              key={item.id}
              className={`hc-sidebar-item ${isActive(item.path) ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') navigate(item.path);
              }}
            >
              <span className="hc-sidebar-icon">{item.icon}</span>
              <span className="hc-sidebar-label">{item.label}</span>
              {isActive(item.path) && <span className="hc-active-indicator" />}
            </div>
          ))}
        </nav>

        <div className="hc-sidebar-footer">
          <div className="hc-sidebar-footer-text">HealthCare v1.0</div>
        </div>
      </aside>

      <main className="hc-main-content">{children}</main>
    </div>
  );
};

export default HealthcareSidebarLayout;

