import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Bot, Search, Calendar, User, Briefcase, Sparkles } from 'lucide-react';

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

  // Mobile bottom navigation
  const MobileNav = () => (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      background: 'white',
      display: 'flex',
      justifyContent: 'space-around',
      padding: '12px 0',
      boxShadow: '0 -2px 10px rgba(0,0,0,0.05)',
      borderTop: '1px solid #f0f0f0',
      zIndex: 9999
    }}>
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        return (
          <button
            key={item.label}
            onClick={() => navigate(item.path)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              border: 'none',
              background: 'none',
              color: isActive ? '#8E44AD' : '#9ca3af',
              fontSize: '10px',
              gap: '4px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              padding: '6px 12px',
              borderRadius: '12px',
              minWidth: '60px'
            }}
          >
            <item.icon size={20} strokeWidth={isActive ? 2.5 : 2} />
            <span style={{ fontWeight: '600' }}>{item.label}</span>
          </button>
        );
      })}
      
      {/* Freelance Hub Button - Always Visible */}
      <button
        onClick={() => navigate('/freelance/home')}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          border: 'none',
          background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
          color: 'white',
          fontSize: '9px',
          gap: '3px',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          padding: '8px 8px',
          borderRadius: '12px',
          minWidth: '65px',
          boxShadow: '0 4px 12px rgba(142, 68, 173, 0.3)',
          position: 'relative',
          animation: 'pulse 2s infinite'
        }}
      >
        <div style={{
          position: 'absolute',
          top: '-2px',
          right: '-2px',
          width: '8px',
          height: '8px',
          background: '#FF6B6B',
          borderRadius: '50%',
          animation: 'blink 1.5s infinite'
        }}></div>
        <Briefcase size={18} strokeWidth={2} />
        <span style={{ fontWeight: '700', lineHeight: '1' }}>Freelance</span>
        <span style={{ fontSize: '7px', opacity: '0.9', lineHeight: '1' }}>Hub</span>
      </button>
    </div>
  );

  // Desktop top navigation
  const DesktopNav = () => (
    <div style={{
      position: 'sticky',
      top: 0,
      background: 'white',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
      borderBottom: '1px solid #f0f0f0'
    }}>
      {/* Brand - Goes to Freelance Hub */}
      <div 
        onClick={() => navigate('/freelance/home')}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '22px',
          fontWeight: '900',
          color: '#8E44AD',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
        onMouseOver={(e) => e.target.style.opacity = '0.8'}
        onMouseOut={(e) => e.target.style.opacity = '1'}
      >
        <div style={{
          width: '36px', 
          height: '36px',
          background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          boxShadow: '0 4px 10px rgba(142, 68, 173, 0.2)'
        }}>
          <Sparkles size={20} fill="white" />
        </div>
        ExpertEase
      </div>

      {/* Nav Items */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.label}
              onClick={() => navigate(item.path)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                border: 'none',
                background: isActive ? '#8E44AD' : 'transparent',
                color: isActive ? 'white' : '#6B7280',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                padding: '10px 20px',
                borderRadius: '8px',
                height: '44px'
              }}
            >
              <item.icon size={18} strokeWidth={isActive ? 2.5 : 2} />
              <span>{item.label}</span>
            </button>
          );
        })}
        
        {/* Freelance Hub Button - Desktop */}
        <button
          onClick={() => navigate('/freelance/home')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            border: 'none',
            background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
            color: 'white',
            fontSize: '14px',
            fontWeight: '700',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            padding: '10px 20px',
            borderRadius: '8px',
            height: '44px',
            boxShadow: '0 4px 12px rgba(142, 68, 173, 0.3)',
            position: 'relative',
            animation: 'pulse 2s infinite'
          }}
        >
          <div style={{
            position: 'absolute',
            top: '-2px',
            right: '-2px',
            width: '8px',
            height: '8px',
            background: '#FF6B6B',
            borderRadius: '50%',
            animation: 'blink 1.5s infinite'
          }}></div>
          <Briefcase size={18} strokeWidth={2} />
          <span>Freelance Hub</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* CSS Animations */}
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.05); }
          100% { transform: scale(1); }
        }
        @keyframes blink {
          0% { opacity: 1; }
          50% { opacity: 0.3; }
          100% { opacity: 1; }
        }
      `}</style>
      
      {/* Desktop Navigation */}
      <div style={{ display: 'none', '@media (min-width: 768px)': { display: 'block' } }}>
        <DesktopNav />
      </div>
      
      {/* Mobile Navigation */}
      <div style={{ display: 'block', '@media (min-width: 768px)': { display: 'none' } }}>
        <MobileNav />
      </div>
    </>
  );
};

export default HousekeepingNavigation;
