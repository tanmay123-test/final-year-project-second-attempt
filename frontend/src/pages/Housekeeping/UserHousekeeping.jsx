import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { housekeepingService } from '../shared/api';
import { Calendar, Clock, MapPin, CheckCircle, AlertCircle, Home, Check, Plus, Minus, ArrowRight, ArrowLeft } from 'lucide-react';
import './Housekeeping.css';

const UserHousekeeping = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState('select'); // select, details, schedule, confirm, success
  const [services, setServices] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [selectedWorker, setSelectedWorker] = useState(null);
  const [selectedService, setSelectedService] = useState(null);
  
  // Form Data
  const [homeSize, setHomeSize] = useState('');
  const [addOns, setAddOns] = useState([]);
  const [extraHours, setExtraHours] = useState(0);
  const [bookingType, setBookingType] = useState('schedule'); // instant, schedule
  const [formData, setFormData] = useState({
    address: '',
    date: '',
    time: ''
  });

  const [estimate, setEstimate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Constants
  const HOME_SIZES = ['Studio', '1 BHK', '2 BHK', '3 BHK', 'Villa', 'Custom'];
  const ADD_ONS = [
    { id: 'balcony', label: 'Balcony cleaning', price: 200 },
    { id: 'terrace', label: 'Terrace cleaning', price: 300 }
  ];
  const EXTRA_HOUR_PRICE = 300;
  const TAX_RATE = 0.18;

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await housekeepingService.getServices();
      // Only set workers initially, services will be fetched after worker selection
      setWorkers(res.data.top_cleaners || []);
    } catch (err) {
      console.error("Failed to fetch data", err);
    }
  };

  const handleSelectWorker = async (worker) => {
    console.log("Selecting worker:", worker);
    setSelectedWorker(worker);
    setServices([]); // Clear previous services to avoid confusion
    
    if (!worker || !worker.id) {
        console.error("Worker ID missing in selection:", worker);
        // Fallback: If ID is missing, we can't fetch filtered services
        return;
    }

    try {
      // Fetch services filtered by this worker's specialization
      console.log(`Fetching services for worker ${worker.id} (${worker.name})`);
      const res = await housekeepingService.getServices(worker.id);
      
      if (res.data.services && res.data.services.length > 0) {
        console.log("Filtered services:", res.data.services);
        setServices(res.data.services);
      } else {
        console.warn("No services returned for worker, falling back to empty or all?");
        // If worker has no services, we should probably show nothing or a message.
        // Showing ALL services is definitely wrong if we want filtering.
        setServices([]);
      }
    } catch (err) {
      console.error("Failed to fetch worker services", err);
    }
  };

  const clearWorkerSelection = async () => {
    setSelectedWorker(null);
    setServices([]); // Clear services when worker is deselected
  };

  const handleSelectService = (service) => {
    setSelectedService(service);
    setStep('details');
  };

  const [customArea, setCustomArea] = useState('');

  const parsePricing = (service) => {
    try {
      if (!service || !service.pricing_json) return null;
      return typeof service.pricing_json === 'string' ? JSON.parse(service.pricing_json) : service.pricing_json;
    } catch {
      return null;
    }
  };

  const getServicePriceForSelection = (service, size) => {
    if (!service) return 0;
    const cfg = parsePricing(service);
    if (cfg && cfg.sizes && size && cfg.sizes[size]?.enabled) {
      const p = parseFloat(cfg.sizes[size].price || 0);
      if (p > 0) return p;
    }
    if (size === 'Custom' && cfg && cfg.custom?.enabled) {
      const rate = parseFloat(cfg.custom.per_sqft || 0);
      const area = parseFloat(customArea || 0);
      if (rate > 0 && area > 0) return rate * area;
    }
    // Fallback to default price field
    return parseFloat(service.price || 0) || 0;
  };

  const getDisplayPrice = (service) => {
    const cfg = parsePricing(service);
    if (!cfg || !cfg.sizes) return service.price;
    let min = Infinity;
    Object.values(cfg.sizes).forEach(v => {
      const p = parseFloat(v?.price || 0);
      if (v?.enabled && p > 0 && p < min) min = p;
    });
    if (min !== Infinity) return min;
    return service.price;
  };

  const toggleAddOn = (id) => {
    if (addOns.includes(id)) {
      setAddOns(addOns.filter(a => a !== id));
    } else {
      setAddOns([...addOns, id]);
    }
  };

  const calculateTotal = () => {
    if (!selectedService) return 0;
    const basePrice = getServicePriceForSelection(selectedService, homeSize);
    let total = basePrice;
    
    // Add-ons
    addOns.forEach(id => {
      const addon = ADD_ONS.find(a => a.id === id);
      if (addon) total += addon.price;
    });

    // Extra Hours
    total += extraHours * EXTRA_HOUR_PRICE;

    // Tax
    const tax = total * TAX_RATE;
    
    return {
      base: total,
      tax: tax,
      total: total + tax
    };
  };

  const handleCheckAvailability = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await housekeepingService.checkAvailability({
        service_type: selectedService.name,
        worker_id: selectedWorker?.id,
        booking_type: bookingType, // Pass booking type (instant/schedule)
        ...formData
      });
      // We rely on local calculation for price, but use API for worker availability
      setEstimate({
        ...calculateTotal(),
        workers_count: res.data.workers_count
      });
      setStep('confirm');
    } catch (err) {
      setError(err.response?.data?.error || "Service unavailable at this time");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmBooking = async () => {
    setLoading(true);
    try {
      const totals = calculateTotal();
      const finalHomeSize = homeSize === 'Custom' && customArea ? `Custom: ${customArea} sqft` : homeSize;
      await housekeepingService.confirmBooking({
        service_type: selectedService.name,
        worker_id: selectedWorker?.id,
        ...formData,
        home_size: finalHomeSize,
        add_ons: JSON.stringify(addOns),
        booking_type: bookingType,
        payment_method: 'card', // Mock
        price: totals.total
      });
      setStep('success');
    } catch (err) {
      setError(err.response?.data?.error || "Booking failed");
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="step-indicator">
      <div className={`step-item ${['select', 'details', 'schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">1</div>
        <span>Professional</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['details', 'schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">2</div>
        <span>Details</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">3</div>
        <span>Schedule</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">4</div>
        <span>Confirm</span>
      </div>
    </div>
  );

  return (
    <div className="housekeeping-container">
      <div className="hk-header-main">
        <button className="back-nav" onClick={() => navigate(-1)}>&larr; Back</button>
        <h1>Book Service</h1>
      </div>

      {renderStepIndicator()}

      {step === 'select' && (
        <div className="step-content">
          
          {/* Worker Selection Section */}
          <div className="worker-selection-section">
            <h2>Select Your Professional</h2>
            {selectedWorker ? (
              <div className="selected-worker-banner">
                <div className="worker-info">
                   <div className="worker-avatar-small">{selectedWorker.name.charAt(0)}</div>
                   <div>
                     <strong>{selectedWorker.name}</strong>
                     <p>{selectedWorker.specialization}</p>
                   </div>
                </div>
                <button className="secondary-btn small" onClick={clearWorkerSelection}>Change</button>
              </div>
            ) : (
              <div className="workers-horizontal-scroll">
                {workers.length > 0 ? workers.map(worker => (
                  <div key={worker.id} className={`worker-card-compact ${!worker.is_online ? 'offline' : ''}`} onClick={() => handleSelectWorker(worker)}>
                    <div className="worker-status-badge">
                      <span className={`status-dot ${worker.is_online ? 'online' : 'offline'}`}></span>
                      {worker.is_online ? 'Online' : 'Offline'}
                    </div>
                    <div className="worker-avatar">{worker.name.charAt(0)}</div>
                    <h3>{worker.name}</h3>
                    <p>{worker.specialization || 'Housekeeping'}</p>
                    <div className="rating">★ {worker.rating || 'New'}</div>
                    <button className="primary-btn small">
                      {worker.is_online ? `Book ${worker.name.split(' ')[0]}` : `Schedule ${worker.name.split(' ')[0]}`}
                    </button>
                  </div>
                )) : (
                  <div className="no-workers-msg">
                    <p>No professionals found.</p>
                    <p className="sub-text">Please check back later.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {selectedWorker ? (
            <>
              <h2>Services by {selectedWorker.name}</h2>
              <div className="service-grid">
                {services.map((service) => (
                  <div key={service.name} className={`service-card ${selectedService?.name === service.name ? 'selected' : ''}`} onClick={() => handleSelectService(service)}>
                    <div className="icon-wrapper">
                      <Home size={32} />
                    </div>
                    <h3>{service.name}</h3>
                    <p>{service.description}</p>
                    <div className="card-footer">
                      <span className="price-tag">${getDisplayPrice(service)}</span>
                      {service.available_count !== undefined && (
                         <span className={`status-text ${service.available_count > 0 ? 'available' : 'busy'}`}>
                           {service.available_count > 0 ? 'Available' : 'Busy'}
                         </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
             <div className="select-prompt">
               <ArrowLeft size={24} className="bounce-left" />
               <p>Please select a professional to view their services</p>
             </div>
          )}
        </div>
      )}

      {step === 'details' && (
        <div className="step-content form-container">
          <h2>Booking Details</h2>
          
          <div className="form-section">
            <label>Home Size</label>
            <div className="options-grid">
              {HOME_SIZES.map(size => (
                <div 
                  key={size} 
                  className={`option-card ${homeSize === size ? 'selected' : ''}`}
                  onClick={() => setHomeSize(size)}
                >
                  {size}
                </div>
              ))}
            </div>
            {homeSize === 'Custom' && (
              <div className="form-group" style={{ marginTop: '12px' }}>
                <label>Area (sqft)</label>
                <input 
                  type="text" 
                  value={customArea}
                  onChange={(e) => setCustomArea(e.target.value.replace(/[^0-9.]/g, ''))}
                  placeholder="e.g. 800"
                />
                <small className="sub-text">Price will auto-calculate if provider supports per-sqft pricing</small>
              </div>
            )}
          </div>

          <div className="form-section">
            <label>Add-Ons</label>
            <div className="addons-list">
              {ADD_ONS.map(addon => (
                <div 
                  key={addon.id} 
                  className={`addon-item ${addOns.includes(addon.id) ? 'selected' : ''}`}
                  onClick={() => toggleAddOn(addon.id)}
                >
                  <div className="addon-check">
                    {addOns.includes(addon.id) ? <Check size={16} /> : <div className="unchecked" />}
                  </div>
                  <span>{addon.label}</span>
                  <span className="price">+${addon.price}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="form-section">
            <label>Extra Hours (${EXTRA_HOUR_PRICE}/hr)</label>
            <div className="counter-control">
              <button onClick={() => setExtraHours(Math.max(0, extraHours - 1))}><Minus size={16}/></button>
              <span>{extraHours}</span>
              <button onClick={() => setExtraHours(extraHours + 1)}><Plus size={16}/></button>
            </div>
          </div>

          <div className="form-actions">
            <button className="secondary-btn" onClick={() => setStep('select')}>Back</button>
            <button className="primary-btn" onClick={() => setStep('schedule')} disabled={!homeSize || (homeSize === 'Custom' && !(parseFloat(customArea) > 0))}>Next <ArrowRight size={16}/></button>
          </div>
        </div>
      )}

      {step === 'schedule' && (
        <div className="step-content form-container">
          <h2>Schedule Service</h2>
          
          <div className="booking-type-toggle">
            <div 
              className={`type-option ${bookingType === 'instant' ? 'active' : ''}`}
              onClick={() => setBookingType('instant')}
            >
              <div className="bolt-icon">⚡</div>
              <div>
                <strong>Instant</strong>
                <p>Get a worker now</p>
              </div>
            </div>
            <div 
              className={`type-option ${bookingType === 'schedule' ? 'active' : ''}`}
              onClick={() => setBookingType('schedule')}
            >
              <Calendar size={20} />
              <div>
                <strong>Schedule</strong>
                <p>Pick date & time</p>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label><MapPin size={16}/> Address</label>
            <input 
              required 
              type="text" 
              value={formData.address}
              onChange={(e) => setFormData({...formData, address: e.target.value})}
              placeholder="Enter your full address"
            />
          </div>

          {bookingType === 'schedule' && (
            <div className="form-row">
              <div className="form-group">
                <label><Calendar size={16}/> Date</label>
                <input 
                  required 
                  type="date" 
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>
              <div className="form-group">
                <label><Clock size={16}/> Time</label>
                <input 
                  required 
                  type="time" 
                  value={formData.time}
                  onChange={(e) => setFormData({...formData, time: e.target.value})}
                />
              </div>
            </div>
          )}

          {bookingType === 'instant' && (
            <div className="info-box">
              <AlertCircle size={20} />
              <p>
                {selectedWorker 
                  ? `We will request ${selectedWorker.name} immediately.` 
                  : "Please select a professional to proceed."}
              </p>
            </div>
          )}

          <div className="form-actions">
            <button className="secondary-btn" onClick={() => setStep('details')}>Back</button>
            <button 
              className="primary-btn" 
              onClick={handleCheckAvailability}
              disabled={!formData.address || !selectedWorker || (bookingType === 'schedule' && (!formData.date || !formData.time))}
              title={!selectedWorker ? "Please select a professional first" : ""}
            >
              {loading ? 'Checking...' : 'Check Availability'}
            </button>
          </div>
          {error && <div className="error-msg"><AlertCircle size={16}/> {error}</div>}
        </div>
      )}

      {step === 'confirm' && estimate && (
        <div className="step-content confirm-container">
          <h2>Order Summary</h2>
          <div className="summary-card">
            <div className="summary-row">
              <span>Service</span>
              <strong>{selectedService.name}</strong>
            </div>
            <div className="summary-row">
              <span>Home Size</span>
              <strong>{homeSize}</strong>
            </div>
            <div className="summary-row">
              <span>Type</span>
              <strong>{bookingType === 'instant' ? 'Instant' : 'Schedule'}</strong>
            </div>
            {bookingType === 'schedule' && (
              <div className="summary-row">
                <span>Date & Time</span>
                <strong>{formData.date} at {formData.time}</strong>
              </div>
            )}
            <div className="summary-row">
              <span>Address</span>
              <strong>{formData.address}</strong>
            </div>
            
            <div className="divider"></div>
            
            <div className="summary-row">
              <span>Base Price</span>
              <strong>${getServicePriceForSelection(selectedService, homeSize)}</strong>
            </div>
            {addOns.length > 0 && (
              <div className="summary-row">
                <span>Add-ons</span>
                <strong>+${addOns.reduce((sum, id) => sum + (ADD_ONS.find(a => a.id === id)?.price || 0), 0)}</strong>
              </div>
            )}
            {extraHours > 0 && (
              <div className="summary-row">
                <span>Extra Hours ({extraHours})</span>
                <strong>+${extraHours * EXTRA_HOUR_PRICE}</strong>
              </div>
            )}
            <div className="summary-row">
              <span>Tax (18%)</span>
              <strong>${estimate.tax.toFixed(2)}</strong>
            </div>
            
            <div className="summary-row total">
              <span>Total</span>
              <strong>${estimate.total.toFixed(2)}</strong>
            </div>
          </div>
          
          <div className="workers-found">
            <CheckCircle size={16} color="green"/> {estimate.workers_count} professionals available nearby
          </div>

          <div className="form-actions">
             <button className="secondary-btn" onClick={() => setStep('schedule')}>Back</button>
             <button className="confirm-btn" onClick={handleConfirmBooking} disabled={loading}>
               {loading ? 'Processing...' : 'Confirm Booking'} <ArrowRight size={16}/>
             </button>
          </div>
        </div>
      )}

      {step === 'success' && (
        <div className="success-container">
          <CheckCircle size={64} color="#2ecc71" />
          <h2>Booking Confirmed!</h2>
          <p>Your booking for <strong>{selectedService.name}</strong> has been placed.</p>
          <p>We are notifying nearby professionals.</p>
          <button className="primary-btn" onClick={() => navigate('/dashboard')}>Go to Dashboard</button>
        </div>
      )}
    </div>
  );
};

export default UserHousekeeping;
