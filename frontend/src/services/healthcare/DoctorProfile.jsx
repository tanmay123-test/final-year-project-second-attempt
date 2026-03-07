import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import DoctorBottomNav from '../../components/DoctorBottomNav';
import { 
  User, CreditCard, Settings, HelpCircle, LogOut, 
  ChevronRight, Star, ShieldCheck, BadgeCheck
} from 'lucide-react';

const DoctorProfile = () => {
  const { worker, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
      navigate('/worker/login');
    }
  };

  // Mock data for stats - in a real app these would come from an API
  const stats = {
    patients: 156,
    experience: '12 years',
    earnings: '₹45K'
  };

  const menuItems = [
    { icon: User, label: 'View Full Details', path: '/doctor/profile/details' },
    { icon: CreditCard, label: 'Subscription & Billing', path: '/doctor/billing' },
    { icon: Settings, label: 'Settings', path: '/doctor/settings' },
    { icon: HelpCircle, label: 'Help & Support', path: '/doctor/support' },
  ];

  return (
    <div className="doctor-profile-page">
      {/* Header Section */}
      <div className="profile-header">
        <div className="header-top">
          <User size={24} className="header-icon" />
          <h1 className="page-title">Profile</h1>
        </div>

        {/* Profile Card */}
        <div className="profile-card">
          <div className="profile-avatar-large">
            {worker?.name ? worker.name[0].toUpperCase() : 'D'}
          </div>
          <div className="profile-info">
            <div className="name-row">
              <h2 className="doctor-name">Dr. {worker?.name || 'Sarah Johnson'}</h2>
              <BadgeCheck size={20} className="verified-badge" fill="#8E44AD" color="white" />
            </div>
            <p className="specialization">{worker?.specialization || 'Cardiologist'}</p>
            <div className="rating-row">
              <Star size={16} fill="#8E44AD" color="#8E44AD" />
              <span className="rating-value">4.9</span>
            </div>
          </div>
        </div>
      </div>

      <div className="content-container">
        {/* ID & Verification Status */}
        <div className="status-card">
          <div className="status-row">
            <div className="status-label">
              <span className="status-icon id-icon">ID</span>
              <span>Worker ID</span>
            </div>
            <span className="status-value">{worker?.worker_id ? `DOC${String(worker.worker_id).padStart(3, '0')}` : 'DOC001'}</span>
          </div>
          <div className="status-divider"></div>
          <div className="status-row">
            <div className="status-label">
              <ShieldCheck size={16} className="status-icon verify-icon" />
              <span>Verification</span>
            </div>
            <span className="status-value verified">
              <span className="check-box">✓</span> Approved
            </span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-row">
          <div className="stat-box">
            <span className="stat-number">{stats.patients}</span>
            <span className="stat-label">Patients</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">{stats.experience}</span>
            <span className="stat-label">Experience</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">{stats.earnings}</span>
            <span className="stat-label">Earnings</span>
          </div>
        </div>

        {/* Menu Items */}
        <div className="menu-list">
          {menuItems.map((item, index) => (
            <div key={index} className="menu-item" onClick={() => navigate(item.path)}>
              <div className="menu-item-left">
                <div className="menu-icon-wrapper">
                  <item.icon size={20} />
                </div>
                <span className="menu-label">{item.label}</span>
              </div>
              <ChevronRight size={20} className="menu-arrow" />
            </div>
          ))}
        </div>

        {/* Logout Button */}
        <button className="logout-button" onClick={handleLogout}>
          <div className="logout-content">
            <div className="logout-icon-wrapper">
              <LogOut size={20} />
            </div>
            <span>Logout</span>
          </div>
        </button>
      </div>

      <DoctorBottomNav />

      <style>{`
        .doctor-profile-page {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 90px;
          font-family: 'Inter', sans-serif;
        }

        .profile-header {
          background: var(--medical-gradient);
          padding: 2rem 1.5rem 4rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
          position: relative;
        }

        .header-top {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 2rem;
        }

        .page-title {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
        }

        .profile-card {
          background: white;
          border-radius: 20px;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1.5rem;
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
          color: var(--text-primary);
          position: absolute;
          bottom: -40px;
          left: 1.5rem;
          right: 1.5rem;
          max-width: 500px;
          margin: 0 auto;
        }

        .profile-avatar-large {
          width: 70px;
          height: 70px;
          border-radius: 50%;
          background: #E8DAEF;
          color: var(--accent-blue);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          font-weight: 700;
          flex-shrink: 0;
        }

        .profile-info {
          flex: 1;
        }

        .name-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.25rem;
        }

        .doctor-name {
          font-size: 1.1rem;
          font-weight: 700;
          margin: 0;
          color: var(--text-primary);
        }

        .specialization {
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin: 0 0 0.5rem 0;
        }

        .rating-row {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-weight: 600;
          font-size: 0.9rem;
          color: var(--text-primary);
        }

        .content-container {
          padding: 4rem 1.5rem 2rem;
          max-width: 600px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .status-card {
          background: white;
          border-radius: 16px;
          padding: 1rem 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .status-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem 0;
        }

        .status-divider {
          height: 1px;
          background: #F0F0F0;
          margin: 0.5rem 0;
        }

        .status-label {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          color: var(--text-secondary);
          font-size: 0.9rem;
        }

        .status-icon {
          color: var(--accent-blue);
        }

        .id-icon {
          background: var(--accent-blue);
          color: white;
          font-size: 0.6rem;
          font-weight: 700;
          padding: 2px 4px;
          border-radius: 4px;
        }

        .status-value {
          font-weight: 600;
          font-size: 0.9rem;
          color: var(--text-primary);
        }

        .status-value.verified {
          color: #27AE60;
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .check-box {
          background: #27AE60;
          color: white;
          width: 16px;
          height: 16px;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.7rem;
        }

        .stats-row {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
        }

        .stat-box {
          background: white;
          border-radius: 16px;
          padding: 1.25rem 0.5rem;
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .stat-number {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        .menu-list {
          background: white;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .menu-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid #F5F7FA;
          cursor: pointer;
          transition: background 0.2s;
        }

        .menu-item:last-child {
          border-bottom: none;
        }

        .menu-item:hover {
          background: #F9FAFB;
        }

        .menu-item-left {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .menu-icon-wrapper {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: #F5F7FA;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-primary);
        }

        .menu-label {
          font-weight: 600;
          color: var(--text-primary);
          font-size: 0.95rem;
        }

        .menu-arrow {
          color: var(--text-secondary);
          opacity: 0.5;
        }

        .logout-button {
          background: #FDEDEC;
          border: none;
          border-radius: 16px;
          padding: 1rem;
          width: 100%;
          cursor: pointer;
          margin-top: 0.5rem;
          transition: background 0.2s;
        }

        .logout-button:hover {
          background: #FADBD8;
        }

        .logout-content {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding-left: 0.5rem;
        }

        .logout-icon-wrapper {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: rgba(231, 76, 60, 0.1);
          color: #E74C3C;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .logout-content span {
          font-weight: 600;
          color: #E74C3C;
          font-size: 1rem;
        }

        @media (min-width: 768px) {
           .profile-header {
             padding: 2rem 2rem 5rem;
           }
           
           .content-container {
             padding-top: 5rem;
           }
        }
      `}</style>
    </div>
  );
};

export default DoctorProfile;
