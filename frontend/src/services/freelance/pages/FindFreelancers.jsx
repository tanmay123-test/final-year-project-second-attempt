import React, { useState, useEffect } from 'react';
import { Search, Filter, Star, Clock, Briefcase, ChevronRight, X, User, CheckCircle } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelanceHome.css';

const FindFreelancers = ({ onBook }) => {
  const [workers, setWorkers] = useState([]);
  const [skills, setSkills] = useState([]);
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchSkills();
    fetchWorkers();
  }, []);

  useEffect(() => {
    fetchWorkers();
  }, [selectedSkills]);

  const fetchSkills = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/freelance/skills');
      setSkills(response.data.skills);
    } catch (err) {
      console.error('Error fetching skills:', err);
    }
  };

  const fetchWorkers = async () => {
    setLoading(true);
    try {
      let url = 'http://localhost:5000/api/freelance/workers';
      if (selectedSkills.length > 0) {
        url += `?skills=${selectedSkills.join(',')}`;
      }
      const response = await axios.get(url);
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

  const filteredWorkers = workers.filter(worker => 
    worker.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    worker.bio?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="find-freelancers-container">
      <div className="find-header">
        <h2>Find Professionals</h2>
        <div className="search-box-v2">
          <Search size={20} />
          <input 
            type="text" 
            placeholder="Search by name or bio..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Skill Filter Chips */}
      <div className="skill-filters-wrapper">
        <label><Filter size={16} /> Filter by Skills:</label>
        <div className="skill-chips-scroll">
          {skills.map(skill => (
            <button
              key={skill.id}
              className={`filter-chip ${selectedSkills.includes(skill.id) ? 'active' : ''}`}
              onClick={() => toggleSkill(skill.id)}
            >
              {skill.name}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner-purple"></div>
          <p>Finding the best experts for you...</p>
        </div>
      ) : filteredWorkers.length === 0 ? (
        <div className="empty-state-new">
          <User size={48} color="#cbd5e1" />
          <p>No professionals found matching your criteria.</p>
          <button onClick={() => {setSelectedSkills([]); setSearchQuery('');}} className="clear-btn">
            Clear all filters
          </button>
        </div>
      ) : (
        <div className="workers-grid-v2">
          {filteredWorkers.map(worker => (
            <div key={worker.id} className="worker-card-v2">
              <div className="worker-card-top">
                <div className="worker-avatar-large">
                  {worker.full_name.charAt(0)}
                  <span className="online-indicator"></span>
                </div>
                <div className="worker-main-info">
                  <div className="name-row">
                    <h3>{worker.full_name}</h3>
                    {worker.rating > 4.5 && <CheckCircle size={16} color="#9B59B6" fill="#9B59B6" />}
                  </div>
                  <p className="worker-location">{worker.clinic_location || 'Remote'}</p>
                  <div className="rating-row">
                    <Star size={14} fill="#FFB800" color="#FFB800" />
                    <span>{worker.rating || '5.0'}</span>
                    <span className="review-count">({worker.experience}+ years exp)</span>
                  </div>
                </div>
                <div className="worker-price-tag">
                  ₹{worker.hourly_rate || '1000'}/hr
                </div>
              </div>

              <p className="worker-bio-short">
                {worker.bio || "Top-rated freelancer with extensive experience in delivering high-quality results."}
              </p>

              <div className="worker-skills-badges">
                {worker.skills_list?.map(skill => (
                  <span key={skill} className="skill-badge-v2">{skill}</span>
                ))}
              </div>

              <div className="worker-card-actions">
                <button className="view-profile-btn">View Profile</button>
                <button className="book-now-btn-purple" onClick={() => onBook(worker)}>
                  Book Now
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FindFreelancers;
