import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Wallet, Clock, Briefcase, Star, User, CheckCircle, ExternalLink, IndianRupee, Shield, Calendar, AlertCircle } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const ProjectDetailPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [acceptingId, setAcceptingId] = useState(null);

  useEffect(() => {
    fetchProjectDetail();
  }, [projectId]);

  const fetchProjectDetail = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/freelance/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProject(response.data.project);
      setProposals(response.data.project.proposals || []);
      setError(null);
    } catch (err) {
      setError('Failed to load project details. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptProposal = async (proposalId) => {
    if (!window.confirm('Are you sure you want to accept this proposal? This will start the contract.')) return;
    
    setAcceptingId(proposalId);
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/proposals/accept', 
        { proposal_id: proposalId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Success state is handled by re-fetching project detail
      await fetchProjectDetail();
      alert('Proposal accepted! The project is now in progress.');
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to accept proposal. Please try again.');
    } finally {
      setAcceptingId(null);
    }
  };

  if (loading) return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Loading project details...</p>
    </div>
  );

  if (error || !project) return (
    <div className="empty-state-dashboard" style={{ margin: '2rem' }}>
      <AlertCircle size={48} color="#ef4444" />
      <h3>Error</h3>
      <p>{error || 'Project not found'}</p>
      <button className="action-btn-purple" onClick={() => navigate(-1)}>Go Back</button>
    </div>
  );

  const isOwner = true; // In a real app, check if project.client_id === currentUserId

  return (
    <div className="project-detail-container">
      <button className="back-btn" onClick={() => navigate(-1)}>
        <ArrowLeft size={18} /> Back to Projects
      </button>

      <header className="detail-header">
        <div className="header-main">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
            <span className={`status-badge-unified ${project.status.toLowerCase()}`}>
              {project.status}
            </span>
            <span className="category-tag">{project.category}</span>
          </div>
          <h1>{project.title}</h1>
          <div className="header-meta">
            <span><Calendar size={14} /> Posted on {new Date(project.created_at).toLocaleDateString()}</span>
            <span><User size={14} /> Client: {project.client_name || 'ExpertEase User'}</span>
          </div>
        </div>
      </header>

      {project.status === 'IN_PROGRESS' && (
        <div className="info-card" style={{ borderLeft: '4px solid #9B59B6', background: '#f5f3ff', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ color: '#6b21a8', marginBottom: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Shield size={18} /> Contract Active
              </h4>
              <p style={{ fontSize: '0.9rem', color: '#6b21a8' }}>Work is underway. You can manage milestones and chat with the freelancer.</p>
            </div>
            <button className="action-btn-purple" onClick={() => navigate(`/freelancer/dashboard`)}>
              View Active Work
            </button>
          </div>
        </div>
      )}

      <div className="info-card">
        <h3>Project Description</h3>
        <p className="description-text">{project.description}</p>
        
        <div className="info-grid">
          <div className="info-item">
            <label>Budget</label>
            <p><IndianRupee size={16} /> {project.budget?.toLocaleString()} ({project.budget_type})</p>
          </div>
          <div className="info-item">
            <label>Deadline</label>
            <p><Clock size={16} /> {new Date(project.deadline).toLocaleDateString()}</p>
          </div>
          <div className="info-item">
            <label>Experience Level</label>
            <p><Star size={16} /> {project.experience_level}</p>
          </div>
        </div>

        <div style={{ marginTop: '2rem' }}>
          <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase' }}>Required Skills</label>
          <div className="skills-list" style={{ marginTop: '0.5rem' }}>
            {project.required_skills?.split(',').map((skill, index) => (
              <span key={index} className="skill-badge">{skill.trim()}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Milestones Section */}
      <section className="milestones-section" style={{ marginBottom: '3rem' }}>
        <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.5rem' }}>Project Milestones</h3>
        <div className="milestones-list">
          {project.milestones && project.milestones.length > 0 ? (
            project.milestones.map((milestone, index) => (
              <div key={index} className="milestone-card" style={{ 
                background: 'white', padding: '1.5rem', borderRadius: '16px', border: '1px solid #e5e7eb',
                marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
              }}>
                <div>
                  <h5 style={{ fontWeight: 700, marginBottom: '0.2rem' }}>{milestone.title}</h5>
                  <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>Amount: ₹{milestone.amount.toLocaleString()}</p>
                </div>
                <span className={`status-badge-unified ${milestone.status.toLowerCase()}`}>
                  {milestone.status}
                </span>
              </div>
            ))
          ) : (
            <p style={{ color: '#9ca3af', textAlign: 'center', padding: '2rem', background: 'white', borderRadius: '16px' }}>
              No milestones defined for this project.
            </p>
          )}
        </div>
      </section>

      {/* Proposals Section (Only for Client) */}
      {isOwner && (
        <section className="proposals-section">
          <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Received Proposals ({proposals.length})</h3>
          </div>
          
          {proposals.length === 0 ? (
            <div className="empty-state-dashboard">
              <User size={40} color="#cbd5e1" />
              <p>No proposals received yet. Your project is still being reviewed by freelancers.</p>
            </div>
          ) : (
            <div className="proposals-list" style={{ display: 'grid', gap: '1.5rem' }}>
              {proposals.map((proposal) => (
                <div key={proposal.id} className="info-card" style={{ margin: 0 }}>
                  <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    <div className="user-avatar" style={{ width: '60px', height: '60px', fontSize: '1.5rem', borderRadius: '16px' }}>
                      {proposal.freelancer_name?.charAt(0)}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <h4 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.2rem' }}>{proposal.freelancer_name}</h4>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f59e0b' }}>
                            <Star size={14} fill="#f59e0b" />
                            <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{proposal.rating || '5.0'}</span>
                            <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>({proposal.completed_projects || 0} projects)</span>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#111827' }}>₹{proposal.proposed_price?.toLocaleString()}</div>
                          <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>Delivery in {proposal.delivery_time} days</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div style={{ marginBottom: '1.5rem' }}>
                    <h5 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#4b5563', marginBottom: '0.5rem' }}>Cover Message</h5>
                    <p style={{ fontSize: '0.9rem', color: '#4b5563', lineHeight: 1.6 }}>
                      {proposal.cover_message}
                    </p>
                  </div>

                  <div className="skills-list" style={{ marginBottom: '1.5rem' }}>
                    {proposal.skills?.split(',').map((skill, idx) => (
                      <span key={idx} className="skill-badge" style={{ background: '#f3f4f6', color: '#4b5563' }}>{skill.trim()}</span>
                    ))}
                  </div>

                  <div className="card-actions-unified">
                    <button 
                      className="action-btn-purple" 
                      style={{ flex: 1 }}
                      disabled={project.status !== 'OPEN' || acceptingId === proposal.id}
                      onClick={() => handleAcceptProposal(proposal.id)}
                    >
                      {acceptingId === proposal.id ? 'Accepting...' : project.status === 'OPEN' ? 'Accept Proposal' : 'Proposal Accepted'}
                    </button>
                    <button 
                      className="action-btn-outline" 
                      style={{ flex: 1 }}
                      onClick={() => navigate(`/freelance/freelancer/${proposal.freelancer_id}`)}
                    >
                      View Profile
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default ProjectDetailPage;
