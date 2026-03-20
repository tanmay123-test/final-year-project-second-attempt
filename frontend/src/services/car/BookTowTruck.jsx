import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Filter, MapPin, Clock, Star, Phone, Mail, Calendar, 
  ChevronRight, Truck, User, AlertCircle
} from 'lucide-react';
import api from '../../shared/api';

const BookTowTruck = () => {
  const navigate = useNavigate();
  const [towTruckOperators, setTowTruckOperators] = useState([]);
  const [filteredOperators, setFilteredOperators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [selectedOperator, setSelectedOperator] = useState(null);
  const [bookingStep, setBookingStep] = useState('list');
  const [bookingData, setBookingData] = useState({
    date: '',
    time: '',
    location: '',
    description: ''
  });
  const [bookingConfirmed, setBookingConfirmed] = useState(false);

  const services = [
    'Emergency Towing',
    'Long Distance Towing',
    'Flatbed Towing',
    'Motorcycle Towing',
    'Heavy Duty Towing'
  ];

  useEffect(() => {
    fetchTowTruckOperators();
  }, []);

  useEffect(() => {
    filterOperators();
  }, [searchQuery, selectedService, towTruckOperators]);

  const fetchTowTruckOperators = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/car/service/workers/approved', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data?.workers) {
        // Filter for tow truck operators only
        const operators = response.data.workers.filter(worker => 
          worker.role === 'Tow Truck Operator'
        );
        setTowTruckOperators(operators);
      }
    } catch (error) {
      console.error('Error fetching tow truck operators:', error);
      // Set empty array to prevent infinite loading
      setTowTruckOperators([]);
    } finally {
      setLoading(false);
    }
  };

  const filterOperators = () => {
    let filtered = towTruckOperators;
    
    if (searchQuery) {
      filtered = filtered.filter(operator => 
        operator.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        operator.specialization?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        operator.city?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    if (selectedService) {
      filtered = filtered.filter(operator => 
        operator.services?.includes(selectedService)
      );
    }
    
    setFilteredOperators(filtered);
  };

  const handleOperatorSelect = (operator) => {
    setSelectedOperator(operator);
    setBookingStep('details');
  };

  const handleBookingSubmit = (e) => {
    e.preventDefault();
    setBookingConfirmed(true);
  };

  const handleBackToList = () => {
    setSelectedOperator(null);
    setBookingStep('list');
    setBookingConfirmed(false);
  };

  if (bookingConfirmed) {
    return (
      <div className="booking-confirmed">
        <div className="confirmation-content">
          <div className="success-icon">
            <AlertCircle size={40} />
          </div>
          <h2>Tow Truck Booking Confirmed!</h2>
          <p>Your tow truck has been successfully booked with {selectedOperator.name}</p>
          
          <div className="booking-summary">
            <div className="summary-item">
              <span className="label">Operator:</span>
              <span className="value">{selectedOperator.name}</span>
            </div>
            <div className="summary-item">
              <span className="label">Date:</span>
              <span className="value">{bookingData.date}</span>
            </div>
            <div className="summary-item">
              <span className="label">Time:</span>
              <span className="value">{bookingData.time}</span>
            </div>
            <div className="summary-item">
              <span className="label">Location:</span>
              <span className="value">{bookingData.location}</span>
            </div>
          </div>
          
          <div className="confirmation-actions">
            <button onClick={() => navigate('/car-service/home')} className="home-btn">
              Back to Home
            </button>
            <button onClick={() => navigate('/car-service/bookings')} className="bookings-btn">
              View My Bookings
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (bookingStep === 'details' && selectedOperator) {
    return (
      <div className="operator-details">
        <div className="operator-profile">
          <div className="profile-header">
            <button onClick={handleBackToList} className="back-btn">
              <ChevronRight size={20} />
              Back to Operators
            </button>
            <div className="profile-avatar">
              <User size={60} />
            </div>
            <div className="profile-info">
              <h2>{selectedOperator.name}</h2>
              <p className="specialization">{selectedOperator.specialization || selectedOperator.experience ? `${selectedOperator.experience || 'Experienced'} Operator` : 'Tow Truck Operator'}</p>
              <div className="rating-large">
                <Star size={20} className="star" />
                <span>{selectedOperator.rating || '4.5'}</span>
                <span className="reviews">({selectedOperator.reviews || '0'} reviews)</span>
              </div>
            </div>
          </div>
          
          <div className="operator-details-grid">
            <div className="detail-card">
              <h3>Contact Information</h3>
              <div className="detail-item">
                <Phone size={16} />
                <span>{selectedOperator.phone || 'Phone not available'}</span>
              </div>
              <div className="detail-item">
                <Mail size={16} />
                <span>{selectedOperator.email || 'Email not available'}</span>
              </div>
              <div className="detail-item">
                <MapPin size={16} />
                <span>{selectedOperator.city || 'Location not specified'}</span>
              </div>
            </div>
            
            <div className="detail-card">
              <h3>Services</h3>
              <div className="services-list">
                {(selectedOperator.services || ['Emergency Towing', 'Long Distance Towing']).map(service => (
                  <div key={service} className="service-item">
                    <Truck size={16} />
                    <span>{service}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="detail-card">
              <h3>Availability</h3>
              <div className="availability-info">
                <span className={`status ${selectedOperator.is_online ? 'online' : 'offline'}`}>
                  {selectedOperator.is_online ? 'Available Now' : 'Currently Offline'}
                </span>
                <p>Response time: {selectedOperator.response_time || '30 minutes'}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="booking-section">
          <form onSubmit={handleBookingSubmit} className="booking-form">
            <h2>Book Tow Truck with {selectedOperator.name}</h2>
            
            <div className="form-grid">
              <div className="form-group">
                <label>Date *</label>
                <input
                  type="date"
                  required
                  value={bookingData.date}
                  onChange={(e) => setBookingData({...bookingData, date: e.target.value})}
                />
              </div>
              
              <div className="form-group">
                <label>Time *</label>
                <input
                  type="time"
                  required
                  value={bookingData.time}
                  onChange={(e) => setBookingData({...bookingData, time: e.target.value})}
                />
              </div>
              
              <div className="form-group full-width">
                <label>Pickup Location *</label>
                <input
                  type="text"
                  required
                  placeholder="Enter pickup location"
                  value={bookingData.location}
                  onChange={(e) => setBookingData({...bookingData, location: e.target.value})}
                />
              </div>
              
              <div className="form-group full-width">
                <label>Description</label>
                <textarea
                  placeholder="Describe your towing needs..."
                  value={bookingData.description}
                  onChange={(e) => setBookingData({...bookingData, description: e.target.value})}
                  rows={4}
                />
              </div>
            </div>
            
            <div className="form-actions">
              <button type="button" onClick={handleBackToList} className="cancel-btn">
                Cancel
              </button>
              <button type="submit" className="submit-btn">
                Confirm Booking
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="book-tow-truck">
      <div className="page-header">
        <h1>Book Tow Truck Operator</h1>
        <p>Find and book reliable tow truck services in your area</p>
      </div>

      <div className="search-filters">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search by name, location, or service..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="filter-dropdown">
          <Filter size={20} />
          <select
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
          >
            <option value="">All Services</option>
            {services.map(service => (
              <option key={service} value={service}>{service}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Finding tow truck operators...</p>
        </div>
      ) : filteredOperators.length > 0 ? (
        <div className="operators-grid">
          {filteredOperators.map(operator => (
            <div key={operator.id} className="operator-card">
              <div className="operator-header">
                <div className="operator-info">
                  <h3>{operator.name || 'Unknown Operator'}</h3>
                  <p className="specialization">{operator.specialization || operator.experience ? `${operator.experience || 'Experienced'} Operator` : 'Tow Truck Operator'}</p>
                  <div className="rating">
                    <Star size={16} className="star" />
                    <span>{operator.rating || '4.5'}</span>
                    <span className="reviews">({operator.reviews || '0'} reviews)</span>
                  </div>
                </div>
                <div className="operator-status">
                  <span className={`status ${operator.is_online ? 'online' : 'offline'}`}>
                    {operator.is_online ? 'Available' : 'Offline'}
                  </span>
                </div>
              </div>
              <div className="operator-details">
                <div className="detail-item">
                  <MapPin size={16} />
                  <span>{operator.city || 'Location not specified'}</span>
                </div>
                <div className="detail-item">
                  <Phone size={16} />
                  <span>{operator.phone || 'Phone not available'}</span>
                </div>
                <div className="detail-item">
                  <Mail size={16} />
                  <span>{operator.email || 'Email not available'}</span>
                </div>
              </div>
              
              <div className="operator-services">
                <h4>Services:</h4>
                <div className="services-tags">
                  {(operator.services || ['Emergency Towing', 'Long Distance Towing']).slice(0, 3).map(service => (
                    <span key={service} className="service-tag">{service}</span>
                  ))}
                  {(operator.services || ['Emergency Towing', 'Long Distance Towing']).length > 3 && (
                    <span className="more-services">+{(operator.services || ['Emergency Towing', 'Long Distance Towing']).length - 3} more</span>
                  )}
                </div>
              </div>
              
              <button 
                onClick={() => handleOperatorSelect(operator)}
                className="select-operator-btn"
              >
                Book Now
                <ChevronRight size={16} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-operators">
          <Truck size={40} />
          <h3>No tow truck operators available</h3>
          <p>Try adjusting your search criteria or check back later</p>
        </div>
      )}

      <style>{`
        .book-tow-truck {
          padding: 2rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .page-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .page-header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .page-header p {
          color: #6b7280;
          font-size: 1.1rem;
        }

        .search-filters {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .search-bar {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: white;
        }

        .search-bar input {
          flex: 1;
          border: none;
          outline: none;
          font-size: 1rem;
        }

        .filter-dropdown {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: white;
        }

        .filter-dropdown select {
          border: none;
          outline: none;
          font-size: 1rem;
          background: transparent;
        }

        .operators-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .operator-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          transition: transform 0.2s;
        }

        .operator-card:hover {
          transform: translateY(-2px);
        }

        .operator-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .operator-info h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }

        .specialization {
          color: #6b7280;
          font-size: 0.9rem;
          margin-bottom: 0.5rem;
        }

        .rating {
          display: flex;
          align-items: center;
          gap: 0.25rem;
        }

        .star {
          color: #fbbf24;
          fill: #fbbf24;
        }

        .reviews {
          color: #6b7280;
          font-size: 0.8rem;
        }

        .status {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .status.online {
          background: #dcfce7;
          color: #16a34a;
        }

        .status.offline {
          background: #f3f4f6;
          color: #6b7280;
        }

        .operator-details {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #6b7280;
          font-size: 0.9rem;
        }

        .operator-services h4 {
          font-size: 0.9rem;
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .services-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .service-tag {
          background: #f3f4f6;
          padding: 0.25rem 0.5rem;
          border-radius: 6px;
          font-size: 0.75rem;
          color: #4b5563;
        }

        .more-services {
          background: #e5e7eb;
          padding: 0.25rem 0.5rem;
          border-radius: 6px;
          font-size: 0.75rem;
          color: #6b7280;
        }

        .select-operator-btn {
          width: 100%;
          padding: 0.75rem;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .select-operator-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }

        .loading-state {
          text-align: center;
          padding: 3rem;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #e5e7eb;
          border-top: 4px solid #7c3aed;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .no-operators {
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }

        .no-operators svg {
          color: #7c3aed;
          opacity: 0.5;
          margin-bottom: 1rem;
        }

        .operator-details {
          display: grid;
          grid-template-columns: 1fr;
          gap: 2rem;
        }

        .operator-profile {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .profile-header {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          margin-bottom: 2rem;
        }

        .back-btn {
          align-self: flex-start;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background: #f3f4f6;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          margin-bottom: 2rem;
        }

        .profile-avatar {
          width: 120px;
          height: 120px;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          margin-bottom: 1rem;
        }

        .profile-info h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .rating-large {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          justify-content: center;
        }

        .operator-details-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .detail-card {
          background: #f9fafb;
          padding: 1.5rem;
          border-radius: 8px;
        }

        .detail-card h3 {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 1rem;
        }

        .services-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .service-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #4b5563;
        }

        .availability-info {
          text-align: center;
        }

        .booking-section {
          background: white;
          border-radius: 12px;
          padding: 2rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          margin-top: 2rem;
        }

        .booking-form h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 1.5rem;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .form-group.full-width {
          grid-column: 1 / -1;
        }

        .form-group label {
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .form-group input,
        .form-group textarea {
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
        }

        .form-group input:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: #7c3aed;
          box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .cancel-btn {
          padding: 0.75rem 1.5rem;
          background: #f3f4f6;
          color: #6b7280;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
        }

        .submit-btn {
          padding: 0.75rem 1.5rem;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .booking-confirmed {
          text-align: center;
          padding: 3rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .success-icon {
          width: 80px;
          height: 80px;
          background: #dcfce7;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #16a34a;
          margin: 0 auto 1.5rem;
        }

        .booking-summary {
          background: #f9fafb;
          padding: 1.5rem;
          border-radius: 8px;
          margin: 2rem 0;
        }

        .summary-item {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem 0;
          border-bottom: 1px solid #e5e7eb;
        }

        .summary-item:last-child {
          border-bottom: none;
        }

        .summary-item .label {
          color: #6b7280;
        }

        .summary-item .value {
          font-weight: 600;
          color: #1f2937;
        }

        .confirmation-actions {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }

        .home-btn,
        .bookings-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
        }

        .home-btn {
          background: #f3f4f6;
          color: #6b7280;
        }

        .bookings-btn {
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          color: white;
        }
      `}</style>
    </div>
  );
};

export default BookTowTruck;
