import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, User } from 'lucide-react';
import '../components/DoctorBottomNav.css'; // Reuse existing styles

const HousekeepingBottomNav = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="doctor-bottom-nav" aria-label="Housekeeping Navigation">
      <Link 
        to="/worker/housekeeping/dashboard" 
        className={`nav-item ${isActive('/worker/housekeeping/dashboard')}`}
        aria-label="Dashboard"
      >
        <LayoutDashboard size={24} aria-hidden="true" />
        <span>Dashboard</span>
      </Link>
      <Link 
        to="/worker/housekeeping/profile" 
        className={`nav-item ${isActive('/worker/housekeeping/profile')}`}
        aria-label="Profile"
      >
        <User size={24} aria-hidden="true" />
        <span>Profile</span>
      </Link>
    </nav>
  );
};

export default HousekeepingBottomNav;
