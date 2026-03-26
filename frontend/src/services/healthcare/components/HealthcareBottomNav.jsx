import React from 'react';
import { useNavigate } from 'react-router-dom';

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
        <span className="nav-tab-icon">🏠</span>
        <span className="nav-tab-label">Home</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'ai-care' ? 'active' : ''}`}
        onClick={() => handleTabClick('ai-care', '/healthcare/ai-care')}
      >
        <span className="nav-tab-icon">🤖</span>
        <span className="nav-tab-label">AI Care</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'explore' ? 'active' : ''}`}
        onClick={() => handleTabClick('explore', '/healthcare/explore')}
      >
        <span className="nav-tab-icon">🔍</span>
        <span className="nav-tab-label">Explore</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'my-care' ? 'active' : ''}`}
        onClick={() => handleTabClick('my-care', '/healthcare/my-care')}
      >
        <span className="nav-tab-icon">❤️</span>
        <span className="nav-tab-label">My Care</span>
      </button>
      
      <button
        className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
        onClick={() => handleTabClick('profile', '/healthcare/profile')}
      >
        <span className="nav-tab-icon">👤</span>
        <span className="nav-tab-label">Profile</span>
      </button>
    </div>
  );
};

export default HealthcareBottomNav;
