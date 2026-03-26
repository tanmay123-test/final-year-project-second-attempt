import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, Bot, Search, Heart, User, Briefcase } from 'lucide-react';
import './HealthcareBottomNav.css';

const HealthcareBottomNav = ({ activeTab = 'home' }) => {
  const navigate = useNavigate();
  const isMobile = window.innerWidth < 768;

  if (!isMobile) return null;

  const handleTabClick = (tab, path) => {
    navigate(path);
  };

  return (
    <div className="healthcare-bottom-nav">
      <button
        className={`nav-tab ${activeTab === 'home' ? 'active' : ''}`}
        onClick={() => handleTabClick('home', '/healthcare/home')}
      >
        <Home size={20} className="nav-tab-icon" />
        <span className="nav-tab-label">Home</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'ai-care' ? 'active' : ''}`}
        onClick={() => handleTabClick('ai-care', '/healthcare/ai-care')}
      >
        <Bot size={20} className="nav-tab-icon" />
        <span className="nav-tab-label">AI Care</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'appointments' ? 'active' : ''}`}
        onClick={() => handleTabClick('appointments', '/healthcare/appointments')}
      >
        <Search size={20} className="nav-tab-icon" />
        <span className="nav-tab-label">Appointments</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'my-care' ? 'active' : ''}`}
        onClick={() => handleTabClick('my-care', '/healthcare/my-care')}
      >
        <Heart size={20} className="nav-tab-icon" />
        <span className="nav-tab-label">My Care</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
        onClick={() => handleTabClick('profile', '/healthcare/profile')}
      >
        <User size={20} className="nav-tab-icon" />
        <span className="nav-tab-label">Profile</span>
      </button>

      {/* Freelance Hub Button - Always Visible */}
      <button
        className="nav-tab freelance-hub-tab"
        onClick={() => navigate('/freelance/home')}
        style={{
          background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
          color: 'white',
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
        <Briefcase size={18} className="nav-tab-icon" />
        <span className="nav-tab-label" style={{ fontSize: '9px', fontWeight: '700' }}>Freelance</span>
      </button>
    </div>
  );
};

export default HealthcareBottomNav;
