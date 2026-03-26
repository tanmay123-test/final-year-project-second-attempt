import React, { useState, useEffect } from 'react';
import { Home, Search, PlusCircle, Folder, Bot, Wallet, Star, LayoutDashboard, User, X, Briefcase, ChevronRight } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import PostProject from './PostProject';
import MyProjects from './MyProjects';
import FindFreelancers from './FindFreelancers';
import AIAssistant from './AIAssistant';
import Profile from './Profile';
import axios from 'axios';
import api from '../../../shared/api';
import '../styles/FreelanceHome.css';

const FreelanceHome = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  
  // Derived state from URL
  const activeTab = searchParams.get('tab') || 'home';
  
  const [featuredFreelancers, setFeaturedFreelancers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Direct Booking State
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [bookingData, setBookingData] = useState({
    title: '',
    description: '',
    amount: '',
    deadline: ''
  });
  const [bookingLoading, setBookingLoading] = useState(false);

  useEffect(() => {
    // Sync search query from URL if present
    const q = searchParams.get('q');
    if (q) setSearchQuery(q);
    
    fetchFeaturedFreelancers();
  }, [searchParams]);

  // Handle booking from profile page
  useEffect(() => {
    const location = window.location;
    if (location.state?.bookFreelancer) {
      const freelancer = location.state.bookFreelancer;
      console.log('Booking freelancer from profile:', freelancer);
      
      // Switch to find tab and trigger booking
      handleTabChange('find');
      
      // Small delay to ensure FindFreelancers component is mounted
      setTimeout(() => {
        handleBookNow(freelancer);
      }, 100);
      
      // Clear the state to prevent re-triggering
      window.history.replaceState({}, document.title, location.pathname);
    }
  }, []);

  const handleTabChange = (tab, extraParams = {}) => {
    setIsTransitioning(true);
    // Use a small timeout to ensure clean unmounting/mounting and prevent flickering
    setTimeout(() => {
      if (tab === 'home') {
        setSearchParams({}, { replace: true });
      } else {
        setSearchParams({ tab, ...extraParams }, { replace: true });
      }
      setIsTransitioning(false);
    }, 50);
  };

  const fetchFeaturedFreelancers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/home/featured-freelancers?limit=3');
      if (response.data && response.data.freelancers) {
        setFeaturedFreelancers(response.data.freelancers);
      }
    } catch (error) {
      console.error('Error fetching featured freelancers:', error);
      // Fallback to empty list or handled error state
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const query = searchQuery.trim();
    if (query) {
      handleTabChange('find', { q: query });
    }
  };

  const handleBookNow = (worker) => {
    setSelectedWorker(worker);
    setBookingData({
      title: `Direct Booking — ${worker.full_name}`,
      description: '',
      amount: worker.hourly_rate?.toString() || '1000',
      deadline: ''
    });
    setShowBookingModal(true);
  };

  const handleDirectBookingSubmit = async (e) => {
    e.preventDefault();
    setBookingLoading(true);
    try {
      console.log('Submitting direct booking:', {
        freelancer_id: selectedWorker.id,
        ...bookingData
      });
      
      const response = await api.post('/api/freelance/bookings', {
        freelancer_id: selectedWorker.id,
        title: bookingData.title,
        description: bookingData.description,
        amount: parseFloat(bookingData.amount),
        deadline: bookingData.deadline
      });
      
      console.log('Direct booking response:', response.data);
      
      if (response.data.success || response.data.booking_id) {
        alert('✅ Direct booking request sent successfully! The freelancer will be notified and you can track this request in your Projects tab.');
        setShowBookingModal(false);
        setBookingData({
          title: '',
          description: '',
          amount: '',
          deadline: ''
        });
        // Redirect to projects tab with direct sub-tab selected
        handleTabChange('projects', { sub: 'direct' });
      } else {
        throw new Error('Booking creation failed');
      }
    } catch (error) {
      console.error('Error creating direct booking:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to create booking. Please try again.';
      alert(`❌ ${errorMessage}`);
    } finally {
      setBookingLoading(false);
    }
  };
  
  const categories = [
    { id: 'web', name: 'Web Development', projects: '245 projects', icon: '🌐' },
    { id: 'app', name: 'App Development', projects: '189 projects', icon: '📱' },
    { id: 'uiux', name: 'UI/UX Design', projects: '312 projects', icon: '🎨' },
    { id: 'marketing', name: 'Digital Marketing', projects: '156 projects', icon: '📢' },
    { id: 'aiml', name: 'AI & Machine Learning', projects: '98 projects', icon: '🤖' },
    { id: 'content', name: 'Content Writing', projects: '203 projects', icon: '✍️' },
  ];

  const renderContent = () => {
    if (isTransitioning) {
      return (
        <div className="tab-loading-state">
          <div className="spinner-purple"></div>
          <p>Switching view...</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'home':
        return (
          <>
            {/* Hero Section */}
            <section className="freelance-hero">
              <div className="hero-container">
                <div className="hero-content">
                  <h1>Find Top Freelancers</h1>
                  <p>Hire experts for your next project — browse 1000+ verified professionals</p>
                </div>
                <div className="hero-search-wrapper">
                  <form onSubmit={handleSearchSubmit} className="search-bar-hero">
                    <Search className="search-icon-hero" size={20} color="#9ca3af" />
                    <input 
                      type="text" 
                      placeholder="Search freelancers or skills..." 
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </form>
                </div>
              </div>
            </section>

            <div className="main-content-wrapper">
              {/* Post Project Banner */}
              <section className="post-project-banner-new">
                <div className="banner-inner">
                  <div className="banner-content">
                    <h3>Have a project idea?</h3>
                    <p>Post it and get proposals from top freelancers instantly</p>
                  </div>
                  <button className="post-btn-new" onClick={() => handleTabChange('post')}>
                    Post Project
                  </button>
                </div>
              </section>

              {/* Categories */}
              <section className="categories-section">
                <div className="section-header">
                  <h2>Browse Categories</h2>
                </div>
                <div className="categories-grid">
                  {categories.map(cat => (
                    <div key={cat.id} className="category-card" onClick={() => {
                      handleTabChange('find');
                      // Simulating search by category
                    }}>
                      <span className="cat-icon">{cat.icon}</span>
                      <div className="cat-info">
                        <h4>{cat.name}</h4>
                        <p>{cat.projects}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Featured Freelancers */}
              <section className="featured-section">
                <div className="section-header">
                  <h2>Featured Freelancers</h2>
                  <button className="view-all-link" onClick={() => handleTabChange('find')}>
                    View All →
                  </button>
                </div>
                
                <div className="freelancers-grid">
                  {loading ? (
                    <div className="loading-featured">
                      <div className="spinner-purple"></div>
                    </div>
                  ) : featuredFreelancers.length > 0 ? (
                    featuredFreelancers.map(free => (
                      <div key={free.id} className="freelancer-card-v2">
                        <div className="card-header-v2" onClick={() => navigate(`/freelance/freelancer/${free.id}`)}>
                          <div className="avatar-circle">
                            {free.full_name?.split(' ').map(n => n[0]).join('')}
                            <span className={`status-indicator ${free.status === 'approved' ? 'online' : 'offline'}`}></span>
                          </div>
                          <div className="header-info">
                            <div className="name-row">
                              <h4>{free.full_name}</h4>
                              <div className="status-dot-v2"></div>
                            </div>
                            <p className="role-text">{free.specialization || 'Professional Freelancer'}</p>
                            <div className="rating-row">
                              <Star size={14} fill="#FFB800" color="#FFB800" />
                              <span className="rating-val">{free.rating || '5.0'}</span>
                              <span className="reviews-count">(87 reviews)</span>
                              <span className="rate-val">₹{free.hourly_rate || '2500'}/hr</span>
                            </div>
                          </div>
                        </div>
                        <div className="skills-tags-v2">
                          {(free.skills || 'React, Node.js, TypeScript').split(',').map((skill, idx) => (
                            <span key={idx} className="skill-tag-v2">{skill.trim()}</span>
                          ))}
                        </div>
                        <button 
                          className="btn-primary-v3" 
                          style={{width: '100%', marginTop: '1.2rem', padding: '0.6rem'}}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleBookNow(free);
                          }}
                        >
                          Book Now
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="empty-featured">
                      <p>No featured freelancers available right now.</p>
                    </div>
                  )}
                </div>
              </section>
            </div>
          </>
        );
      case 'post':
        return (
          <PostProject 
            onBack={() => handleTabChange('home')} 
            onSuccess={() => handleTabChange('projects')} 
          />
        );
      case 'projects':
        return <MyProjects />;
      case 'find':
        return <FindFreelancers onBook={handleBookNow} initialQuery={searchQuery} />;
      case 'ai':
        return <AIAssistant />;
      case 'wallet':
        return (
          <div className="wallet-placeholder">
            <Wallet size={48} color="#534AB7" />
            <h3>My Wallet</h3>
            <p>View your transaction history and manage funds.</p>
          </div>
        );
      case 'profile':
        return <Profile />;
      default:
        return null;
    }
  };

  return (
    <div className="freelance-container">
      {/* Desktop Top Navigation (Visible on all tabs) */}
      <header className="freelance-top-nav desktop-only">
        <div className="nav-container">
          <div className="nav-left" onClick={() => navigate('/freelance/home')} style={{cursor:'pointer'}}>
            <span className="brand-name">FreelanceHub</span>
          </div>
          
          <div className="nav-center">
            <form onSubmit={handleSearchSubmit} className="search-bar-nav">
              <Search size={18} color="#9ca3af" />
              <input 
                type="text" 
                placeholder="Search freelancers or skills..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>

          <div className="nav-right">
            <nav className="nav-links-desktop">
              <button className={`nav-link-item ${activeTab === 'home' ? 'active' : ''}`} onClick={() => handleTabChange('home')}>
                <Home size={18} /> <span>Home</span>
              </button>
              <button className={`nav-link-item ${activeTab === 'post' ? 'active' : ''}`} onClick={() => handleTabChange('post')}>
                <PlusCircle size={18} /> <span>Post</span>
              </button>
              <button className={`nav-link-item ${activeTab === 'projects' ? 'active' : ''}`} onClick={() => handleTabChange('projects')}>
                <Folder size={18} /> <span>Projects</span>
              </button>
              <button className={`nav-link-item ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => handleTabChange('ai')}>
                <Bot size={18} /> <span>AI</span>
              </button>
              <button className={`nav-link-item ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => handleTabChange('profile')}>
                <User size={18} /> <span>Profile</span>
              </button>
            </nav>
            <button className="post-project-btn-desktop" onClick={() => handleTabChange('post')}>
              Post Project
            </button>
          </div>
        </div>
      </header>

      {renderContent()}

      {/* Direct Booking Modal */}
      {showBookingModal && selectedWorker && (
        <div className="modal-overlay-new">
          <div className="modal-content-new booking-modal-v2">
            <div className="modal-header-v2">
              <div className="freelancer-info-header">
                <div className="avatar-circle-v3">
                  {selectedWorker.full_name?.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="header-details">
                  <div className="name-row">
                    <h2>{selectedWorker.full_name}</h2>
                    <div className="price-tag-badge">
                      ₹{selectedWorker.hourly_rate || '200'}/hr
                    </div>
                  </div>
                  <div className="spec-rating-row">
                    <span>{selectedWorker.specialization || 'Freelancer'}</span>
                    <div className="stars-row">
                      <Star size={14} fill="#FFB800" color="#FFB800" />
                      <Star size={14} fill="#FFB800" color="#FFB800" />
                      <Star size={14} fill="#FFB800" color="#FFB800" />
                      <Star size={14} fill="#FFB800" color="#FFB800" />
                      <Star size={14} fill="#FFB800" color="#FFB800" />
                      <span>5 (87)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <form onSubmit={handleDirectBookingSubmit} className="direct-booking-form-v2">
              <div className="form-group-v3">
                <label>PROJECT TITLE</label>
                <input 
                  type="text" 
                  placeholder="e.g. Blog post for my SaaS product"
                  value={bookingData.title}
                  onChange={(e) => setBookingData({...bookingData, title: e.target.value})}
                  required
                />
              </div>

              <div className="form-group-v3">
                <label>WHAT DO YOU NEED HELP WITH?</label>
                <textarea 
                  rows="4"
                  placeholder="Describe your requirements clearly..."
                  value={bookingData.description}
                  onChange={(e) => setBookingData({...bookingData, description: e.target.value})}
                  required
                />
              </div>

              <div className="form-row-v2">
                <div className="form-group-v3 half">
                  <label>YOUR BUDGET</label>
                  <div className="input-with-currency">
                    <span>₹</span>
                    <input 
                      type="number" 
                      placeholder="0"
                      value={bookingData.amount}
                      onChange={(e) => setBookingData({...bookingData, amount: e.target.value})}
                      required
                    />
                  </div>
                </div>

                <div className="form-group-v3 half">
                  <label>DEADLINE</label>
                  <input 
                    type="date" 
                    value={bookingData.deadline}
                    onChange={(e) => setBookingData({...bookingData, deadline: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div className="modal-actions-v3">
                <button type="submit" className="submit-btn-v3" disabled={bookingLoading}>
                  {bookingLoading ? 'Sending...' : 'Send Booking Request →'}
                </button>
                <button type="button" className="cancel-link-v3" onClick={() => setShowBookingModal(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Mobile Bottom Nav (Hidden on Desktop) */}
      <nav className="freelance-bottom-nav mobile-only">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => handleTabChange('home')}
        >
          <Home size={24} />
          <span>Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'post' ? 'active' : ''}`}
          onClick={() => handleTabChange('post')}
        >
          <PlusCircle size={24} />
          <span>Post</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
          onClick={() => handleTabChange('projects')}
        >
          <Folder size={24} />
          <span>Projects</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => handleTabChange('ai')}
        >
          <Bot size={24} />
          <span>AI</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => handleTabChange('profile')}
        >
          <User size={24} />
          <span>Profile</span>
        </button>
      </nav>
    </div>
  );
};

export default FreelanceHome;
