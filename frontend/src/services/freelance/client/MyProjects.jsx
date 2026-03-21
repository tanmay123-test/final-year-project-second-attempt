import React, { useState, useEffect } from 'react';
import { 
  Briefcase, Clock, CheckCircle, AlertCircle, MessageSquare, 
  ChevronRight, MessageCircle, ShieldAlert, User, XCircle, 
  Home, PlusCircle, Folder, Bot, Search, IndianRupee 
} from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import '../styles/MyProjects.css';
import ProjectDetailsModal from './ProjectDetailsModal';

const MyProjects = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [viewMode, setViewMode] = useState('posted'); // 'posted' or 'direct'
  const [projects, setProjects] = useState([]);
  const [directBookings, setDirectBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeStatus, setActiveStatus] = useState('OPEN');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [milestones, setMilestones] = useState([]);
  
  const statusTabs = [
    { label: 'Open', value: 'OPEN' },
    { label: 'Active', value: 'IN_PROGRESS' },
    { label: 'Done', value: 'COMPLETED' },
    { label: 'Cancelled', value: 'CANCELLED' }
  ];

  useEffect(() => {
    const sub = searchParams.get('sub');
    const view = searchParams.get('view');

    if (sub === 'direct' || view === 'direct') {
      setViewMode('direct');
    } else {
      setViewMode('posted');
    }
  }, [searchParams]);

  useEffect(() => {
    if (viewMode === 'posted') {
      fetchMyProjects();
    } else {
      fetchDirectBookings();
    }
  }, [activeStatus, viewMode]);

  const fetchMyProjects = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/freelancer/projects/my-projects?status=${activeStatus}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data.projects || []);
      setError('');
    } catch (err) {
      setError('Failed to load your projects');
    } finally {
      setLoading(false);
    }
  };

  const fetchDirectBookings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:5000/api/freelancer/bookings/my-bookings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDirectBookings(response.data.bookings || []);
      setError('');
    } catch (err) {
      setError('Failed to load direct bookings');
    } finally {
      setLoading(false);
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'OPEN': return 'Open';
      case 'IN_PROGRESS': return 'Active';
      case 'COMPLETED': return 'Done';
      case 'CANCELLED': return 'Cancelled';
      default: return status;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'OPEN': return 'status-open';
      case 'IN_PROGRESS': return 'status-active';
      case 'COMPLETED': return 'status-done';
      case 'CANCELLED': return 'status-cancelled';
      default: return '';
    }
  };

  const handleViewProposals = async (project) => {
    setSelectedProject(project);
    setIsModalOpen(true);

    try {
      const token = localStorage.getItem('token');
      const proposalsRes = await axios.get(`http://localhost:5000/api/freelance/projects/${project.id}/proposals`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProposals(proposalsRes.data.proposals || []);

      // Milestones are already part of the project object from the main list
      setMilestones(project.milestones || []); 

    } catch (err) {
      console.error("Error fetching project details:", err);
      // Handle error display if needed
    }
  };

  return (
    <div className="my-projects-page">
      <div className="my-projects-hero">
        <div className="hero-content">
          <h1>My Projects</h1>
          <p>Track and manage your posted projects</p>
        </div>
      </div>

      <div className="projects-content-wrapper">
        {/* Toggle Tabs */}
        <div className="view-mode-tabs">
          <button 
            className={viewMode === 'posted' ? 'active' : ''} 
            onClick={() => setSearchParams({ view: 'posted' })}
          >
            Posted Projects
          </button>
          <button 
            className={viewMode === 'direct' ? 'active' : ''} 
            onClick={() => setSearchParams({ view: 'direct' })}
          >
            Direct Bookings
          </button>
        </div>

        {/* Filter Tabs (Pill shaped) */}
        {viewMode === 'posted' && (
          <div className="filter-pills-container">
            {statusTabs.map(tab => (
              <button
                key={tab.value}
                className={`filter-pill ${activeStatus === tab.value ? 'active' : ''}`}
                onClick={() => setActiveStatus(tab.value)}
              >
                {tab.label}
              </button>
            ))}
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="spinner-purple"></div>
            <p>Loading your engagements...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <AlertCircle size={40} color="#ef4444" />
            <p>{error}</p>
          </div>
        ) : (
          <div className="projects-list-container">
            {viewMode === 'posted' ? (
              projects.length === 0 ? (
                <div className="empty-state-card">
                  <Briefcase size={48} color="#cbd5e1" />
                  <h3>No {activeStatus.toLowerCase()} projects found</h3>
                  <p>You haven't posted any projects with this status yet.</p>
                  <button className="post-btn-empty" onClick={() => navigate('/freelance/home?tab=post')}>Post a Project</button>
                </div>
              ) : (
                projects.map(project => (
                  <div key={project.id} className="project-card-v3">
                    <div className="card-header-v3">
                      <div className="header-main-v3">
                        <h3>{project.title}</h3>
                        <div className="tags-row-v3">
                          <span className="tag-v3">{project.category || 'web'}</span>
                          <span className="tag-v3">{project.experience_level || 'expert'}</span>
                        </div>
                      </div>
                      <span className={`status-badge-v3 ${getStatusClass(project.status || 'OPEN')}`}>
                        {getStatusLabel(project.status || 'OPEN')}
                      </span>
                    </div>

                    <p className="description-v3">{project.description}</p>

                    <div className="meta-grid-v3">
                      <div className="meta-item-v3">
                        <IndianRupee size={16} />
                        <span>₹{(project.budget_amount || 0).toLocaleString()}</span>
                      </div>
                      <div className="meta-item-v3">
                        <Clock size={16} />
                        <span>{project.deadline || '2026-04-15'}</span>
                      </div>
                      <div className="meta-item-v3">
                        <User size={16} />
                        <span>{project.proposals_count || 0} proposals</span>
                      </div>
                    </div>

                    {project.milestones && project.milestones.length > 0 && (
                      <div className="milestones-section-v3">
                        <label>MILESTONES</label>
                        {project.milestones.map((m, idx) => (
                          <div key={idx} className="milestone-row-v3">
                            <div className="m-info-v3">
                              <CheckCircle size={16} color="#534AB7" />
                              <span>{m.title}</span>
                            </div>
                            <span className="m-amount-v3">₹{(m.amount || 0).toLocaleString()}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    <button 
                      className="view-proposals-btn-v3"
                      onClick={() => handleViewProposals(project)}
                    >
                      <User size={18} />
                      View Proposals ({project.proposals_count || 0})
                    </button>
                  </div>
                ))
              )
            ) : (
              /* Direct Bookings View */
              directBookings.length === 0 ? (
                <div className="empty-state-card">
                  <ShieldAlert size={48} color="#cbd5e1" />
                  <h3>No direct bookings yet</h3>
                  <p>When you hire freelancers directly, they will appear here.</p>
                  <button className="post-btn-empty" onClick={() => navigate('/freelance/home?tab=find')}>Find Freelancers</button>
                </div>
              ) : (
                directBookings.map(booking => (
                  <div key={booking.id} className="project-card-v3">
                    <div className="card-header-v3">
                      <div className="header-main-v3">
                        <h3>{booking.project_title}</h3>
                        <p className="booking-freelancer-name">Hired: <strong>{booking.freelancer_name}</strong></p>
                      </div>
                      <span className={`status-badge-v3 status-active`}>
                        {booking.status}
                      </span>
                    </div>
                    
                    <p className="description-v3">{booking.project_description}</p>

                    <div className="meta-grid-v3">
                      <div className="meta-item-v3">
                        <IndianRupee size={16} />
                        <span>₹{(booking.amount || 0).toLocaleString()}</span>
                      </div>
                      <div className="meta-item-v3">
                        <Clock size={16} />
                        <span>{new Date(booking.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <button className="view-proposals-btn-v3" onClick={() => navigate(`/freelance/project/${booking.id}`)}>
                      View Booking Details
                    </button>
                  </div>
                ))
              )
            )}
          </div>
        )}
      </div>

      {isModalOpen && (
        <ProjectDetailsModal 
          project={selectedProject}
          proposals={proposals}
          milestones={milestones}
          onClose={() => setIsModalOpen(false)}
          onAction={() => {
            setIsModalOpen(false);
            fetchMyProjects();
          }}
        />
      )}
    </div>
  );
};

export default MyProjects;
