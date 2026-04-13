import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { Home, Bot, Search, Heart, User } from 'lucide-react';
import '../styles/HealthcareDashboard.css';
import '../styles/healthcare-shared.css';
import HealthcareSidebarLayout from '../components/HealthcareSidebarLayout';
import HealthcareBottomNav from '../components/HealthcareBottomNav';

const HealthcareDashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [specializations, setSpecializations] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('home');

  const scrollRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setStartX(e.pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    e.preventDefault();
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX) * 2; // Scroll speed
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  const firstName = user?.name?.split(' ')[0] || user?.first_name || 'User';
  const token = localStorage.getItem('token');

  const fallbackSpecs = [
    { id: 1, name: 'General', icon: '🩺' },
    { id: 2, name: 'Cardiology', icon: '❤️' },
    { id: 3, name: 'Dermatology', icon: '🧴' },
    { id: 4, name: 'Pediatrics', icon: '👶' },
    { id: 5, name: 'Orthopedics', icon: '🦴' },
    { id: 6, name: 'Neurology', icon: '🧠' }
  ];

  const fallbackDoctors = [
    {
      id: 1,
      name: 'Dr. Sarah Johnson',
      specialization: 'Cardiology',
      rating: 4.8,
      experience: '12',
      location: 'City Hospital',
      fee: 800,
      initial: 'S'
    },
    {
      id: 2,
      name: 'Dr. Michael Chen',
      specialization: 'Dermatology',
      rating: 4.6,
      experience: '8',
      location: 'Metro Medical Center',
      fee: 600,
      initial: 'M'
    },
    {
      id: 3,
      name: 'Dr. Emily Rodriguez',
      specialization: 'Pediatrics',
      rating: 4.9,
      experience: '15',
      location: 'Children\'s Hospital',
      fee: 700,
      initial: 'E'
    }
  ];

  useEffect(() => {
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };

    // Fetch specializations
    fetch('/healthcare/specializations', { headers })
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setSpecializations(data);
        } else {
          setSpecializations(fallbackSpecs);
        }
      })
      .catch(() => setSpecializations(fallbackSpecs));

    // Fetch doctors
    fetch('/healthcare/doctors', { headers })
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          const sorted = data
            .filter(d => d.is_approved !== false)
            .sort((a, b) => (b.rating || 0) - (a.rating || 0))
            .slice(0, 6);
          setDoctors(sorted);
        } else {
          setDoctors(fallbackDoctors);
        }
        setLoading(false);
      })
      .catch(() => {
        setDoctors(fallbackDoctors);
        setLoading(false);
      });
  }, [token]);

  const handleSearchClick = () => {
    navigate('/healthcare/explore');
  };

  const handleSpecClick = (specName) => {
    navigate(`/healthcare/explore?spec=${specName}`);
  };

  const handleBookNow = (doctorId) => {
    navigate(`/healthcare/book/${doctorId}`);
  };

  const handleTabClick = (tab, path) => {
    setActiveTab(tab);
    navigate(path);
  };

  const SkeletonCard = () => (
    <div className="doctor-card skeleton-card">
      <div className="skeleton skeleton-avatar"></div>
      <div className="skeleton skeleton-text"></div>
      <div className="skeleton skeleton-text short"></div>
    </div>
  );

  return (
    <HealthcareSidebarLayout>
      <div className="dashboard-inner">
        <div className="healthcare-dashboard">
          {/* Mobile Navigation Tabs (Hidden on Desktop) */}
          <div className="mobile-only" style={{ 
            backgroundColor: 'white', 
            margin: '0 0 20px 0', 
            borderRadius: '16px', 
            padding: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
            marginBottom: '20px',
            display: window.innerWidth < 768 ? 'block' : 'none'
          }}>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                onClick={() => navigate('/healthcare/home')}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '12px',
                  border: 'none',
                  backgroundColor: '#8E44AD',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <Home size={18} />
                Home
              </button>
              <button
                onClick={() => navigate('/healthcare/ai-care')}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  borderRadius: '12px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  color: '#6B7280',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <Bot size={18} />
                AI Care
              </button>
            </div>
          </div>

          {/* Header Section */}
          <div className="healthcare-header">
            <div className="header-top-row">
              <div>
                <div className="welcome-text">Welcome back 👋</div>
                <div className="user-name">{firstName}</div>
              </div>
              <button className="notif-btn" onClick={() => navigate('/healthcare/notifications')}>
                🔔
              </button>
            </div>

            <div className="search-bar" onClick={handleSearchClick}>
              <span className="search-icon">🔍</span>
              <span className="search-placeholder">Search doctors, specializations...</span>
            </div>
          </div>

          {/* Sections... */}
          <div className="section">
            <div className="section-header">
              <h2 className="section-title">Specializations</h2>
              <button className="view-all-btn" onClick={() => navigate('/healthcare/explore')}>
                View All ›
              </button>
            </div>

            <div 
              className={`spec-scroll-row ${isDragging ? 'dragging' : ''}`}
              ref={scrollRef}
              onMouseDown={handleMouseDown}
              onMouseLeave={handleMouseLeave}
              onMouseUp={handleMouseUp}
              onMouseMove={handleMouseMove}
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
            >
              {specializations.map((spec) => (
                <div
                  key={spec.id || spec.name}
                  className="spec-card"
                  onClick={() => handleSpecClick(spec.name)}
                >
                  <div className="spec-icon">{spec.icon || '🩺'}</div>
                  <div className="spec-label">{spec.name}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Doctors Section */}
          <div className="section">
            <div className="section-header">
              <h2 className="section-title">Top Doctors</h2>
              <button className="view-all-btn" onClick={() => navigate('/healthcare/explore')}>
                See All ›
              </button>
            </div>

            {loading ? (
              <div className="doctors-list">
                {[1, 2, 3].map((i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : (
              <div className="doctors-list">
                {doctors.map((doctor) => (
                  <div key={doctor.id} className="doctor-card">
                    <div className="doctor-card-top">
                      <div className="doctor-avatar">{doctor.initial}</div>
                      <div className="doctor-info">
                        <div className="doctor-name">{doctor.name}</div>
                        <div className="doctor-spec">{doctor.specialization}</div>
                        <div className="doctor-meta-row">
                          <span>⭐ {doctor.rating || '4.5'}</span>
                          <span>🕐 {doctor.experience || '5'} yrs</span>
                        </div>
                        <div className="doctor-location">📍 {doctor.location || 'City Hospital'}</div>
                      </div>
                    </div>
                    <div className="doctor-card-bottom">
                      <div className="doctor-fee">
                        ₹{doctor.fee || 500}
                        <span>/ visit</span>
                      </div>
                      <button className="book-now-btn" onClick={() => handleBookNow(doctor.id)}>
                        Book Now
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <HealthcareBottomNav activeTab={activeTab} />
        </div>
      </div>
    </HealthcareSidebarLayout>
  );
};

export default HealthcareDashboard;
