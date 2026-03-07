import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Clock, FileText, Calendar, User } from 'lucide-react';
import './DoctorBottomNav.css';

const DoctorBottomNav = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="doctor-bottom-nav" aria-label="Doctor Navigation">
      <Link 
        to="/doctor/dashboard" 
        className={`nav-item ${isActive('/doctor/dashboard')}`}
        aria-label="Dashboard"
      >
        <LayoutDashboard size={24} aria-hidden="true" />
        <span>Dashboard</span>
      </Link>
      <Link 
        to="/doctor/availability" 
        className={`nav-item ${isActive('/doctor/availability')}`}
        aria-label="Availability"
      >
        <Clock size={24} aria-hidden="true" />
        <span>Availability</span>
      </Link>
      <Link 
        to="/doctor/requests" 
        className={`nav-item ${isActive('/doctor/requests')}`}
        aria-label="Requests"
      >
        <FileText size={24} aria-hidden="true" />
        <span>Requests</span>
      </Link>
      <Link 
        to="/doctor/appointments" 
        className={`nav-item ${isActive('/doctor/appointments')}`}
        aria-label="Appointments"
      >
        <Calendar size={24} aria-hidden="true" />
        <span>Appointments</span>
      </Link>
      <Link 
        to="/doctor/profile" 
        className={`nav-item ${isActive('/doctor/profile')}`}
        aria-label="Profile"
      >
        <User size={24} aria-hidden="true" />
        <span>Profile</span>
      </Link>
    </nav>
  );
};

export default DoctorBottomNav;
