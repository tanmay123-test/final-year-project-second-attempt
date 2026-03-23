import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  FileText, 
  ChevronRight, 
  Search, 
  LayoutDashboard, 
  Briefcase, 
  Wallet,
  Trash2,
  User,
  Check,
  X
} from 'lucide-react';
import api from '../../../shared/api';
import '../styles/FreelancerDashboard.css';

const FreelancerProposals = () => {
  const navigate = useNavigate();
  const [activeMainTab, setActiveMainTab] = useState('proposals');
  const [proposals, setProposals] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');
  const [activeNavTab, setActiveNavTab] = useState('proposals');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (activeMainTab === 'proposals') {
      fetchProposals();
    } else {
      fetchBookings();
    }
  }, [activeMainTab, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/freelancer/browse?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const fetchProposals = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/freelancer/proposals/my-proposals?status=${statusFilter.toLowerCase()}`);
      if (response.data.success) {
        setProposals(response.data.proposals);
      }
    } catch (error) {
      console.error('Error fetching proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/freelancer/bookings/direct');
      if (response.data.success) {
        setBookings(response.data.bookings);
      }
    } catch (error) {
      console.error('Error fetching bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async (id) => {
    if (!window.confirm('Are you sure you want to withdraw this proposal?')) return;
    try {
      const response = await api.delete(`/api/freelancer/proposals/${id}`);
      if (response.data.success) {
        setProposals(proposals.filter(p => p.id !== id));
      }
    } catch (error) {
      alert('Failed to withdraw proposal');
    }
  };

  const handleBookingAction = async (id, action) => {
    try {
      const response = await api.put(`/api/freelancer/bookings/${id}/${action}`, {});
      if (response.data.success) {
        // Update local state
        setBookings(bookings.map(b => 
          b.id === id ? { ...b, status: action === 'accept' ? 'ACCEPTED' : 'DECLINED' } : b
        ));
      }
    } catch (error) {
      alert(`Failed to ${action} booking`);
    }
  };

  const getStatusColor = (status) => {
    const s = status?.toLowerCase();
    if (s === 'pending' || s === 'awaiting' || s === 'awaiting response') return 'amber';
    if (s === 'accepted' || s === 'active' || s === 'work in progress') return 'green';
    if (s === 'rejected' || s === 'declined' || s === 'you declined this') return 'red';
    return 'gray';
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

  // Counts for filters
  const counts = {
    All: proposals.length,
    Pending: proposals.filter(p => p.status === 'PENDING').length,
    Accepted: proposals.filter(p => p.status === 'ACCEPTED').length,
    Rejected: proposals.filter(p => p.status === 'REJECTED').length,
  };

  return (
    <div className="freelancer-provider-dashboard proposals-page-v2">
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

      <main className="dashboard-content-v2">
        <div className="dashboard-inner">
          <div className="page-header-v2">
            <h1>My Proposals</h1>
          </div>

          {/* Tab Switcher */}
          <div className="main-tabs-v2">
            <button 
              className={`main-tab-v2 ${activeMainTab === 'proposals' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('proposals')}
            >
              My Proposals
            </button>
            <button 
              className={`main-tab-v2 ${activeMainTab === 'bookings' ? 'active' : ''}`}
              onClick={() => setActiveMainTab('bookings')}
            >
              Direct Bookings
            </button>
          </div>

          {activeMainTab === 'proposals' ? (
            <div className="proposals-section-v2">
              {/* Filter Pills */}
              <div className="filter-pills-v2">
                {['All', 'Pending', 'Accepted', 'Rejected'].map(filter => (
                  <button
                    key={filter}
                    className={`filter-pill-v2 ${statusFilter === filter ? 'active' : ''}`}
                    onClick={() => setStatusFilter(filter)}
                  >
                    {filter} ({counts[filter] || 0})
                  </button>
                ))}
              </div>

              {loading ? (
                <div className="loading-skeleton-v2">
                  {[1, 2, 3].map(i => <div key={i} className="skeleton skeleton-card"></div>)}
                </div>
              ) : proposals.length === 0 ? (
                <div className="empty-state-v2">
                  <FileText size={48} />
                  <p>No proposals found</p>
                </div>
              ) : (
                <div className="cards-list-v2">
                  {proposals.map(proposal => (
                    <div key={proposal.id} className="data-card-v2 proposal-card-v2">
                      <div className="card-info-v2">
                        <h4>{proposal.project_title}</h4>
                        <p>₹{proposal.proposed_price?.toLocaleString()} • {proposal.delivery_time} • {new Date(proposal.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="card-actions-v2">
                        <span className={`status-badge-v2 ${getStatusColor(proposal.status)}`}>
                          {proposal.status}
                        </span>
                        {proposal.status === 'PENDING' && (
                          <button 
                            className="withdraw-btn-v2"
                            onClick={() => handleWithdraw(proposal.id)}
                            title="Withdraw Proposal"
                          >
                            <Trash2 size={18} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="bookings-section-v2">
              <p className="sub-heading-v2">Clients have directly invited you to work on these projects.</p>
              
              {loading ? (
                <div className="loading-skeleton-v2">
                  {[1, 2, 3].map(i => <div key={i} className="skeleton skeleton-card"></div>)}
                </div>
              ) : bookings.length === 0 ? (
                <div className="empty-state-v2">
                  <Briefcase size={48} />
                  <p>No direct bookings yet</p>
                </div>
              ) : (
                <div className="cards-list-v2">
                  {bookings.map(booking => (
                    <div key={booking.id} className="data-card-v2 booking-card-v2">
                      <div className="booking-main-v2">
                        <div className="title-row-v2">
                          <h4>{booking.project_title}</h4>
                          <span className={`status-badge-v2 ${getStatusColor(booking.status === 'AWAITING' ? 'awaiting response' : booking.status)}`}>
                            {booking.status === 'AWAITING' ? 'Awaiting Response' : (booking.status === 'ACCEPTED' ? 'Work in progress' : 'You declined this')}
                          </span>
                        </div>
                        <p className="booking-meta-v2">₹{booking.budget?.toLocaleString()} • {booking.duration || '45 days'} • Deadline: {new Date(booking.deadline).toLocaleDateString()}</p>
                        
                        <div className="client-info-v2">
                          <div className="client-avatar-v2">
                            {booking.client_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'C'}
                          </div>
                          <span>{booking.client_name}</span>
                        </div>
                      </div>

                      {booking.status === 'AWAITING' && (
                        <div className="booking-buttons-v2">
                          <button 
                            className="accept-btn-v2"
                            onClick={() => handleBookingAction(booking.id, 'accept')}
                          >
                            Accept
                          </button>
                          <button 
                            className="decline-btn-v2"
                            onClick={() => handleBookingAction(booking.id, 'decline')}
                          >
                            Decline
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
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

export default FreelancerProposals;
