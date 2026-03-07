import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Bot, Compass, Calendar, User } from 'lucide-react';
import './BottomNav.css';

const BottomNav = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="bottom-nav" aria-label="Main Navigation">
      <Link 
        to="/services" 
        className={`nav-item ${isActive('/services')}`}
        aria-label="Home"
      >
        <Home size={24} aria-hidden="true" />
        <span>Home</span>
      </Link>
      <Link 
        to="#" 
        className={`nav-item ${isActive('/ai-care')}`}
        aria-label="AI Care"
      >
        <Bot size={24} aria-hidden="true" />
        <span>AI Care</span>
      </Link>
      <Link 
        to="/doctors" 
        className={`nav-item ${isActive('/doctors')}`}
        aria-label="Explore Doctors"
      >
        <Compass size={24} aria-hidden="true" />
        <span>Explore</span>
      </Link>
      <Link 
        to="/dashboard" 
        className={`nav-item ${isActive('/dashboard')}`}
        aria-label="Appointments"
      >
        <Calendar size={24} aria-hidden="true" />
        <span>Appointments</span>
      </Link>
      <Link 
        to="/profile" 
        className={`nav-item ${isActive('/profile')}`}
        aria-label="User Profile"
      >
        <User size={24} aria-hidden="true" />
        <span>Profile</span>
      </Link>
    </nav>
  );
};

export default BottomNav;
