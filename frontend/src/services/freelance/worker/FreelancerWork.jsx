import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Briefcase, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  MessageSquare, 
  Send, 
  Upload, 
  ChevronDown, 
  ChevronUp,
  LayoutDashboard,
  Search,
  FileText,
  Wallet,
  User,
  MoreHorizontal
} from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const FreelancerWork = () => {
  const navigate = useNavigate();
  const [activeMainTab, setActiveMainTab] = useState('active');
  const [activeNavTab, setActiveNavTab] = useState('work');
  const [activeWork, setActiveWork] = useState([]);
  const [directBookings, setDirectBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchWorkData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/freelancer/browse?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  useEffect(() => {
    if (activeProjectId) {
      fetchMessages(activeProjectId);
      const interval = setInterval(() => fetchMessages(activeProjectId), 5000);
      return () => clearInterval(interval);
    }
  }, [activeProjectId]);

  const fetchWorkData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const [workRes, bookingsRes] = await Promise.all([
        axios.get('http://localhost:5000/api/freelancer/work/my-work', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('http://localhost:5000/api/freelancer/bookings/direct', { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      if (workRes.data.success) {
        setActiveWork(workRes.data.work);
        if (workRes.data.work.length > 0) {
          setActiveProjectId(workRes.data.work[0].project_id);
        }
      }
      if (bookingsRes.data.success) {
        setDirectBookings(bookingsRes.data.bookings.filter(b => b.status === 'ACCEPTED' || b.status === 'COMPLETED'));
      }
    } catch (error) {
      console.error('Error fetching work data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (projectId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/freelancer/work/${projectId}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setMessages(response.data.messages);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeProjectId) return;
    
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`http://localhost:5000/api/freelancer/work/${activeProjectId}/messages`, {
        message: newMessage
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setNewMessage('');
        fetchMessages(activeProjectId);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleSubmitMilestone = async (milestoneId) => {
    if (!window.confirm('Mark this milestone as submitted?')) return;
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`http://localhost:5000/api/freelancer/work/${activeProjectId}/submit-milestone`, {
        milestoneId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        fetchWorkData();
      }
    } catch (error) {
      alert('Failed to submit milestone');
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'browse', label: 'Browse', icon: Search },
    { id: 'proposals', label: 'Proposals', icon: FileText },
    { id: 'work', label: 'My Work', icon: Briefcase },
    { id: 'wallet', label: 'Wallet', icon: Wallet },
  ];

  const handleNavClick = (id) => {
    setActiveNavTab(id);
    if (id === 'dashboard') navigate('/freelancer/dashboard');
    else if (id === 'browse') navigate('/freelancer/browse');
    else if (id === 'proposals') navigate('/freelancer/proposals');
    else if (id === 'work') navigate('/freelancer/work');
    else if (id === 'wallet') navigate('/freelancer/wallet');
  };

  const activeProject = activeWork.find(p => p.project_id === activeProjectId);

  if (loading) {
    return (
      <div className="dashboard-loading-v2">
        <div className="skeleton-hero"></div>
        <div className="skeleton-grid">
          {[1, 2, 3].map(i => <div key={i} className="skeleton skeleton-card"></div>)}
        </div>
      </div>
    );
  }

  return (
    <div className="freelancer-provider-dashboard my-work-page-v2">
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
                className={`nav-link ${activeNavTab === item.id ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </button>
            ))}
            <div className="user-profile-circle">S</div>
          </nav>
        </div>
      </header>

      {/* Mobile Hero Header */}
      <div className="mobile-only work-hero-header-v2">
        <h1>My Work</h1>
      </div>

      <main className="dashboard-content-v2">
        <div className="dashboard-inner">
          <div className="page-header-v2 desktop-only">
            <h1>My Work</h1>
          </div>

          {/* Project Selection Tabs (Horizontal Scroll on Mobile) */}
          <div className="project-tabs-scroll-v2">
            {activeWork.map(project => (
              <button 
                key={project.project_id}
                className={`project-tab-v2 ${activeProjectId === project.project_id ? 'active' : ''}`}
                onClick={() => setActiveProjectId(project.project_id)}
              >
                {project.title}
              </button>
            ))}
          </div>

          {activeProject && (
            <div className="active-project-view-v2">
              <div className="project-card-header-v2">
                <div className="title-row-v2">
                  <h3>{activeProject.title}</h3>
                  <div className="status-badges-v2">
                    <span className="status-badge-v2 green">In Progress</span>
                    <span className="status-badge-v2 indigo">Project Hire</span>
                  </div>
                </div>
                
                <div className="project-details-v2">
                  <label>Project Details</label>
                  <p>{activeProject.description}</p>
                </div>

                <div className="milestones-section-v2">
                  <label>Milestones</label>
                  <div className="milestones-list-v2">
                    {activeProject.milestones?.map(m => (
                      <div key={m.id} className="milestone-item-v2">
                        <span className="m-name-v2">{m.title}</span>
                        <span className={`status-badge-v2 ${m.status.toLowerCase()}`}>
                          {m.status.charAt(0).toUpperCase() + m.status.slice(1).toLowerCase()}
                        </span>
                        {m.status === 'PENDING' && (
                          <button 
                            className="m-submit-btn-v2"
                            onClick={() => handleSubmitMilestone(m.id)}
                          >
                            Submit
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="deliverables-section-v2">
                  <label>Upload Deliverables</label>
                  <div className="upload-box-v2">
                    <Upload size={32} />
                    <p>Drag & drop files or click to upload</p>
                  </div>
                  <div className="action-buttons-v2">
                    <button className="btn-outline-v2">
                      <CheckCircle size={18} />
                      Submit Milestone
                    </button>
                    <button className="btn-outline-v2">
                      Mark Complete
                    </button>
                  </div>
                </div>

                {/* Messages Card */}
                <div className="messages-card-v2">
                  <div className="messages-header-v2">
                    <h3>Messages</h3>
                  </div>
                  <div className="messages-body-v2">
                    {messages.map((msg, idx) => (
                      <div key={idx} className={`msg-wrapper-v2 ${msg.sender_id === activeProject.freelancer_id ? 'sent' : 'received'}`}>
                        <div className="msg-bubble-v2">
                          <p>{msg.message}</p>
                          <span className="msg-time-v2">
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <form onSubmit={handleSendMessage} className="msg-input-v2">
                    <input 
                      type="text" 
                      placeholder="Type a message..." 
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                    />
                    <button type="submit" className="send-btn-v2">
                      <Send size={18} />
                    </button>
                  </form>
                </div>
              </div>
            </div>
          )}

          {/* Direct Bookings Section */}
          <section className="section-container-v2 direct-bookings-section-v2">
            <div className="section-header-v2">
              <div className="section-title-v2">
                <User size={20} />
                <h2>Direct Bookings</h2>
              </div>
              <p className="sub-heading-v2">Clients who directly hired you — manage your work and communication here</p>
            </div>
            
            <div className="section-body-v2">
              <div className="cards-list-v2">
                {directBookings.length === 0 ? (
                  <div className="empty-state-v2">
                    <p>No direct bookings found</p>
                  </div>
                ) : (
                  directBookings.map(booking => (
                    <div key={booking.id} className="data-card-v2 booking-work-card-v2">
                      <div className="booking-info-v2">
                        <div className="title-row-v2">
                          <h4>{booking.project_title}</h4>
                          <span className={`status-badge-v2 ${booking.status.toLowerCase()}`}>
                            {booking.status === 'ACCEPTED' ? 'In Progress' : 'Completed'}
                          </span>
                        </div>
                        <p className="meta-text-v2">₹{booking.budget?.toLocaleString()} • {booking.duration || '45 days'} • Deadline: {new Date(booking.deadline).toLocaleDateString()}</p>
                        
                        <div className="client-footer-v2">
                          <div className="client-info-v2">
                            <div className="client-avatar-v2">
                              {booking.client_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'C'}
                            </div>
                            <span>{booking.client_name}</span>
                          </div>
                          
                          {booking.status === 'ACCEPTED' ? (
                            <button className="view-work-btn-v2">View Work</button>
                          ) : (
                            <span className="payment-released-v2">Payment released ✓</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="mobile-only dashboard-bottom-nav">
        {navItems.map(item => (
          <button 
            key={item.id} 
            className={`mobile-nav-item ${activeNavTab === item.id ? 'active' : ''}`}
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

export default FreelancerWork;
