import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Car, 
  Wrench, 
  Brain, 
  Car as GarageIcon, 
  CalendarCheck, 
  User, 
  MessageSquare, 
  LogOut, 
  LayoutDashboard, 
  Search, 
  Plus, 
  Star, 
  MapPin, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  UserPlus, 
  Filter, 
  ChevronRight,
  Truck,
  Droplet
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../shared/api';

const CarServiceHome = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  const [defaultCar, setDefaultCar] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('home');
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // Set user name from auth context
        console.log('AuthContext user data:', user);
        if (user?.user_name || user?.name) {
          setUserName(user.user_name || user.name);
        } else {
          // Try to get user info from localStorage as fallback
          const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
          console.log('Stored user data:', storedUser);
          if (storedUser.user_name || storedUser.name) {
            setUserName(storedUser.user_name || storedUser.name);
          }
        }
        
        // Fetch default car
        try {
          const carResponse = await api.get('/api/car/cars', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (carResponse.data?.cars) {
            // Get the default car from the cars list
            const cars = carResponse.data.cars;
            const defaultCar = cars.find(car => car.is_default) || cars[0];
            setDefaultCar(defaultCar);
          }
        } catch (carError) {
          console.log('Car profile not found or backend unavailable:', carError.message);
          // Don't show error to user for missing profile, just continue
        }

        // Fetch recent bookings
        try {
          const bookingsResponse = await api.get('/api/car/jobs', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          if (bookingsResponse.data?.jobs) {
            setBookings(bookingsResponse.data.jobs.slice(0, 3)); // Show recent 3
          }
        } catch (bookingsError) {
          console.log('Bookings not available:', bookingsError.message);
          // Don't show error to user for missing bookings, just continue
        }
        
      } catch (error) {
        console.error('Error fetching user data:', error);
        // Only show error for critical failures
        if (error.code !== 'NETWORK_ERROR') {
          console.error('Critical error:', error);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    logout();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return '#10B981';
      case 'confirmed': return '#3B82F6';
      case 'pending': return '#F59E0B';
      case 'cancelled': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return <CheckCircle size={16} />;
      case 'confirmed': return <CheckCircle size={16} />;
      case 'pending': return <Clock size={16} />;
      case 'cancelled': return <XCircle size={16} />;
      default: return <AlertCircle size={16} />;
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="car-service-home">
      {/* Header */}
      <header className="top-header">
        <div className="header-left">
          <div className="logo">
            <Car size={30} />
            <span>ExpertEase</span>
          </div>
        </div>
        <div className="header-right">
          <button onClick={() => handleNavigation('/car-service/book-mechanic')} className="header-btn">
            <Search size={20} />
            Find Mechanic
          </button>
          <button onClick={() => handleNavigation('/car-service/profile')} className="header-btn">
            <User size={20} />
            Hi, {user?.name || 'User'}
          </button>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </header>

      <div className="main-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <nav className="main-nav">
            <ul>
              <li className="active" onClick={() => handleNavigation('/car-service/home')}>
                <LayoutDashboard size={20} />
                <span>Home</span>
              </li>
              <li onClick={() => handleNavigation('/car-service/book-mechanic')}>
                <Wrench size={20} />
                <span>Book Mechanic</span>
              </li>
              <li onClick={() => handleNavigation('/car-service/ai-mechanic')}>
                <Brain size={20} />
                <span>AI Mechanic</span>
              </li>
              <li onClick={() => handleNavigation('/car-service/garage')}>
                <GarageIcon size={20} />
                <span>My Garage</span>
              </li>
              <li onClick={() => handleNavigation('/car-service/bookings')}>
                <CalendarCheck size={20} />
                <span>My Bookings</span>
              </li>
              <li onClick={() => handleNavigation('/car-service/profile')}>
                <User size={20} />
                <span>Profile</span>
              </li>
              <li onClick={() => handleNavigation('/car-service/ask-expert')}>
                <MessageSquare size={20} />
                <span>Ask Expert</span>
              </li>
            </ul>
          </nav>
          
          <div className="sidebar-bottom">
            <button onClick={handleLogout} className="sidebar-logout-btn">
              <LogOut size={20} />
              <span>Logout</span>
            </button>
            <button onClick={() => handleNavigation('/services')} className="back-to-services-btn">
              <Car size={20} />
              <span>Back to Services</span>
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {/* Hero Section */}
          <section className="hero-section">
            <div className="hero-content">
              <h1>Welcome back, {userName || 'User'}! 👋</h1>
              <p>Manage your car services from one place</p>
            </div>
          </section>

          {/* Default Car Section */}
          {defaultCar ? (
            <section className="default-car-section">
              <h2>Your Default Car</h2>
              <div className="car-card">
                <div className="car-header">
                  <div className="car-info">
                    <h3>{defaultCar.brand} {defaultCar.model}</h3>
                    <div className="car-details">
                      <span className="car-detail">
                        <span className="label">Year:</span>
                        <span className="value">{defaultCar.year}</span>
                      </span>
                      <span className="car-detail">
                        <span className="label">Fuel:</span>
                        <span className="value">{defaultCar.fuel_type}</span>
                      </span>
                      <span className="car-detail">
                        <span className="label">Reg:</span>
                        <span className="value">{defaultCar.registration_number}</span>
                      </span>
                    </div>
                  </div>
                  <div className="default-badge">
                    <Star size={16} />
                    <span>Default</span>
                  </div>
                </div>
              </div>
            </section>
          ) : (
            <section className="no-car-section">
              <h2>Your Default Car</h2>
              <div className="no-car-card">
                <div className="no-car-content">
                  <GarageIcon size={40} />
                  <h3>No car added yet</h3>
                  <p>Add your first car to get started with car services</p>
                  <button 
                    onClick={() => handleNavigation('/car-service/garage')}
                    className="add-car-btn"
                  >
                    <Plus size={16} />
                    Add Your First Car
                  </button>
                </div>
              </div>
            </section>
          )}

          {/* Quick Actions */}
          <section className="quick-actions">
            <h2>Quick Actions</h2>
            <div className="actions-grid">
              <button 
                onClick={() => handleNavigation('/car-service/book-mechanic')} 
                className="action-card"
              >
                <div className="action-icon">
                  <Wrench size={32} />
                </div>
                <h3>Book Mechanic</h3>
                <p>Find and book a mechanic</p>
              </button>
              
              <button 
                onClick={() => handleNavigation('/car-service/garage')} 
                className="action-card"
              >
                <div className="action-icon">
                  <GarageIcon size={32} />
                </div>
                <h3>My Garage</h3>
                <p>Manage your vehicles</p>
              </button>
              
              <button 
                onClick={() => handleNavigation('/car-service/ai-mechanic')} 
                className="action-card"
              >
                <div className="action-icon">
                  <Brain size={32} />
                </div>
                <h3>AI Mechanic</h3>
                <p>Get AI assistance</p>
              </button>
              
              <button 
                onClick={() => handleNavigation('/car-service/book-tow-truck')} 
                className="action-card"
              >
                <div className="action-icon">
                  <Truck size={32} />
                </div>
                <h3>Book Tow Truck Operator</h3>
                <p>Request towing service</p>
              </button>
              
              <button 
                onClick={() => handleNavigation('/car-service/bookings')} 
                className="action-card"
              >
                <div className="action-icon">
                  <CalendarCheck size={32} />
                </div>
                <h3>My Bookings</h3>
                <p>View all bookings</p>
              </button>
              
              <button 
                onClick={() => handleNavigation('/car-service/fuel-delivery')} 
                className="action-card"
              >
                <div className="action-icon">
                  <Droplet size={32} />
                </div>
                <h3>Fuel Delivery Agent</h3>
                <p>Request fuel delivery</p>
              </button>
            </div>
          </section>

          {/* Recent Bookings */}
          <section className="recent-bookings">
            <div className="section-header">
              <h2>Recent Bookings</h2>
              {bookings.length > 0 && (
                <button 
                  onClick={() => handleNavigation('/car-service/bookings')}
                  className="view-all-btn"
                >
                  View All
                  <ChevronRight size={16} />
                </button>
              )}
            </div>
            {bookings.length > 0 ? (
              <div className="bookings-list">
                {bookings.map((booking) => (
                  <div key={booking.id} className="booking-item">
                    <div className="booking-status">
                      <div 
                        className="status-icon" 
                        style={{ color: getStatusColor(booking.status) }}
                      >
                        {getStatusIcon(booking.status)}
                      </div>
                      <span 
                        className="status-text"
                        style={{ color: getStatusColor(booking.status) }}
                      >
                        {booking.status}
                      </span>
                    </div>
                    <div className="booking-details">
                      <h4>{booking.service_type || 'General Service'}</h4>
                      <p>{booking.mechanic_name || 'Mechanic'}</p>
                      <div className="booking-meta">
                        <span className="date">
                          <Clock size={14} />
                          {new Date(booking.date).toLocaleDateString()}
                        </span>
                        <span className="location">
                          <MapPin size={14} />
                          {booking.location || 'Location'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-bookings">
                <CalendarCheck size={40} />
                <h3>No recent bookings</h3>
                <p>When you book services, they will appear here</p>
              </div>
            )}
          </section>
        </main>
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        <button 
          onClick={() => handleNavigation('/car-service/home')}
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
        >
          <LayoutDashboard size={24} />
          <span>Home</span>
        </button>
        
        <button 
          onClick={() => handleNavigation('/car-service/book-mechanic')}
          className={`nav-item ${activeTab === 'book' ? 'active' : ''}`}
        >
          <Wrench size={24} />
          <span>Book</span>
        </button>
        
        <button 
          onClick={() => handleNavigation('/car-service/garage')}
          className={`nav-item ${activeTab === 'garage' ? 'active' : ''}`}
        >
          <GarageIcon size={24} />
          <span>Garage</span>
        </button>
        
        <button 
          onClick={() => handleNavigation('/car-service/ai-mechanic')}
          className={`nav-item ${activeTab === 'ai' ? 'active' : ''}`}
        >
          <Brain size={24} />
          <span>AI</span>
        </button>
        
        <button 
          onClick={() => handleNavigation('/car-service/bookings')}
          className={`nav-item ${activeTab === 'bookings' ? 'active' : ''}`}
        >
          <CalendarCheck size={24} />
          <span>Bookings</span>
        </button>
        
        <button 
          onClick={() => handleNavigation('/car-service/profile')}
          className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
        >
          <User size={24} />
          <span>Profile</span>
        </button>
      </div>

      <style>{`
        .car-service-home {
          min-height: 100vh;
          background: #f8f9fa;
        }

        /* Header Styles */
        .top-header {
          background: white;
          padding: 1rem 2rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .header-left .logo {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 700;
          font-size: 1.25rem;
          color: #7c3aed;
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .header-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border: 1px solid #e5e7eb;
          background: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .header-btn:hover {
          background: #f3f4f6;
          border-color: #7c3aed;
        }

        .logout-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .logout-btn:hover {
          background: #dc2626;
        }

        /* Layout */
        .main-layout {
          display: flex;
          min-height: calc(100vh - 70px);
        }

        /* Sidebar */
        .sidebar {
          width: 280px;
          background: white;
          border-right: 1px solid #e5e7eb;
          display: flex;
          flex-direction: column;
        }

        .main-nav ul {
          list-style: none;
          padding: 1.5rem 0;
          margin: 0;
        }

        .main-nav li {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1.5rem;
          cursor: pointer;
          transition: background 0.2s;
          color: #6b7280;
        }

        .main-nav li:hover {
          background: #f3f4f6;
        }

        .main-nav li.active {
          background: linear-gradient(135deg, #f3f4f6 0%, #ede9fe 100%);
          color: #7c3aed;
          border-right: 3px solid #7c3aed;
          font-weight: 600;
        }

        .sidebar-bottom {
          margin-top: auto;
          padding: 1rem;
          border-top: 1px solid #e5e7eb;
        }

        .sidebar-logout-btn, .back-to-services-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          width: 100%;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          border: 1px solid #e5e7eb;
          background: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .sidebar-logout-btn:hover {
          background: #fef2f2;
          border-color: #ef4444;
          color: #ef4444;
        }

        .back-to-services-btn:hover {
          background: #f3f4f6;
          border-color: #7c3aed;
          color: #7c3aed;
        }

        /* Main Content */
        .main-content {
          flex: 1;
          padding: 2rem;
          padding-bottom: 6rem; /* Add bottom padding for navigation */
          overflow-y: auto;
        }

        /* Hero Section */
        .hero-section {
          margin-bottom: 2rem;
        }

        .hero-content h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .hero-content p {
          font-size: 1.1rem;
          color: #6b7280;
          margin: 0;
        }

        /* Default Car Section */
        .default-car-section {
          margin-bottom: 2rem;
        }

        .default-car-section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 1rem;
        }

        .car-card {
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          border-radius: 16px;
          padding: 1.5rem;
          color: white;
          position: relative;
          overflow: hidden;
          box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
        }

        .car-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .car-info h3 {
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 1rem;
          text-transform: capitalize;
        }

        .car-details {
          display: flex;
          gap: 2rem;
          flex-wrap: wrap;
        }

        .car-detail {
          display: flex;
          flex-direction: column;
        }

        .car-detail .label {
          font-size: 0.875rem;
          opacity: 0.8;
          margin-bottom: 0.25rem;
        }

        .car-detail .value {
          font-size: 1rem;
          font-weight: 600;
        }

        .default-badge {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          background: rgba(255,255,255,0.2);
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .no-car-section {
          margin-bottom: 2rem;
        }

        .no-car-section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 1rem;
        }

        .no-car-card {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          border: 2px dashed #e5e7eb;
          text-align: center;
        }

        .no-car-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .no-car-content h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin: 0;
        }

        .no-car-content p {
          color: #6b7280;
          margin: 0;
        }

        .no-car-content .add-car-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: #7c3aed;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .no-car-content .add-car-btn:hover {
          background: #6d28d9;
        }

        /* Quick Actions */
        .quick-actions {
          margin-bottom: 2rem;
        }

        .quick-actions h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 1rem;
        }

        .actions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
        }

        .action-card {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 1.5rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
        }

        .action-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
          border-color: #7c3aed;
        }

        .action-icon {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          color: white;
          box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }

        .action-card h3 {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .action-card p {
          font-size: 0.875rem;
          color: #6b7280;
          margin: 0;
        }

        /* Recent Bookings */
        .recent-bookings {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          border: 1px solid #e5e7eb;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .section-header h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1f2937;
        }

        .view-all-btn {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          color: #7c3aed;
          background: none;
          border: none;
          font-weight: 500;
          cursor: pointer;
          transition: color 0.2s;
        }

        .view-all-btn:hover {
          color: #6d28d9;
        }

        .bookings-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .booking-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 8px;
          border-left: 4px solid #e5e7eb;
        }

        .booking-status {
          display: flex;
          flex-direction: column;
          align-items: center;
          min-width: 80px;
        }

        .booking-details h4 {
          font-size: 1rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }

        .booking-details p {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .booking-meta {
          display: flex;
          gap: 1rem;
        }

        .booking-meta span {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.75rem;
          color: #9ca3af;
        }

        .no-bookings {
          text-align: center;
          padding: 3rem 2rem;
          background: white;
          border-radius: 12px;
          border: 2px dashed #e5e7eb;
        }

        .no-bookings h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin: 1rem 0 0.5rem;
        }

        .no-bookings p {
          color: #6b7280;
          margin: 0;
        }

        .no-bookings svg {
          color: #7c3aed;
          opacity: 0.5;
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
          padding: 0.5rem 0;
          z-index: 1000;
          box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }

        .nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
          padding: 0.5rem 1rem;
          background: none;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          color: #6b7280;
          text-decoration: none;
          font-size: 0.75rem;
        }

        .nav-item:hover {
          background: #f3f4f6;
          color: #7c3aed;
        }

        .nav-item.active {
          color: #7c3aed;
          background: #ede9fe;
        }

        .nav-item svg {
          transition: all 0.2s;
        }

        .nav-item.active svg {
          transform: scale(1.1);
        }

        /* Loading */
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 50vh;
          color: #7c3aed;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3e8ff;
          border-top: 4px solid #7c3aed;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        /* Responsive */
        @media (max-width: 768px) {
          .main-layout {
            flex-direction: column;
          }
          
          .sidebar {
            width: 100%;
            order: 2;
          }
          
          .main-content {
            order: 1;
            padding: 1rem;
          }
          
          .actions-grid {
            grid-template-columns: 1fr;
          }
          
          .car-details {
            flex-direction: column;
            gap: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default CarServiceHome;
