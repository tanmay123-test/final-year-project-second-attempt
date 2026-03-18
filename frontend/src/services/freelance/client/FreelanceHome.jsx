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
import '../styles/FreelanceHome.css';

const FreelanceHome = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('home');
  const [featuredFreelancers, setFeaturedFreelancers] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Direct Booking State
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [bookingData, setBookingData] = useState({
    title: '',
    description: '',
    amount: ''
  });
  const [bookingLoading, setBookingLoading] = useState(false);

  useEffect(() => {
    // Handle URL parameters if any (for navigation simulation)
    const tab = searchParams.get('tab');
    const q = searchParams.get('q');
    if (tab) setActiveTab(tab);
    if (q) setSearchQuery(q);
    
    fetchFeaturedFreelancers();
  }, [searchParams]);

  const fetchFeaturedFreelancers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5000/api/home/featured-freelancers?limit=3');
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
      setActiveTab('find');
      // Update search params without navigating away
      setSearchParams({ tab: 'find', q: query }, { replace: true });
    }
  };

  const handleBookNow = (worker) => {
    setSelectedWorker(worker);
    setBookingData({
      title: `Direct Booking — ${worker.full_name}`,
      description: '',
      amount: worker.hourly_rate?.toString() || '1000'
    });
    setShowBookingModal(true);
  };

  const handleDirectBookingSubmit = async (e) => {
    e.preventDefault();
    setBookingLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/bookings', {
        freelancer_id: selectedWorker.id,
        ...bookingData
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Direct booking request sent! You can track it in the Projects tab.');
      setShowBookingModal(false);
      setActiveTab('projects');
    } catch (error) {
      console.error('Error creating direct booking:', error);
      alert(error.response?.data?.error || 'Failed to create booking');
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
    switch (activeTab) {
      case 'home':
        return (
          <>
            {/* Desktop Top Navigation (Visible on Desktop only) */}
            <header className="freelance-top-nav desktop-only">
              <div className="nav-container">
                <div className="nav-left">
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
                    <button className={`nav-link-item ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>
                      <Home size={18} /> <span>Home</span>
                    </button>
                    <button className={`nav-link-item ${activeTab === 'post' ? 'active' : ''}`} onClick={() => setActiveTab('post')}>
                      <PlusCircle size={18} /> <span>Post</span>
                    </button>
                    <button className={`nav-link-item ${activeTab === 'projects' ? 'active' : ''}`} onClick={() => setActiveTab('projects')}>
                      <Folder size={18} /> <span>Projects</span>
                    </button>
                    <button className={`nav-link-item ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => setActiveTab('ai')}>
                      <Bot size={18} /> <span>AI</span>
                    </button>
                    <button className="nav-link-item" onClick={() => navigate('/services')}>
                      <User size={18} /> <span>Profile</span>
                    </button>
                  </nav>
                  <button className="post-project-btn-desktop" onClick={() => setActiveTab('post')}>
                    Post Project
                  </button>
                </div>
              </div>
            </header>

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
                  <button className="post-btn-new" onClick={() => setActiveTab('post')}>
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
                      setActiveTab('find');
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
                  <button className="view-all-link" onClick={() => setActiveTab('find')}>
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
                      <div key={free.id} className="freelancer-card-v2" onClick={() => navigate(`/freelance/freelancer/${free.id}`)}>
                        <div className="card-header-v2">
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
            onBack={() => setActiveTab('home')} 
            onSuccess={() => setActiveTab('projects')} 
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
      {renderContent()}

      {/* Direct Booking Modal */}
      {showBookingModal && selectedWorker && (
        <div className="modal-overlay-new">
          <div className="modal-content-new booking-modal">
            <div className="modal-header-new">
              <h2>Book {selectedWorker.full_name}</h2>
              <button className="close-btn-new" onClick={() => setShowBookingModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleDirectBookingSubmit} className="direct-booking-form">
              <div className="form-group-v2">
                <label>Project Title</label>
                <input 
                  type="text" 
                  value={bookingData.title}
                  onChange={(e) => setBookingData({...bookingData, title: e.target.value})}
                  required
                />
              </div>
              <div className="form-group-v2">
                <label>Description of work</label>
                <textarea 
                  rows="4"
                  placeholder="What do you need help with?"
                  value={bookingData.description}
                  onChange={(e) => setBookingData({...bookingData, description: e.target.value})}
                  required
                />
              </div>
              <div className="form-group-v2">
                <label>Budget (₹)</label>
                <input 
                  type="number" 
                  value={bookingData.amount}
                  onChange={(e) => setBookingData({...bookingData, amount: e.target.value})}
                  required
                />
              </div>
              <div className="modal-actions-v2">
                <button type="button" className="cancel-btn-v2" onClick={() => setShowBookingModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn-v2" disabled={bookingLoading}>
                  {bookingLoading ? 'Sending...' : 'Send Booking Request'}
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
          onClick={() => setActiveTab('home')}
        >
          <Home size={24} />
          <span>Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'post' ? 'active' : ''}`}
          onClick={() => setActiveTab('post')}
        >
          <PlusCircle size={24} />
          <span>Post</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
          onClick={() => setActiveTab('projects')}
        >
          <Folder size={24} />
          <span>Projects</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <Bot size={24} />
          <span>AI</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <User size={24} />
          <span>Profile</span>
        </button>
      </nav>
    </div>
  );
};

export default FreelanceHome;
