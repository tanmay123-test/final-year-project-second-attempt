import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, User, Mail, Phone, MapPin, Calendar,
  Award, Wrench, Clock, Star, CheckCircle,
  Edit, Camera, Shield, FileText, AlertCircle
} from 'lucide-react';

const MechanicDetails = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchWorkerDetails();
  }, []);

  const fetchWorkerDetails = async () => {
    try {
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (storedData && token) {
        const data = JSON.parse(storedData);
        setWorkerData(data);
        
        // Fetch comprehensive worker details
        try {
          const workerId = data.id || data.workerId || 7;
          const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/details`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const detailsData = await response.json();
            setWorkerData({ ...data, ...detailsData });
          }
        } catch (error) {
          console.log('🔄 Details API not available, using enhanced data:', error.message);
        }
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading worker details:', error);
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setFormData({
      name: workerData?.name || 'John Smith',
      email: workerData?.email || 'john.smith@email.com',
      phone: workerData?.phone || '+91 98765 43210',
      address: workerData?.address || '123 Main Street, Bangalore, Karnataka 560001',
      specialization: workerData?.specialization || 'Automobile Mechanic',
      experience: workerData?.experience || '8 years',
      bio: workerData?.bio || 'Experienced automobile mechanic specializing in engine diagnostics and repairs.',
      services: workerData?.services || ['Engine Repair', 'Brake Service', 'Oil Change', 'Tire Service'],
      availability: workerData?.availability || {
        monday: true,
        tuesday: true,
        wednesday: true,
        thursday: true,
        friday: true,
        saturday: false,
        sunday: false
      }
    });
    setEditing(true);
  };

  const handleSave = async () => {
    try {
      const token = localStorage.getItem('workerToken');
      const workerId = workerData?.id || workerData?.workerId || 7;
      
      const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/update`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setWorkerData({ ...workerData, ...formData });
        setEditing(false);
        alert('Profile updated successfully!');
      } else {
        alert('Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile');
    }
  };

  if (loading) {
    return (
      <div className="mechanic-details-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading profile details...</p>
        </div>
        <style>{`
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: #f8fafc;
          }
          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #8B5CF6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="mechanic-details-page">
      {/* Header */}
      <div className="details-header">
        <div className="header-actions">
          <button className="back-button" onClick={() => navigate('/worker/car/mechanic/profile')}>
            <ArrowLeft size={20} />
            <span>Back to Profile</span>
          </button>
          {!editing && (
            <button className="edit-button" onClick={handleEdit}>
              <Edit size={18} />
              <span>Edit Profile</span>
            </button>
          )}
        </div>
        <h1>Full Profile Details</h1>
      </div>

      <div className="details-content">
        {/* Profile Overview */}
        <div className="profile-overview-card">
          <div className="profile-header-section">
            <div className="avatar-section">
              <div className="avatar-large">
                {workerData?.name ? workerData.name[0].toUpperCase() : 'M'}
                <button className="camera-button">
                  <Camera size={16} />
                </button>
              </div>
              <div className="verification-badge">
                <Shield size={16} />
                <span>Verified Professional</span>
              </div>
            </div>
            <div className="basic-info">
              {editing ? (
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="edit-input name-input"
                />
              ) : (
                <h2>{workerData?.name || 'John Smith'}</h2>
              )}
              <div className="rating-display">
                <Star size={16} fill="#8B5CF6" color="#8B5CF6" />
                <span>4.6</span>
                <span className="rating-count">(127 reviews)</span>
              </div>
              <p className="specialization-tag">
                {editing ? (
                  <input
                    type="text"
                    value={formData.specialization}
                    onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                    className="edit-input specialization-input"
                  />
                ) : (
                  workerData?.specialization || 'Automobile Mechanic'
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="info-card">
          <h3>Contact Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <Mail size={18} className="info-icon" />
              <div className="info-content">
                <label>Email</label>
                {editing ? (
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="edit-input"
                  />
                ) : (
                  <span>{workerData?.email || 'john.smith@email.com'}</span>
                )}
              </div>
            </div>
            <div className="info-item">
              <Phone size={18} className="info-icon" />
              <div className="info-content">
                <label>Phone</label>
                {editing ? (
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="edit-input"
                  />
                ) : (
                  <span>{workerData?.phone || '+91 98765 43210'}</span>
                )}
              </div>
            </div>
            <div className="info-item">
              <MapPin size={18} className="info-icon" />
              <div className="info-content">
                <label>Address</label>
                {editing ? (
                  <textarea
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className="edit-input textarea"
                    rows={2}
                  />
                ) : (
                  <span>{workerData?.address || '123 Main Street, Bangalore, Karnataka 560001'}</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Professional Information */}
        <div className="info-card">
          <h3>Professional Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <Wrench size={18} className="info-icon" />
              <div className="info-content">
                <label>Experience</label>
                {editing ? (
                  <input
                    type="text"
                    value={formData.experience}
                    onChange={(e) => setFormData({ ...formData, experience: e.target.value })}
                    className="edit-input"
                  />
                ) : (
                  <span>{workerData?.experience || '8 years'}</span>
                )}
              </div>
            </div>
            <div className="info-item">
              <Award size={18} className="info-icon" />
              <div className="info-content">
                <label>Certifications</label>
                <div className="certification-list">
                  <span className="cert-badge">Automotive Service Excellence</span>
                  <span className="cert-badge">Engine Diagnostics</span>
                  <span className="cert-badge">Hybrid Vehicle Specialist</span>
                </div>
              </div>
            </div>
            <div className="info-item">
              <Calendar size={18} className="info-icon" />
              <div className="info-content">
                <label>Member Since</label>
                <span>{workerData?.created_at ? new Date(workerData.created_at).toLocaleDateString() : 'March 15, 2022'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bio */}
        <div className="info-card">
          <h3>Professional Bio</h3>
          {editing ? (
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              className="edit-input bio-textarea"
              rows={4}
              placeholder="Tell customers about your experience and expertise..."
            />
          ) : (
            <p className="bio-text">
              {workerData?.bio || 'Experienced automobile mechanic specializing in engine diagnostics and repairs. With over 8 years of hands-on experience, I provide reliable and efficient service for all types of vehicles. Specialized in modern engine technology and hybrid vehicles.'}
            </p>
          )}
        </div>

        {/* Services */}
        <div className="info-card">
          <h3>Services Offered</h3>
          <div className="services-grid">
            {(editing ? formData.services : (workerData?.services || ['Engine Repair', 'Brake Service', 'Oil Change', 'Tire Service'])).map((service, index) => (
              <div key={index} className="service-item">
                <CheckCircle size={16} className="service-icon" />
                <span>{service}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Availability */}
        <div className="info-card">
          <h3>Availability</h3>
          <div className="availability-grid">
            {Object.keys(editing ? formData.availability : (workerData?.availability || {
              monday: true, tuesday: true, wednesday: true, thursday: true, 
              friday: true, saturday: false, sunday: false
            })).map((day, index) => (
              <div key={day} className="availability-item">
                <span className="day-name">{day.charAt(0).toUpperCase() + day.slice(1)}</span>
                <div className={`availability-status ${editing ? formData.availability[day] : workerData?.availability?.[day] ? 'available' : 'unavailable'}`}>
                  {editing ? (
                    <input
                      type="checkbox"
                      checked={formData.availability[day]}
                      onChange={(e) => setFormData({
                        ...formData,
                        availability: { ...formData.availability, [day]: e.target.checked }
                      })}
                    />
                  ) : (
                    <CheckCircle size={16} />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Overview */}
        <div className="info-card">
          <h3>Performance Overview</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">28500</div>
              <div className="stat-label">Total Earnings</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">127</div>
              <div className="stat-label">Jobs Completed</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">4.6</div>
              <div className="stat-label">Average Rating</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">98%</div>
              <div className="stat-label">Completion Rate</div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {editing && (
          <div className="action-buttons">
            <button className="save-button" onClick={handleSave}>
              <CheckCircle size={18} />
              <span>Save Changes</span>
            </button>
            <button className="cancel-button" onClick={() => setEditing(false)}>
              <span>Cancel</span>
            </button>
          </div>
        )}
      </div>

      <style>{`
        .mechanic-details-page {
          background-color: #f8fafc;
          min-height: 100vh;
          font-family: 'Inter', sans-serif;
        }

        .details-header {
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          padding: 1.5rem;
          color: white;
        }

        .header-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .back-button, .edit-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .back-button:hover, .edit-button:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .details-header h1 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .details-content {
          padding: 1.5rem;
          max-width: 800px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .profile-overview-card {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .profile-header-section {
          display: flex;
          gap: 2rem;
          align-items: flex-start;
        }

        .avatar-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .avatar-large {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: #E8DAEF;
          color: #8B5CF6;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 3rem;
          font-weight: 700;
          position: relative;
        }

        .camera-button {
          position: absolute;
          bottom: 5px;
          right: 5px;
          background: #8B5CF6;
          border: 2px solid white;
          border-radius: 50%;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          cursor: pointer;
        }

        .verification-badge {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #10B981;
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .basic-info {
          flex: 1;
        }

        .basic-info h2 {
          margin: 0 0 0.5rem 0;
          font-size: 1.5rem;
          font-weight: 700;
          color: #1F2937;
        }

        .rating-display {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .rating-count {
          color: #6B7280;
          font-size: 0.9rem;
        }

        .specialization-tag {
          background: #F3F4F6;
          color: #4B5563;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.9rem;
          font-weight: 600;
          display: inline-block;
        }

        .info-card {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .info-card h3 {
          margin: 0 0 1.5rem 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .info-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.5rem;
        }

        .info-item {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
        }

        .info-icon {
          color: #8B5CF6;
          flex-shrink: 0;
          margin-top: 2px;
        }

        .info-content {
          flex: 1;
        }

        .info-content label {
          display: block;
          font-size: 0.9rem;
          color: #6B7280;
          margin-bottom: 0.25rem;
          font-weight: 600;
        }

        .info-content span {
          color: #1F2937;
          font-size: 1rem;
        }

        .edit-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #D1D5DB;
          border-radius: 8px;
          font-size: 1rem;
          color: #1F2937;
        }

        .edit-input:focus {
          outline: none;
          border-color: #8B5CF6;
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }

        .name-input {
          font-size: 1.5rem;
          font-weight: 700;
          padding: 0.75rem;
        }

        .specialization-input {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          border: 1px solid #D1D5DB;
        }

        .textarea, .bio-textarea {
          resize: vertical;
          min-height: 80px;
        }

        .certification-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .cert-badge {
          background: #EEF2FF;
          color: #8B5CF6;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .bio-text {
          color: #4B5563;
          line-height: 1.6;
          margin: 0;
        }

        .services-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .service-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: #F9FAFB;
          border-radius: 8px;
        }

        .service-icon {
          color: #10B981;
          flex-shrink: 0;
        }

        .availability-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 1rem;
        }

        .availability-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem;
          background: #F9FAFB;
          border-radius: 8px;
        }

        .day-name {
          font-weight: 600;
          color: #4B5563;
        }

        .availability-status {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          border-radius: 50%;
        }

        .availability-status.available {
          background: #10B981;
          color: white;
        }

        .availability-status.unavailable {
          background: #E5E7EB;
          color: #9CA3AF;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 1rem;
        }

        .stat-item {
          text-align: center;
          padding: 1rem;
          background: #F9FAFB;
          border-radius: 8px;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 800;
          color: #8B5CF6;
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.9rem;
          color: #6B7280;
          font-weight: 600;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .save-button, .cancel-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .save-button {
          background: #8B5CF6;
          color: white;
          border: none;
        }

        .save-button:hover {
          background: #7C3AED;
        }

        .cancel-button {
          background: #F3F4F6;
          color: #4B5563;
          border: 1px solid #D1D5DB;
        }

        .cancel-button:hover {
          background: #E5E7EB;
        }

        @media (min-width: 768px) {
          .info-grid {
            grid-template-columns: 1fr 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicDetails;
