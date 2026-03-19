import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  FileText, 
  Briefcase, 
  Wallet, 
  Star, 
  Clock, 
  ChevronRight, 
  Bell,
  User,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  MapPin,
  ExternalLink,
  Plus
} from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const FreelancerDashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/freelancer/browse?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      // Using existing backend endpoint
      const response = await axios.get('http://localhost:5000/api/freelancer/dashboard', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setDashboardData(response.data.dashboard);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyNow = (projectId) => {
    navigate(`/freelance/projects/${projectId}`);
  };

  if (loading) {
    return (
      <div className="dashboard-loading-v2">
        <div className="skeleton skeleton-hero"></div>
        <div className="skeleton-grid">
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton skeleton-card"></div>)}
        </div>
        <div className="skeleton-layout">
          <div className="skeleton-main">
            <div className="skeleton skeleton-section"></div>
            <div className="skeleton skeleton-section"></div>
          </div>
          <div className="skeleton-side desktop-only">
            <div className="skeleton skeleton-sidebar"></div>
          </div>
        </div>
      </div>
    );
  }

  const { 
    name, 
    role, 
    avatarInitials, 
    stats, 
    profileCompletion, 
    activeProjects, 
    recentProposals, 
    pendingBookings,
    recommendedProjects 
  } = dashboardData || {};

  const handleBookingAction = async (bookingId, status) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/api/freelance/bookings/respond', {
        booking_id: bookingId,
        status: status
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        alert(`Booking ${status.toLowerCase()} successfully!`);
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error responding to booking:', error);
      alert(error.response?.data?.error || 'Failed to respond to booking');
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'browse', label: 'Browse', icon: Search },
    { id: 'proposals', label: 'Proposals', icon: FileText },
    { id: 'work', label: 'Work', icon: Briefcase },
    { id: 'wallet', label: 'Wallet', icon: Wallet },
  ];

  const getStatusColor = (status) => {
    const s = status?.toLowerCase();
    if (s === 'pending' || s === 'open') return 'amber';
    if (s === 'accepted' || s === 'active' || s === 'completed' || s === 'in_progress') return 'green';
    if (s === 'rejected' || s === 'cancelled' || s === 'declined') return 'red';
    return 'gray';
  };

  const handleNavClick = (id) => {
    setActiveTab(id);
    if (id === 'dashboard') navigate('/freelancer/dashboard');
    else if (id === 'browse') navigate('/freelancer/browse');
    else if (id === 'proposals') navigate('/freelancer/proposals');
    else if (id === 'work') navigate('/freelancer/work');
    else if (id === 'wallet') navigate('/freelancer/wallet');
  };

  return (
    <div className="freelancer-provider-dashboard">
      {/* Desktop Top Navbar */}
      <header className="dashboard-top-nav desktop-only">
        <div className="nav-container">
          <div className="nav-left">
            <div className="brand-logo">Freelance<span>Hub</span></div>
          </div>
          
          <div className="nav-center">
            <form onSubmit={handleSearchSubmit} className="search-box">
              <Search size={18} />
              <input 
                type="text" 
                placeholder="Search projects, clients..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </form>
          </div>
          
          <nav className="nav-right">
            {navItems.map(item => (
              <button 
                key={item.id} 
                className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </button>
            ))}
            <div className="user-profile-circle">
              {avatarInitials || <User size={20} />}
            </div>
          </nav>
        </div>
      </header>

      <main className="dashboard-content-v2">
        <div className="dashboard-inner">
          {/* Hero Banner */}
          <section className="hero-banner-v2">
            <div className="hero-main-info">
              <div className="hero-avatar-v2">
                <div className="avatar-circle">
                  {avatarInitials || <User size={40} />}
                </div>
              </div>
              <div className="hero-text-v2">
                <h1>{name || 'Freelancer'}</h1>
                <p>{role || 'Professional Freelancer'}</p>
                <div className="hero-badge-v2">
                  <Star size={14} fill="currentColor" />
                  <span>Top Rated Freelancer</span>
                </div>
              </div>
            </div>
            
            <div className="hero-completion-v2 desktop-only">
              <div className="completion-info-v2">
                <span>Profile Completion</span>
                <span className="completion-pct-v2">{profileCompletion || 0}%</span>
              </div>
              <div className="progress-track-v2">
                <div 
                  className="progress-fill-v2" 
                  style={{ width: `${profileCompletion || 0}%` }}
                ></div>
              </div>
            </div>
          </section>

          {/* Stats Grid */}
          <section className="stats-grid-v2">
            <div className="stat-card-v2">
              <div className="stat-icon-v2 purple">
                <Wallet size={20} />
              </div>
              <div className="stat-content-v2">
                <span className="stat-label-v2">Total Earnings</span>
                <h3 className="stat-value-v2">₹{stats?.total_earnings?.toLocaleString() || '0'}</h3>
              </div>
            </div>
            
            <div className="stat-card-v2">
              <div className="stat-icon-v2 blue">
                <Briefcase size={20} />
              </div>
              <div className="stat-content-v2">
                <span className="stat-label-v2">Active Projects</span>
                <h3 className="stat-value-v2">{stats?.active_projects || 0}</h3>
              </div>
            </div>
            
            <div className="stat-card-v2">
              <div className="stat-icon-v2 indigo">
                <FileText size={20} />
              </div>
              <div className="stat-content-v2">
                <span className="stat-label-v2">Proposals Sent</span>
                <h3 className="stat-value-v2">{stats?.proposals_sent || 0}</h3>
              </div>
            </div>
            
            <div className="stat-card-v2">
              <div className="stat-icon-v2 purple">
                <Star size={20} />
              </div>
              <div className="stat-content-v2">
                <span className="stat-label-v2">Rating</span>
                <h3 className="stat-value-v2 purple-text">{stats?.rating || '0.0'}</h3>
              </div>
            </div>
          </section>

          {/* Profile Completion (Mobile only) */}
          <section className="mobile-only profile-card-mobile">
            <div className="completion-card-v2">
              <div className="completion-header-v2">
                <div className="completion-title-v2">
                  <User size={18} />
                  <h3>Profile Completion</h3>
                </div>
                <span className="completion-pct-v2">{profileCompletion || 0}%</span>
              </div>
              <div className="progress-track-v2">
                <div 
                  className="progress-fill-v2" 
                  style={{ width: `${profileCompletion || 0}%` }}
                ></div>
              </div>
              <p className="completion-text-v2">Complete your profile to attract more clients</p>
            </div>
          </section>

          <div className="dashboard-layout-v2">
            {/* Main Column */}
            <div className="layout-main-v2">
              {/* Active Projects */}
              <section className="section-container-v2">
                <div className="section-header-v2">
                  <div className="section-title-v2">
                    <Briefcase size={20} />
                    <h2>Active Projects</h2>
                  </div>
                </div>
                
                <div className="section-body-v2">
                  {activeProjects && activeProjects.length > 0 ? (
                    <div className="cards-list-v2">
                      {activeProjects.map((project, idx) => (
                        <div key={idx} className="data-card-v2">
                          <div className="card-info-v2">
                            <h4>{project.project_title || project.title}</h4>
                            <p>{project.client_name} • Deadline: {new Date(project.deadline).toLocaleDateString()}</p>
                          </div>
                          <div className={`status-badge-v2 ${getStatusColor(project.status)}`}>
                            {project.status || 'Active'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state-v2">
                      <div className="empty-icon-v2">
                        <Briefcase size={40} />
                      </div>
                      <p>No active projects</p>
                    </div>
                  )}
                </div>
              </section>

              {/* Direct Booking Requests */}
              {pendingBookings && pendingBookings.length > 0 && (
                <section className="section-container-v2">
                  <div className="section-header-v2">
                    <div className="section-title-v2">
                      <Bell size={20} className="pulse-icon" />
                      <h2>New Booking Requests</h2>
                    </div>
                  </div>
                  
                  <div className="section-body-v2">
                    <div className="cards-list-v2">
                      {pendingBookings.map((booking, idx) => (
                        <div key={idx} className="data-card-v2 highlight-card">
                          <div className="card-info-v2">
                            <h4>{booking.project_title}</h4>
                            <p>From: <strong>{booking.client_name}</strong> • Budget: ₹{booking.amount?.toLocaleString()}</p>
                            <p className="card-desc-short">{booking.project_description}</p>
                            {booking.deadline && <p className="deadline-text">Deadline: {new Date(booking.deadline).toLocaleDateString()}</p>}
                          </div>
                          <div className="card-actions-v2">
                            <button 
                              className="accept-btn-v2"
                              onClick={() => handleBookingAction(booking.id, 'ACCEPTED')}
                            >
                              Accept
                            </button>
                            <button 
                              className="decline-btn-v2"
                              onClick={() => handleBookingAction(booking.id, 'DECLINED')}
                            >
                              Decline
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              )}

              {/* Recent Proposals */}
              <section className="section-container-v2">
                <div className="section-header-v2">
                  <div className="section-title-v2">
                    <FileText size={20} />
                    <h2>Recent Proposals</h2>
                  </div>
                </div>
                
                <div className="section-body-v2">
                  {recentProposals && recentProposals.length > 0 ? (
                    <div className="cards-list-v2">
                      {recentProposals.map((proposal, idx) => (
                        <div key={idx} className="data-card-v2">
                          <div className="card-info-v2">
                            <h4>{proposal.project_title}</h4>
                            <p>₹{proposal.budget?.toLocaleString()} • {proposal.duration || '6 weeks'}</p>
                          </div>
                          <div className={`status-badge-v2 ${getStatusColor(proposal.status)}`}>
                            {proposal.status || 'Pending'}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state-v2">
                      <div className="empty-icon-v2">
                        <FileText size={40} />
                      </div>
                      <p>No recent proposals</p>
                    </div>
                  )}
                </div>
              </section>
            </div>

            {/* Sidebar Column (Desktop only) */}
            <aside className="layout-sidebar-v2 desktop-only">
              <section className="section-container-v2 sticky-sidebar-v2">
                <div className="section-header-v2">
                  <div className="section-title-v2">
                    <Search size={20} />
                    <h2>Browse Projects</h2>
                  </div>
                </div>
                
                <div className="section-body-v2">
                  <div className="recommended-list-v2">
                    {recommendedProjects && recommendedProjects.length > 0 ? (
                      recommendedProjects.map((project, idx) => (
                        <div key={idx} className="recommended-card-v2">
                          <h4>{project.title}</h4>
                          <div className="rec-meta-v2">
                            <span>{project.category}</span>
                            <span>•</span>
                            <span>{project.experience_level}</span>
                            <span>•</span>
                            <span>Posted 1 day ago</span>
                          </div>
                          
                          <div className="rec-skills-v2">
                            {(project.required_skills || project.skills || "").split(',').slice(0, 3).map((skill, sIdx) => (
                              <span key={sIdx} className="skill-tag-v2">{skill.trim()}</span>
                            ))}
                          </div>
                          
                          <div className="rec-footer-v2">
                            <span className="rec-budget-v2">₹{project.budget_amount?.toLocaleString() || project.budget?.toLocaleString()}</span>
                            <button className="apply-now-btn-v2" onClick={() => handleApplyNow(project.id)}>Apply Now</button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="empty-text-v2">No matching projects found</p>
                    )}
                  </div>
                </div>
              </section>
            </aside>
          </div>
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="mobile-only dashboard-bottom-nav">
        {navItems.map(item => (
          <button 
            key={item.id} 
            className={`mobile-nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => handleNavClick(item.id)}
          >
            <item.icon size={22} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

export default FreelancerDashboard;
