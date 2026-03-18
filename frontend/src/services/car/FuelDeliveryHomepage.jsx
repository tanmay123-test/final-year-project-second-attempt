import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Fuel, 
  Home,
  Package,
  History,
  Target,
  User,
  MapPin,
  Phone,
  Mail,
  LogOut,
  Truck
} from 'lucide-react';
import { carService } from '../../shared/api';

const FuelDeliveryHomepage = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [isOnline, setIsOnline] = useState(true);
  const [serviceRadius, setServiceRadius] = useState(26);
  const [loading, setLoading] = useState(true);
  const [version, setVersion] = useState(Date.now()); // Force re-render
  const [performanceData, setPerformanceData] = useState({
    vehicleType: 'N/A',
    vehicleNumber: 'N/A',
    rating: 0.0,
    totalDeliveries: 0
  });
  const [jobsData, setJobsData] = useState({
    jobsAccepted: 0,
    earnings: 0
  });

  const handleOnlineToggle = () => {
    setIsOnline(!isOnline);
  };

  const handleRadiusChange = (e) => {
    setServiceRadius(e.target.value);
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('workerToken');
      localStorage.removeItem('workerData');
      localStorage.removeItem('workerId');
      navigate('/worker/car/fuel-delivery/login');
    }
  };

  const fetchJobsAndEarnings = async (workerId) => {
    try {
      // Fetch delivery history to get real earnings
      const response = await fetch(`http://localhost:5000/api/fuel-delivery/history/${workerId}`);
      const data = await response.json();
      
      if (data.success && data.history) {
        // Calculate real earnings from completed deliveries
        const completedDeliveries = data.history.filter(d => d.status === 'completed');
        const totalEarnings = completedDeliveries.reduce((sum, d) => sum + (d.estimated_earnings || 0), 0);
        
        // Check if worker has active delivery
        const activeResponse = await fetch(`http://localhost:5000/api/fuel-delivery/active-delivery/${workerId}`);
        const activeData = await activeResponse.json();
        const hasActiveDelivery = activeData.success && activeData.delivery;
        
        setJobsData({
          jobsAccepted: hasActiveDelivery ? 1 : 0,
          earnings: totalEarnings
        });
      } else {
        setJobsData({
          jobsAccepted: 0,
          earnings: 0
        });
      }
    } catch (error) {
      console.error('Error fetching jobs and earnings:', error);
      // Set default values on error
      setJobsData({
        jobsAccepted: 0,
        earnings: 0
      });
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('workerToken');
    const storedWorkerData = localStorage.getItem('workerData');
    
    if (!token || !storedWorkerData) {
      navigate('/worker/car/fuel-delivery/login');
      return;
    }

    try {
      const worker = JSON.parse(storedWorkerData);
      console.log('Worker data from localStorage:', worker); // Debug log
      
      // Check if the worker data has the required fields, if not, clear cache and re-login
      if (!worker.city || !worker.phone_number || !worker.vehicle_type || !worker.vehicle_number) {
        console.log('Worker data missing required fields, clearing cache...');
        console.log('Missing fields:', {
          city: worker.city,
          phone_number: worker.phone_number,
          vehicle_type: worker.vehicle_type,
          vehicle_number: worker.vehicle_number
        });
        localStorage.removeItem('workerToken');
        localStorage.removeItem('workerData');
        navigate('/worker/car/fuel-delivery/login');
        return;
      }
      
      setWorkerData(worker);
      
      // Set performance data from worker data
      setPerformanceData({
        vehicleType: worker.vehicle_type || 'N/A',
        vehicleNumber: worker.vehicle_number || 'N/A',
        rating: worker.rating || 0.0,
        totalDeliveries: worker.total_deliveries || 0
      });
      
      // Fetch jobs and earnings data
      fetchJobsAndEarnings(worker.id);
      
      setLoading(false);
    } catch (error) {
      console.error('Error parsing worker data:', error);
      navigate('/worker/car/fuel-delivery/login');
    }
  }, [navigate]);

  // Set up periodic updates for jobs and earnings
  useEffect(() => {
    if (!workerData) return;

    const interval = setInterval(() => {
      fetchJobsAndEarnings(workerData.id);
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [workerData]);

  const menuItems = [
    {
      icon: Home,
      label: 'dashboard',
      path: '/worker/car/fuel-delivery/home'
    },
    {
      icon: Package,
      label: 'Jobs',
      path: '/worker/car/fuel-delivery/requests'
    },
    {
      icon: Fuel,
      label: 'Active Delivery',
      path: '/worker/car/fuel-delivery/active-delivery'
    },
    {
      icon: History,
      label: 'Delivery History & Earnings',
      path: '/worker/car/fuel-delivery/history'
    },
    {
      icon: Target,
      label: 'Performance, Reputation & Safety',
      path: '/worker/car/fuel-delivery/performance'
    },
    {
      icon: User,
      label: 'profile',
      path: '/worker/car/fuel-delivery/profile'
    }
  ];

  if (loading || !workerData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fuel-delivery-homepage">
      <style>{`
        .fuel-delivery-homepage {
          min-height: 100vh;
          background: #f8f9fa;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
          position: relative;
        }

        .header {
          background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
          color: white;
          padding: 20px 16px;
          border-radius: 0 0 20px 20px;
        }

        .header-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .logo-icon {
          width: 32px;
          height: 32px;
          background: white;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .logo-text {
          font-size: 18px;
          font-weight: 700;
        }

        .header-actions {
          display: flex;
          gap: 12px;
        }

        .header-btn {
          padding: 8px 16px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          background: rgba(255, 255, 255, 0.1);
          color: white;
          border-radius: 8px;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .header-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .welcome-section {
          margin-top: 16px;
        }

        .welcome-text {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 4px;
        }

        .role-text {
          font-size: 14px;
          opacity: 0.9;
          margin-bottom: 12px;
        }

        .contact-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          font-size: 12px;
          opacity: 0.8;
        }

        .contact-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .status-radius-container {
          background: white;
          margin: 20px 16px;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .status-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .status-title {
          font-size: 16px;
          font-weight: 600;
          color: #333;
        }

        .toggle-section {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .toggle-switch {
          position: relative;
          width: 44px;
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
          background-color: #ccc;
          transition: .3s;
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
          transition: .3s;
          border-radius: 50%;
        }

        input:checked + .toggle-slider {
          background-color: #4CAF50;
        }

        input:checked + .toggle-slider:before {
          transform: translateX(20px);
        }

        .toggle-label {
          font-size: 14px;
          font-weight: 500;
          color: #666;
        }

        .status-details-line {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
          flex-wrap: wrap;
        }

        .status-badge-online {
          background: #4CAF50;
          color: white;
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .status-info-item {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: #666;
        }

        .service-radius-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .radius-title {
          font-size: 14px;
          font-weight: 500;
          color: #333;
        }

        .radius-value {
          font-size: 14px;
          font-weight: 600;
          color: #ff6b35;
        }

        .slider-container {
          margin-top: 8px;
        }

        .radius-slider {
          width: 100%;
          height: 4px;
          border-radius: 2px;
          outline: none;
          -webkit-appearance: none;
          background: transparent;
        }

        .radius-slider::-webkit-slider-runnable-track {
          width: 100%;
          height: 4px;
          border-radius: 2px;
          background: linear-gradient(to right, #ff6b35 0%, #ff6b35 var(--progress), #e0e0e0 var(--progress), #e0e0e0 100%);
        }

        .radius-slider::-moz-range-track {
          width: 100%;
          height: 4px;
          border-radius: 2px;
          background: linear-gradient(to right, #ff6b35 0%, #ff6b35 var(--progress), #e0e0e0 var(--progress), #e0e0e0 100%);
        }

        .radius-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 2px solid #ff6b35;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          margin-top: -6px;
        }

        .radius-slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: 2px solid #ff6b35;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .stats-cards {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin: 0 16px 20px;
        }

        .stat-card {
          background: white;
          border-radius: 16px;
          padding: 24px;
          text-align: center;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        .stat-number {
          font-size: 32px;
          font-weight: 700;
          color: #333;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #666;
        }

        .bottom-navigation {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: white;
          border-top: 1px solid #e0e0e0;
          display: flex;
          justify-content: space-around;
          padding: 8px 0;
          z-index: 1000;
        }

        .nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          padding: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
          border-radius: 8px;
          min-width: 50px;
        }

        .nav-item:hover {
          background: #f5f5f5;
        }

        .nav-item.active {
          color: #ff6b35;
        }

        .nav-item svg {
          color: #666;
        }

        .nav-item.active svg {
          color: #ff6b35;
        }

        .nav-label {
          font-size: 11px;
          color: #666;
          margin-top: 2px;
        }

        .nav-item.active .nav-label {
          color: #ff6b35;
        }

        .performance-section {
          background: white;
          margin: 0 16px 20px;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .performance-header {
          margin-bottom: 16px;
        }

        .performance-title {
          font-size: 16px;
          font-weight: 600;
          color: #333;
        }

        .performance-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }

        .performance-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e9ecef;
        }

        .performance-icon {
          font-size: 20px;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .performance-content {
          flex: 1;
        }

        .performance-label {
          font-size: 12px;
          color: #666;
          margin-bottom: 2px;
        }

        .performance-value {
          font-size: 14px;
          font-weight: 600;
          color: #333;
        }

        @media (max-width: 480px) {
          .performance-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      {/* Header */}
      <div className="header">
        <div className="header-top">
          <div className="logo">
            <div className="logo-icon">
              <Fuel size={20} color="#ff6b35" />
            </div>
            <div className="logo-text">FuelFleet</div>
          </div>
          <div className="header-actions">
            <button className="header-btn" onClick={() => setVersion(Date.now())}>Refresh</button>
            <button className="header-btn">Profile</button>
            <button className="header-btn" onClick={handleLogout}>Logout</button>
          </div>
        </div>
        
        <div className="welcome-section">
          <div className="welcome-text">Welcome back, {workerData.name || 'Agent'}!</div>
          <div className="role-text">Fuel Delivery Agent</div>
          <div className="contact-info">
            <div className="contact-item">
              <MapPin size={12} />
              <span>{(() => {
                console.log('Location data:', { city: workerData.city, location: workerData.location });
                return workerData.city || workerData.location || 'Location not set';
              })()}</span>
            </div>
            <div className="contact-item">
              <Phone size={12} />
              <span>{(() => {
                console.log('Phone data:', { phone_number: workerData.phone_number, phone: workerData.phone });
                return workerData.phone_number || workerData.phone || 'Phone not set';
              })()}</span>
            </div>
            <div className="contact-item">
              <Mail size={12} />
              <span>{workerData.email || 'Email not set'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Combined Status and Radius Control */}
      <div className="status-radius-container">
        <div className="status-header">
          <div className="status-title">Status Control</div>
          <div className="toggle-section">
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={isOnline}
                onChange={handleOnlineToggle}
              />
              <span className="toggle-slider"></span>
            </label>
            <span className="toggle-label">{isOnline ? 'On' : 'Off'}</span>
          </div>
        </div>
        
        <div className="status-details-line">
          <div className="status-badge-online">
            Online
          </div>
          <div className="status-info-item">
            <MapPin size={14} /> Radius: {serviceRadius}km
          </div>
          <div className="status-info-item">
            <Truck size={14} /> Fuel Delivery Agent
          </div>
        </div>

        <div className="service-radius-section">
          <div className="radius-title">Service Radius</div>
          <div className="radius-value">{serviceRadius}km</div>
        </div>
        
        <div className="slider-container">
          <input 
            type="range" 
            min="1" 
            max="50" 
            value={serviceRadius}
            onChange={handleRadiusChange}
            className="radius-slider"
            style={{
              '--progress': `${((serviceRadius - 1) / 49) * 100}%`
            }}
          />
        </div>
      </div>

      {/* Performance Section */}
      <div className="performance-section">
        <div className="performance-header">
          <div className="performance-title">Performance Overview</div>
        </div>
        <div className="performance-grid">
          <div className="performance-item">
            <div className="performance-icon">🚗</div>
            <div className="performance-content">
              <div className="performance-label">Vehicle</div>
              <div className="performance-value">{performanceData.vehicleType} - {performanceData.vehicleNumber}</div>
            </div>
          </div>
          <div className="performance-item">
            <div className="performance-icon">📊</div>
            <div className="performance-content">
              <div className="performance-label">Status</div>
              <div className="performance-value">{isOnline ? 'ONLINE' : 'OFFLINE'}</div>
            </div>
          </div>
          <div className="performance-item">
            <div className="performance-icon">⭐</div>
            <div className="performance-content">
              <div className="performance-label">Rating</div>
              <div className="performance-value">{performanceData.rating.toFixed(1)}</div>
            </div>
          </div>
          <div className="performance-item">
            <div className="performance-icon">📦</div>
            <div className="performance-content">
              <div className="performance-label">Total Deliveries</div>
              <div className="performance-value">{performanceData.totalDeliveries}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-cards">
        <div className="stat-card">
          <div className="stat-number">{jobsData.jobsAccepted}</div>
          <div className="stat-label">Jobs</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">₹{jobsData.earnings.toLocaleString()}</div>
          <div className="stat-label">Earnings</div>
        </div>
      </div>
    </div>
  );
};

export default FuelDeliveryHomepage;
