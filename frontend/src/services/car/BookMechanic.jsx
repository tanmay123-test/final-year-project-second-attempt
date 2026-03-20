import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Filter, MapPin, Clock, Star, Phone, Mail, Calendar, 
  ChevronRight, User, AlertCircle, Wrench
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../shared/api';

const BookMechanic = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [mechanics, setMechanics] = useState([]);
  const [filteredMechanics, setFilteredMechanics] = useState([]);
  const [selectedMechanic, setSelectedMechanic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [bookingStep, setBookingStep] = useState('list'); // list, booking-type, issue-description, confirmation
  const [bookingType, setBookingType] = useState(''); // 'instant' or 'prebook'
  const [issueDescription, setIssueDescription] = useState('');
  const [bookingConfirmed, setBookingConfirmed] = useState(false);

  const services = [
    'General Service',
    'Oil Change',
    'Brake Service',
    'Battery Service',
    'Tire Service',
    'Engine Diagnostics',
    'AC Service',
    'Transmission Service'
  ];

  useEffect(() => {
    fetchMechanics();
  }, []);

  useEffect(() => {
    filterMechanics();
  }, [searchQuery, selectedService, mechanics]);

  const fetchMechanics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/car/service/workers/approved', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data?.workers) {
        // Filter for mechanics only
        const mechanicWorkers = response.data.workers.filter(worker => 
          worker.role === 'Mechanic'
        );
        setMechanics(mechanicWorkers);
      }
    } catch (error) {
      console.error('Error fetching mechanics:', error);
      // Set empty array to prevent infinite loading
      setMechanics([]);
    } finally {
      setLoading(false);
    }
  };

  const filterMechanics = () => {
    let filtered = mechanics;
    
    if (searchQuery) {
      filtered = filtered.filter(mechanic => 
        mechanic.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        mechanic.specialization?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        mechanic.city?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    if (selectedService) {
      filtered = filtered.filter(mechanic => 
        mechanic.services?.includes(selectedService)
      );
    }
    
    setFilteredMechanics(filtered);
  };

  const handleMechanicSelect = (mechanic) => {
    setSelectedMechanic(mechanic);
    setBookingStep('booking-type');
  };

  const handleBookingTypeSelect = (type) => {
    setBookingType(type);
    setBookingStep('issue-description');
  };

  const handleIssueSubmit = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Create booking based on type
      const bookingData = {
        mechanic_id: selectedMechanic.id,
        booking_type: bookingType, // 'instant' or 'prebook'
        issue_description: issueDescription,
        user_id: user?.id
      };
      
      const response = await api.post('/api/car/book-mechanic', bookingData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data?.success) {
        setBookingConfirmed(true);
        setBookingStep('confirmation');
      }
    } catch (error) {
      console.error('Booking error:', error);
      alert('Error booking mechanic. Please try again.');
    }
  };

  const handleBackToList = () => {
    setSelectedMechanic(null);
    setBookingStep('list');
    setBookingType('');
    setIssueDescription('');
    setBookingConfirmed(false);
  };

  const renderMechanicList = () => (
    <div className="book-mechanic-container">
      <div className="search-filters">
        <div className="search-bar">
          <Search size={20} />
          <input
            type="text"
            placeholder="Search mechanics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="service-filter">
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
          <p>Finding mechanics near you...</p>
        </div>
      ) : filteredMechanics.length > 0 ? (
        <div className="mechanics-grid">
          {filteredMechanics.map(mechanic => (
            <div key={mechanic.id} className="mechanic-card">
              <div className="mechanic-header">
                <div className="mechanic-info">
                  <h3>{mechanic.name || 'Unknown Mechanic'}</h3>
                  <p className="specialization">{mechanic.specialization || mechanic.experience ? `${mechanic.experience || 'Experienced'} Mechanic` : 'General Mechanic'}</p>
                  <div className="rating">
                    <Star size={16} className="star" />
                    <span>{mechanic.rating || '4.5'}</span>
                    <span className="reviews">({mechanic.reviews || '0'} reviews)</span>
                  </div>
                </div>
                <div className="mechanic-status">
                  <span className={`status ${mechanic.is_online ? 'online' : 'offline'}`}>
                    {mechanic.is_online ? 'Available' : 'Offline'}
                  </span>
                </div>
              </div>
              <div className="mechanic-details">
                <div className="detail-item">
                  <MapPin size={16} />
                  <span>{mechanic.city || 'Location not specified'}</span>
                </div>
                <div className="detail-item">
                  <Phone size={16} />
                  <span>{mechanic.phone || 'Phone not available'}</span>
                </div>
                <div className="detail-item">
                  <Mail size={16} />
                  <span>{mechanic.email || 'Email not available'}</span>
                </div>
              </div>
              
              <div className="mechanic-services">
                <h4>Services:</h4>
                <div className="services-tags">
                  {(mechanic.services || ['General Service', 'Maintenance', 'Diagnostics']).slice(0, 3).map(service => (
                    <span key={service} className="service-tag">{service}</span>
                  ))}
                  {(mechanic.services || ['General Service', 'Maintenance', 'Diagnostics']).length > 3 && (
                    <span className="more-services">+{(mechanic.services || ['General Service', 'Maintenance', 'Diagnostics']).length - 3} more</span>
                  )}
                </div>
              </div>
              
              <button 
                onClick={() => handleMechanicSelect(mechanic)}
                className="select-mechanic-btn"
              >
                Select Mechanic
                <ChevronRight size={16} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-mechanics">
          <User size={40} />
          <h3>No mechanics available</h3>
          <p>Try adjusting your search criteria or check back later</p>
        </div>
      )}
    </div>
  );

  const renderBookingTypeSelection = () => (
    <div className="booking-type-container">
      <div className="booking-type-header">
        <button onClick={handleBackToList} className="back-btn">
          <ChevronRight size={20} />
          Back to Mechanics
        </button>
        <h2>Select Booking Type</h2>
        <p>Choose how you want to book {selectedMechanic?.name || 'this mechanic'}</p>
      </div>
      
      <div className="mechanic-summary">
        <div className="mechanic-info">
          <h3>{selectedMechanic?.name || 'Unknown Mechanic'}</h3>
          <p className="specialization">{selectedMechanic?.specialization || selectedMechanic?.experience ? `${selectedMechanic?.experience || 'Experienced'} Mechanic` : 'General Mechanic'}</p>
          <div className="rating">
            <Star size={16} className="star" />
            <span>{selectedMechanic?.rating || '4.5'}</span>
            <span className="reviews">({selectedMechanic?.reviews || '0'} reviews)</span>
          </div>
        </div>
      </div>
      
      <div className="booking-type-options">
        <button 
          onClick={() => handleBookingTypeSelect('instant')}
          className="booking-type-card instant"
        >
          <div className="booking-type-icon">
            <Clock size={32} />
          </div>
          <h3>Instant Book</h3>
          <p>Book immediately for urgent issues</p>
          <div className="booking-type-features">
            <span>✓ Immediate response</span>
            <span>✓ Emergency service</span>
            <span>✓ Quick booking</span>
          </div>
        </button>
        
        <button 
          onClick={() => handleBookingTypeSelect('prebook')}
          className="booking-type-card prebook"
        >
          <div className="booking-type-icon">
            <Calendar size={32} />
          </div>
          <h3>Pre-Book (Schedule)</h3>
          <p>Schedule for a later time</p>
          <div className="booking-type-features">
            <span>✓ Choose your time</span>
            <span>✓ Plan ahead</span>
            <span>✓ Flexible scheduling</span>
          </div>
        </button>
      </div>
    </div>
  );

  const renderIssueDescription = () => (
    <div className="issue-description-container">
      <div className="issue-header">
        <button onClick={handleBackToList} className="back-btn">
          <ChevronRight size={20} />
          Back to Mechanics
        </button>
        <h2>Describe Your Issue</h2>
        <p>Tell {selectedMechanic?.name || 'the mechanic'} about your car problem</p>
      </div>
      
      <div className="mechanic-summary">
        <div className="mechanic-info">
          <h3>{selectedMechanic?.name || 'Unknown Mechanic'}</h3>
          <p className="booking-type">
            Booking Type: <span className={`type-badge ${bookingType}`}>
              {bookingType === 'instant' ? 'Instant Book' : 'Pre-Book'}
            </span>
          </p>
        </div>
      </div>
      
      <form onSubmit={handleIssueSubmit} className="issue-form">
        <div className="form-group">
          <label htmlFor="issue">Issue Description *</label>
          <textarea
            id="issue"
            value={issueDescription}
            onChange={(e) => setIssueDescription(e.target.value)}
            required
            placeholder="Please describe your car issue in detail (e.g., 'engine making strange noise', 'brakes not working properly', 'car won't start', etc.)"
            rows={6}
          />
        </div>
        
        <div className="form-actions">
          <button type="button" onClick={handleBackToList} className="cancel-btn">
            Cancel
          </button>
          <button type="submit" className="submit-btn">
            {bookingType === 'instant' ? 'Book Instantly' : 'Schedule Appointment'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderConfirmation = () => (
    <div className="confirmation-container">
      <div className="confirmation-content">
        <div className="success-icon">
          <AlertCircle size={40} />
        </div>
        <h2>Booking Confirmed!</h2>
        <p>
          {bookingType === 'instant' 
            ? `Your instant booking with ${selectedMechanic?.name || 'the mechanic'} has been confirmed. The mechanic will contact you shortly.`
            : `Your appointment with ${selectedMechanic?.name || 'the mechanic'} has been scheduled. The mechanic will contact you to arrange timing.`
          }
        </p>
        
        <div className="booking-summary">
          <div className="summary-item">
            <span className="label">Mechanic:</span>
            <span className="value">{selectedMechanic?.name || 'Unknown'}</span>
          </div>
          <div className="summary-item">
            <span className="label">Booking Type:</span>
            <span className="value">{bookingType === 'instant' ? 'Instant Book' : 'Pre-Book'}</span>
          </div>
          <div className="summary-item">
            <span className="label">Issue:</span>
            <span className="value">{issueDescription}</span>
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

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Finding mechanics near you...</p>
      </div>
    );
  }

  return (
    <div className="book-mechanic-page">
      <style>{`
        .book-mechanic-page {
          padding: 2rem;
          max-width: 1200px;
          margin: 0 auto;
          min-height: 100vh;
          background: #f9fafb;
        }

        .book-mechanic-container {
          max-width: 1200px;
          margin: 0 auto;
        }

        .search-filters {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
          background: white;
          padding: 1rem;
          border-radius: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .search-bar, .service-filter {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex: 1;
        }

        .search-bar input, .service-filter select {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
        }

        .mechanics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .mechanic-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          transition: transform 0.2s;
        }

        .mechanic-card:hover {
          transform: translateY(-2px);
        }

        .mechanic-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .mechanic-info h3 {
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

        .mechanic-details {
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

        .mechanic-services h4 {
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

        .select-mechanic-btn {
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

        .select-mechanic-btn:hover {
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

        .no-mechanics {
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }

        .no-mechanics svg {
          color: #7c3aed;
          opacity: 0.5;
          margin-bottom: 1rem;
        }

        .booking-type-container {
          max-width: 800px;
          margin: 0 auto;
        }

        .booking-type-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .back-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background: #f3f4f6;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          margin-bottom: 2rem;
          align-self: flex-start;
        }

        .booking-type-header h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .mechanic-summary {
          background: white;
          padding: 1.5rem;
          border-radius: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          margin-bottom: 2rem;
        }

        .mechanic-summary h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .booking-type {
          color: #6b7280;
          font-size: 0.9rem;
        }

        .type-badge {
          padding: 0.25rem 0.5rem;
          border-radius: 6px;
          font-weight: 500;
        }

        .type-badge.instant {
          background: #dcfce7;
          color: #16a34a;
        }

        .type-badge.prebook {
          background: #dbeafe;
          color: #1e40af;
        }

        .booking-type-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .booking-type-card {
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
        }

        .booking-type-card:hover {
          border-color: #7c3aed;
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(124, 58, 237, 0.1);
        }

        .booking-type-icon {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          margin: 0 auto 1rem;
        }

        .booking-type-card h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .booking-type-card p {
          color: #6b7280;
          margin-bottom: 1rem;
        }

        .booking-type-features {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          text-align: left;
        }

        .booking-type-features span {
          color: #4b5563;
          font-size: 0.9rem;
        }

        .issue-description-container {
          max-width: 600px;
          margin: 0 auto;
        }

        .issue-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .issue-form {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .form-group textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
          resize: vertical;
        }

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

        .confirmation-container {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 60vh;
        }

        .confirmation-content {
          text-align: center;
          background: white;
          padding: 3rem;
          border-radius: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          max-width: 500px;
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

        .confirmation-content h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 1rem;
        }

        .confirmation-content p {
          color: #6b7280;
          margin-bottom: 2rem;
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

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 50vh;
        }

        @media (max-width: 768px) {
          .book-mechanic-page {
            padding: 1rem;
          }
          
          .search-filters {
            flex-direction: column;
          }
          
          .mechanics-grid {
            grid-template-columns: 1fr;
          }
          
          .booking-type-options {
            grid-template-columns: 1fr;
          }
          
          .form-actions {
            flex-direction: column;
          }
          
          .confirmation-actions {
            flex-direction: column;
          }
        }
      `}</style>
      {bookingStep === 'list' && renderMechanicList()}
      {bookingStep === 'booking-type' && renderBookingTypeSelection()}
      {bookingStep === 'issue-description' && renderIssueDescription()}
      {bookingStep === 'confirmation' && renderConfirmation()}
    </div>
  );
};

export default BookMechanic;
