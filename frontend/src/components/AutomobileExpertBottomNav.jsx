import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  Home, 
  Wrench, 
  Settings, 
  MessageCircle, 
  DollarSign, 
  HelpCircle 
} from 'lucide-react';

const AutomobileExpertBottomNav = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const navItems = [
    {
      path: '/worker/car/automobile-expert/homepage',
      icon: Home,
      label: 'Dashboard',
      id: 'dashboard'
    },
    {
      path: '/worker/car/automobile-expert/requests',
      icon: Wrench,
      label: 'Consultation Requests Queue',
      id: 'requests'
    },
    {
      path: '/worker/car/automobile-expert/active',
      icon: MessageCircle,
      label: 'Active Consultation (Chat/Call)',
      id: 'active'
    },
    {
      path: '/worker/car/automobile-expert/consultation-menu',
      icon: DollarSign,
      label: 'Consultation History & Performance',
      id: 'history'
    },
    {
      path: '/worker/car/automobile-expert/report-user',
      icon: HelpCircle,
      label: 'Report User',
      id: 'report'
    },
    {
      path: '/worker/car/automobile-expert/queue-status',
      icon: Settings,
      label: 'Queue Status',
      id: 'queue'
    }
  ];

  return (
    <div style={{
      position: 'fixed',
      bottom: '0',
      left: '0',
      right: '0',
      backgroundColor: 'white',
      borderTop: '1px solid #e5e7eb',
      padding: '8px 0',
      zIndex: 1000,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        maxWidth: '600px',
        margin: '0 auto'
      }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.path);
          
          return (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              style={{
                background: 'none',
                border: 'none',
                padding: '8px 4px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '2px',
                minWidth: '50px',
                transition: 'all 0.2s ease',
                color: active ? '#8b5cf6' : '#9ca3af'
              }}
              onMouseOver={(e) => {
                if (!active) {
                  e.target.style.color = '#8b5cf6';
                  e.target.style.transform = 'translateY(-1px)';
                }
              }}
              onMouseOut={(e) => {
                if (!active) {
                  e.target.style.color = '#9ca3af';
                  e.target.style.transform = 'translateY(0)';
                }
              }}
            >
              <Icon 
                size={20} 
                style={{ 
                  strokeWidth: active ? 2.5 : 2,
                  transition: 'all 0.2s ease'
                }} 
              />
              <span style={{
                fontSize: '10px',
                fontWeight: active ? '600' : '500',
                textAlign: 'center',
                lineHeight: '1.2',
                maxWidth: '60px',
                wordWrap: 'break-word'
              }}>
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default AutomobileExpertBottomNav;
