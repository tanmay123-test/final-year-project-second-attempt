import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Clock, 
  Briefcase, 
  ChevronRight, 
  X,
  LayoutDashboard,
  FileText,
  Wallet,
  Calendar,
  DollarSign,
  User
} from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const BrowseProjects = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialSearchQuery = searchParams.get('q') || '';
  
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('browse');
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [searchQuery, setSearchQuery] = useState(initialSearchQuery);
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

  const navItems = [
    { id: 'dashboard', label: 'Home', icon: LayoutDashboard },
    { id: 'browse', label: 'Browse', icon: Search },
    { id: 'proposals', label: 'Proposals', icon: FileText },
    { id: 'work', label: 'My Work', icon: Briefcase },
    { id: 'wallet', label: 'Wallet', icon: Wallet },
  ];

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

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // In browse page, search filters the local list or we can re-fetch
    // For now, let's just update local searchQuery state which filters the list
  };

  const handleNavClick = (id) => {
    setActiveTab(id);
    if (id === 'dashboard') navigate('/freelancer/dashboard');
    else if (id === 'browse') navigate('/freelancer/browse');
    else if (id === 'proposals') navigate('/freelancer/proposals');
    else if (id === 'work') navigate('/freelancer/work');
    else if (id === 'wallet') navigate('/freelancer/wallet');
  };

  const handleApplyClick = (project) => {
    setSelectedProject(project);
    setProposalData({
      proposed_price: project.budget_amount?.toString() || '',
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

  const filteredProjects = projects.filter(project => 
    project.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (project.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
    (project.required_skills || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="freelancer-provider-dashboard browse-projects-page">
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
                className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
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
        <div className="dashboard-inner browse-layout-inner">
          <div className="browse-layout-v2">
            {/* Filters Sidebar */}
            <aside className="filters-sidebar-v2">
              <div className="filters-header-v2">
                <h3>Filters</h3>
              </div>
              
              <div className="filters-body-v2">
                <div className="filter-group-v2">
                  <label>Category</label>
                  <select 
                    value={filters.category} 
                    onChange={(e) => setFilters({...filters, category: e.target.value})}
                  >
                    {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                  </select>
                </div>

                <div className="filter-group-v2">
                  <label>Budget Range</label>
                  <input 
                    type="range" 
                    min="0" 
                    max="10000" 
                    value={filters.budgetRange}
                    onChange={(e) => setFilters({...filters, budgetRange: parseInt(e.target.value)})}
                    className="budget-slider-v2"
                  />
                  <div className="range-labels-v2">
                    <span>$0 - $10000</span>
                  </div>
                </div>

                <div className="filter-group-v2">
                  <label>Skills</label>
                  <div className="skill-input-wrapper-v2">
                    <input 
                      type="text" 
                      placeholder="e.g., React, Python" 
                      value={filters.skills}
                      onChange={(e) => setFilters({...filters, skills: e.target.value})}
                    />
                  </div>
                </div>

                <div className="filter-group-v2">
                  <label>Experience Level</label>
                  <select 
                    value={filters.experienceLevel}
                    onChange={(e) => setFilters({...filters, experienceLevel: e.target.value})}
                  >
                    {expLevels.map(level => <option key={level} value={level}>{level}</option>)}
                  </select>
                </div>

                <button className="clear-filters-btn-v2" onClick={() => setFilters({
                  category: 'All categories',
                  budgetRange: 5000,
                  skills: '',
                  experienceLevel: 'Any level'
                })}>
                  Clear Filters
                </button>
              </div>
            </aside>

            {/* Projects List */}
            <section className="projects-feed-v2">
              <div className="feed-header-v2">
                <h2>Browse Projects</h2>
              </div>

              {loading ? (
                <div className="loading-projects-v2">
                  <div className="skeleton-list">
                    {[1, 2, 3].map(i => <div key={i} className="skeleton skeleton-section"></div>)}
                  </div>
                </div>
              ) : filteredProjects.length === 0 ? (
                <div className="empty-projects-v2">
                  <Briefcase size={48} />
                  <p>No projects found matching your criteria.</p>
                </div>
              ) : (
                <div className="projects-list-v2">
                  {filteredProjects.map(project => (
                    <div key={project.id} className="browse-project-card-v2" onClick={() => handleApplyClick(project)}>
                      <div className="card-top-v2">
                        <div className="title-row-v2">
                          <h3>{project.title}</h3>
                          <span className="status-badge-v2 green">open</span>
                        </div>
                    <div className="card-body-v2">
                      <div className="meta-row-v2">
                        <div className="meta-item-v2">
                          <DollarSign size={16} />
                          <span className="budget-text-v2">₹{project.budget_amount || '3,000 - 5,000'}</span>
                        </div>
                        <div className="meta-item-v2">
                          <Calendar size={16} />
                          <span>{new Date(project.created_at || '2026-04-20').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                        </div>
                      </div>
                      <div className="skills-row-v2">
                        {(project.required_skills || 'React, Node.js, Stripe').split(',').map((skill, i) => (
                          <span key={i} className="skill-tag-v2">{skill.trim()}</span>
                        ))}
                      </div>
                    </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <nav className="mobile-only dashboard-bottom-nav">
        {navItems.map(item => (
          <button 
            key={item.id} 
            className={`mobile-nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => handleNavClick(item.id)}
          >
            <item.icon size={22} />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Apply Modal */}
      {showApplyModal && selectedProject && (
        <div className="modal-overlay-v2">
          <div className="apply-modal-v2">
            <div className="modal-header-v2">
              <h3>Apply for {selectedProject.title}</h3>
              <button className="close-btn-v2" onClick={() => setShowApplyModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleProposalSubmit} className="apply-form-v2">
              <div className="form-group-v2">
                <label>Proposed Price (₹)</label>
                <input 
                  type="number" 
                  value={proposalData.proposed_price}
                  onChange={(e) => setProposalData({...proposalData, proposed_price: e.target.value})}
                  required
                />
              </div>
              <div className="form-group-v2">
                <label>Estimated Delivery Time</label>
                <input 
                  type="text" 
                  placeholder="e.g., 5 days"
                  value={proposalData.delivery_time}
                  onChange={(e) => setProposalData({...proposalData, delivery_time: e.target.value})}
                  required
                />
              </div>
              <div className="form-group-v2">
                <label>Cover Message / Proposal</label>
                <textarea 
                  rows="5"
                  placeholder="Explain why you're the best fit for this project..."
                  value={proposalData.cover_message}
                  onChange={(e) => setProposalData({...proposalData, cover_message: e.target.value})}
                  required
                />
              </div>
              <div className="modal-actions-v2">
                <button type="button" className="cancel-btn-v2" onClick={() => setShowApplyModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn-purple-v2" disabled={submitting}>
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
