import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  MapPin, 
  Phone, 
  Mail, 
  Calendar, 
  Award, 
  Settings, 
  LogOut,
  Wrench,
  Truck,
  Zap,
  Car,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Home,
  Briefcase,
  DollarSign,
  Shield,
  UserCircle,
  Star,
  TrendingUp,
  Users
} from 'lucide-react';
import { carService } from '../../shared/api';

const CarServiceHomepage = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    totalJobs: 0,
    completedJobs: 0,
    pendingJobs: 0,
    earnings: 0,
    rating: 0,
    todayJobs: 0,
    completionRate: 0,
    avgResponseTime: 0,
    fairnessScore: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [isOnline, setIsOnline] = useState(true);
  const [serviceRadius, setServiceRadius] = useState(26); // Add radius state

  useEffect(() => {
    fetchWorkerData();
  }, []);

  const fetchWorkerData = async () => {
    try {
      // Get worker data from localStorage
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (!storedData || !token) {
        navigate('/worker/car/mechanic/login');
        return;
      }

      const worker = JSON.parse(storedData);
      console.log('Worker data from localStorage:', worker);
      
      setWorkerData(worker);
      
      // Fetch dynamic data from backend
      try {
        // Get worker stats
        const statsResponse = await carService.getWorkerStats(worker.id || worker.worker_id);
        if (statsResponse.data) {
          setStats(prev => ({
            ...prev,
            ...statsResponse.data
          }));
        }

        // Get worker rating
        const ratingResponse = await carService.getWorkerRating(worker.id || worker.worker_id);
        if (ratingResponse.data) {
          setStats(prev => ({
            ...prev,
            rating: ratingResponse.data.rating || 0
          }));
        }

        // Get recent activity/jobs
        const activityResponse = await carService.getWorkerRecentActivity(worker.id || worker.worker_id);
        if (activityResponse.data && activityResponse.data.activities) {
          setRecentActivity(activityResponse.data.activities);
        }

        // Get performance metrics
        const performanceResponse = await carService.getWorkerPerformance(worker.id || worker.worker_id);
        if (performanceResponse.data) {
          setStats(prev => ({
            ...prev,
            ...performanceResponse.data
          }));
        }
      } catch (apiError) {
        console.log('API endpoints not available, using default values:', apiError.message);
        // Set default values if API fails - don't show error to user
        setStats({
          totalJobs: 0,
          completedJobs: 0,
          pendingJobs: 0,
          earnings: 0,
          rating: 0,
          todayJobs: 0,
          completionRate: 0,
          avgResponseTime: 0,
          fairnessScore: 0
        });
        setRecentActivity([]);
      }
      
    } catch (err) {
      console.error('Error fetching worker data:', err);
      setError('Failed to load worker data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('workerToken');
    localStorage.removeItem('workerData');
    navigate('/worker/car/mechanic/login');
  };

  const getWorkerIcon = (role) => {
    switch (role?.toLowerCase()) {
      case 'mechanic':
        return <Wrench size={24} className="role-icon" />;
      case 'fuel delivery agent':
        return <Zap size={24} className="role-icon" />;
      case 'automobile expert':
        return <Car size={24} className="role-icon" />;
      case 'tow truck operator':
        return <Truck size={24} className="role-icon" />;
      default:
        return <Wrench size={24} className="role-icon" />;
    }
  };

  const getRoleColor = (role) => {
    switch (role?.toLowerCase()) {
      case 'mechanic':
        return '#2563eb';
      case 'fuel delivery agent':
        return '#dc2626';
      case 'automobile expert':
        return '#16a34a';
      case 'tow truck operator':
        return '#ea580c';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="homepage-loading">
        <div className="loading-spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  if (error || !workerData) {
    return (
      <div className="homepage-error">
        <AlertCircle size={48} />
        <h3>Error Loading Dashboard</h3>
        <p>{error || 'No worker data found'}</p>
        <button onClick={() => navigate('/worker/car/mechanic/login')}>
          Go to Login
        </button>
      </div>
    );
  }

  return (
    <div className="car-service-homepage">
      {/* Header */}
      <div className="homepage-header">
        <div className="header-content">
          <div className="worker-info">
            <div className="worker-avatar">
              {getWorkerIcon(workerData.role)}
            </div>
            <div className="worker-details">
              <h1>Welcome back, {workerData.name || 'Worker'}!</h1>
              <p className="worker-role" style={{ color: getRoleColor(workerData.role) }}>
                {workerData.role || 'Car Service Worker'}
              </p>
              <div className="worker-meta">
                <span className="meta-item">
                  <MapPin size={14} />
                  {workerData.city || 'Location not set'}
                </span>
                <span className="meta-item">
                  <Phone size={14} />
                  {workerData.phone || 'Phone not set'}
                </span>
                <span className="meta-item">
                  <Mail size={14} />
                  {workerData.email || 'Email not set'}
                </span>
              </div>
            </div>
          </div>
          <div className="header-actions">
            <button className="action-btn secondary" onClick={() => navigate('/worker/car/mechanic/profile')}>
              <Settings size={16} />
              Profile
            </button>
            <button className="action-btn logout" onClick={handleLogout}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="homepage-content">
        {/* Status Control Section */}
        <div className="status-control-section">
          <div className="status-control-card">
            <div className="status-header">
              <h2>Status Control</h2>
              <div className="status-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={isOnline}
                    onChange={(e) => setIsOnline(e.target.checked)}
                  />
                  <span className="toggle-slider"></span>
                </label>
                <span className={`status-text ${isOnline ? 'online' : 'offline'}`}>
                  {isOnline ? 'On' : 'Off'}
                </span>
              </div>
            </div>
            
            <div className="status-pills">
              <div className={`status-pill ${isOnline ? 'online' : 'offline'}`}>
                <div className="status-dot"></div>
                {isOnline ? 'Online' : 'Offline'}
              </div>
              <div className="status-pill radius">
                <MapPin size={16} />
                Radius: {serviceRadius}km
              </div>
              <div className="status-pill mechanic">
                <Wrench size={16} />
                Mechanic
              </div>
            </div>

            <div className="service-radius-section">
              <label className="radius-label">Service Radius</label>
              <div className="radius-slider">
                <div className="slider-track">
                  <div 
                    className="slider-fill" 
                    style={{ width: `${(serviceRadius / 50) * 100}%` }}
                  ></div>
                </div>
                <input 
                  type="range" 
                  min="1" 
                  max="50" 
                  value={serviceRadius}
                  className="slider"
                  onChange={(e) => {
                    const value = parseInt(e.target.value);
                    setServiceRadius(value);
                  }}
                />
                <div className="slider-value">{serviceRadius}km</div>
              </div>
            </div>
          </div>

          {/* Today's Stats Cards - Below Status Control */}
          <div className="today-stats-cards-full">
            <div className="today-stat-card">
              <div className="stat-icon-wrapper">
                <div className="stat-icon-small today-icon">
                  <Calendar size={20} />
                </div>
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats.todayJobs}</div>
                <div className="stat-change positive">+{Math.floor(stats.todayJobs * 0.4)}</div>
                <div className="stat-label">Today's Jobs</div>
              </div>
            </div>
            
            <div className="today-stat-card">
              <div className="stat-icon-wrapper">
                <div className="stat-icon-small earnings-icon">
                  <Award size={20} />
                </div>
              </div>
              <div className="stat-content">
                <div className="stat-number">₹{stats.earnings?.toLocaleString() || 0}</div>
                <div className="stat-change positive">+₹{Math.floor((stats.earnings || 0) * 0.25)}</div>
                <div className="stat-label">Today's Earnings</div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card primary">
            <div className="stat-icon">
              <Calendar size={24} />
            </div>
            <div className="stat-content">
              <h3>{stats.totalJobs}</h3>
              <p>Total Jobs</p>
            </div>
          </div>
          
          <div className="stat-card success">
            <div className="stat-icon">
              <CheckCircle size={24} />
            </div>
            <div className="stat-content">
              <h3>{stats.completedJobs}</h3>
              <p>Completed</p>
            </div>
          </div>
          
          <div className="stat-card warning">
            <div className="stat-icon">
              <Clock size={24} />
            </div>
            <div className="stat-content">
              <h3>{stats.pendingJobs}</h3>
              <p>Pending</p>
            </div>
          </div>
          
          <div className="stat-card info">
            <div className="stat-icon">
              <Award size={24} />
            </div>
            <div className="stat-content">
              <h3>₹{stats.earnings}</h3>
              <p>Total Earnings</p>
            </div>
          </div>
        </div>

        {/* Rating and Today's Jobs */}
        <div className="secondary-stats">
          <div className="rating-card">
            <div className="rating-header">
              <Star size={20} className="star-icon" />
              <span>Your Rating</span>
            </div>
            <div className="rating-value">
              <span className="rating-number">{stats.rating.toFixed(1)}</span>
              <div className="rating-stars">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    size={16}
                    className={star <= Math.floor(stats.rating) ? "star-filled" : "star-empty"}
                  />
                ))}
              </div>
            </div>
          </div>
          
          <div className="today-jobs-card">
            <div className="today-header">
              <Users size={20} className="today-icon" />
              <span>Today's Jobs</span>
            </div>
            <div className="today-value">
              <span className="today-number">{stats.todayJobs}</span>
              <span className="today-label">jobs assigned</span>
            </div>
          </div>
        </div>

        
        {/* Performance Section */}
        <div className="performance-section">
          <h2><Zap size={20} /> Performance</h2>
          <div className="performance-grid">
            <div className="performance-card">
              <p className="performance-value">{stats.completionRate || 0}%</p>
              <span className="performance-label">Completion</span>
            </div>
            <div className="performance-card">
              <p className="performance-value">{stats.avgResponseTime || 0}min</p>
              <span className="performance-label">Avg Response</span>
            </div>
            <div className="performance-card">
              <p className="performance-value">{stats.fairnessScore || 0}</p>
              <span className="performance-label">Fairness</span>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="recent-activity">
          <h2>Recent Activity</h2>
          <div className="activity-list">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity, index) => (
                <div key={index} className="activity-item">
                  <div className={`activity-icon ${activity.status?.toLowerCase() || 'info'}`}>
                    {activity.status === 'completed' && <CheckCircle size={16} />}
                    {activity.status === 'in-progress' && <Clock size={16} />}
                    {activity.status === 'pending' && <Clock size={16} />}
                    {activity.status === 'cancelled' && <XCircle size={16} />}
                    {(!activity.status || activity.status === 'info') && <AlertCircle size={16} />}
                  </div>
                  <div className="activity-content">
                    <div className="activity-header">
                      <span className="customer-name">{activity.customerName || 'Unknown Customer'}</span>
                      <span className="activity-time">
                        {activity.time || new Date(activity.createdAt).toLocaleString([], {hour: '2-digit', minute:'2-digit'})}
                      </span>
                    </div>
                    <p className="service-description">{activity.service || activity.description || 'No service description'}</p>
                    <span className={`activity-status ${activity.status?.toLowerCase() || 'pending'}`}>
                      {activity.status || 'Pending'}
                    </span>
                  </div>
                  <div className={`activity-amount ${activity.earnings > 0 ? 'positive' : activity.earnings < 0 ? 'negative' : 'neutral'}`}>
                    {activity.earnings > 0 ? `₹${activity.earnings}` : 
                     activity.earnings < 0 ? `-₹${Math.abs(activity.earnings)}` : 
                     '-'}
                  </div>
                </div>
              ))
            ) : (
              <div className="no-activity">
                <AlertCircle size={32} />
                <p>No recent activity</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        <div className="nav-item active" onClick={() => navigate('/worker/car/mechanic/dashboard')}>
          <Home size={20} />
          <span>Dashboard</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/jobs')}>
          <Briefcase size={20} />
          <span>Jobs</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/active-jobs')}>
          <CheckCircle size={20} />
          <span>Active Jobs</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/performance')}>
          <TrendingUp size={20} />
          <span>Performance & Safety</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/slots')}>
          <Clock size={20} />
          <span>Slots</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/profile')}>
          <UserCircle size={20} />
          <span>Profile</span>
        </div>
      </div>

      <style>{`
        .car-service-homepage {
          min-height: 100vh;
          background: #f3f4f6;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
          position: relative;
        }

        .homepage-header {
          background: white;
          padding: 1.5rem 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border-radius: 0 0 1rem 1rem;
        }

        .header-content {
          max-width: 100%;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .worker-info {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .worker-avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: linear-gradient(135deg, #8B5CF6, #7C3AED);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 600;
          font-size: 1.2rem;
          box-shadow: 0 4px 6px rgba(139, 92, 246, 0.2);
        }

        .worker-details h1 {
          margin: 0;
          font-size: 1.25rem;
          color: #1f2937;
          font-weight: 600;
        }

        .worker-role {
          font-size: 0.875rem;
          font-weight: 500;
          margin: 0.25rem 0;
          color: #6b7280;
        }

        .worker-status {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          color: #10b981;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .worker-status::before {
          content: '';
          width: 6px;
          height: 6px;
          background: #10b981;
          border-radius: 50%;
        }

        .worker-meta {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 0.5rem;
          color: #6b7280;
          font-size: 0.875rem;
        }

        .header-actions {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 0.5rem;
        }

        .profile-section {
          text-align: right;
        }

        .profile-name {
          font-size: 1rem;
          font-weight: 600;
          color: #1f2937;
        }

        .profile-role {
          font-size: 0.75rem;
          color: #6b7280;
        }

        .profile-status {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          color: #10b981;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .profile-status::before {
          content: '';
          width: 6px;
          height: 6px;
          background: #10b981;
          border-radius: 50%;
        }

        .action-btn {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .action-btn.logout {
          background: #ef4444;
          color: white;
        }

        .action-btn.logout:hover {
          background: #dc2626;
        }

        .homepage-content {
          max-width: 100%;
          margin: 0 auto;
          padding: 1rem;
        }

        /* Stats Cards - White Theme */
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .stat-card {
          background: white;
          border-radius: 1rem;
          padding: 1.25rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          align-items: center;
          gap: 1rem;
          transition: transform 0.2s;
        }

        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .stat-card.primary .stat-icon {
          background: linear-gradient(135deg, #8B5CF6, #7C3AED);
        }

        .stat-card.success .stat-icon {
          background: linear-gradient(135deg, #10b981, #059669);
        }

        .stat-card.warning .stat-icon {
          background: linear-gradient(135deg, #f59e0b, #d97706);
        }

        .stat-card.info .stat-icon {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
        }

        .stat-content h3 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
        }

        .stat-content p {
          margin: 0.25rem 0 0 0;
          color: #6b7280;
          font-size: 0.875rem;
        }

        /* Secondary Stats - White Cards */
        .secondary-stats {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .rating-card, .today-jobs-card {
          background: white;
          border-radius: 1rem;
          padding: 1.25rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .rating-header, .today-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 1rem;
          color: #374151;
          font-weight: 600;
          font-size: 0.875rem;
        }

        .star-icon {
          color: #8B5CF6;
        }

        .today-icon {
          color: #8B5CF6;
        }

        .rating-value {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .rating-number {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
        }

        .today-value {
          display: flex;
          flex-direction: column;
        }

        .today-number {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
        }

        .today-label {
          color: #6b7280;
          font-size: 0.75rem;
        }

        /* Performance Section - White Card */
        .performance-section {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .performance-section h2 {
          margin: 0 0 1rem 0;
          color: #1f2937;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .performance-section h2 svg {
          color: #8B5CF6;
        }

        .performance-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1rem;
        }

        .performance-card {
          text-align: center;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 0.75rem;
          transition: all 0.2s;
        }

        .performance-card:hover {
          background: #f3f4f6;
        }

        .performance-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin: 0 0 0.25rem 0;
          line-height: 1;
        }

        .performance-label {
          color: #6b7280;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        /* Recent Activity - White Card */
        .recent-activity {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .recent-activity h2 {
          margin: 0 0 1rem 0;
          color: #1f2937;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .activity-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .activity-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 0.75rem;
          transition: all 0.2s;
        }

        .activity-item:hover {
          background: #f3f4f6;
        }

        .activity-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          flex-shrink: 0;
        }

        .activity-icon.success {
          background: #10b981;
        }

        .activity-icon.pending {
          background: #f59e0b;
        }

        .activity-icon.in-progress {
          background: #3b82f6;
        }

        .activity-icon.cancelled {
          background: #ef4444;
        }

        .activity-icon.info {
          background: #8B5CF6;
        }

        .activity-content {
          flex: 1;
          min-width: 0;
        }

        .activity-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.25rem;
        }

        .customer-name {
          font-weight: 600;
          color: #1f2937;
          font-size: 0.875rem;
        }

        .service-description {
          margin: 0.25rem 0;
          color: #6b7280;
          font-size: 0.813rem;
          line-height: 1.3;
        }

        .activity-status {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.025em;
          margin-top: 0.25rem;
        }

        .activity-status.completed {
          background: #d1fae5;
          color: #065f46;
        }

        .activity-status.in-progress {
          background: #dbeafe;
          color: #1e40af;
        }

        .activity-status.pending {
          background: #fef3c7;
          color: #92400e;
        }

        .activity-status.cancelled {
          background: #fee2e2;
          color: #991b1b;
        }

        .activity-time {
          color: #9ca3af;
          font-size: 0.75rem;
        }

        .activity-amount {
          font-weight: 600;
          color: #1f2937;
          font-size: 0.875rem;
          text-align: right;
        }

        .activity-amount.positive {
          color: #10b981;
        }

        .activity-amount.negative {
          color: #ef4444;
        }

        .no-activity {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 2rem;
          color: #9ca3af;
          text-align: center;
        }

        .no-activity svg {
          margin-bottom: 1rem;
          opacity: 0.5;
        }

        /* Status Control Section */
        .status-control-section {
          display: block;
          margin-bottom: 1.5rem;
        }

        .status-control-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .status-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .status-header h2 {
          margin: 0;
          color: #1f2937;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .status-toggle {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .toggle-switch {
          position: relative;
          display: inline-block;
          width: 50px;
          height: 24px;
        }

        .toggle-switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }

        .toggle-slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #e5e7eb;
          transition: 0.4s;
          border-radius: 24px;
        }

        .toggle-slider:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: 0.4s;
          border-radius: 50%;
        }

        .toggle-switch input:checked + .toggle-slider {
          background-color: #10b981;
        }

        .toggle-switch input:not(:checked) + .toggle-slider {
          background-color: #ef4444;
        }

        .toggle-switch input:checked + .toggle-slider:before {
          transform: translateX(26px);
        }

        .toggle-switch input:not(:checked) + .toggle-slider:before {
          transform: translateX(3px);
        }

        .status-text {
          font-weight: 600;
          font-size: 0.875rem;
          transition: color 0.3s ease;
        }

        .status-text.online {
          color: #10b981;
        }

        .status-text.offline {
          color: #ef4444;
        }

        .status-pills {
          display: flex;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
        }

        .status-pill {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.3s ease;
        }

        .status-pill.online {
          background: #d1fae5;
          color: #065f46;
        }

        .status-pill.offline {
          background: #fee2e2;
          color: #991b1b;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          transition: background-color 0.3s ease;
        }

        .status-pill.online .status-dot {
          background: #10b981;
        }

        .status-pill.offline .status-dot {
          background: #ef4444;
        }

        .service-radius-section {
          margin-bottom: 1rem;
        }

        .radius-label {
          display: block;
          margin-bottom: 0.75rem;
          color: #374151;
          font-weight: 500;
          font-size: 0.875rem;
        }

        .radius-slider {
          position: relative;
        }

        .slider-track {
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          transform: translateY(-50%);
          pointer-events: none;
        }

        .slider-fill {
          height: 100%;
          background: #8B5CF6;
          border-radius: 4px;
          transition: width 0.3s ease;
          position: relative;
        }

        .slider {
          width: 100%;
          height: 8px;
          background: transparent;
          outline: none;
          -webkit-appearance: none;
          position: relative;
          z-index: 2;
          cursor: pointer;
        }

        .slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #8B5CF6;
          cursor: pointer;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
          transition: all 0.2s ease;
          position: relative;
          z-index: 3;
          top: -8px;
        }

        .slider::-webkit-slider-thumb:hover {
          transform: scale(1.1);
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }

        .slider::-moz-range-thumb {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #8B5CF6;
          cursor: pointer;
          border: 3px solid white;
          box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
          transition: all 0.2s ease;
          position: relative;
          z-index: 3;
          top: -8px;
        }

        .slider::-moz-range-thumb:hover {
          transform: scale(1.1);
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }

        .slider-value {
          text-align: center;
          margin-top: 1rem;
          color: #6b7280;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .today-stats-cards-full {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .today-stat-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .stat-icon-wrapper {
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .stat-icon-small {
          width: 48px;
          height: 48px;
          border-radius: 0.75rem;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .today-icon {
          background: #8B5CF6;
        }

        .earnings-icon {
          background: #8B5CF6;
        }

        .stat-content {
          flex: 1;
        }

        .stat-number {
          font-size: 1.75rem;
          font-weight: 700;
          color: #1f2937;
          line-height: 1;
        }

        .stat-change {
          font-size: 0.875rem;
          font-weight: 600;
          margin-top: 0.25rem;
        }

        .stat-change.positive {
          color: #10b981;
        }

        .stat-label {
          color: #6b7280;
          font-size: 0.75rem;
          margin-top: 0.25rem;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
          .secondary-stats {
            grid-template-columns: 1fr;
          }
          
          .performance-grid {
            grid-template-columns: 1fr;
            gap: 0.75rem;
          }
          
          .stats-grid {
            grid-template-columns: 1fr;
          }

          .today-stats-cards-full {
            grid-template-columns: 1fr;
            gap: 1rem;
          }

          .status-pills {
            flex-wrap: wrap;
            gap: 0.5rem;
          }

          .status-pill {
            font-size: 0.75rem;
            padding: 0.375rem 0.75rem;
          }

          .slider {
            height: 6px;
          }

          .slider::-webkit-slider-thumb {
            width: 20px;
            height: 20px;
            border: 2px solid white;
          }

          .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border: 2px solid white;
          }
        }

        /* Loading and Error States */
        .homepage-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          color: #6b7280;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #e5e7eb;
          border-top: 3px solid #8B5CF6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .homepage-error {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          color: #6b7280;
          text-align: center;
          padding: 2rem;
        }

        .homepage-error h3 {
          margin: 1rem 0;
          color: #1f2937;
        }

        .homepage-error button {
          margin-top: 1rem;
          padding: 0.75rem 1.5rem;
          background: #8B5CF6;
          color: white;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
        }

        .homepage-error button:hover {
          background: #7C3AED;
        }

        /* Bottom Navigation */
        .bottom-navigation {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: white;
          border-top: 1px solid #e5e7eb;
          display: flex;
          justify-content: space-around;
          align-items: center;
          padding: 0.5rem 0;
          z-index: 9999;
          box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
        }

        .nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
          cursor: pointer;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          transition: all 0.2s ease;
          min-width: 60px;
        }

        .nav-item:hover {
          background: #f8fafc;
          transform: translateY(-2px);
        }

        .nav-item.active {
          color: #8B5CF6;
        }

        .nav-item.active svg {
          color: #8B5CF6;
        }

        .nav-item svg {
          color: #6b7280;
          transition: color 0.2s ease;
        }

        .nav-item:hover svg {
          color: #8B5CF6;
        }

        .nav-item span {
          font-size: 0.75rem;
          font-weight: 500;
          color: #6b7280;
          transition: color 0.2s ease;
        }

        .nav-item.active span {
          color: #8B5CF6;
          font-weight: 600;
        }

        .nav-item:hover span {
          color: #8B5CF6;
        }
      `}</style>
    </div>
  );
};

export default CarServiceHomepage;
