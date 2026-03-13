import React, { useState, useEffect } from 'react';
import { Briefcase, Clock, CheckCircle, AlertCircle, MessageSquare, ChevronRight, MessageCircle, ShieldAlert, User } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelanceHome.css';

const MyProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeStatus, setActiveStatus] = useState('OPEN');

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
                <span className={`status-pill ${project.status.toLowerCase()}`}>
                  {getStatusLabel(project.status)}
                </span>
              </div>
              
              <p className="card-meta">
                {project.category} • {project.experience_level}
              </p>

              <p className="card-description">{project.description}</p>

              <div className="card-details-grid">
                <div className="detail-item">
                  <span className="detail-icon">₹</span>
                  <span>₹{project.budget_amount.toLocaleString()}</span>
                </div>
                <div className="detail-item">
                  <Clock size={16} />
                  <span>{project.deadline}</span>
                </div>
                <div className="detail-item">
                  <MessageSquare size={16} />
                  <span>{project.proposals_count} proposals</span>
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
                      <span className="m-amount">₹{m.amount.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="card-actions">
                {project.status === 'OPEN' && (
                  <button className="primary-action-btn">
                    <User size={18} />
                    View Proposals ({project.proposals_count})
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
    </div>
  );
};

export default MyProjects;
