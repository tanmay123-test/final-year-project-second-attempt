import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  MapPin, 
  Mail, 
  LogOut, 
  CheckCircle, 
  DollarSign, 
  Power,
  Car,
  Award,
  TrendingUp,
  Wrench
} from 'lucide-react';
import api from '../../shared/api';
import { useAuth } from '../../context/AuthContext';
import AutomobileExpertBottomNav from '../../components/AutomobileExpertBottomNav';

const AutomobileExpertHomepage = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [statsData, setStatsData] = useState({
    completedJobs: 0,
    totalEarnings: 0,
    activeJobs: 0,
    avgRating: 0
  });

  useEffect(() => {
    // Get worker data from localStorage
    const storedWorkerData = localStorage.getItem('automobileExpertData');
    const storedToken = localStorage.getItem('automobileExpertToken');

    if (storedWorkerData && storedToken) {
      const worker = JSON.parse(storedWorkerData);
      setWorkerData(worker);
      setIsOnline(worker.is_online === 1);
      fetchStatsData();
    } else {
      navigate('/worker/car/automobile-expert/login');
    }
    setLoading(false);
  }, [navigate]);

  const fetchStatsData = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      const response = await api.get(`/api/expert-availability/dashboard/${workerId}`);
      if (response.data) {
        const data = response.data;
        setStatsData({
          completedJobs: data.performance_stats?.total_consultations || 0,
          totalEarnings: 0, // Add earnings tracking later
          activeJobs: data.current_consultation ? 1 : 0,
          avgRating: data.performance_stats?.rating || 0
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleOnlineToggle = async () => {
    try {
      const workerData = JSON.parse(localStorage.getItem('automobileExpertData') || '{}');
      const workerId = workerData.id;
      
      if (isOnline) {
        // Go offline
        const response = await api.post('/api/expert-availability/go-offline', {
          expert_id: parseInt(workerId)
        });

        if (response.data.success) {
          setIsOnline(false);
          // Update local storage
          const updatedWorkerData = { ...workerData, is_online: 0 };
          setWorkerData(updatedWorkerData);
          localStorage.setItem('automobileExpertData', JSON.stringify(updatedWorkerData));
        }
      } else {
        // Go online
        const response = await api.post('/api/expert-availability/go-online', {
          expert_id: parseInt(workerId)
        });

        if (response.data.success) {
          setIsOnline(true);
          // Update local storage
          const updatedWorkerData = { ...workerData, is_online: 1 };
          setWorkerData(updatedWorkerData);
          localStorage.setItem('automobileExpertData', JSON.stringify(updatedWorkerData));
        }
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('automobileExpertToken');
    localStorage.removeItem('automobileExpertData');
    navigate('/worker/car/automobile-expert/login');
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid #e5e7eb', 
            borderTop: '4px solid #8b5cf6', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ marginTop: '16px', color: '#8b5cf6' }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', paddingBottom: '80px' }}>
      <style>{`
        .dashboard-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 16px 16px 100px 16px;
        }
        
        @media (min-width: 640px) {
          .dashboard-container {
            padding: 20px 20px 100px 20px;
          }
        }
        
        @media (min-width: 768px) {
          .dashboard-container {
            padding: 24px 24px 100px 24px;
          }
        }
        
        @media (min-width: 1024px) {
          .dashboard-container {
            padding: 32px 32px 100px 32px;
          }
        }
        
        .header-section {
          background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
          border-radius: 16px;
          padding: 20px;
          color: white;
          margin-bottom: 20px;
          box-shadow: 0 4px 20px rgba(139, 92, 246, 0.15);
        }
        
        @media (min-width: 640px) {
          .header-section {
            padding: 24px;
            margin-bottom: 24px;
          }
        }
        
        .header-content {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        @media (min-width: 768px) {
          .header-content {
            flex-direction: row;
            justify-content: space-between;
            align-items: flex-start;
          }
        }
        
        .header-title {
          flex: 1;
        }
        
        .header-actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
          align-items: stretch;
        }
        
        @media (min-width: 640px) {
          .header-actions {
            flex-direction: row;
            align-items: center;
            justify-content: flex-end;
          }
        }
        
        .stats-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
          margin-bottom: 20px;
        }
        
        @media (min-width: 640px) {
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 24px;
          }
        }
        
        @media (min-width: 1024px) {
          .stats-grid {
            grid-template-columns: repeat(4, 1fr);
          }
        }
        
        .stat-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        @media (min-width: 640px) {
          .stat-card {
            padding: 24px;
          }
        }
        
        .stat-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .info-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
          margin-bottom: 20px;
        }
        
        @media (min-width: 768px) {
          .info-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 24px;
          }
        }
        
        .info-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
        }
        
        @media (min-width: 640px) {
          .info-card {
            padding: 24px;
          }
        }
        
        .status-section {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
          margin-bottom: 20px;
        }
        
        @media (min-width: 640px) {
          .status-section {
            padding: 24px;
            margin-bottom: 24px;
          }
        }
        
        .status-button {
          width: 100%;
          padding: 12px 16px;
          border-radius: 8px;
          border: none;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          min-width: 120px;
        }
        
        @media (min-width: 640px) {
          .status-button {
            width: auto;
            min-width: 140px;
            padding: 12px 20px;
          }
        }
        
        .status-button.online {
          background: #10b981;
          color: white;
        }
        
        .status-button.offline {
          background: #ef4444;
          color: white;
        }
        
        .status-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .logout-button {
          background: rgba(255, 255, 255, 0.2);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          padding: 10px 16px;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s ease;
        }
        
        .logout-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }
        
        .expert-info-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 12px;
        }
        
        @media (min-width: 640px) {
          .expert-info-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
          }
        }
        
        .quick-actions-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 12px;
        }
        
        @media (min-width: 640px) {
          .quick-actions-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
          }
        }
        
        @media (min-width: 1024px) {
          .quick-actions-grid {
            grid-template-columns: repeat(4, 1fr);
          }
        }
        
        .quick-action-button {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 16px;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          text-align: center;
        }
        
        @media (min-width: 640px) {
          .quick-action-button {
            padding: 20px;
          }
        }
        
        .quick-action-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
          border-color: #8b5cf6;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      <div className="dashboard-container">
        {/* Header Section */}
        <div className="header-section">
          <div className="header-content">
            <div className="header-title">
              <h1 style={{ fontSize: 'clamp(20px, 5vw, 28px)', fontWeight: '700', margin: '0 0 8px 0', lineHeight: '1.2' }}>
                Automobile Expert Dashboard
              </h1>
              <p style={{ fontSize: 'clamp(14px, 3vw, 16px)', opacity: 0.9, margin: 0, lineHeight: '1.4' }}>
                Welcome back, {workerData?.name || 'Expert'}!
              </p>
            </div>
            <div className="header-actions">
              <button 
                onClick={handleOnlineToggle}
                className={`status-button ${isOnline ? 'online' : 'offline'}`}
              >
                <Power size={16} />
                {isOnline ? '🟢 Online' : '🔴 Offline'}
              </button>
              <button 
                onClick={handleLogout}
                className="logout-button"
              >
                <LogOut size={18} />
                <span style={{ display: 'none' }}>Logout</span>
              </button>
            </div>
          </div>
          
          <div className="expert-info-grid">
            <div>
              <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '4px' }}>Email</div>
              <div style={{ fontSize: '16px', fontWeight: '600', wordBreak: 'break-word' }}>{workerData?.email || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '4px' }}>Expertise</div>
              <div style={{ fontSize: '16px', fontWeight: '600' }}>{workerData?.area_of_expertise || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '4px' }}>Experience</div>
              <div style={{ fontSize: '16px', fontWeight: '600' }}>{workerData?.experience_years || '0'} years</div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Completed Jobs</div>
                <div style={{ fontSize: 'clamp(24px, 4vw, 32px)', fontWeight: '700', color: '#111827' }}>
                  {statsData.completedJobs}
                </div>
              </div>
              <div style={{ 
                width: 'clamp(40px, 6vw, 50px)', 
                height: 'clamp(40px, 6vw, 50px)', 
                borderRadius: '10px', 
                background: '#dbeafe', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <CheckCircle style={{ width: 'clamp(18px, 3vw, 24px)', height: 'clamp(18px, 3vw, 24px)', color: '#3b82f6' }} />
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '12px' }}>
              Total consultations completed successfully
            </div>
          </div>

          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Earnings</div>
                <div style={{ fontSize: 'clamp(20px, 4vw, 28px)', fontWeight: '700', color: '#111827' }}>
                  ₹{statsData.totalEarnings.toLocaleString()}
                </div>
              </div>
              <div style={{ 
                width: 'clamp(40px, 6vw, 50px)', 
                height: 'clamp(40px, 6vw, 50px)', 
                borderRadius: '10px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <DollarSign style={{ width: 'clamp(18px, 3vw, 24px)', height: 'clamp(18px, 3vw, 24px)', color: '#16a34a' }} />
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '12px' }}>
              Total revenue from all consultations
            </div>
          </div>

          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Active Jobs</div>
                <div style={{ fontSize: 'clamp(24px, 4vw, 32px)', fontWeight: '700', color: '#111827' }}>
                  {statsData.activeJobs}
                </div>
              </div>
              <div style={{ 
                width: 'clamp(40px, 6vw, 50px)', 
                height: 'clamp(40px, 6vw, 50px)', 
                borderRadius: '10px', 
                background: '#fef3c7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Car style={{ width: 'clamp(18px, 3vw, 24px)', height: 'clamp(18px, 3vw, 24px)', color: '#d97706' }} />
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '12px' }}>
              Currently active consultations
            </div>
          </div>

          <div className="stat-card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Avg Rating</div>
                <div style={{ fontSize: 'clamp(24px, 4vw, 32px)', fontWeight: '700', color: '#111827' }}>
                  {statsData.avgRating.toFixed(1)} ⭐
                </div>
              </div>
              <div style={{ 
                width: 'clamp(40px, 6vw, 50px)', 
                height: 'clamp(40px, 6vw, 50px)', 
                borderRadius: '10px', 
                background: '#fef3c7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Award style={{ width: 'clamp(18px, 3vw, 24px)', height: 'clamp(18px, 3vw, 24px)', color: '#d97706' }} />
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '12px' }}>
              Average customer rating
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="info-grid">
          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '10px', 
                background: '#eff6ff', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <User style={{ width: '24px', height: '24px', color: '#3b82f6' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 4px 0' }}>
                  Expert Profile
                </h3>
                <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                  Your professional information
                </p>
              </div>
            </div>
            <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '8px' }}><strong>Name:</strong> {workerData?.name || 'N/A'}</div>
              <div style={{ marginBottom: '8px' }}><strong>Email:</strong> {workerData?.email || 'N/A'}</div>
              <div style={{ marginBottom: '8px' }}><strong>Experience:</strong> {workerData?.experience_years || '0'} years</div>
              <div><strong>Expertise:</strong> {workerData?.area_of_expertise || 'N/A'}</div>
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '10px', 
                background: '#eff6ff', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Wrench style={{ width: '24px', height: '24px', color: '#3b82f6' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 4px 0' }}>
                  Service Details
                </h3>
                <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                  Your service information
                </p>
              </div>
            </div>
            <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '8px' }}><strong>Worker Type:</strong> Automobile Expert</div>
              <div style={{ marginBottom: '8px' }}><strong>Specialization:</strong> {workerData?.area_of_expertise || 'N/A'}</div>
              <div><strong>Status:</strong> {workerData?.approval_status || 'PENDING'}</div>
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
              <div style={{ 
                width: '50px', 
                height: '50px', 
                borderRadius: '10px', 
                background: '#eff6ff', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <TrendingUp style={{ width: '24px', height: '24px', color: '#3b82f6' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', margin: '0 0 4px 0' }}>
                  Performance
                </h3>
                <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
                  Your service metrics
                </p>
              </div>
            </div>
            <div style={{ fontSize: '14px', color: '#374151', lineHeight: '1.6' }}>
              <div style={{ marginBottom: '8px' }}><strong>Completed Jobs:</strong> {statsData.completedJobs}</div>
              <div style={{ marginBottom: '8px' }}><strong>Total Earnings:</strong> ₹{statsData.totalEarnings.toLocaleString()}</div>
              <div><strong>Average Rating:</strong> {statsData.avgRating.toFixed(1)} ⭐</div>
            </div>
          </div>
        </div>

        
        {/* Bottom Navigation Bar */}
        <AutomobileExpertBottomNav />
      </div>
    </div>
  );
};

export default AutomobileExpertHomepage;
