import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Bot, Search, Calendar, User, Sparkles } from 'lucide-react';
import { styled } from '../../../stitches.config';

const NavContainer = styled('div', {
  position: 'fixed',
  background: 'white',
  zIndex: 9999,
  display: 'flex',
  boxShadow: '0 4px 20px rgba(0,0,0,0.04)',
  borderTop: '1px solid #f0f0f0',

  // Mobile Styles (Bottom Bar)
  bottom: 0,
  left: 0,
  right: 0,
  padding: '12px 0',
  justifyContent: 'space-around',

  // Desktop Styles (Top Bar)
  '@md': {
    top: 0,
    bottom: 'auto',
    left: 0,
    right: 0,
    width: '100%',
    height: '64px',
    padding: '0 32px',
    justifyContent: 'center',
    gap: '40px',
    borderTop: 'none',
    borderBottom: '1px solid #f0f0f0',
    boxShadow: '0 2px 10px rgba(0,0,0,0.05)',
  },
});

const Brand = styled('div', {
  display: 'none',
  '@md': {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '22px',
    fontWeight: '900',
    color: '#8E44AD',
    position: 'absolute',
    left: '32px',
    height: '100%',
    fontFamily: '$heading',
    letterSpacing: '-0.5px',
    cursor: 'pointer',
    '&:hover': {
      opacity: 0.8,
    },
  },
});

const BrandIcon = styled('div', {
  width: '32px', 
  height: '32px',
  background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
  borderRadius: '10px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
  boxShadow: '0 4px 10px rgba(142, 68, 173, 0.2)',
});

const NavItem = styled('button', {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  border: 'none',
  background: 'none',
  color: '#9ca3af',
  fontSize: '10px',
  gap: '4px',
  cursor: 'pointer',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  padding: '6px 12px',
  borderRadius: '12px',
  position: 'relative',

  '&:hover': {
    color: '#8E44AD',
    background: 'rgba(142, 68, 173, 0.05)',
  },

  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: '-2px',
    left: '50%',
    width: '0%',
    height: '2px',
    background: '#8E44AD',
    transition: 'all 0.3s ease',
    transform: 'translateX(-50%)',
    borderRadius: '2px',
  },

  variants: {
    active: {
      true: {
        color: '#8E44AD',
        '&::after': {
          width: '60%',
        },
      },
    },
  },

  '@md': {
    flexDirection: 'row',
    fontSize: '15px',
    fontWeight: '600',
    gap: '10px',
    height: '44px',
    padding: '0 24px',
    '&::after': {
      bottom: '0',
    },
  },
});

const HousekeepingNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { icon: Home, label: 'Home', path: '/housekeeping/home' },
    { icon: Search, label: 'Book', path: '/housekeeping/booking/create' },
    { icon: Bot, label: 'AI Chat', path: '/housekeeping/ai-chat' },
    { icon: Calendar, label: 'Bookings', path: '/housekeeping/bookings' },
    { icon: User, label: 'Profile', path: '/housekeeping/profile' },
  ];

  return (
    <NavContainer>
      <Brand onClick={() => navigate('/services')}>
        <BrandIcon>
          <Sparkles size={20} fill="white" />
        </BrandIcon>
        ExpertEase
      </Brand>
      {navItems.map((item) => {
        const isActive = location.pathname === item.path;
        return (
          <NavItem 
            key={item.label} 
            active={isActive}
            onClick={() => navigate(item.path)}
          >
            <item.icon size={20} strokeWidth={isActive ? 2.5 : 2} />
            <span>{item.label}</span>
          </NavItem>
        );
      })}
    </NavContainer>
  );
};

export default HousekeepingNavigation;
