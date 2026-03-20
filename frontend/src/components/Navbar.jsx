import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Menu, X, Stethoscope, User, LogOut, LayoutDashboard, Search, Briefcase } from 'lucide-react';

const Navbar = () => {
  const { user, worker, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMobileMenuOpen(false);
  };

  const closeMenu = () => setIsMobileMenuOpen(false);

  const isActive = (path) => location.pathname === path ? 'active' : '';

  const getWorkerDashboardPath = () => {
    if (!worker) return '/worker/dashboard';
    const service = worker.service || '';
    if (service.includes('healthcare')) return '/doctor/dashboard';
    if (service.includes('housekeeping')) return '/worker/housekeeping/dashboard';
    if (service.includes('freelance')) return '/freelancer/dashboard';
    if (service.includes('car')) return '/worker/car/homepage';
    return '/worker/dashboard';
  };

  const getWorkerName = () => {
    if (!worker) return '';
    if (worker.name) return worker.name;
    const emailPrefix = worker.email.split('@')[0];
    const service = worker.service || '';
    if (service.includes('healthcare')) return `Dr. ${emailPrefix}`;
    return emailPrefix;
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand" onClick={closeMenu}>
          <div className="brand-icon-wrapper">
            <Stethoscope size={24} color="white" strokeWidth={2.5} />
          </div>
          <span className="brand-text">ExpertEase</span>
        </Link>

        <button className="mobile-menu-btn" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} aria-label="Toggle menu">
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <div className={`navbar-links ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
          {user ? (
            // User Logged In
            <>
              <Link to="/dashboard" className={`nav-link ${isActive('/dashboard')}`} onClick={closeMenu}>
                <LayoutDashboard size={18} />
                <span>Dashboard</span>
              </Link>
              <Link to="/doctors" className={`nav-link ${isActive('/doctors')}`} onClick={closeMenu}>
                <Search size={18} />
                <span>Find Housekeeping Worker</span>
              </Link>
              <div className="user-profile">
                <div className="user-avatar">
                  <User size={16} />
                </div>
                <span className="user-name">Hi, {user.user_name}</span>
              </div>
              <button onClick={handleLogout} className="btn-logout">
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </>
          ) : worker ? (
            // Worker Logged In
            <>
              <Link to={getWorkerDashboardPath()} className={`nav-link ${isActive(getWorkerDashboardPath())}`} onClick={closeMenu}>
                <LayoutDashboard size={18} />
                <span>Dashboard</span>
              </Link>
              <div className="user-profile">
                <div className="user-avatar worker">
                  <Briefcase size={16} />
                </div>
                <span className="user-name">{getWorkerName()}</span>
              </div>
              <button onClick={handleLogout} className="btn-logout">
                <LogOut size={18} />
                <span>Logout</span>
              </button>
            </>
          ) : (
            // Not Logged In
            <>
              <Link to="/login" className={`nav-link ${isActive('/login')}`} onClick={closeMenu}>
                <span>Patient Login</span>
              </Link>
              <Link to="/worker/login" className="btn-nav-primary" onClick={closeMenu}>
                <span>Provider Login</span>
              </Link>
            </>
          )}
        </div>
      </div>
      
      {/* Overlay for mobile menu */}
      {isMobileMenuOpen && <div className="navbar-overlay" onClick={closeMenu}></div>}
    </nav>
  );
};

export default Navbar;
