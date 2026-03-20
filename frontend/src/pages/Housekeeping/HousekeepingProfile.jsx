import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import HousekeepingBottomNav from '../../components/HousekeepingBottomNav';
import { housekeepingService } from '../shared/api';
import { 
  User, CreditCard, Settings, HelpCircle, LogOut, 
  ChevronRight, Star, ShieldCheck, BadgeCheck, DollarSign, CheckCircle
} from 'lucide-react';
import '../Housekeeping/Housekeeping.css'; // Ensure we have styles

const HousekeepingProfile = () => {
  const { worker, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    completed: 0,
    rating: 0,
    earnings: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
        // Fetch real stats from API
        const balanceRes = await housekeepingService.getWorkerBalance();
        // For completed jobs and rating, we might need a stats endpoint or calculate from bookings
        // For now, let's use the balance and mock/calculate others if possible
        // Or if we can get bookings, we count completed ones
        const bookingsRes = await housekeepingService.getUserBookings(); // This returns bookings for the worker
        const bookings = bookingsRes.data.bookings || [];
        const completed = bookings.filter(b => b.status === 'COMPLETED').length;
        
        // Mock rating or calculate if we had reviews
        // Assuming worker object has rating
        const rating = worker?.rating || 4.8;

        setStats({
            completed: completed,
            rating: rating,
            earnings: balanceRes.data.balance
        });
    } catch (err) {
        console.error("Failed to load stats", err);
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
      navigate('/worker/login');
    }
  };

  const menuItems = [
    { icon: User, label: 'Personal Details', path: '/worker/housekeeping/details' },
    { icon: CreditCard, label: 'Payment Settings', path: '/worker/housekeeping/billing' },
    { icon: Settings, label: 'App Settings', path: '/worker/housekeeping/settings' },
    { icon: HelpCircle, label: 'Help & Support', path: '/worker/housekeeping/support' },
  ];

  return (
    <div className="doctor-profile-page">
      {/* Header Section - Reusing Doctor Profile styles which are global or copied */}
      <div className="profile-header" style={{background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)'}}>
        <div className="header-top">
          <User size={24} className="header-icon" />
          <h1 className="page-title">Profile</h1>
        </div>

        {/* Profile Card */}
        <div className="profile-card">
          <div className="profile-avatar-large" style={{background: '#F4ECF7', color: '#8E44AD'}}>
            {worker?.name ? worker.name[0].toUpperCase() : 'W'}
          </div>
          <div className="profile-info">
            <div className="name-row">
              <h2 className="doctor-name">{worker?.name || 'Housekeeper'}</h2>
              <BadgeCheck size={20} className="verified-badge" fill="#8E44AD" color="white" />
            </div>
            <p className="specialization">{worker?.specialization || 'General Cleaning'}</p>
            <div className="rating-row">
              <Star size={16} fill="#F1C40F" color="#F1C40F" />
              <span className="rating-value">{stats.rating}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="content-container">
        {/* ID & Verification Status */}
        <div className="status-card">
          <div className="status-row">
            <div className="status-label">
              <span className="status-icon id-icon" style={{background: '#8E44AD'}}>ID</span>
              <span>Worker ID</span>
            </div>
            <span className="status-value">{worker?.worker_id ? `HK${String(worker.worker_id).padStart(3, '0')}` : 'HK001'}</span>
          </div>
          <div className="status-divider"></div>
          <div className="status-row">
            <div className="status-label">
              <ShieldCheck size={16} className="status-icon verify-icon" style={{color: '#8E44AD'}} />
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
            <span className="stat-number">{stats.completed}</span>
            <span className="stat-label">Jobs Done</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">{stats.rating}</span>
            <span className="stat-label">Rating</span>
          </div>
          <div className="stat-box">
            <span className="stat-number">${stats.earnings.toFixed(0)}</span>
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

      <HousekeepingBottomNav />

      {/* Reusing styles from DoctorProfile via inline or global css, 
          but including specific overrides if needed */}
      <style>{`
        .doctor-profile-page {
          background-color: #F5F7FA;
          min-height: 100vh;
          padding-bottom: 90px;
          font-family: 'Inter', sans-serif;
        }

        .profile-header {
          background: linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%);
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
          color: #2C3E50;
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
          color: #8E44AD;
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
          color: #2C3E50;
        }

        .specialization {
          font-size: 0.9rem;
          color: #7F8C8D;
          margin: 0 0 0.5rem 0;
        }

        .rating-row {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-weight: 600;
          font-size: 0.9rem;
          color: #2C3E50;
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
          color: #7F8C8D;
          font-size: 0.9rem;
        }

        .status-icon {
          color: #8E44AD;
        }

        .id-icon {
          background: #8E44AD;
          color: white;
          font-size: 0.6rem;
          font-weight: 700;
          padding: 2px 4px;
          border-radius: 4px;
        }

        .status-value {
          font-weight: 600;
          font-size: 0.9rem;
          color: #2C3E50;
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
          color: #2C3E50;
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.8rem;
          color: #7F8C8D;
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
          color: #2C3E50;
        }

        .menu-label {
          font-weight: 600;
          color: #2C3E50;
          font-size: 0.95rem;
        }

        .menu-arrow {
          color: #7F8C8D;
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
      `}</style>
    </div>
  );
};

export default HousekeepingProfile;
