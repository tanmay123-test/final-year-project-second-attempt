import React, { useState, useEffect } from 'react';
import { Search, Filter, Clock, Briefcase, ChevronRight, X } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const BrowseProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [proposalData, setProposalData] = useState({
    proposed_price: '',
    delivery_time: '',
    cover_message: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [filters, setFilters] = useState({
    category: 'All categories',
    budgetRange: 5000,
    skills: '',
    experienceLevel: 'Any level'
  });

  const categories = ['All categories', 'Web Development', 'App Development', 'UI/UX Design', 'Digital Marketing', 'AI & Machine Learning', 'Content Writing'];
  const expLevels = ['Any level', 'Entry Level', 'Intermediate', 'Expert'];

  useEffect(() => {
    fetchProjects();
  }, [filters.category]);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/freelance/projects${filters.category !== 'All categories' ? `?category=${filters.category}` : ''}`);
      setProjects(response.data.projects);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyClick = (project) => {
    setSelectedProject(project);
    setProposalData({
      proposed_price: project.budget_amount.toString(),
      delivery_time: '7 days',
      cover_message: ''
    });
    setShowApplyModal(true);
  };

  const handleProposalSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/proposals', {
        project_id: selectedProject.id,
        ...proposalData
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Proposal submitted successfully!');
      setShowApplyModal(false);
      setSelectedProject(null);
    } catch (error) {
      console.error('Error submitting proposal:', error);
      const errorMsg = error.response?.data?.error || 'Failed to submit proposal. Please try again.';
      alert(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="browse-projects-container">
      <div className="browse-layout">
        {/* Filters Sidebar */}
        <aside className="filters-sidebar">
          <h3>Filters</h3>
          
          <div className="filter-group">
            <label>Category</label>
            <select 
              value={filters.category} 
              onChange={(e) => setFilters({...filters, category: e.target.value})}
            >
              {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>

          <div className="filter-group">
            <label>Budget Range</label>
            <input 
              type="range" 
              min="0" 
              max="10000" 
              value={filters.budgetRange}
              onChange={(e) => setFilters({...filters, budgetRange: parseInt(e.target.value)})}
            />
            <div className="range-labels">
              <span>₹0</span>
              <span>₹{filters.budgetRange}</span>
            </div>
          </div>

          <div className="filter-group">
            <label>Skills</label>
            <input 
              type="text" 
              placeholder="e.g., React, Python" 
              value={filters.skills}
              onChange={(e) => setFilters({...filters, skills: e.target.value})}
            />
          </div>

          <div className="filter-group">
            <label>Experience Level</label>
            <select 
              value={filters.experienceLevel}
              onChange={(e) => setFilters({...filters, experienceLevel: e.target.value})}
            >
              {expLevels.map(level => <option key={level} value={level}>{level}</option>)}
            </select>
          </div>

          <button className="clear-filters-btn" onClick={() => setFilters({
            category: 'All categories',
            budgetRange: 5000,
            skills: '',
            experienceLevel: 'Any level'
          })}>
            Clear Filters
          </button>
        </aside>

        {/* Projects List */}
        <main className="projects-feed">
          <div className="feed-header">
            <h2>Browse Projects</h2>
          </div>

          {loading ? (
            <div className="loading-projects">
              <div className="spinner"></div>
              <p>Finding the best projects for you...</p>
            </div>
          ) : projects.length === 0 ? (
            <div className="empty-projects">
              <Briefcase size={48} color="#cbd5e1" />
              <p>No projects found matching your criteria.</p>
            </div>
          ) : (
            <div className="projects-grid-vertical">
              {projects.map(project => (
                <div key={project.id} className="browse-project-card">
                  <div className="card-content">
                    <div className="card-header">
                      <h3>{project.title}</h3>
                      <button 
                        className="apply-btn-purple"
                        onClick={() => handleApplyClick(project)}
                      >
                        Apply
                      </button>
                    </div>
                    <div className="card-meta-row">
                      <span className="budget">
                        <span className="currency">$</span> 
                        {project.budget_amount}
                      </span>
                      <span className="date">
                        <Clock size={14} />
                        {new Date(project.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="skills-row">
                      {project.required_skills?.split(',').map(skill => (
                        <span key={skill} className="skill-badge-light">{skill.trim()}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Apply Modal */}
      {showApplyModal && selectedProject && (
        <div className="modal-overlay">
          <div className="apply-modal">
            <div className="modal-header">
              <h3>Apply for {selectedProject.title}</h3>
              <button className="close-btn" onClick={() => setShowApplyModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleProposalSubmit} className="apply-form">
              <div className="form-group">
                <label>Proposed Price ($)</label>
                <input 
                  type="number" 
                  value={proposalData.proposed_price}
                  onChange={(e) => setProposalData({...proposalData, proposed_price: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Estimated Delivery Time</label>
                <input 
                  type="text" 
                  placeholder="e.g., 5 days"
                  value={proposalData.delivery_time}
                  onChange={(e) => setProposalData({...proposalData, delivery_time: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Cover Message / Proposal</label>
                <textarea 
                  rows="5"
                  placeholder="Explain why you're the best fit for this project..."
                  value={proposalData.cover_message}
                  onChange={(e) => setProposalData({...proposalData, cover_message: e.target.value})}
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowApplyModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn-purple" disabled={submitting}>
                  {submitting ? 'Submitting...' : 'Submit Proposal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BrowseProjects;
