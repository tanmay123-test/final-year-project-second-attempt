import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Filter, MapPin, Clock, Star, Phone, Mail, Calendar, 
  ChevronRight, Droplet, User, AlertCircle
} from 'lucide-react';
import api from '../../shared/api';

const FuelDelivery = () => {
  const navigate = useNavigate();
  const [fuelAgents, setFuelAgents] = useState([]);
  const [filteredAgents, setFilteredAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [bookingStep, setBookingStep] = useState('list');
  const [bookingData, setBookingData] = useState({
    date: '',
    time: '',
    location: '',
    fuelType: 'petrol',
    quantity: '',
    description: ''
  });
  const [bookingConfirmed, setBookingConfirmed] = useState(false);

  const services = [
    'Petrol Delivery',
    'Diesel Delivery',
    'Emergency Fuel',
    'Bulk Fuel Delivery',
    'Marine Fuel'
  ];

  useEffect(() => {
    fetchFuelAgents();
  }, []);

  useEffect(() => {
    filterAgents();
  }, [searchQuery, selectedService, fuelAgents]);

  const fetchFuelAgents = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/car/service/workers/approved', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data?.workers) {
        // Filter for fuel delivery agents only
        const agents = response.data.workers.filter(worker => 
          worker.role === 'Fuel Delivery Agent'
        );
        setFuelAgents(agents);
      }
    } catch (error) {
      console.error('Error fetching fuel agents:', error);
      // Set empty array to prevent infinite loading
      setFuelAgents([]);
    } finally {
      setLoading(false);
    }
  };

  const filterAgents = () => {
    let filtered = fuelAgents;
    
    if (searchQuery) {
      filtered = filtered.filter(agent => 
        agent.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.specialization?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.city?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    if (selectedService) {
      filtered = filtered.filter(agent => 
        agent.services?.includes(selectedService)
      );
    }
    
    setFilteredAgents(filtered);
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    setBookingStep('fuel-type'); // Show fuel type selection first
  };

  const handleFuelTypeSelect = (fuelType) => {
    setBookingData({...bookingData, fuelType});
    setBookingStep('details'); // Then show booking form
  };

  const handleBookingSubmit = (e) => {
    e.preventDefault();
    setBookingConfirmed(true);
  };

  const handleBackToList = () => {
    setSelectedAgent(null);
    setBookingStep('list');
  };

  const renderAgentList = () => (
    <div className="agents-list">
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

      {bookingStep === 'list' && renderAgentList()}
      {bookingStep === 'fuel-type' && selectedAgent && renderFuelTypeSelection()}
      {bookingStep === 'details' && selectedAgent && renderBookingForm()}
      {bookingStep === 'confirmed' && renderConfirmation()}
    </div>
  );

  const renderFuelTypeSelection = () => (
    <div className="fuel-type-selection">
      <div className="selection-header">
        <button onClick={handleBackToList} className="back-btn">
          <ChevronRight size={20} />
          Back to Agents
        </button>
        <h2>Select Fuel Type for {selectedAgent.name}</h2>
        <p>Choose the type of fuel you need delivered</p>
      </div>
      
      <div className="fuel-type-options">
        <button onClick={() => handleFuelTypeSelect('petrol')} className="fuel-type-card petrol">
          <div className="fuel-icon">
            <Droplet size={40} />
          </div>
          <h3>Petrol</h3>
          <p>Standard gasoline for most vehicles</p>
          <div className="fuel-features">
            <span>✓ Quick Delivery</span>
            <span>✓ Available Everywhere</span>
            <span>✓ Best Price</span>
          </div>
        </button>          
        <button onClick={() => handleFuelTypeSelect('diesel')} className="fuel-type-card diesel">
          <div className="fuel-icon">
            <Droplet size={40} />
          </div>
          <h3>Diesel</h3>
          <p>Efficient diesel for trucks and heavy vehicles</p>
          <div className="fuel-features">
            <span>✓ Better Mileage</span>
            <span>✓ Heavy Duty</span>
            <span>✓ Cost Effective</span>
          </div>
        </button>          
        <button onClick={() => handleFuelTypeSelect('premium')} className="fuel-type-card premium">
          <div className="fuel-icon">
            <Droplet size={40} />
          </div>
          <h3>Premium</h3>
          <p>High-quality fuel for performance vehicles</p>
          <div className="fuel-features">
            <span>✓ Premium Quality</span>
            <span>✓ Enhanced Performance</span>
            <span>✓ Engine Protection</span>
          </div>
        </button>          
        <button onClick={() => handleFuelTypeSelect('other')} className="fuel-type-card other">
          <div className="fuel-icon">
            <Droplet size={40} />
          </div>
          <h3>Other</h3>
          <p>Specialized fuel for specific requirements</p>
          <div className="fuel-features">
            <span>✓ Custom Solutions</span>
            <span>✓ Expert Advice</span>
            <span>✓ Special Handling</span>
          </div>
        </button>
      </div>
    </div>
  );

  if (bookingConfirmed) {
    return (
      <div className="booking-confirmed">
        <div className="confirmation-content">
          <div className="success-icon">
            <AlertCircle size={40} />
          </div>
          <h2>Fuel Delivery Booking Confirmed!</h2>
          <p>Your fuel delivery has been successfully booked with {selectedAgent.name}</p>
          
          <div className="booking-summary">
            <div className="summary-item">
              <span className="label">Agent:</span>
              <span className="value">{selectedAgent.name}</span>
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
            <div className="summary-item">
              <span className="label">Fuel Type:</span>
              <span className="value">{bookingData.fuelType}</span>
            </div>
            <div className="summary-item">
              <span className="label">Quantity:</span>
              <span className="value">{bookingData.quantity} liters</span>
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

  if (bookingStep === 'fuel-type' && selectedAgent) {
    return (
      <div className="fuel-type-selection">
        <div className="selection-header">
          <button onClick={handleBackToList} className="back-btn">
            <ChevronRight size={20} />
            Back to Agents
          </button>
          <h2>Select Fuel Type for {selectedAgent.name}</h2>
          <p>Choose the type of fuel you need delivered</p>
        </div>
        
        <div className="fuel-type-options">
          <button onClick={() => handleFuelTypeSelect('petrol')} className="fuel-type-card petrol">
            <div className="fuel-icon">
              <Droplet size={40} />
            </div>
            <h3>Petrol</h3>
            <p>Standard gasoline for most vehicles</p>
            <div className="fuel-features">
              <span>✓ Quick Delivery</span>
              <span>✓ Available Everywhere</span>
              <span>✓ Best Price</span>
            </div>
          </button>
          
          <button onClick={() => handleFuelTypeSelect('diesel')} className="fuel-type-card diesel">
            <div className="fuel-icon">
              <Droplet size={40} />
            </div>
            <h3>Diesel</h3>
            <p>Efficient diesel for trucks and heavy vehicles</p>
            <div className="fuel-features">
              <span>✓ Better Mileage</span>
              <span>✓ Heavy Duty</span>
              <span>✓ Cost Effective</span>
            </div>
          </button>
          
          <button onClick={() => handleFuelTypeSelect('premium')} className="fuel-type-card premium">
            <div className="fuel-icon">
              <Droplet size={40} />
            </div>
            <h3>Premium</h3>
            <p>High-quality fuel for performance vehicles</p>
            <div className="fuel-features">
              <span>✓ Premium Quality</span>
              <span>✓ Enhanced Performance</span>
              <span>✓ Engine Protection</span>
            </div>
          </button>
          
          <button onClick={() => handleFuelTypeSelect('other')} className="fuel-type-card other">
            <div className="fuel-icon">
              <Droplet size={40} />
            </div>
            <h3>Other</h3>
            <p>Specialized fuel for specific requirements</p>
            <div className="fuel-features">
              <span>✓ Custom Solutions</span>
              <span>✓ Expert Advice</span>
              <span>✓ Special Handling</span>
            </div>
          </button>
        </div>
      </div>
    );
  }

  if (bookingStep === 'details' && selectedAgent) {
    return (
      <div className="agent-details">
        <div className="agent-profile">
          <div className="profile-header">
            <button onClick={handleBackToList} className="back-btn">
              <ChevronRight size={20} />
              Back to Agents
            </button>
            <div className="profile-avatar">
              <User size={60} />
            </div>
            <div className="profile-info">
              <h2>{selectedAgent.name}</h2>
              <p className="specialization">{selectedAgent.specialization || selectedAgent.experience ? `${selectedAgent.experience || 'Experienced'} Agent` : 'Fuel Delivery Agent'}</p>
              <div className="rating-large">
                <Star size={20} className="star" />
                <span>{selectedAgent.rating || '4.5'}</span>
                <span className="reviews">({selectedAgent.reviews || '0'} reviews)</span>
              </div>
            </div>
          </div>
          
          <div className="agent-details-grid">
            <div className="detail-card">
              <h3>Contact Information</h3>
              <div className="detail-item">
                <Phone size={16} />
                <span>{selectedAgent.phone || 'Phone not available'}</span>
              </div>
              <div className="detail-item">
                <Mail size={16} />
                <span>{selectedAgent.email || 'Email not available'}</span>
              </div>
              <div className="detail-item">
                <MapPin size={16} />
                <span>{selectedAgent.city || 'Location not specified'}</span>
              </div>
            </div>
            
            <div className="detail-card">
              <h3>Services</h3>
              <div className="services-list">
                {(selectedAgent.services || ['Petrol Delivery', 'Diesel Delivery', 'Emergency Fuel']).map(service => (
                  <div key={service} className="service-item">
                    <Droplet size={16} />
                    <span>{service}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="detail-card">
              <h3>Availability</h3>
              <div className="availability-info">
                <span className={`status ${selectedAgent.is_online ? 'online' : 'offline'}`}>
                  {selectedAgent.is_online ? 'Available Now' : 'Currently Offline'}
                </span>
                <p>Response time: {selectedAgent.response_time || '30 minutes'}</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="booking-section">
          <form onSubmit={handleBookingSubmit} className="booking-form">
            <h2>Book Fuel Delivery with {selectedAgent.name}</h2>
            
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
              
              <div className="form-group">
                <label>Fuel Type *</label>
                <select
                  required
                  value={bookingData.fuelType}
                  onChange={(e) => {
                    setBookingData({...bookingData, fuelType: e.target.value, quantity: ''});
                  }}
                >
                  <option value="">Select Fuel Type</option>
                  <option value="petrol">Petrol</option>
                  <option value="diesel">Diesel</option>
                  <option value="premium">Premium</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              {bookingData.fuelType && (
                <div className="form-group">
                  <label>Quantity (liters) *</label>
                  {(bookingData.fuelType === 'petrol' || bookingData.fuelType === 'diesel') ? (
                    bookingData.quantity === 'custom' ? (
                      <input
                        type="number"
                        required
                        min="1"
                        placeholder="Enter custom quantity"
                        value={bookingData.quantity === 'custom' ? '' : bookingData.quantity}
                        onChange={(e) => setBookingData({...bookingData, quantity: e.target.value})}
                      />
                    ) : (
                      <select
                        required
                        value={bookingData.quantity}
                        onChange={(e) => setBookingData({...bookingData, quantity: e.target.value})}
                      >
                        <option value="">Select Quantity</option>
                        <option value="5">5 Liters</option>
                        <option value="10">10 Liters</option>
                        <option value="20">20 Liters</option>
                        <option value="30">30 Liters</option>
                        <option value="50">50 Liters</option>
                        <option value="custom">Custom Quantity</option>
                      </select>
                    )
                  ) : (
                    <input
                      type="number"
                      required
                      min="1"
                      placeholder="Enter quantity"
                      value={bookingData.quantity}
                      onChange={(e) => setBookingData({...bookingData, quantity: e.target.value})}
                    />
                  )}
                </div>
              )}
              
              <div className="form-group full-width">
                <label>Delivery Location *</label>
                <input
                  type="text"
                  required
                  placeholder="Enter delivery location"
                  value={bookingData.location}
                  onChange={(e) => setBookingData({...bookingData, location: e.target.value})}
                />
              </div>
              
              <div className="form-group full-width">
                <label>Additional Notes</label>
                <textarea
                  placeholder="Any special requirements..."
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
    <div className="fuel-delivery">
      <div className="page-header">
        <h1>Book Fuel Delivery Agent</h1>
        <p>Find and book reliable fuel delivery services in your area</p>
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
          <p>Finding fuel delivery agents...</p>
        </div>
      ) : filteredAgents.length > 0 ? (
        <div className="agents-grid">
          {filteredAgents.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <div className="agent-info">
                  <h3>{agent.name || 'Unknown Agent'}</h3>
                  <p className="specialization">{agent.specialization || agent.experience ? `${agent.experience || 'Experienced'} Agent` : 'Fuel Delivery Agent'}</p>
                  <div className="rating">
                    <Star size={16} className="star" />
                    <span>{agent.rating || '4.5'}</span>
                    <span className="reviews">({agent.reviews || '0'} reviews)</span>
                  </div>
                </div>
                <div className="agent-status">
                  <span className={`status ${agent.is_online ? 'online' : 'offline'}`}>
                    {agent.is_online ? 'Available' : 'Offline'}
                  </span>
                </div>
              </div>
              <div className="agent-details">
                <div className="detail-item">
                  <MapPin size={16} />
                  <span>{agent.city || 'Location not specified'}</span>
                </div>
                <div className="detail-item">
                  <Phone size={16} />
                  <span>{agent.phone || 'Phone not available'}</span>
                </div>
                <div className="detail-item">
                  <Mail size={16} />
                  <span>{agent.email || 'Email not available'}</span>
                </div>
              </div>
              
              <div className="agent-services">
                <h4>Services:</h4>
                <div className="services-tags">
                  {(agent.services || ['Petrol Delivery', 'Diesel Delivery', 'Emergency Fuel']).slice(0, 3).map(service => (
                    <span key={service} className="service-tag">{service}</span>
                  ))}
                  {(agent.services || ['Petrol Delivery', 'Diesel Delivery', 'Emergency Fuel']).length > 3 && (
                    <span className="more-services">+{(agent.services || ['Petrol Delivery', 'Diesel Delivery', 'Emergency Fuel']).length - 3} more</span>
                  )}
                </div>
              </div>
              
              <button 
                onClick={() => handleAgentSelect(agent)}
                className="select-agent-btn"
              >
                Book Now
                <ChevronRight size={16} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-agents">
          <Droplet size={40} />
          <h3>No fuel delivery agents available</h3>
          <p>Try adjusting your search criteria or check back later</p>
        </div>
      )}

      <style>{`
        .agents-list {
          padding: 2rem;
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

        .search-bar, .filter-dropdown {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex: 1;
        }

        .search-bar input, .filter-dropdown select {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
        }

        .agents-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .agent-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          transition: transform 0.2s;
          cursor: pointer;
        }

        .agent-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }

        .agent-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .agent-info h3 {
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

        .agent-status {
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

        .agent-details {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-top: 1rem;
        }

        .detail-card {
          background: #f9fafb;
          padding: 1rem;
          border-radius: 8px;
        }

        .detail-card h3 {
          font-size: 1rem;
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.75rem;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #6b7280;
          font-size: 0.9rem;
        }

        .agent-services {
          margin-top: 1rem;
        }

        .agent-services h4 {
          font-size: 0.9rem;
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .services-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
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

        .select-agent-btn {
          width: 100%;
          padding: 0.75rem 1rem;
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

        .select-agent-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }

        .no-agents {
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }

        .no-agents svg {
          color: #7c3aed;
          opacity: 0.5;
          margin-bottom: 1rem;
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

        .fuel-type-selection {
          padding: 2rem;
          max-width: 800px;
          margin: 0 auto;
        }

        .selection-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .selection-header h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .fuel-type-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-top: 2rem;
        }

        .fuel-type-card {
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
        }

        .fuel-type-card:hover {
          border-color: #7c3aed;
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        }

        .fuel-icon {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
        }

        .fuel-icon svg {
          color: white;
          font-size: 24px;
        }

        .fuel-type-card h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin: 1rem 0 0.5rem;
        }

        .fuel-type-card p {
          color: #6b7280;
          font-size: 0.9rem;
          margin-bottom: 1rem;
        }

        .fuel-features {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .fuel-features span {
          font-size: 0.8rem;
          color: #059669;
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
        }

        .agent-profile {
          margin-bottom: 2rem;
        }

        .profile-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .profile-avatar {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .profile-avatar svg {
          color: white;
          font-size: 30px;
        }

        .rating-large {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 1.1rem;
        }

        .rating-large .star {
          width: 20px;
          height: 20px;
        }

        .rating-large .reviews {
          font-size: 0.9rem;
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
        .form-group select,
        .form-group textarea {
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: #7c3aed;
          box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          margin-top: 2rem;
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
          margin: 0 auto 1.5rem;
        }

        .success-icon svg {
          color: #16a34a;
          font-size: 40px;
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

        .page-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .page-header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1f2937;
        }

        .page-header p {
          color: #6b7280;
          font-size: 1rem;
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

        .agents-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .agent-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          transition: transform 0.2s;
        }

        .agent-card:hover {
          transform: translateY(-2px);
        }

        .agent-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .agent-info h3 {
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

        .agent-details {
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

        .agent-services h4 {
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

        .select-agent-btn {
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

        .select-agent-btn:hover {
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

        .no-agents {
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }

        .no-agents svg {
          color: #7c3aed;
          opacity: 0.5;
          margin-bottom: 1rem;
        }

        .agent-details {
          display: grid;
          grid-template-columns: 1fr;
          gap: 2rem;
        }

        .agent-profile {
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

        .agent-details-grid {
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
        .form-group select,
        .form-group textarea {
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
        }

        .form-group input:focus,
        .form-group select:focus,
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

export default FuelDelivery;
