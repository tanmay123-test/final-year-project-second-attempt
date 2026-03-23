import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Star, Clock, Briefcase, MapPin, CheckCircle, MessageSquare, DollarSign, Calendar, X, Shield, IndianRupee, TrendingUp } from 'lucide-react';
import api from '../../../shared/api';
import '../styles/FreelancerDashboard.css';

const FreelancerProfilePage = () => {
  const { freelancerId } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [bookingData, setBookingData] = useState({
    title: '',
    description: '',
    amount: ''
  });
  const [bookingLoading, setBookingLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, [freelancerId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/freelance/freelancer/${freelancerId}`);
      setProfile(response.data.profile);
      setError(null);
    } catch (err) {
      setError('Freelancer profile not found. They may have deactivated their account.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBookingSubmit = async (e) => {
    e.preventDefault();
    setBookingLoading(true);
    try {
      await api.post('/api/freelance/bookings', {
        freelancer_id: parseInt(freelancerId),
        ...bookingData
      });
      alert('Direct booking request sent successfully! The freelancer will review it.');
      setIsModalOpen(false);
      setBookingData({ title: '', description: '', amount: '' });
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to send booking request. Please try again.');
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <p>Loading freelancer profile...</p>
    </div>
  );

  if (error || !profile) return (
    <div className="empty-state-dashboard" style={{ margin: '2rem' }}>
      <X size={48} color="#ef4444" />
      <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Profile Not Found</h3>
      <p style={{ color: '#6b7280', marginBottom: '2rem' }}>{error || 'The requested freelancer profile does not exist.'}</p>
      <button className="action-btn-purple" onClick={() => navigate(-1)}>Go Back</button>
    </div>
  );

  return (
    <div className="project-detail-container">
      <button className="back-btn" onClick={() => navigate(-1)}>
        <ArrowLeft size={18} /> Back
      </button>

      <div className="info-card profile-hero-card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
        <div className="user-avatar" style={{ 
          width: '100px', height: '100px', fontSize: '2.5rem', margin: '0 auto 1.5rem',
          position: 'relative', background: '#f5f3ff', color: '#9B59B6', borderRadius: '24px'
        }}>
          {profile.full_name?.charAt(0)}
          {profile.status === 'APPROVED' && (
            <div className="online-indicator" style={{ 
              position: 'absolute', bottom: '5px', right: '5px', width: '18px', height: '18px',
              background: '#10b981', border: '3px solid white', borderRadius: '50%'
            }}></div>
          )}
        </div>
        
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>{profile.full_name}</h1>
        <p style={{ color: '#9B59B6', fontWeight: 700, fontSize: '1.1rem', marginBottom: '1rem' }}>
          {profile.specialization || 'Professional Freelancer'}
        </p>
        
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', color: '#6b7280', fontSize: '0.95rem', marginBottom: '2rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}><IndianRupee size={16} /> ₹{profile.hourly_rate?.toLocaleString()}/hr</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}><Briefcase size={16} /> {profile.experience || 0} years exp</span>
          <span className="status-badge-unified approved" style={{ fontSize: '0.75rem' }}>{profile.status}</span>
        </div>

        <p style={{ maxWidth: '600px', margin: '0 auto 2.5rem', color: '#4b5563', lineHeight: 1.6, fontSize: '1.05rem' }}>
          {profile.bio || 'Highly skilled professional dedicated to delivering top-quality results on ExpertEase.'}
        </p>
        
        <button className="action-btn-purple" style={{ padding: '1rem 3rem', fontSize: '1rem' }} onClick={() => setIsModalOpen(true)}>
          Hire {profile.full_name.split(' ')[0]}
        </button>
      </div>

      <div className="stats-grid" style={{ marginBottom: '3rem' }}>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: '#fffbeb', color: '#f59e0b' }}>
            <Star size={20} fill="#f59e0b" />
          </div>
          <div className="stat-info">
            <p>Rating</p>
            <h3>{profile.rating || '5.0'}</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: '#f0fdf4', color: '#10b981' }}>
            <CheckCircle size={20} />
          </div>
          <div className="stat-info">
            <p>Completed</p>
            <h3>{profile.completed_projects || 0} Projects</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: '#eff6ff', color: '#3b82f6' }}>
            <TrendingUp size={20} />
          </div>
          <div className="stat-info">
            <p>Proposals Sent</p>
            <h3>{profile.proposals_sent || 0}</h3>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ backgroundColor: '#f5f3ff', color: '#9B59B6' }}>
            <Calendar size={20} />
          </div>
          <div className="stat-info">
            <p>Member Since</p>
            <h3>{new Date(profile.created_at).getFullYear()}</h3>
          </div>
        </div>
      </div>

      <div className="info-card">
        <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Shield size={20} color="#9B59B6" /> Skills & Expertise
        </h3>
        <div className="skills-list">
          {profile.skills?.split(',').map((skill, index) => (
            <span key={index} className="skill-badge" style={{ padding: '0.6rem 1.2rem', fontSize: '0.95rem' }}>
              {skill.trim()}
            </span>
          ))}
        </div>
      </div>

      <section className="reviews-section" style={{ marginTop: '3rem' }}>
        <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1.5rem' }}>Client Reviews</h3>
        {profile.reviews && profile.reviews.length > 0 ? (
          <div style={{ display: 'grid', gap: '1.5rem' }}>
            {profile.reviews.map((review, index) => (
              <div key={index} className="info-card" style={{ margin: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div className="user-avatar" style={{ width: '40px', height: '40px', fontSize: '0.9rem' }}>
                      {review.client_name?.charAt(0)}
                    </div>
                    <div>
                      <h5 style={{ fontWeight: 700 }}>{review.client_name}</h5>
                      <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>{new Date(review.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', color: '#f59e0b' }}>
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} size={14} fill={i < review.rating ? "#f59e0b" : "none"} />
                    ))}
                  </div>
                </div>
                <p style={{ color: '#4b5563', lineHeight: 1.5 }}>{review.comment}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state-dashboard">
            <MessageSquare size={40} color="#cbd5e1" />
            <p>No reviews yet for this freelancer.</p>
          </div>
        )}
      </section>

      {/* Direct Booking Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="apply-modal" style={{ maxWidth: '500px' }}>
            <div className="modal-header">
              <h3>Hire {profile.full_name}</h3>
              <button className="icon-btn" onClick={() => setIsModalOpen(false)}><X size={20} /></button>
            </div>
            <form onSubmit={handleBookingSubmit} style={{ padding: '1.5rem' }}>
              <div className="form-group" style={{ marginBottom: '1.2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Project Title</label>
                <input 
                  type="text" 
                  placeholder="e.g. Design a landing page"
                  required
                  value={bookingData.title}
                  onChange={(e) => setBookingData({...bookingData, title: e.target.value})}
                  style={{ width: '100%', padding: '0.8rem', borderRadius: '10px', border: '1px solid #e5e7eb' }}
                />
              </div>
              <div className="form-group" style={{ marginBottom: '1.2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Description</label>
                <textarea 
                  placeholder="Describe your project requirements..."
                  required
                  rows={4}
                  value={bookingData.description}
                  onChange={(e) => setBookingData({...bookingData, description: e.target.value})}
                  style={{ width: '100%', padding: '0.8rem', borderRadius: '10px', border: '1px solid #e5e7eb', resize: 'none' }}
                />
              </div>
              <div className="form-group" style={{ marginBottom: '2rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Offered Amount (₹)</label>
                <input 
                  type="number" 
                  placeholder="e.g. 5000"
                  required
                  value={bookingData.amount}
                  onChange={(e) => setBookingData({...bookingData, amount: e.target.value})}
                  style={{ width: '100%', padding: '0.8rem', borderRadius: '10px', border: '1px solid #e5e7eb' }}
                />
              </div>
              <button 
                type="submit" 
                className="action-btn-purple" 
                style={{ width: '100%', padding: '1rem' }}
                disabled={bookingLoading}
              >
                {bookingLoading ? 'Sending Request...' : 'Send Hire Request'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FreelancerProfilePage;
