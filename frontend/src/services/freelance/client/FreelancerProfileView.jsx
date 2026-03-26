import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { 
  User, Mail, Phone, MapPin, Calendar, Star, Briefcase, 
  ArrowLeft, MessageCircle, ExternalLink, CheckCircle, Clock,
  Shield, Award, TrendingUp, DollarSign, Edit
} from 'lucide-react';
import api from '../../../shared/api';
import '../styles/FreelanceHome.css';
import '../styles/FreelancerProfileView.css';

const FreelancerProfileView = () => {
  const { freelancerId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [freelancer, setFreelancer] = useState(location.state?.freelancer || null);
  const [loading, setLoading] = useState(!location.state?.freelancer);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (!freelancer && freelancerId) {
      fetchFreelancerProfile();
    }
  }, [freelancerId, freelancer]);

  const fetchFreelancerProfile = async () => {
    setLoading(true);
    try {
      console.log('Fetching freelancer profile for ID:', freelancerId);
      const response = await api.get(`/api/freelance/workers/${freelancerId}`);
      console.log('Freelancer profile response:', response.data);
      
      if (response.data.worker) {
        setFreelancer(response.data.worker);
        setError('');
      } else {
        setError('Freelancer not found');
      }
    } catch (err) {
      console.error('Error fetching freelancer profile:', err);
      setError('Failed to load freelancer profile');
    } finally {
      setLoading(false);
    }
  };

  const handleBookNow = () => {
    // Pass the freelancer data back to the parent for booking
    navigate('/freelance/home?tab=find', { 
      state: { bookFreelancer: freelancer } 
    });
  };

  const handleMessage = () => {
    // Navigate to messaging or open chat
    navigate('/freelance/home?tab=messages', { 
      state: { freelancer } 
    });
  };

  if (loading) {
    return (
      <div className="freelance-profile-loading">
        <div className="loading-spinner"></div>
        <p>Loading freelancer profile...</p>
      </div>
    );
  }

  if (error || !freelancer) {
    return (
      <div className="freelancer-profile-error">
        <div className="error-container">
          <User size={64} color="#ccc" />
          <h3>Profile Not Found</h3>
          <p>{error || 'This freelancer profile could not be loaded.'}</p>
          <button onClick={() => navigate('/freelance/home?tab=find')}>
            Back to Find Freelancers
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="freelancer-profile-view">
      {/* Header */}
      <div className="profile-header">
        <button 
          className="back-button"
          onClick={() => navigate('/freelance/home?tab=find')}
        >
          <ArrowLeft size={20} />
          Back to Freelancers
        </button>
      </div>

      <div className="profile-content">
        {/* Main Profile Card */}
        <div className="profile-main-card">
          <div className="profile-avatar-section">
            <div className="avatar-large">
              {freelancer.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'F'}
            </div>
            <div className="online-indicator">
              <span className="online-dot"></span>
              Available for work
            </div>
          </div>

          <div className="profile-info-section">
            <div className="profile-name-section">
              <h1>{freelancer.full_name || freelancer.name || 'Freelancer'}</h1>
              <p className="profile-title">{freelancer.specialization || freelancer.profession || 'Freelancer'}</p>
              <div className="profile-location">
                <MapPin size={16} />
                <span>{freelancer.clinic_location || freelancer.location || 'Remote'}</span>
              </div>
            </div>

            {/* Debug Info */}
            <div style={{ 
              padding: '10px', 
              background: '#f0f8ff', 
              margin: '10px 0', 
              borderRadius: '5px',
              fontSize: '12px',
              border: '1px solid #d0e8ff'
            }}>
              <strong>🔍 Debug Info:</strong>
              <br />• ID: {freelancer.id}
              <br />• Name: {freelancer.full_name || freelancer.name || 'N/A'}
              <br />• Specialization: {freelancer.specialization || freelancer.profession || 'N/A'}
              <br />• Skills: {freelancer.skills || 'N/A'}
              <br />• Skills List: {JSON.stringify(freelancer.skills_list || [])}
            </div>

            <div className="profile-stats">
              <div className="stat-item">
                <Star size={16} fill="#FFB800" color="#FFB800" />
                <span>{freelancer.rating || '5.0'}</span>
                <small>({freelancer.reviews_count || '87'} reviews)</small>
              </div>
              <div className="stat-item">
                <Briefcase size={16} />
                <span>{freelancer.experience || '0'}+ years</span>
                <small>experience</small>
              </div>
              <div className="stat-item">
                <DollarSign size={16} />
                <span>₹{freelancer.hourly_rate || '500'}/hr</span>
                <small>hourly rate</small>
              </div>
            </div>

            <div className="profile-actions">
              <button className="btn-primary-large" onClick={handleBookNow}>
                Book Now
              </button>
              <button className="btn-secondary-large" onClick={handleMessage}>
                <MessageCircle size={18} />
                Message
              </button>
            </div>
          </div>
        </div>

        {/* Tabs Section */}
        <div className="profile-tabs">
          <div className="tab-headers">
            {['overview', 'portfolio', 'reviews', 'availability'].map(tab => (
              <button
                key={tab}
                className={`tab-header ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          <div className="tab-content">
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="about-section">
                  <h3>About</h3>
                  <p>{freelancer.bio || "Experienced professional delivering high-quality work on time and within budget. Passionate about creating innovative solutions and maintaining excellent client relationships."}</p>
                </div>

                <div className="skills-section">
                  <h3>Skills</h3>
                  <div className="skills-grid">
                    {freelancer.skills_list && freelancer.skills_list.length > 0 ? (
                      freelancer.skills_list.map((skill, idx) => (
                        <span key={idx} className="skill-badge">{skill.trim()}</span>
                      ))
                    ) : freelancer.skills ? (
                      freelancer.skills.split(',').map((skill, idx) => (
                        <span key={idx} className="skill-badge">{skill.trim()}</span>
                      ))
                    ) : (
                      <span className="skill-badge">No skills listed</span>
                    )}
                  </div>
                </div>

                <div className="details-grid">
                  <div className="detail-card">
                    <CheckCircle size={20} color="#10b981" />
                    <div>
                      <h4>Verified Profile</h4>
                      <p>Identity and skills verified</p>
                    </div>
                  </div>
                  <div className="detail-card">
                    <Award size={20} color="#f59e0b" />
                    <div>
                      <h4>Top Rated</h4>
                      <p>Consistently excellent reviews</p>
                    </div>
                  </div>
                  <div className="detail-card">
                    <TrendingUp size={20} color="#3b82f6" />
                    <div>
                      <h4>Quick Response</h4>
                      <p>Typically replies within 2 hours</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'portfolio' && (
              <div className="portfolio-tab">
                <h3>Portfolio</h3>
                <div className="portfolio-grid">
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="portfolio-item">
                      <div className="portfolio-placeholder">
                        <Briefcase size={32} color="#ccc" />
                      </div>
                      <h4>Sample Project {i}</h4>
                      <p>Brief description of the project and technologies used.</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="reviews-tab">
                <h3>Client Reviews</h3>
                <div className="reviews-list">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="review-item">
                      <div className="review-header">
                        <div className="reviewer-avatar">C</div>
                        <div className="reviewer-info">
                          <h4>Client {i}</h4>
                          <div className="review-rating">
                            {[1, 2, 3, 4, 5].map(star => (
                              <Star key={star} size={14} fill="#FFB800" color="#FFB800" />
                            ))}
                          </div>
                        </div>
                        <span className="review-date">2 weeks ago</span>
                      </div>
                      <p className="review-text">
                        "Excellent work! Delivered on time and exceeded expectations. Would definitely hire again."
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'availability' && (
              <div className="availability-tab">
                <h3>Availability</h3>
                <div className="availability-info">
                  <div className="availability-status">
                    <Clock size={20} color="#10b981" />
                    <span>Available for new projects</span>
                  </div>
                  <div className="availability-details">
                    <p><strong>Response Time:</strong> Within 2 hours</p>
                    <p><strong>Availability:</strong> Full-time, Part-time, Hourly</p>
                    <p><strong>Timezone:</strong> {freelancer.timezone || 'IST (UTC+5:30)'}</p>
                    <p><strong>Languages:</strong> English, Hindi</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FreelancerProfileView;
