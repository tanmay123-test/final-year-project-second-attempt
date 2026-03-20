import React, { useState, useEffect } from 'react';
import { Briefcase, Clock, CheckCircle, AlertCircle, MessageSquare, ChevronRight } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelanceHome.css';

const MyProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMyProjects();
  }, []);

  const fetchMyProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      // Note: We'll need a specific endpoint for user's own projects
      const response = await axios.get('http://localhost:5000/api/freelance/my-projects', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data.projects);
    } catch (err) {
      setError('Failed to load your projects');
      // Fallback dummy data for demo
      setProjects([
        {
          id: 1,
          title: 'E-commerce App Development',
          status: 'IN_PROGRESS',
          proposals_count: 12,
          budget_amount: 45000,
          created_at: '2024-03-01',
          freelancer: 'Aditya Verma'
        },
        {
          id: 2,
          title: 'Logo Design for Startup',
          status: 'OPEN',
          proposals_count: 5,
          budget_amount: 5000,
          created_at: '2024-03-05'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'OPEN': return <Clock size={16} className="text-blue" />;
      case 'IN_PROGRESS': return <AlertCircle size={16} className="text-orange" />;
      case 'COMPLETED': return <CheckCircle size={16} className="text-green" />;
      default: return <Clock size={16} />;
    }
  };

  return (
    <div className="my-projects-container">
      <header className="page-header">
        <h2>My Projects</h2>
      </header>

      {loading ? (
        <div className="loading-state">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <Briefcase size={48} />
          <p>You haven't posted any projects yet.</p>
        </div>
      ) : (
        <div className="projects-list">
          {projects.map(project => (
            <div key={project.id} className="project-status-card">
              <div className="status-badge">
                {getStatusIcon(project.status)}
                <span>{project.status.replace('_', ' ')}</span>
              </div>
              
              <div className="project-main">
                <h3>{project.title}</h3>
                <p className="budget">Budget: ₹{project.budget_amount}</p>
              </div>

              <div className="project-stats">
                <div className="stat">
                  <MessageSquare size={14} />
                  <span>{project.proposals_count} Proposals</span>
                </div>
                <div className="stat">
                  <Clock size={14} />
                  <span>Posted {new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {project.freelancer && (
                <div className="assigned-freelancer">
                  <span>Working with: <strong>{project.freelancer}</strong></span>
                </div>
              )}

              <button className="view-details-btn">
                View Details <ChevronRight size={16} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyProjects;
