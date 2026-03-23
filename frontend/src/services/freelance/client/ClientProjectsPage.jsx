import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Clock, Wallet, Search, Plus, Filter, ArrowRight, FileText, IndianRupee, AlertCircle, XCircle } from 'lucide-react';
import api from '../../../shared/api';
import '../styles/FreelancerDashboard.css';

const ClientProjectsPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('ALL');
  const [projects, setProjects] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [projectsRes, statsRes] = await Promise.all([
        api.get(`/api/freelance/my-projects${activeTab !== 'ALL' ? `?status=${activeTab}` : ''}`),
        api.get('/api/freelance/client/dashboard')
      ]);
      setProjects(projectsRes.data.projects);
      setDashboardStats(statsRes.data.dashboard);
    } catch (error) {
      console.error('Error fetching client projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelProject = async (e, projectId) => {
    e.stopPropagation(); // Prevent navigation to detail page
    if (!window.confirm('Are you sure you want to cancel this project? This action cannot be undone.')) return;
    
    setCancellingId(projectId);
    try {
      await api.post(`/api/freelance/projects/${projectId}/cancel`, {});
      fetchData();
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to cancel project');
    } finally {
      setCancellingId(null);
    }
  };

  const tabs = [
    { id: 'ALL', label: 'All' },
    { id: 'OPEN', label: 'Open' },
    { id: 'IN_PROGRESS', label: 'In Progress' },
    { id: 'COMPLETED', label: 'Completed' },
    { id: 'CANCELLED', label: 'Cancelled' }
  ];

  if (loading && !projects.length) return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Loading your projects...</p>
    </div>
  );

  return (
    <div className="project-detail-container">
      <header className="detail-header">
        <div className="header-main">
          <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>My Projects</h1>
          <p style={{ color: '#6b7280' }}>Manage your posted projects and active contracts</p>
        </div>
        <button className="action-btn-purple" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }} onClick={() => navigate('/freelance/home')}>
          <Plus size={18} /> Post New Project
        </button>
      </header>

      {dashboardStats && (
        <div className="stats-grid" style={{ marginBottom: '3rem' }}>
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#eff6ff', color: '#3b82f6' }}>
              <Plus size={20} />
            </div>
            <div className="stat-info">
              <p>Open</p>
              <h3>{dashboardStats.open_projects || 0}</h3>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#fffbeb', color: '#f59e0b' }}>
              <Clock size={20} />
            </div>
            <div className="stat-info">
              <p>In Progress</p>
              <h3>{dashboardStats.in_progress_projects || 0}</h3>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#f0fdf4', color: '#10b981' }}>
              <Briefcase size={20} />
            </div>
            <div className="stat-info">
              <p>Completed</p>
              <h3>{dashboardStats.completed_projects || 0}</h3>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ backgroundColor: '#f5f3ff', color: '#9B59B6' }}>
              <Wallet size={20} />
            </div>
            <div className="stat-info">
              <p>Total Spent</p>
              <h3>₹{dashboardStats.total_spent?.toLocaleString() || 0}</h3>
            </div>
          </div>
        </div>
      )}

      <div className="segmented-tabs-wrapper" style={{ marginBottom: '2rem' }}>
        <div className="segmented-tabs">
          {tabs.map(tab => (
            <button 
              key={tab.id}
              className={activeTab === tab.id ? 'active' : ''} 
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="projects-list-unified">
        {projects.length === 0 ? (
          <div className="empty-state-dashboard">
            <Briefcase size={60} color="#cbd5e1" style={{ marginBottom: '1.5rem' }} />
            <h3>No projects found</h3>
            <p style={{ maxWidth: '300px', margin: '1rem auto 2rem' }}>
              {activeTab === 'ALL' 
                ? "You haven't posted any projects yet. Start by posting your first project." 
                : `You don't have any projects with status: ${activeTab}.`}
            </p>
            <button className="action-btn-purple" onClick={() => navigate('/freelance/home')}>
              Post your first project
            </button>
          </div>
        ) : (
          projects.map(project => (
            <div 
              key={project.id} 
              className="info-card project-list-card" 
              onClick={() => navigate(`/freelance/project/${project.id}`)}
              style={{ cursor: 'pointer', transition: 'transform 0.2s', position: 'relative' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.5rem' }}>
                    <span className={`status-badge-unified ${project.status.toLowerCase()}`}>
                      {project.status}
                    </span>
                    <span style={{ fontSize: '0.8rem', color: '#9ca3af', fontWeight: 600 }}>{project.category}</span>
                  </div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{project.title}</h3>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#111827' }}>
                    <IndianRupee size={14} style={{ marginBottom: '-2px' }} /> {project.budget?.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{project.budget_type}</div>
                </div>
              </div>

              <div className="card-meta-unified" style={{ padding: '0.8rem 0' }}>
                <div className="meta-item">
                  <FileText size={14} /> <span>{project.proposals_count || 0} Proposals</span>
                </div>
                <div className="meta-item">
                  <Clock size={14} /> <span>Due: {new Date(project.deadline).toLocaleDateString()}</span>
                </div>
                <div className="meta-item">
                  <Calendar size={14} /> <span>Posted: {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="card-actions-unified" style={{ marginTop: '1rem' }}>
                <button 
                  className="action-btn-purple" 
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/freelance/project/${project.id}`);
                  }}
                >
                  View Proposals <ArrowRight size={16} />
                </button>
                {project.status === 'OPEN' && (
                  <button 
                    className="action-btn-outline" 
                    style={{ color: '#ef4444', borderColor: '#fee2e2' }}
                    disabled={cancellingId === project.id}
                    onClick={(e) => handleCancelProject(e, project.id)}
                  >
                    {cancellingId === project.id ? 'Cancelling...' : 'Cancel Project'}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ClientProjectsPage;
