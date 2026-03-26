import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Star, 
  Clock, 
  Briefcase, 
  ChevronRight, 
  X, 
  User, 
  CheckCircle, 
  MapPin,
  ChevronDown
} from 'lucide-react';
import api from '../../../shared/api';
import { useNavigate } from 'react-router-dom';
import '../styles/FreelanceHome.css';

const FindFreelancers = ({ onBook, initialQuery = '' }) => {
  const [workers, setWorkers] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [sortBy, setSortBy] = useState('Best Match');
  
  const [filters, setFilters] = useState({
    category: 'All',
    budget: 1000,
    experience: 'Any level',
    availability: 'Any'
  });

  const navigate = useNavigate();

  const handleViewProfile = (worker) => {
    console.log('Viewing profile for:', worker);
    // Navigate to freelancer profile page
    navigate(`/freelance/freelancer/${worker.id || worker.worker_id}`, {
      state: { freelancer: worker }
    });
  };

  const categories = ['All', 'Web Development', 'App Development', 'UI/UX Design', 'Content Writing', 'Digital Marketing'];
  const experienceLevels = ['Any level', 'Entry Level', 'Intermediate', 'Expert'];
  const availabilityOptions = ['Any', 'Available Now', 'Full-time', 'Part-time'];

  useEffect(() => {
    setSearchQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    fetchSkills();
    fetchWorkers();
  }, []);

  useEffect(() => {
    fetchWorkers();
  }, [selectedSkills, filters.category]);

  const fetchSkills = async () => {
    try {
      const response = await api.get('/api/freelance/skills');
      setSkills(response.data.skills);
    } catch (err) {
      console.error('Error fetching skills:', err);
    }
  };

  const fetchWorkers = async () => {
    setLoading(true);
    try {
      let url = '/api/freelance/workers';
      const params = [];
      if (selectedSkills.length > 0) params.push(`skills=${selectedSkills.join(',')}`);
      if (filters.category !== 'All') params.push(`category=${filters.category}`);
      
      if (params.length > 0) url += `?${params.join('&')}`;
      
      const response = await api.get(url);
      setWorkers(response.data.workers);
    } catch (err) {
      console.error('Error fetching workers:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSkill = (skillId) => {
    if (selectedSkills.includes(skillId)) {
      setSelectedSkills(selectedSkills.filter(id => id !== skillId));
    } else {
      setSelectedSkills([...selectedSkills, skillId]);
    }
  };

  const handleClearFilters = () => {
    setSelectedSkills([]);
    setFilters({
      category: 'All',
      budget: 1000,
      experience: 'Any level',
      availability: 'Any'
    });
    setSearchQuery('');
  };

  const filteredWorkers = workers.filter(worker => 
    worker.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    worker.bio?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    worker.specialization?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="find-professionals-page-v2">
      {/* Mobile Top Header */}
      <div className="mobile-only find-header-mobile">
        <div className="search-bar-header">
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Search freelancers..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="quick-skill-pills">
          {['All', 'React', 'Python', 'Design', 'Writing', 'Node.js'].map(pill => (
            <button key={pill} className={`skill-pill ${pill === 'All' ? 'active' : ''}`}>{pill}</button>
          ))}
        </div>
        <div className="mobile-filter-row">
          <button className="mobile-filter-dropdown">Any Category <ChevronDown size={14} /></button>
          <button className="mobile-filter-dropdown">Any Level <ChevronDown size={14} /></button>
          <button className="mobile-filter-dropdown">Sort: Best <ChevronDown size={14} /></button>
        </div>
      </div>

      <div className="find-layout-v2">
        {/* Sidebar Filters (Desktop) */}
        <aside className="find-sidebar-v2 desktop-only">
          <div className="sidebar-section">
            <h3>Filters</h3>
            
            <div className="filter-group-v3">
              <label>SEARCH</label>
              <div className="input-with-icon-v2">
                <input 
                  type="text" 
                  placeholder="e.g. tanmay" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            <div className="filter-group-v3">
              <label>CATEGORY</label>
              <select 
                value={filters.category}
                onChange={(e) => setFilters({...filters, category: e.target.value})}
              >
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div className="filter-group-v3">
              <label>SKILLS</label>
              <div className="skills-cloud-v2">
                {skills.slice(0, 8).map(skill => (
                  <button
                    key={skill.id}
                    className={`skill-tag-btn ${selectedSkills.includes(skill.id) ? 'active' : ''}`}
                    onClick={() => toggleSkill(skill.id)}
                  >
                    {skill.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group-v3">
              <label>BUDGET (₹/HR)</label>
              <input 
                type="range" 
                min="0" 
                max="5000" 
                step="100"
                value={filters.budget}
                onChange={(e) => setFilters({...filters, budget: parseInt(e.target.value)})}
                className="budget-range-v2"
              />
              <span className="range-value-v2">Up to ₹{filters.budget}/hr</span>
            </div>

            <div className="filter-group-v3">
              <label>EXPERIENCE LEVEL</label>
              <select 
                value={filters.experience}
                onChange={(e) => setFilters({...filters, experience: e.target.value})}
              >
                {experienceLevels.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>

            <div className="filter-group-v3">
              <label>AVAILABILITY</label>
              <select 
                value={filters.availability}
                onChange={(e) => setFilters({...filters, availability: e.target.value})}
              >
                {availabilityOptions.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>

            <button className="clear-filters-btn-v3" onClick={handleClearFilters}>
              Clear Filters
            </button>
          </div>
        </aside>

        {/* Results Section */}
        <main className="results-container-v2">
          <div className="results-header-v2">
            <div className="results-count">
              {filteredWorkers.length} freelancers found {searchQuery && `for "${searchQuery}"`}
            </div>
            <div className="sort-dropdown-v2 desktop-only">
              <span>Sort:</span>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option>Best Match</option>
                <option>Newest First</option>
                <option>Price: Low to High</option>
                <option>Price: High to Low</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="loading-grid-v2">
              {[1, 2, 3].map(i => <div key={i} className="skeleton skeleton-worker-card"></div>)}
            </div>
          ) : filteredWorkers.length === 0 ? (
            <div className="empty-results-v2">
              <User size={64} />
              <h3>No professionals found</h3>
              <p>Try adjusting your search or filters to find more results.</p>
              <button onClick={handleClearFilters}>Reset all filters</button>
            </div>
          ) : (
            <div className="workers-list-v3">
              {filteredWorkers.map(worker => (
                <div key={worker.id} className="worker-card-v3">
                  <div className="worker-card-main-v2">
                    <div className="worker-avatar-v3">
                      <div className="avatar-circle-v3">
                        {worker.full_name.split(' ').map(n => n[0]).join('').toUpperCase() || 'F'}
                      </div>
                      <span className="online-status-dot"></span>
                    </div>
                    
                    <div className="worker-info-v3">
                      <div className="name-row-v3">
                        <div className="name-spec-v3">
                          <h3 
                            style={{ cursor: 'pointer', color: '#667eea' }}
                            onClick={() => handleViewProfile(worker)}
                            title="Click to view profile"
                          >
                            {worker.full_name}
                          </h3>
                          <p>{worker.specialization || 'Freelancer'} • {worker.clinic_location || 'Remote'}</p>
                        </div>
                        <div className="price-tag-v3">
                          ₹{worker.hourly_rate || '500'}/hr
                        </div>
                      </div>
                      
                      <div className="rating-row-v3">
                        <div className="stars-v3">
                          <Star size={14} fill="#FFB800" color="#FFB800" />
                          <span>{worker.rating || '5.0'}</span>
                          <span className="exp-text-v3">({worker.experience || 0}+ yrs exp)</span>
                        </div>
                        <div className="location-v3">
                          <MapPin size={14} />
                          <span>{worker.clinic_location || 'Mumbai'}</span>
                        </div>
                      </div>

                      <p className="worker-bio-v3">
                        {worker.bio || "Experienced professional delivering high-quality work on time and within budget."}
                      </p>

                      <div className="skills-tags-v3">
                        {(worker.skills || 'React, Node.js, TypeScript').split(',').map((skill, idx) => (
                          <span key={idx} className="skill-tag-v3">{skill.trim()}</span>
                        ))}
                      </div>

                      <div className="card-actions-v3">
                        <button 
                          className="btn-secondary-v3"
                          onClick={() => handleViewProfile(worker)}
                        >
                          View Profile
                        </button>
                        <button className="btn-primary-v3" onClick={() => onBook(worker)}>
                          Book Now
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default FindFreelancers;
