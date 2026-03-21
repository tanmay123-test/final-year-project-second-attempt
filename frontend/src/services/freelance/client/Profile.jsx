import React, { useState, useEffect } from 'react';
import { 
  User, Mail, Phone, MapPin, Calendar, Edit2, 
  ShieldCheck, Briefcase, MessageSquare, Star, 
  Lock, Bell, CreditCard, LogOut, X, Check, Loader2,
  Home, PlusCircle, Folder, Bot, Search
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingField, setEditingField] = useState(null); // 'personal', 'skills', 'password'
  const [editData, setFormData] = useState({});
  const [updateLoading, setUpdateLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/freelancer/profile/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data && response.data.profile) {
        setProfile(response.data.profile);
        setFormData(response.data.profile);
      } else {
        // Fallback for missing profile data
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        const fallbackProfile = {
          name: userData.full_name || 'User',
          email: userData.email || '',
          avatarInitials: (userData.full_name || 'U').split(' ').map(n => n[0]).join(''),
          role: userData.role || 'Client',
          isVerified: true,
          location: 'Not set',
          memberSince: new Date().toISOString(),
          stats: { totalProjects: 0, totalProposals: 0, rating: '5.0' },
          skills: [],
          recentActivity: []
        };
        setProfile(fallbackProfile);
        setFormData(fallbackProfile);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      // Fallback on error
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      const errorFallback = {
        name: userData.full_name || 'User',
        email: userData.email || '',
        avatarInitials: (userData.full_name || 'U').split(' ').map(n => n[0]).join(''),
        role: userData.role || 'Client',
        isVerified: false,
        location: 'Unknown',
        memberSince: new Date().toISOString(),
        stats: { totalProjects: 0, totalProposals: 0, rating: 'N/A' },
        skills: [],
        recentActivity: []
      };
      setProfile(errorFallback);
      setFormData(errorFallback);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setUpdateLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.put('http://localhost:5000/api/freelancer/profile/update', editData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(response.data.profile);
      setEditingField(null);
      alert('Profile updated successfully');
    } catch (error) {
      alert('Failed to update profile');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelancer/auth/logout', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      navigate('/login');
    }
  };

  if (loading) {
    return (
      <div className="profile-loading">
        <Loader2 className="spinner" size={40} />
        <p>Loading your profile...</p>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-hero">
        <div className="hero-content">
          <h1>My Profile</h1>
          <p>Manage your account and preferences</p>
        </div>
      </div>

      <div className="profile-content-wrapper">
        <div className="profile-grid">
          {/* Left Column: Avatar & Account Settings */}
          <div className="profile-col-left">
            {/* Avatar Card */}
            <div className="profile-card avatar-card">
              <div className="avatar-circle-large">
                {profile.avatarInitials}
              </div>
              <h2 className="user-name-title">{profile.name}</h2>
              <p className="user-email-text">{profile.email}</p>
              
              <div className="badge-row">
                <span className="role-badge">{profile.role}</span>
                {profile.isVerified && (
                  <span className="verified-badge">
                    <ShieldCheck size={14} /> Verified
                  </span>
                )}
              </div>

              <button className="edit-profile-btn" onClick={() => setEditingField('personal')}>
                Edit Profile
              </button>

              <div className="profile-stats-row">
                <div className="stat-box">
                  <span className="stat-val">{profile.stats.totalProjects}</span>
                  <span className="stat-label">Projects</span>
                </div>
                <div className="divider"></div>
                <div className="stat-box">
                  <span className="stat-val">{profile.stats.totalProposals}</span>
                  <span className="stat-label">Proposals</span>
                </div>
                <div className="divider"></div>
                <div className="stat-box">
                  <span className="stat-val">{profile.stats.rating}</span>
                  <span className="stat-label">Rating</span>
                </div>
              </div>
            </div>

            {/* Account Settings */}
            <div className="profile-card settings-card">
              <div className="card-header">
                <ShieldCheck size={20} color="#534AB7" />
                <h3>Account Settings</h3>
              </div>
              
              <div className="settings-list">
                <button className="setting-item" onClick={() => setEditingField('password')}>
                  <div className="item-left">
                    <Lock size={18} />
                    <span>Change Password</span>
                  </div>
                  <ChevronRight size={16} />
                </button>
                <button className="setting-item">
                  <div className="item-left">
                    <Bell size={18} />
                    <span>Notifications</span>
                  </div>
                  <ChevronRight size={16} />
                </button>
                <button className="setting-item">
                  <div className="item-left">
                    <CreditCard size={18} />
                    <span>Payment Methods</span>
                  </div>
                  <ChevronRight size={16} />
                </button>
                <button className="setting-item logout-btn-trigger" onClick={handleLogout}>
                  <div className="item-left">
                    <LogOut size={18} />
                    <span>Logout</span>
                  </div>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Personal Info & Skills */}
          <div className="profile-col-right">
            {/* Personal Information */}
            <div className="profile-card info-card">
              <div className="card-header-with-action">
                <div className="card-header-title">
                  <User size={20} color="#534AB7" />
                  <h3>Personal Information</h3>
                </div>
                <button className="text-action-btn" onClick={() => setEditingField('personal')}>Edit</button>
              </div>

              <div className="info-details-list">
                <div className="info-row">
                  <span className="info-label">Full Name</span>
                  <span className="info-val">{profile.name}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Email</span>
                  <span className="info-val">{profile.email}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Phone</span>
                  <span className="info-val">{profile.phone || 'Not provided'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Location</span>
                  <span className="info-val">{profile.location}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Member Since</span>
                  <span className="info-val">{new Date(profile.memberSince).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
                </div>
              </div>
            </div>

            {/* Skills & Interests */}
            <div className="profile-card skills-card">
              <div className="card-header-with-action">
                <div className="card-header-title">
                  <Briefcase size={20} color="#534AB7" />
                  <h3>Skills & Interests</h3>
                </div>
                <button className="text-action-btn" onClick={() => setEditingField('skills')}>Edit</button>
              </div>
              
              <div className="skills-pill-container">
                {profile.skills.length > 0 ? (
                  profile.skills.map((skill, idx) => (
                    <span key={idx} className="skill-pill">{skill.trim()}</span>
                  ))
                ) : (
                  <p className="no-data-text">No skills added yet.</p>
                )}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="profile-card activity-card">
              <div className="card-header">
                <MessageSquare size={20} color="#534AB7" />
                <h3>Recent Activity</h3>
              </div>
              
              <div className="activity-list">
                {profile.recentActivity.map((act, idx) => (
                  <div key={idx} className="activity-item">
                    <div className="act-content">
                      <p className="act-title">
                        {act.type === 'POSTED' ? 'Posted ' : 'Received '}
                        <strong>{act.title}</strong>
                      </p>
                      <span className="act-time">{act.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Logout button for mobile only (at bottom) */}
        <button className="mobile-logout-btn mobile-only" onClick={handleLogout}>
          Logout
        </button>
      </div>

      {/* Edit Modals / Inline Forms */}
      {editingField === 'personal' && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Edit Personal Information</h3>
              <button className="close-modal" onClick={() => setEditingField(null)}><X size={20} /></button>
            </div>
            <form onSubmit={handleUpdateProfile} className="edit-form">
              <div className="form-group">
                <label>Full Name</label>
                <input 
                  type="text" 
                  value={editData.name} 
                  onChange={(e) => setFormData({...editData, name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input 
                  type="text" 
                  value={editData.phone} 
                  onChange={(e) => setFormData({...editData, phone: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Location</label>
                <input 
                  type="text" 
                  value={editData.location} 
                  onChange={(e) => setFormData({...editData, location: e.target.value})}
                />
              </div>
              <button type="submit" className="save-btn" disabled={updateLoading}>
                {updateLoading ? <Loader2 className="spinner" size={18} /> : 'Save Changes'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper component for Chevron
const ChevronRight = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m9 18 6-6-6-6"/>
  </svg>
);

export default Profile;
