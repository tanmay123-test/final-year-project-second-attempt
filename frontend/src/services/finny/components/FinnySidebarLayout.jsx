import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Home, PiggyBank, Calculator, Target, Brain } from 'lucide-react';
import './FinnySidebarLayout.css';
import FinnyBottomNav from './FinnyBottomNav';

const FinnySidebarLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActivePath = (prefixes) => {
    return prefixes.some((p) => location.pathname === p || location.pathname.startsWith(`${p}/`));
  };

  const isFinnyActive =
    location.pathname === '/finny' ||
    isActivePath(['/finny/quick', '/finny/summary', '/finny/analytics', '/finny/chat']);

  const navItems = [
    { key: 'finny', label: 'Finny', icon: Home, path: '/finny', active: isFinnyActive },
    {
      key: 'budget',
      label: 'Budget',
      icon: PiggyBank,
      path: '/finny/budget',
      active: isActivePath(['/finny/budget']),
    },
    {
      key: 'loan',
      label: 'Loan',
      icon: Calculator,
      path: '/finny/loan',
      active: isActivePath(['/finny/loan']),
    },
    {
      key: 'goal-jar',
      label: 'Goal Jar',
      icon: Target,
      path: '/finny/goals',
      active: isActivePath(['/finny/goals', '/finny/goal-jar']),
    },
    {
      key: 'ai-coach',
      label: 'AI Coach',
      icon: Brain,
      path: '/finny/ai-coach',
      // Some pages still use "/finny/coach"
      active: isActivePath(['/finny/ai-coach', '/finny/coach']),
    },
  ];

  return (
    <div className="finny-layout">
      <aside className="finny-layout-sidebar">
        <div className="finny-layout-sidebar-header">
          <div className="finny-layout-brand-title">Finny</div>
          <div className="finny-layout-brand-subtitle">Smart Tracker</div>
        </div>

        <nav className="finny-layout-sidebar-nav" aria-label="Finny navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                type="button"
                className={`finny-layout-sidebar-item ${item.active ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
                <Icon size={20} color={item.active ? '#F4B400' : '#6B7280'} />
                <span className="finny-layout-sidebar-label">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="finny-main-content">{children}</main>
      <FinnyBottomNav />
    </div>
  );
};

export default FinnySidebarLayout;

