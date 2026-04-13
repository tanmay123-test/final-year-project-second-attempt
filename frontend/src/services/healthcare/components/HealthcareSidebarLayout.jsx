import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Bot, Search, Heart, User, Stethoscope, Sparkles } from 'lucide-react';
import './HealthcareSidebarLayout.css';

const HealthcareSidebarLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { id: 'home', icon: Home, label: 'Home', path: '/healthcare/home' },
    { id: 'ai-care', icon: Bot, label: 'AI Care', path: '/healthcare/ai-care' },
    { id: 'appointments', icon: Search, label: 'Appointments', path: '/healthcare/appointments' },
    { id: 'my-care', icon: Heart, label: 'My Care', path: '/healthcare/my-care' },
    { id: 'profile', icon: User, label: 'Profile', path: '/healthcare/profile' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="hc-layout">
      <aside className="hc-sidebar">
        <div className="hc-sidebar-brand" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          <div className="hc-brand-icon">
            <Stethoscope size={24} color="white" />
          </div>
          <span className="hc-brand-text">ExpertEase</span>
        </div>

        <nav className="hc-sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
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
                <Icon size={20} className="hc-sidebar-icon" />
                <span className="hc-sidebar-label">{item.label}</span>
                {isActive(item.path) && <span className="hc-active-indicator" />}
              </div>
            );
          })}
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

