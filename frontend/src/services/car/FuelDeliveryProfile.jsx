import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Fuel, DollarSign, Target, User, Settings, HelpCircle, 
  CreditCard, BarChart3, ArrowLeft, Star, BadgeCheck,
  MapPin, Phone, Mail, Calendar, TrendingUp
} from 'lucide-react';
import { carService } from '../../shared/api';
import api from '../../shared/api';

const FuelDeliveryProfile = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [earnings, setEarnings] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [ratings, setRatings] = useState([]);

  useEffect(() => {
    fetchWorkerData();
    fetchEarnings();
    fetchPerformance();
    fetchRatings();
  }, []);

  const fetchRatings = async () => {
    try {
      const storedData = localStorage.getItem('fuelDeliveryData');
      const token = localStorage.getItem('fuelDeliveryToken');
      
      if (storedData && token) {
        const data = JSON.parse(storedData);
        const workerId = data.id || data.workerId;
        
        try {
          const response = await api.get(`/api/car/fuel-delivery/${workerId}/ratings`);

          if (response.data) {
            setRatings(response.data.ratings || response.data || []);
            setRatings(ratingsData.ratings || ratingsData || []);
          }
        } catch (error) {
          console.log('⚠️ Ratings API not available');
          setRatings([]);
        }
      }
    } catch (error) {
      console.error('Error fetching ratings:', error);
      setRatings([]);
    }
  };

  const fetchWorkerData = async () => {
    try {
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (!storedData || !token) {
        navigate('/worker/car/fuel-delivery/login');
        return;
      }

      const data = JSON.parse(storedData);
      const workerId = data.id || data.workerId;
      
      // Fetch fresh worker data from backend
      try {
        const response = await carService.getFuelDeliveryProfile(workerId);
        
        if (response.data) {
          setWorkerData(response.data);
        } else {
          // Fallback to stored data if API fails
          setWorkerData(data);
        }
      } catch (error) {
        console.log('⚠️ Profile API not available, using stored data');
        setWorkerData(data);
      }
    } catch (error) {
      console.error('Error loading worker data:', error);
    }
    setLoading(false);
  };

  const fetchEarnings = async () => {
    try {
      const storedData = localStorage.getItem('fuelDeliveryData');
      const token = localStorage.getItem('fuelDeliveryToken');
      
      if (storedData && token) {
        const data = JSON.parse(storedData);
        const workerId = data.id || data.workerId;
        
        try {
          const response = await api.get(`/api/car/fuel-delivery/${workerId}/transactions`);

          if (response.data) {
            const transactions = response.data.transactions || response.data || [];
            
            // Calculate earnings from real transactions
            const completedTransactions = transactions.filter(t => t.status === 'completed');
            const thisMonthTransactions = completedTransactions.filter(t => {
              const transactionDate = new Date(t.completed_at || t.createdAt);
              const thisMonth = new Date();
              return transactionDate.getMonth() === thisMonth.getMonth() && 
                     transactionDate.getFullYear() === thisMonth.getFullYear();
            });

            const totalEarnings = completedTransactions.reduce((sum, t) => sum + (t.amount || t.price || 0), 0);
            const thisMonthEarnings = thisMonthTransactions.reduce((sum, t) => sum + (t.amount || t.price || 0), 0);
            const averagePerDelivery = completedTransactions.length > 0 ? totalEarnings / completedTransactions.length : 0;

            setEarnings({
              totalEarnings,
              thisMonth: thisMonthEarnings,
              completedDeliveries: completedTransactions.length,
              averagePerDelivery: Math.round(averagePerDelivery)
            });
          } else {
            // No transactions yet
            setEarnings({
              totalEarnings: 0,
              thisMonth: 0,
              completedDeliveries: 0,
              averagePerDelivery: 0
            });
          }
        } catch (error) {
          console.log('⚠️ Transactions API not available');
          // No hardcoded fallback - only zeros if no data
          setEarnings({
            totalEarnings: 0,
            thisMonth: 0,
            completedDeliveries: 0,
            averagePerDelivery: 0
          });
        }
      }
    } catch (error) {
      console.error('Error fetching earnings:', error);
      // No hardcoded fallback
      setEarnings({
        totalEarnings: 0,
        thisMonth: 0,
        completedDeliveries: 0,
        averagePerDelivery: 0
      });
    }
  };

  const fetchPerformance = async () => {
    try {
      const storedData = localStorage.getItem('fuelDeliveryData');
      const token = localStorage.getItem('fuelDeliveryToken');
      
      if (storedData && token) {
        const data = JSON.parse(storedData);
        const workerId = data.id || data.workerId;
        
        try {
          const response = await api.get(`/api/car/fuel-delivery/${workerId}/performance`);

          if (response.data) {
            setPerformance(performanceData);
          } else {
            // Calculate from real transactions and ratings
            await calculatePerformanceFromData(workerId, token);
          }
        } catch (error) {
          console.log('⚠️ Performance API not available, calculating from data');
          await calculatePerformanceFromData(workerId, token);
        }
      }
    } catch (error) {
      console.error('Error fetching performance:', error);
      // No hardcoded fallback
      setPerformance({
        overallScore: 0,
        deliverySpeed: 0,
        customerSatisfaction: 0,
        reliability: 0
      });
    }
  };

  const calculatePerformanceFromData = async (workerId, token) => {
    try {
      const [transactionsResponse, ratingsResponse] = await Promise.all([
        api.get(`/api/car/fuel-delivery/${workerId}/transactions`),
        api.get(`/api/car/fuel-delivery/${workerId}/ratings`)
      ]);

      let transactions = [];
      let ratings = [];

      if (transactionsResponse.data) {
        transactions = transactionsResponse.data.transactions || transactionsResponse.data || [];
      }

      if (ratingsResponse.data) {
        ratings = ratingsResponse.data.ratings || ratingsResponse.data || [];
      }

      // Calculate performance metrics from real data
      const completedTransactions = transactions.filter(t => t.status === 'completed');
      const totalTransactions = transactions.length;
      
      // Delivery Speed - based on actual delivery times
      const deliverySpeed = completedTransactions.length > 0 
        ? Math.min((completedTransactions.filter(t => {
            const created = new Date(t.created_at);
            const completed = new Date(t.completed_at);
            const hours = (completed - created) / (1000 * 60 * 60);
            return hours <= 2; // Fast delivery within 2 hours
          }).length / completedTransactions.length) * 10, 10)
        : 0;

      // Customer Satisfaction - based on actual ratings
      const averageRating = ratings.length > 0 
        ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length 
        : 0;
      const customerSatisfaction = (averageRating / 5) * 10;

      // Reliability - based on completion rate
      const reliability = totalTransactions > 0 
        ? (completedTransactions.length / totalTransactions) * 10 
        : 0;

      // Overall Score
      const overallScore = (deliverySpeed + customerSatisfaction + reliability) / 3;

      setPerformance({
        overallScore: Math.round(overallScore * 10) / 10,
        deliverySpeed: Math.round(deliverySpeed * 10) / 10,
        customerSatisfaction: Math.round(customerSatisfaction * 10) / 10,
        reliability: Math.round(reliability * 10) / 10
      });

    } catch (error) {
      console.error('Error calculating performance:', error);
      setPerformance({
        overallScore: 0,
        deliverySpeed: 0,
        customerSatisfaction: 0,
        reliability: 0
      });
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('workerToken');
      localStorage.removeItem('workerData');
      navigate('/worker/car/services');
    }
  };

  const menuItems = [
    { icon: User, label: 'View Full Details', path: '/worker/car/fuel-delivery/details' },
    { icon: CreditCard, label: 'Payment History', path: '/worker/car/fuel-delivery/payments' },
    { icon: BarChart3, label: 'Analytics', path: '/worker/car/fuel-delivery/analytics' },
    { icon: Settings, label: 'Settings', path: '/worker/car/fuel-delivery/settings' },
    { icon: HelpCircle, label: 'Help & Support', path: '/worker/car/fuel-delivery/support' },
  ];

  if (loading) {
    return (
      <div className="loading-container">
        <style>{`
          .loading-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <style>{`
        .profile-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #FED7AA 0%, #FDBA74 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
        }
        .profile-wrapper {
          width: 100%;
          max-width: 600px;
          background: white;
          border-radius: 20px;
          box-shadow: 0 20px 40px rgba(251, 146, 60, 0.2);
          overflow: hidden;
        }
        .profile-header {
          background: rgba(254, 215, 170, 0.1);
          backdrop-filter: blur(20px);
          padding: 2rem 1.5rem;
          border-bottom: 1px solid rgba(251, 146, 60, 0.2);
        }
        .header-content {
          max-width: 100%;
        }
        .back-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #EA580C;
          text-decoration: none;
          font-weight: 500;
          margin-bottom: 1rem;
        }
        .page-title {
          font-size: 2rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }
        .profile-card {
          background: white;
          padding: 2rem;
          display: flex;
          align-items: center;
          gap: 2rem;
        }
        .profile-avatar-large {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #FB923C 0%, #EA580C 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          font-weight: 700;
          color: white;
        }
        .profile-info {
          flex: 1;
        }
        .name-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }
        .mechanic-name {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin: 0;
        }
        .specialization {
          color: #6b7280;
          margin: 0 0 0.5rem 0;
        }
        .rating-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .rating-value {
          font-weight: 600;
          color: #1f2937;
        }
        .rating-count {
          color: #6b7280;
          font-size: 0.9rem;
        }
        .worker-details-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #E5E7EB;
        }
        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .detail-label {
          font-size: 0.8rem;
          color: #6B7280;
          font-weight: 600;
        }
        .detail-value {
          font-size: 0.9rem;
          color: #1F2937;
          font-weight: 500;
        }
        .content-container {
          padding: 2rem 1.5rem;
        }
        .status-card, .earnings-card, .performance-card {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          box-shadow: 0 4px 12px rgba(251, 146, 60, 0.1);
        }
        .card-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
        }
        .card-icon {
          color: #FB923C;
        }
        .card-header h3 {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1f2937;
          margin: 0;
        }
        .status-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .status-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
          color: #374151;
        }
        .status-icon {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.8rem;
          font-weight: 600;
        }
        .id-icon {
          background: #fed7aa;
          color: #EA580C;
        }
        .verification-icon {
          background: #dcfce7;
          color: #16a34a;
        }
        .status-value {
          font-weight: 600;
          color: #1f2937;
        }
        .earnings-main {
          text-align: center;
          margin-bottom: 1.5rem;
        }
        .total-earnings {
          font-size: 2.5rem;
          font-weight: 700;
          color: #1f2937;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
        }
        .currency {
          font-size: 1.5rem;
          color: #FB923C;
        }
        .earnings-subtitle {
          color: #6b7280;
          margin-top: 0.5rem;
        }
        .earnings-stats {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 1rem;
        }
        .earnings-stat {
          text-align: center;
        }
        .stat-label {
          font-size: 0.8rem;
          color: #6b7280;
          margin-bottom: 0.25rem;
        }
        .stat-value {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1f2937;
        }
        .performance-score {
          text-align: center;
          margin-bottom: 1.5rem;
        }
        .score-circle {
          width: 80px;
          height: 80px;
          border: 4px solid #e5e7eb;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 0.5rem;
          background: linear-gradient(135deg, #FB923C 0%, #EA580C 100%);
          border-color: #FB923C;
        }
        .score-value {
          font-size: 1.8rem;
          font-weight: 700;
          color: white;
        }
        .score-label {
          color: #6b7280;
          font-size: 0.9rem;
        }
        .performance-metrics {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 1rem;
        }
        .metric-item {
          text-align: center;
        }
        .metric-label {
          font-size: 0.8rem;
          color: #6b7280;
          margin-bottom: 0.25rem;
        }
        .metric-score {
          font-size: 1rem;
          font-weight: 600;
          color: #1f2937;
        }
        .menu-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-top: 2rem;
        }
        .menu-item {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(251, 146, 60, 0.1);
        }
        .menu-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 20px rgba(251, 146, 60, 0.2);
        }
        .menu-icon {
          color: #FB923C;
          margin-bottom: 0.5rem;
        }
        .menu-label {
          font-size: 0.9rem;
          font-weight: 600;
          color: #1f2937;
        }
      `}</style>

      <div className="profile-wrapper">
        <div className="profile-header">
          <div className="header-content">
            <a href="/worker/car/fuel-delivery/home" className="back-button">
              <ArrowLeft size={20} />
              <span>Back to Dashboard</span>
            </a>
            <h1 className="page-title">Fuel Delivery Profile</h1>
          </div>
        </div>

        <div className="content-container">
          {/* Profile Card */}
          <div className="profile-card">
            <div className="profile-avatar-large">
              {workerData?.name ? workerData.name[0].toUpperCase() : 'F'}
            </div>
            <div className="profile-info">
              <div className="name-row">
                <h2 className="mechanic-name">{workerData?.name || 'Fuel Delivery'}</h2>
                <BadgeCheck size={20} className="verified-badge" fill="#FB923C" color="white" />
              </div>
              <p className="specialization">{workerData?.vehicle_type || 'Fuel Delivery'} Professional</p>
              <div className="rating-row">
                <Star size={16} fill="#FB923C" color="#FB923C" />
                <span className="rating-value">
                  {ratings && ratings.length > 0 
                    ? (ratings.reduce((sum, rating) => sum + rating.rating, 0) / ratings.length).toFixed(1)
                    : '0.0'
                  }
                </span>
                <span className="rating-count">({ratings?.length || 0} reviews)</span>
              </div>
              <div className="worker-details-row">
                <div className="detail-item">
                  <span className="detail-label">Email:</span>
                  <span className="detail-value">{workerData?.email || 'Not provided'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Phone:</span>
                  <span className="detail-value">{workerData?.phone || 'Not provided'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Vehicle:</span>
                  <span className="detail-value">{workerData?.vehicle_type || 'Not specified'}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Service Area:</span>
                  <span className="detail-value">{workerData?.service_area || 'Not specified'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Status Card */}
          <div className="status-card">
            <div className="card-header">
              <User size={20} className="card-icon" />
              <h3>Account Status</h3>
            </div>
            <div className="status-row">
              <div className="status-label">
                <span className="status-icon id-icon">ID</span>
                <span>Worker ID</span>
              </div>
              <span className="status-value">{workerData?.id || 'FD-001'}</span>
            </div>
            <div className="status-row" style={{ marginTop: '1rem' }}>
              <div className="status-label">
                <span className="status-icon verification-icon">✓</span>
                <span>Verification Status</span>
              </div>
              <span className="status-value">Verified</span>
            </div>
          </div>

          {/* Earnings Card */}
          <div className="earnings-card">
            <div className="card-header">
              <DollarSign size={20} className="card-icon" />
              <h3>Earnings Overview</h3>
            </div>
            <div className="earnings-main">
              <div className="total-earnings">
                <span className="currency">₹</span>
                <span>{earnings?.totalEarnings?.toLocaleString() || '0'}</span>
              </div>
              <div className="earnings-subtitle">Total Earned</div>
            </div>
            <div className="earnings-stats">
              <div className="earnings-stat">
                <span className="stat-label">This Month</span>
                <span className="stat-value">₹{earnings?.thisMonth?.toLocaleString() || '0'}</span>
              </div>
              <div className="earnings-stat">
                <span className="stat-label">Deliveries</span>
                <span className="stat-value">{earnings?.completedDeliveries || '0'}</span>
              </div>
              <div className="earnings-stat">
                <span className="stat-label">Avg/Delivery</span>
                <span className="stat-value">₹{earnings?.averagePerDelivery || '0'}</span>
              </div>
            </div>
          </div>

          {/* Performance Card */}
          <div className="performance-card">
            <div className="card-header">
              <Target size={20} className="card-icon" />
              <h3>Performance Score</h3>
            </div>
            <div className="performance-score">
              <div className="score-circle">
                <div className="score-value">{performance?.overallScore || '0'}</div>
              </div>
              <div className="score-label">Your Performance Score</div>
            </div>
            <div className="performance-metrics">
              <div className="metric-item">
                <span className="metric-label">Speed</span>
                <span className="metric-score">{performance?.deliverySpeed || '0'}/10</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Satisfaction</span>
                <span className="metric-score">{performance?.customerSatisfaction || '0'}/10</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Reliability</span>
                <span className="metric-score">{performance?.reliability || '0'}/10</span>
              </div>
            </div>
          </div>

          {/* Menu Grid */}
          <div className="menu-grid">
            {menuItems.map((item, index) => (
              <div key={index} className="menu-item" onClick={() => navigate(item.path)}>
                <item.icon size={24} className="menu-icon" />
                <span className="menu-label">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FuelDeliveryProfile;
