import React, { useState, useEffect } from 'react';
import { Briefcase, Clock, CheckCircle, AlertCircle, MessageSquare, ChevronRight, MessageCircle, ShieldAlert, User, XCircle } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelanceHome.css';

const MyProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeStatus, setActiveStatus] = useState('OPEN');
  
  // Proposals View State
  const [selectedProject, setSelectedProject] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [loadingProposals, setLoadingProposals] = useState(false);
  const [showProposalsModal, setShowProposalsModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const statusTabs = [
    { label: 'Open', value: 'OPEN' },
    { label: 'Active', value: 'IN_PROGRESS' },
    { label: 'Done', value: 'COMPLETED' },
    { label: 'Cancelled', value: 'CANCELLED' }
  ];

  useEffect(() => {
    fetchMyProjects();
  }, [activeStatus]);

  const fetchMyProjects = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/freelance/my-projects?status=${activeStatus}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data.projects);
    } catch (err) {
      setError('Failed to load your projects');
    } finally {
      setLoading(false);
    }
  };

  const handleViewProposals = async (project) => {
    setSelectedProject(project);
    setShowProposalsModal(true);
    setLoadingProposals(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/freelance/projects/${project.id}/proposals`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProposals(Array.isArray(response.data.proposals) ? response.data.proposals : []);
    } catch (err) {
      console.error('Error fetching proposals:', err);
      setProposals([]);
    } finally {
      setLoadingProposals(false);
    }
  };

  const handleAcceptProposal = async (proposalId) => {
    if (!window.confirm('Are you sure you want to accept this proposal? This will start the project.')) return;
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/proposals/accept', {
        proposal_id: proposalId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Proposal accepted! Project is now in progress.');
      setShowProposalsModal(false);
      fetchMyProjects(); // Refresh list
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Failed to accept proposal. Please try again.';
      alert(errorMsg);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'OPEN': return 'Open';
      case 'IN_PROGRESS': return 'In Progress';
      case 'COMPLETED': return 'Completed';
      case 'CANCELLED': return 'Cancelled';
      default: return status;
    }
  };

  return (
    <div className="my-projects-container">
      {/* Header Banner */}
      <div className="my-projects-hero">
        <h1>My Projects</h1>
        <p>Track and manage your posted projects</p>
      </div>

      {/* Status Tabs */}
      <div className="status-tabs-container">
        {statusTabs.map(tab => (
          <button
            key={tab.value}
            className={`status-tab ${activeStatus === tab.value ? 'active' : ''}`}
            onClick={() => setActiveStatus(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner-purple"></div>
          <p>Fetching your projects...</p>
        </div>
      ) : error ? (
        <div className="error-state">{error}</div>
      ) : projects.length === 0 ? (
        <div className="empty-state-new">
          <p>No {activeStatus.toLowerCase().replace('_', ' ')} projects</p>
        </div>
      ) : (
        <div className="projects-list-new">
          {projects.map(project => (
            <div key={project.id} className="project-card-new">
              <div className="card-header-row">
                <h3>{project.title}</h3>
                <span className={`status-pill ${(project.status || 'OPEN').toLowerCase()}`}>
                  {getStatusLabel(project.status || 'OPEN')}
                </span>
              </div>
              
              <p className="card-meta">
                {project.category || 'General'} • {project.experience_level || 'Any level'}
              </p>

              <p className="card-description">{project.description}</p>

              {project.status === 'IN_PROGRESS' && project.freelancer_name && (
                <div className="active-freelancer-info">
                  <User size={16} />
                  <span>Working with: <strong>{project.freelancer_name}</strong></span>
                </div>
              )}

              <div className="card-details-grid">
                <div className="detail-item">
                  <span className="detail-icon">₹</span>
                  <span>₹{(project.budget_amount || 0).toLocaleString()}</span>
                </div>
                <div className="detail-item">
                  <Clock size={16} />
                  <span>{project.deadline || 'No deadline'}</span>
                </div>
                <div className="detail-item">
                  <MessageSquare size={16} />
                  <span>{project.proposals_count || 0} proposals</span>
                </div>
              </div>

              {project.milestones && project.milestones.length > 0 && (
                <div className="milestones-preview">
                  <label>Milestones</label>
                  {project.milestones.map((m, idx) => (
                    <div key={idx} className="milestone-preview-row">
                      <div className="m-left">
                        <CheckCircle size={14} className={m.status === 'PAID' ? 'text-green' : 'text-gray'} />
                        <span>{m.title}</span>
                      </div>
                      <span className="m-amount">₹{(m.amount || 0).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="card-actions">
                {(project.status === 'OPEN' || !project.status) && (
                  <button 
                    className="primary-action-btn"
                    onClick={() => handleViewProposals(project)}
                  >
                    <User size={18} />
                    View Proposals ({project.proposals_count || 0})
                  </button>
                )}
                {project.status === 'IN_PROGRESS' && (
                  <>
                    <button className="secondary-action-btn">
                      <MessageCircle size={18} />
                      Chat
                    </button>
                    <button className="danger-action-btn">
                      <ShieldAlert size={18} />
                      Dispute
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Proposals Modal */}
      {showProposalsModal && selectedProject && (
        <div className="modal-overlay-new">
          <div className="modal-content-new">
            <div className="modal-header-new">
              <h2>Proposals for "{selectedProject.title}"</h2>
              <button className="close-btn-new" onClick={() => setShowProposalsModal(false)}>
                <XCircle size={20} />
              </button>
            </div>
            
            <div className="modal-body-new">
              {loadingProposals ? (
                <div className="loading-state">
                  <div className="spinner-purple"></div>
                  <p>Loading proposals...</p>
                </div>
              ) : proposals.length === 0 ? (
                <div className="empty-state-new">
                  <p>No proposals received yet.</p>
                </div>
              ) : (
                <div className="proposals-list-modal">
                  {proposals.map(proposal => (
                    <div key={proposal.id} className="proposal-item-card">
                      <div className="proposal-card-top">
                        <div className="freelancer-info-row">
                          <div className="f-avatar-small">
                            <User size={18} />
                          </div>
                          <span className="f-name-small">{proposal.freelancer_name || `Freelancer #${proposal.freelancer_id}`}</span>
                        </div>
                        <div className="proposal-rating-small">
                          {proposal.freelancer_rating ? `★ ${proposal.freelancer_rating}` : 'New'}
                        </div>
                        <span className="proposal-price-tag">₹{proposal.proposed_price.toLocaleString()}</span>
                      </div>

                      <p className="proposal-msg-text">{proposal.cover_message}</p>

                      <div className="proposal-meta-row">
                        <div className="p-meta-item">
                          <Clock size={14} />
                          <span>{proposal.delivery_time}</span>
                        </div>
                        <div className="p-meta-item">
                          <ShieldAlert size={14} />
                          <span>Verified Pro</span>
                        </div>
                      </div>

                      <div className="proposal-actions-row">
                        <button 
                          className="accept-proposal-btn"
                          onClick={() => handleAcceptProposal(proposal.id)}
                          disabled={actionLoading}
                        >
                          {actionLoading ? 'Accepting...' : 'Accept Proposal'}
                        </button>
                        <button className="reject-proposal-btn" disabled={actionLoading}>
                          Decline
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyProjects;
