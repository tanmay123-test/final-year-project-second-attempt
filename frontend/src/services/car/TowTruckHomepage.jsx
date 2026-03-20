import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Truck,
  Home,
  Package,
  History,
  Target,
  User,
  MapPin,
  Phone,
  Mail,
  LogOut,
  Settings,
  TrendingUp,
  DollarSign,
  Clock,
  CheckCircle,
  AlertCircle,
  Users,
  Navigation
} from 'lucide-react';

const TowTruckHomepage = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [jobsData, setJobsData] = useState({
    activeJobs: 0,
    totalEarnings: 0,
    completedToday: 0
  });

  const handleOnlineToggle = async () => {
    try {
      const newStatus = !isOnline;
      const workerId = localStorage.getItem('workerId');
      
      const response = await fetch(`http://localhost:5000/api/tow-truck/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('workerToken')}`
        },
        body: JSON.stringify({
          is_online: newStatus
        })
      });

      if (response.ok) {
        setIsOnline(newStatus);
        if (workerData) {
          setWorkerData({...workerData, is_online: newStatus ? 1 : 0});
        }
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('workerToken');
      localStorage.removeItem('workerData');
      localStorage.removeItem('workerId');
      navigate('/worker/car/tow-truck/login');
    }
  };

  useEffect(() => {
    const storedWorkerData = localStorage.getItem('workerData');
    const workerId = localStorage.getItem('workerId');
    
    if (storedWorkerData && workerId) {
      const parsedData = JSON.parse(storedWorkerData);
      setWorkerData(parsedData);
      setIsOnline(parsedData.is_online === 1);
      setLoading(false);
      
      // Fetch jobs and earnings data
      fetchJobsAndEarnings(workerId);
    } else {
      navigate('/worker/car/tow-truck/login');
    }
  }, [navigate]);

  const fetchJobsAndEarnings = async (workerId) => {
    try {
      // Fetch active jobs count
      const response = await fetch(`http://localhost:5000/api/tow-truck/active-jobs/${workerId}`);
      const data = await response.json();
      
      if (data.success) {
        setJobsData({
          activeJobs: data.activeJobs || 0,
          totalEarnings: data.totalEarnings || 0,
          completedToday: data.completedToday || 0
        });
      }
    } catch (error) {
      console.error('Error fetching jobs and earnings:', error);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '48px', 
            height: '48px', 
            border: '4px solid #dcfce7', 
            borderTop: '4px solid #16a34a', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ marginTop: '16px', color: '#16a34a' }}>Loading dashboard...</p>
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
          background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
          border-radius: 16px;
          padding: 24px;
          color: white;
          margin-bottom: 24px;
          box-shadow: 0 4px 20px rgba(22, 163, 74, 0.15);
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
        }
        
        .status-button.online {
          background: #16a34a;
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
                Tow Truck Dashboard
              </h1>
              <p style={{ fontSize: '14px', opacity: 0.9, margin: 0 }}>
                Welcome back, {workerData?.name || 'Operator'}!
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
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.phone || ''}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>City</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.city || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>Truck Type</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.truck_type || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '2px' }}>Registration</div>
              <div style={{ fontSize: '14px', fontWeight: '600' }}>{workerData?.truck_registration || 'N/A'}</div>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="stats-row">
          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Active Jobs</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  {jobsData.activeJobs}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Package style={{ width: '20px', height: '20px', color: '#16a34a' }} />
              </div>
            </div>
          </div>

          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Total Earnings</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  ₹{jobsData.totalEarnings.toLocaleString()}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <DollarSign style={{ width: '20px', height: '20px', color: '#16a34a' }} />
              </div>
            </div>
          </div>

          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Completed Today</div>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#111827' }}>
                  {jobsData.completedToday}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <CheckCircle style={{ width: '20px', height: '20px', color: '#16a34a' }} />
              </div>
            </div>
          </div>

          <div className="stat-box">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Status</div>
                <div style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                  {isOnline ? '🟢 Online' : '🔴 Offline'}
                </div>
              </div>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: isOnline ? '#dcfce7' : '#fef3c7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <AlertCircle style={{ width: '20px', height: '20px', color: isOnline ? '#16a34a' : '#f59e0b' }} />
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
                background: '#f0fdf4', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <User style={{ width: '20px', height: '20px', color: '#16a34a' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Operator Details
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Your professional information
                </p>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#374151', lineHeight: '1.5' }}>
              <div style={{ marginBottom: '4px' }}><strong>Name:</strong> {workerData?.name || 'N/A'}</div>
              <div style={{ marginBottom: '4px' }}><strong>Email:</strong> {workerData?.email || 'N/A'}</div>
              <div style={{ marginBottom: '4px' }}><strong>Experience:</strong> {workerData?.experience || 'N/A'} years</div>
              <div><strong>Truck Model:</strong> {workerData?.truck_model || 'N/A'}</div>
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#f0fdf4', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Navigation style={{ width: '20px', height: '20px', color: '#16a34a' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Service Area
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Your operating location
                </p>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#374151', lineHeight: '1.5' }}>
              <div style={{ marginBottom: '4px' }}><strong>City:</strong> {workerData?.city || 'N/A'}</div>
              <div style={{ marginBottom: '4px' }}><strong>Phone:</strong> {workerData?.phone || 'N/A'}</div>
              <div><strong>Truck Capacity:</strong> {workerData?.truck_capacity || 'N/A'}</div>
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#f0fdf4', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Truck style={{ width: '20px', height: '20px', color: '#16a34a' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Vehicle Information
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Your tow truck details
                </p>
              </div>
            </div>
            <div style={{ fontSize: '13px', color: '#374151', lineHeight: '1.5' }}>
              <div style={{ marginBottom: '4px' }}><strong>Type:</strong> {workerData?.truck_type || 'N/A'}</div>
              <div style={{ marginBottom: '4px' }}><strong>Model:</strong> {workerData?.truck_model || 'N/A'}</div>
              <div><strong>Registration:</strong> {workerData?.truck_registration || 'N/A'}</div>
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
                ? 'You are currently online and available for tow requests' 
                : 'You are currently offline and not receiving requests'
              }
            </p>
          </div>
          <button 
            onClick={handleOnlineToggle}
            className={`status-button ${isOnline ? 'online' : 'offline'}`}
          >
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
            onClick={() => navigate('/worker/car/tow-truck/home')}
          >
            <Home size={20} style={{ color: '#16a34a' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#16a34a' }}>Dashboard</span>
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
            onClick={() => navigate('/worker/car/tow-truck/requests')}
          >
            <Package size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Tow Requests</span>
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
            onClick={() => navigate('/worker/car/tow-truck/active-job')}
          >
            <Truck size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Active Jobs</span>
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
            onClick={() => navigate('/worker/car/tow-truck/history')}
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
            onClick={() => navigate('/worker/car/tow-truck/performance')}
          >
            <Target size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Performance</span>
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
            onClick={() => navigate('/worker/car/tow-truck/details')}
          >
            <User size={20} style={{ color: '#6b7280' }} />
            <span style={{ fontSize: '12px', fontWeight: '500', color: '#6b7280' }}>Profile</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TowTruckHomepage;
