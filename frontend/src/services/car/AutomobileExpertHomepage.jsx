import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Phone, 
  Mail, 
  MapPin, 
  Wrench, 
  Clock, 
  DollarSign, 
  CheckCircle, 
  AlertCircle, 
  Power,
  Car,
  Settings,
  TrendingUp,
  Award,
  LogOut
} from 'lucide-react';

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
      const response = await fetch(`http://localhost:5000/api/automobile-expert/stats/${workerId}`);
      if (response.ok) {
        const data = await response.json();
        setStatsData({
          completedJobs: data.completedJobs || 0,
          totalEarnings: data.totalEarnings || 0,
          activeJobs: data.activeJobs || 0,
          avgRating: data.avgRating || 0
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
      const response = await fetch(`http://localhost:5000/api/automobile-expert/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          expert_id: parseInt(workerId),
          is_online: !isOnline
        })
      });

      if (response.ok) {
        const result = await response.json();
        setIsOnline(!isOnline);
        // Update local storage
        const updatedWorkerData = { ...workerData, is_online: !isOnline ? 1 : 0 };
        setWorkerData(updatedWorkerData);
        localStorage.setItem('automobileExpertData', JSON.stringify(updatedWorkerData));
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
            borderTop: '4px solid #3b82f6', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ marginTop: '16px', color: '#3b82f6' }}>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      <style>{`
        .dashboard-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px 20px 100px 20px;
        }
        
        @media (min-width: 768px) {
          .dashboard-container {
            padding: 32px 32px 100px 32px;
          }
        }
        
        .header-card {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          border-radius: 16px;
          padding: 24px;
          color: white;
          margin-bottom: 24px;
          box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);
        }
        
        .stats-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        
        .stat-box {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stat-box:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }
        
        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        
        .info-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
        }
        
        .status-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
          margin-bottom: 24px;
        }
        
        .status-button {
          width: 100%;
          padding: 12px 20px;
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
        }
        
        .status-button.online {
          background: #3b82f6;
          color: white;
        }
        
        .status-button.offline {
          background: #f3f4f6;
          color: #6b7280;
        }
        
        .status-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      <div className="dashboard-container">
        {/* Header Card */}
        <div className="header-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: '700', margin: '0 0 4px 0' }}>
                Automobile Expert Dashboard
              </h1>
              <p style={{ fontSize: '14px', opacity: 0.9, margin: 0 }}>
                Welcome back, {workerData?.name || 'Expert'}!
              </p>
            </div>
            <button 
              onClick={handleLogout}
              style={{ 
                background: 'rgba(255, 255, 255, 0.2)', 
                border: '1px solid rgba(255, 255, 255, 0.3)', 
                borderRadius: '6px', 
                padding: '8px 12px',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: '500'
              }}
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>Phone</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.phone || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>Email</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.email || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>Expertise</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.area_of_expertise || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>Experience</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.experience_years || '0'} years</div>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="stats-row">
          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Completed Jobs</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  {statsData.completedJobs}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dbeafe', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <CheckCircle style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
            </div>
          </div>

          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Total Earnings</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  ₹{statsData.totalEarnings.toLocaleString()}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dbeafe', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <DollarSign style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
            </div>
          </div>

          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Active Jobs</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  {statsData.activeJobs}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dbeafe', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Car style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
            </div>
          </div>

          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Avg Rating</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  {statsData.avgRating.toFixed(1)} ⭐
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dbeafe', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Award style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="info-grid">
          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#eff6ff', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <User style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Expert Profile
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Your professional information
                </p>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#374151', lineHeight: '1.5' }}>
              <div style={{ marginBottom: '4px' }}><strong>Name:</strong> {workerData?.name || 'N/A'}</div>
              <div style={{ marginBottom: '4px' }}><strong>Email:</strong> {workerData?.email || 'N/A'}</div>
              <div style={{ marginBottom: '4px' }}><strong>Experience:</strong> {workerData?.experience_years || '0'} years</div>
              <div><strong>Expertise:</strong> {workerData?.area_of_expertise || 'N/A'}</div>
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#eff6ff', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Wrench style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Service Details
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Your service information
                </p>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#374151', lineHeight: '1.5' }}>
              <div style={{ marginBottom: '4px' }}><strong>Worker Type:</strong> Automobile Expert</div>
              <div style={{ marginBottom: '4px' }}><strong>Specialization:</strong> {workerData?.area_of_expertise || 'N/A'}</div>
              <div><strong>Status:</strong> {workerData?.approval_status || 'PENDING'}</div>
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#eff6ff', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <TrendingUp style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Performance
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Your service metrics
                </p>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#374151', lineHeight: '1.5' }}>
              <div style={{ marginBottom: '4px' }}><strong>Completed Jobs:</strong> {statsData.completedJobs}</div>
              <div style={{ marginBottom: '4px' }}><strong>Total Earnings:</strong> ₹{statsData.totalEarnings.toLocaleString()}</div>
              <div><strong>Average Rating:</strong> {statsData.avgRating.toFixed(1)} ⭐</div>
            </div>
          </div>
        </div>

        {/* Status Card */}
        <div className="status-card">
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
              Availability Status
            </h3>
            <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
              {isOnline 
                ? 'You are currently online and available for automobile expert consultations.' 
                : 'You are currently offline and not receiving consultation requests.'
              }
            </p>
          </div>
          <button 
            onClick={handleOnlineToggle}
            className={`status-button ${isOnline ? 'online' : 'offline'}`}
          >
            <Power size={16} />
            {isOnline ? '🟢 Go Offline' : '🔴 Go Online'}
          </button>
        </div>

        {/* Bottom Navigation Bar */}
        <div style={{
          position: 'fixed',
          bottom: '0',
          left: '0',
          right: '0',
          background: 'white',
          borderTop: '1px solid #e5e7eb',
          padding: '12px 16px',
          display: 'flex',
          justifyContent: 'space-around',
          alignItems: 'center',
          zIndex: 1000,
          boxShadow: '0 -4px 12px rgba(0, 0, 0, 0.08)'
        }}>
          <div 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              minWidth: '60px'
            }}
            onClick={() => navigate('/worker/car/automobile-expert/home')}
          >
            <Car size={20} style={{ color: '#3b82f6' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#3b82f6' }}>Dashboard</span>
          </div>
          
          <div 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              minWidth: '60px'
            }}
            onClick={() => navigate('/worker/car/automobile-expert/requests')}
          >
            <Wrench size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Requests</span>
          </div>
          
          <div 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              minWidth: '60px'
            }}
            onClick={() => navigate('/worker/car/automobile-expert/active')}
          >
            <Settings size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Active</span>
          </div>
          
          <div 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              minWidth: '60px'
            }}
            onClick={() => navigate('/worker/car/automobile-expert/earnings')}
          >
            <DollarSign size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Earnings</span>
          </div>
          
          <div 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s ease',
              minWidth: '60px'
            }}
            onClick={() => navigate('/worker/car/automobile-expert/profile')}
          >
            <User size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Profile</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomobileExpertHomepage;
