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
                <span>Find Doctors</span>
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
              <Link to="/worker/dashboard" className={`nav-link ${isActive('/worker/dashboard')}`} onClick={closeMenu}>
                <LayoutDashboard size={18} />
                <span>Dashboard</span>
              </Link>
              <div className="user-profile">
                <div className="user-avatar worker">
                  <Briefcase size={16} />
                </div>
                <span className="user-name">Dr. {worker.email.split('@')[0]}</span>
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
