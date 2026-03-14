import React, { useState, useEffect } from 'react';
import { Home, Search, FileText, Briefcase, Wallet, Bell, Star, CheckCircle, Clock, MessageSquare, Calendar, Check, X } from 'lucide-react';
import axios from 'axios';
import BrowseProjects from './BrowseProjects';
import FreelancerProposals from './FreelancerProposals';
import FreelancerWork from './FreelancerWork';
import '../styles/FreelancerDashboard.css';

const FreelancerDashboard = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [statsData, setStatsData] = useState(null);
  const [notificationsData, setNotificationsData] = useState([]);
  const [bookingsData, setBookingsData] = useState([]);
  const [standardProjects, setStandardProjects] = useState([]);
  const [dashboardTab, setDashboardTab] = useState('posted'); // 'posted' or 'direct'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    // Phase 3: Poll for direct bookings every 5 seconds for status = pending
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [statsRes, bookingsRes, projectsRes] = await Promise.all([
        axios.get('http://localhost:5000/api/freelance/stats', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get('http://localhost:5000/api/freelance/my-bookings', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get('http://localhost:5000/api/freelance/projects', {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      setStatsData(statsRes.data.stats);
      setNotificationsData(statsRes.data.notifications);
      setBookingsData(bookingsRes.data.bookings);
      setStandardProjects(projectsRes.data.projects);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBookingResponse = async (bookingId, status) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/bookings/respond', {
        booking_id: bookingId,
        status: status
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDashboardData();
    } catch (error) {
      console.error('Error responding to booking:', error);
    }
  };

  const ProjectCard = ({ project, type }) => {
    const isDirect = type === 'direct';
    return (
      <div className="project-card-unified">
        <div className="card-header-unified">
          <div className="title-area">
            <h4>{isDirect ? `${project.client_name} — ${project.project_title}` : project.title}</h4>
            {isDirect && <span className="direct-label">Direct Booking</span>}
          </div>
          <span className={`status-badge-unified ${project.status?.toLowerCase() || 'open'}`}>
            {project.status || 'OPEN'}
          </span>
        </div>
        
        <p className="description-text">
          {isDirect ? project.project_description : project.description}
        </p>

        <div className="card-meta-unified">
          <div className="meta-item">
            <Wallet size={14} />
            <span>₹{(isDirect ? project.amount : project.budget_amount).toLocaleString()}</span>
          </div>
          <div className="meta-item">
            <Clock size={14} />
            <span>{new Date(project.created_at).toLocaleDateString()}</span>
          </div>
          {!isDirect && project.category && (
            <div className="meta-item">
              <Briefcase size={14} />
              <span>{project.category}</span>
            </div>
          )}
        </div>

        <div className="card-actions-unified">
          {isDirect ? (
            <div className="booking-actions-bar">
              <button className="accept-btn-v2" onClick={() => handleBookingResponse(project.id, 'ACCEPTED')}>
                <Check size={16} /> Accept
              </button>
              <button className="decline-btn-v2" onClick={() => handleBookingResponse(project.id, 'DECLINED')}>
                <X size={16} /> Decline
              </button>
            </div>
          ) : (
            <>
              <button className="action-btn-outline">View Details</button>
              <button className="action-btn-outline">Message Client</button>
              <button className="action-btn-purple">Send Proposal</button>
            </>
          )}
        </div>
      </div>
    );
  };

  const stats = [
    { label: 'Total Earnings', value: statsData ? `₹${statsData.total_earnings.toLocaleString()}` : '₹0', icon: Wallet, color: '#10b981' },
    { label: 'Active Projects', value: statsData ? statsData.active_projects.toString() : '0', icon: Briefcase, color: '#3b82f6' },
    { label: 'Proposals Sent', value: statsData ? statsData.proposals_sent.toString() : '0', icon: FileText, color: '#6366f1' },
    { label: 'Rating', value: statsData ? statsData.rating.toString() : '0.0', icon: Star, color: '#f59e0b' },
  ];

  const getNotifIcon = (type) => {
    switch (type) {
      case 'PROPOSAL_ACCEPTED': return CheckCircle;
      case 'NEW_MESSAGE': return MessageSquare;
      case 'MILESTONE_SUBMITTED': return Bell;
      default: return Bell;
    }
  };

  const getNotifColor = (type) => {
    switch (type) {
      case 'PROPOSAL_ACCEPTED': return '#10b981';
      case 'NEW_MESSAGE': return '#3b82f6';
      case 'MILESTONE_SUBMITTED': return '#6366f1';
      default: return '#94a3b8';
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <>
            <section className="welcome-section">
              <h1>Freelancer Dashboard</h1>
            </section>

            {/* Stats Grid */}
            <div className="stats-grid">
              {stats.map((stat, i) => (
                <div key={i} className="stat-card">
                  <div className="stat-icon" style={{ backgroundColor: `${stat.color}15`, color: stat.color }}>
                    <stat.icon size={20} />
                  </div>
                  <div className="stat-info">
                    <p>{stat.label}</p>
                    <h3>{stat.value}</h3>
                  </div>
                </div>
              ))}
            </div>

            {/* Segmented Control Tabs */}
            <div className="segmented-tabs-wrapper">
              <div className="segmented-tabs">
                <button 
                  className={dashboardTab === 'posted' ? 'active' : ''} 
                  onClick={() => setDashboardTab('posted')}
                >
                  Posted Projects ({standardProjects.length})
                </button>
                <button 
                  className={dashboardTab === 'direct' ? 'active' : ''} 
                  onClick={() => setDashboardTab('direct')}
                >
                  Direct Bookings ({bookingsData.length})
                </button>
              </div>
            </div>

            {/* Dual Section Content */}
            <section className="dual-projects-section">
              {dashboardTab === 'posted' ? (
                <div className="projects-list-unified">
                  {standardProjects.length === 0 ? (
                    <div className="empty-state-dashboard">
                      <Search size={40} color="#cbd5e1" />
                      <p>No projects posted yet.</p>
                    </div>
                  ) : (
                    standardProjects.map(proj => <ProjectCard key={proj.id} project={proj} type="posted" />)
                  )}
                </div>
              ) : (
                <div className="projects-list-unified">
                  {bookingsData.length === 0 ? (
                    <div className="empty-state-dashboard">
                      <Calendar size={40} color="#cbd5e1" />
                      <p>No direct bookings yet.</p>
                    </div>
                  ) : (
                    bookingsData.map(booking => <ProjectCard key={booking.id} project={booking} type="direct" />)
                  )}
                </div>
              )}
            </section>

            {/* Earnings Chart Placeholder */}
            <section className="earnings-overview">
              <div className="section-header">
                <h3>Earnings Overview</h3>
                <select>
                  <option>This Week</option>
                  <option>This Month</option>
                </select>
              </div>
              <div className="chart-placeholder">
                <div className="chart-empty-message">Earnings chart placeholder</div>
              </div>
            </section>

            {/* Notifications */}
            <section className="notifications-section">
              <div className="section-header">
                <h3><Bell size={18} /> Notifications</h3>
              </div>
              <div className="notifications-list">
                {notificationsData.length === 0 ? (
                  <p className="empty-notif">No new notifications</p>
                ) : (
                  notificationsData.map(notif => (
                    <div key={notif.id} className="notification-item">
                      <div className="notif-icon-circle" style={{ backgroundColor: `${getNotifColor(notif.type)}15`, color: getNotifColor(notif.type) }}>
                        {React.createElement(getNotifIcon(notif.type), { size: 16 })}
                      </div>
                      <div className="notif-content">
                        <p>{notif.message}</p>
                        <span>{new Date(notif.created_at).toLocaleString()}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </>
        );
      case 'browse':
        return <BrowseProjects />;
      case 'proposals':
        return <FreelancerProposals />;
      case 'work':
        return <FreelancerWork />;
      case 'wallet':
        return (
          <div className="placeholder-content">
            <Wallet size={48} color="#9B59B6" />
            <h3>My Earnings</h3>
            <p>Withdraw funds and view transaction history.</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="freelancer-dashboard">
      <main className="dashboard-main">
        {renderContent()}
      </main>

      {/* Bottom Navigation */}
      <nav className="dashboard-bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <Home size={22} />
          <span>Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'browse' ? 'active' : ''}`}
          onClick={() => setActiveTab('browse')}
        >
          <Search size={22} />
          <span>Browse</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'proposals' ? 'active' : ''}`}
          onClick={() => setActiveTab('proposals')}
        >
          <FileText size={22} />
          <span>Proposals</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'work' ? 'active' : ''}`}
          onClick={() => setActiveTab('work')}
        >
          <Briefcase size={22} />
          <span>My Work</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'wallet' ? 'active' : ''}`}
          onClick={() => setActiveTab('wallet')}
        >
          <Wallet size={22} />
          <span>Wallet</span>
        </button>
      </nav>
    </div>
  );
};

export default FreelancerDashboard;
