import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { housekeepingService } from '../../../../frontend/src/services/api';
import { Calendar, Clock, MapPin, CheckCircle, AlertCircle, Home, Check, Plus, Minus, ArrowRight, ArrowLeft } from 'lucide-react';
import '../../../../frontend/src/pages/Housekeeping/Housekeeping.css';

const BookingFlow = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [step, setStep] = useState('select'); // select, details, type-selection, schedule, confirm, success
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [recommendedWorkers, setRecommendedWorkers] = useState([]);
  const [selectedWorker, setSelectedWorker] = useState(null);
  
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
  const [availableSlots, setAvailableSlots] = useState([]);
  const [fetchingSlots, setFetchingSlots] = useState(false);

  // Constants
  const HOME_SIZES = ['Studio', '1 BHK', '2 BHK', '3 BHK', 'Villa'];
  const ADD_ONS = [
    { id: 'balcony', label: 'Balcony cleaning', price: 200 },
    { id: 'terrace', label: 'Terrace cleaning', price: 300 }
  ];
  const EXTRA_HOUR_PRICE = 300;
  const TAX_RATE = 0.18;

  useEffect(() => {
    let interval;
    
    const fetchSlots = async (isPolling = false) => {
      if (!isPolling) setFetchingSlots(true);
      try {
        // Add timestamp is handled in api.js now, but ensuring we get fresh data
        const res = await housekeepingService.getSlots(selectedService.name, formData.date, selectedWorker?.id);
        setAvailableSlots(res.data.slots || []);
      } catch (e) {
        console.error(e);
        if (!isPolling) setAvailableSlots([]);
      } finally {
        if (!isPolling) setFetchingSlots(false);
      }
    };

    if (step === 'schedule' && bookingType === 'schedule' && formData.date && selectedService) {
      fetchSlots(false); // Initial fetch
      interval = setInterval(() => fetchSlots(true), 5000); // Poll every 5s
    }
    
    return () => clearInterval(interval);
  }, [step, bookingType, formData.date, selectedService, selectedWorker]);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        // Handle pre-selected worker from navigation (e.g. from Home)
        const preSelectedWorker = location.state?.worker;
        if (preSelectedWorker) {
            console.log("Pre-selected worker:", preSelectedWorker);
            setSelectedWorker(preSelectedWorker);
        }

        // Fetch services (filtered if worker is pre-selected)
        const res = await housekeepingService.getServices(preSelectedWorker?.id);
        const fetchedServices = res.data.services || [];
        setServices(fetchedServices);

        // Pre-select service if passed from navigation state
        if (location.state?.serviceType) {
          const preSelected = fetchedServices.find(s => s.name === location.state.serviceType);
          if (preSelected) {
            setSelectedService(preSelected);
            setStep('details');
          }
        }
      } catch (err) {
        console.error("Failed to fetch services", err);
      }
    };
    fetchServices();
  }, [location.state]);

  useEffect(() => {
    let interval;
    if ((step === 'details' || step === 'schedule') && selectedService) {
       const fetchWorkers = () => {
           // Add timestamp to prevent caching
           housekeepingService.getRecommendedWorkers(selectedService.name + `&_t=${new Date().getTime()}`)
             .then(res => {
                console.log("[DEBUG] Fetched workers:", res.data);
                if (Array.isArray(res.data)) {
                   const newWorkers = res.data;
                   setRecommendedWorkers(newWorkers);
                   
                   // Update selectedWorker if it exists in the new list to reflect status changes
                   setSelectedWorker(prevSelected => {
                       if (!prevSelected) return null;
                       const updated = newWorkers.find(w => w.id === prevSelected.id);
                       return updated ? updated : prevSelected;
                   });
                }
             })
             .catch(err => console.error("Failed to fetch recommended workers", err));
       };
       
       fetchWorkers(); // Initial fetch
       interval = setInterval(fetchWorkers, 5000); // Poll every 5s for real-time status
    }
    return () => clearInterval(interval);
  }, [step, selectedService]);

  const handleSelectService = (service) => {
    setSelectedService(service);
    setStep('details');
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
    let total = selectedService.price;
    
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
        booking_type: bookingType,
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
      await housekeepingService.confirmBooking({
        service_type: selectedService.name,
        worker_id: selectedWorker?.id,
        ...formData,
        home_size: homeSize,
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
      <div className={`step-item ${['select', 'details', 'type-selection', 'schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">1</div>
        <span>Service</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['details', 'type-selection', 'schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">2</div>
        <span>Details</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['type-selection', 'schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">3</div>
        <span>Type</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['schedule', 'confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">4</div>
        <span>Schedule</span>
      </div>
      <div className="step-line"></div>
      <div className={`step-item ${['confirm', 'success'].includes(step) ? 'active' : ''}`}>
        <div className="step-circle">5</div>
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
          {selectedWorker && (
             <div className="selected-worker-banner" style={{
                 backgroundColor: '#F3E5F5', 
                 padding: '12px', 
                 borderRadius: '12px', 
                 marginBottom: '16px', 
                 display: 'flex', 
                 alignItems: 'center', 
                 gap: '12px',
                 border: '1px solid #8E44AD'
             }}>
                 <div style={{
                     width: '40px', height: '40px', 
                     borderRadius: '50%', backgroundColor: '#8E44AD', 
                     color: 'white', display: 'flex', 
                     alignItems: 'center', justifyContent: 'center', 
                     fontWeight: 'bold',
                     fontSize: '18px'
                 }}>
                     {selectedWorker.name ? selectedWorker.name.charAt(0) : '?'}
                 </div>
                 <div>
                     <p style={{margin: 0, fontWeight: 'bold', color: '#8E44AD'}}>Booking for {selectedWorker.name}</p>
                     <p style={{margin: 0, fontSize: '12px', color: '#666'}}>Select a service to proceed</p>
                 </div>
                 <button 
                    onClick={() => {
                        setSelectedWorker(null);
                        // Re-fetch all services when clearing worker
                        housekeepingService.getServices().then(res => setServices(res.data.services || []));
                    }} 
                    style={{marginLeft: 'auto', background: 'none', border: 'none', color: '#666', cursor: 'pointer', textDecoration: 'underline', fontSize: '12px'}}
                 >
                    Change
                 </button>
             </div>
          )}
          <h2>Select a Service</h2>
          <div className="service-grid">
            {services.map((service) => (
              <div key={service.name} className={`service-card ${selectedService?.name === service.name ? 'selected' : ''}`} onClick={() => handleSelectService(service)}>
                <div className="icon-wrapper">
                  <Home size={32} />
                </div>
                <h3>{service.name}</h3>
                <p>{service.description}</p>
                <div className="card-footer">
                  <span className="price-tag">${service.price}</span>
                  {service.available_count !== undefined && (
                     <span className={`status-text ${service.available_count > 0 ? 'available' : 'busy'}`}>
                       {service.available_count > 0 ? `${service.available_count} Online` : 'Busy'}
                     </span>
                  )}
                </div>
              </div>
            ))}
          </div>
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

          {recommendedWorkers.length > 0 && (
             <div className="form-section">
                <label>Recommended Professionals (Optional)</label>
                <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', padding: '4px' }}>
                   {recommendedWorkers.map(worker => (
                      <div 
                         key={worker.id}
                         onClick={() => setSelectedWorker(selectedWorker?.id === worker.id ? null : worker)}
                         style={{
                            minWidth: '140px',
                            border: selectedWorker?.id === worker.id ? '2px solid #8E44AD' : '1px solid #E5E7EB',
                            borderRadius: '12px',
                            padding: '12px',
                            cursor: 'pointer',
                            backgroundColor: selectedWorker?.id === worker.id ? '#F3E5F5' : 'white',
                            position: 'relative',
                            transition: 'all 0.2s'
                         }}
                      >
                         {selectedWorker?.id === worker.id && (
                            <div style={{ position: 'absolute', top: -6, right: -6, backgroundColor: '#8E44AD', borderRadius: '50%', padding: '2px' }}>
                               <Check size={12} color="white" />
                            </div>
                         )}
                         <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                            <div style={{ position: 'relative', width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#E0E0E0', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                               {worker.photo_url ? <img src={worker.photo_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <span style={{ fontSize: '12px', fontWeight: 'bold' }}>{worker.name[0]}</span>}
                               {/* Online Status Dot */}
                               <div style={{
                                   position: 'absolute', 
                                   bottom: 2, 
                                   right: 2, 
                                   width: 8, 
                                   height: 8, 
                                   borderRadius: '50%', 
                                   backgroundColor: worker.is_online ? '#2ECC71' : '#95A5A6',
                                   border: '1px solid white'
                               }} title={worker.is_online ? "Online" : "Offline"} />
                            </div>
                            <div>
                               <p style={{ margin: 0, fontWeight: 'bold', fontSize: '12px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '80px' }}>{worker.name}</p>
                               <p style={{ margin: 0, fontSize: '10px', color: '#666' }}>⭐ {worker.rating}</p>
                            </div>
                         </div>
                         <div style={{ fontSize: '10px', color: '#4B5563' }}>
                            <p style={{ margin: '0 0 2px 0' }}>{worker.completed_jobs} Jobs</p>
                            <p style={{ margin: 0, color: '#8E44AD', fontWeight: '500' }}>{Math.round(worker.score * 100)}% Match</p>
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          )}

          <div className="form-actions">
            <button className="secondary-btn" onClick={() => setStep('select')}>Back</button>
            <button className="primary-btn" onClick={() => setStep('type-selection')} disabled={!homeSize}>Next <ArrowRight size={16}/></button>
          </div>
        </div>
      )}

      {step === 'type-selection' && (
        <div className="step-content form-container">
          <h2>Booking Type</h2>
          
          <div className="booking-type-toggle" style={{display: 'flex', gap: '16px', marginBottom: '24px'}}>
             {/* Instant Card */}
            <div 
              className={`type-card ${bookingType === 'instant' ? 'active' : ''}`}
              onClick={() => {
                  if (selectedWorker && !selectedWorker.is_online) return;
                  setBookingType('instant');
              }}
              style={{
                  flex: 1,
                  border: bookingType === 'instant' ? '2px solid #8E44AD' : '1px solid #E5E7EB',
                  borderRadius: '12px',
                  padding: '24px',
                  cursor: (selectedWorker && !selectedWorker.is_online) ? 'not-allowed' : 'pointer',
                  backgroundColor: bookingType === 'instant' ? '#F3E5F5' : 'white',
                  opacity: (selectedWorker && !selectedWorker.is_online) ? 0.6 : 1,
                  textAlign: 'center',
                  transition: 'all 0.2s',
                  position: 'relative'
              }}
            >
               <div style={{fontSize: '2rem', marginBottom: '12px', color: '#8E44AD'}}>⚡</div>
               <h3 style={{color: '#8E44AD', marginBottom: '4px', marginTop: 0}}>Instant</h3>
               <p style={{color: '#666', fontSize: '0.9rem', margin: 0}}>Get a worker now</p>
            </div>

            {/* Schedule Card */}
            <div 
              className={`type-card ${bookingType === 'schedule' ? 'active' : ''}`}
              onClick={() => setBookingType('schedule')}
              style={{
                  flex: 1,
                  border: bookingType === 'schedule' ? '2px solid #8E44AD' : '1px solid #E5E7EB',
                  borderRadius: '12px',
                  padding: '24px',
                  cursor: 'pointer',
                  backgroundColor: bookingType === 'schedule' ? '#F3E5F5' : 'white',
                  textAlign: 'center',
                  transition: 'all 0.2s'
              }}
            >
               <div style={{fontSize: '2rem', marginBottom: '12px', color: '#8E44AD'}}>📅</div>
               <h3 style={{color: '#8E44AD', marginBottom: '4px', marginTop: 0}}>Schedule</h3>
               <p style={{color: '#666', fontSize: '0.9rem', margin: 0}}>Pick date & time</p>
            </div>
          </div>

          <div className="price-calculation-card" style={{
              border: '1px solid #E5E7EB',
              borderRadius: '12px',
              padding: '20px',
              backgroundColor: 'white',
              marginBottom: '24px'
          }}>
              <h3 style={{fontSize: '1.1rem', marginBottom: '16px', color: '#333', marginTop: 0}}>Price Calculation</h3>
              
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#666'}}>
                  <span>Base Price</span>
                  <span>${selectedService?.price}</span>
              </div>
              
              {(addOns.length > 0 || extraHours > 0) && (
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#666'}}>
                      <span>Add-ons</span>
                      <span>${
                          addOns.reduce((sum, id) => sum + (ADD_ONS.find(a => a.id === id)?.price || 0), 0) + 
                          (extraHours * EXTRA_HOUR_PRICE)
                      }</span>
                  </div>
              )}
              
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '16px', color: '#666'}}>
                  <span>Tax (18%)</span>
                  <span>${calculateTotal().tax.toFixed(2)}</span>
              </div>
              
              <div style={{
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  paddingTop: '16px', 
                  borderTop: '1px solid #E5E7EB',
                  fontWeight: 'bold',
                  fontSize: '1.1rem',
                  color: '#2C3E50'
              }}>
                  <span>Total</span>
                  <span style={{color: '#2ECC71'}}>${calculateTotal().total.toFixed(2)}</span>
              </div>
          </div>

          <button 
             className="secondary-btn"
             onClick={() => {
                 setLoading(true);
                 setTimeout(() => {
                     setLoading(false);
                     alert("Availability confirmed!");
                 }, 800);
             }}
             style={{
                 width: '100%',
                 marginBottom: '24px',
                 justifyContent: 'center'
             }}
          >
             Check Availability
          </button>

          <div className="form-actions">
            <button className="secondary-btn" onClick={() => setStep('details')}>Back</button>
            <button className="primary-btn" onClick={() => setStep('schedule')}>Next <ArrowRight size={16}/></button>
          </div>
        </div>
      )}

      {step === 'schedule' && (
        <div className="step-content form-container">
          <h2>Schedule Service</h2>
          
          {selectedWorker && !selectedWorker.is_online && (
             <div className="warning-banner" style={{padding: '10px', background: '#FFF3E0', border: '1px solid #FFCC80', borderRadius: '8px', marginBottom: '16px', color: '#E65100', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '8px'}}>
                <AlertCircle size={16} />
                <span>{selectedWorker.name} is currently offline. Please select a time slot.</span>
             </div>
          )}

          <div className="form-group">
            <label><MapPin size={16}/> Address</label>
            <input 
              required 
              type="text" 
              value={formData.address}
              onChange={(e) => setFormData({...formData, address: e.target.value})}
              placeholder="Enter your full address"
              className="form-input"
            />
          </div>

          {bookingType === 'schedule' && (
            <div className="form-column">
              <div className="form-group">
                <label><Calendar size={16}/> Date</label>
                <input 
                  required 
                  type="date" 
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value, time: ''})}
                  min={new Date().toISOString().split('T')[0]}
                  className="form-input"
                />
              </div>
              
              <div className="form-group">
                <label><Clock size={16}/> Available Time Slots</label>
                {!formData.date ? (
                  <div className="no-slots">Please select a date first</div>
                ) : fetchingSlots ? (
                  <div className="no-slots">Loading available slots...</div>
                ) : (
                  <div className="slots-grid">
                    {availableSlots.length > 0 ? availableSlots.map(slot => (
                      <button 
                        key={slot.time}
                        className={`slot-btn ${formData.time === slot.time ? 'selected' : ''}`}
                        onClick={() => setFormData({...formData, time: slot.time})}
                      >
                        <div>{slot.time}</div>
                        <div style={{fontSize: '0.75rem', opacity: 0.8}}>{slot.count} available</div>
                      </button>
                    )) : (
                      <div className="no-slots">No slots available for this date</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {bookingType === 'instant' && (
            <div className="info-box">
              <AlertCircle size={20} />
              <p>
                {selectedWorker 
                  ? `Request will be sent directly to ${selectedWorker.name}.` 
                  : "Please select a professional to proceed with instant booking."}
              </p>
            </div>
          )}

          <div className="form-actions">
            <button className="secondary-btn" onClick={() => setStep('type-selection')}>Back</button>
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
              <strong>${selectedService.price}</strong>
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
             <button className="primary-btn" onClick={handleConfirmBooking} disabled={loading}>
               {loading ? 'Processing...' : 'Confirm Booking'} <ArrowRight size={16}/>
             </button>
          </div>
          {error && <div className="error-msg" style={{marginTop: '1rem'}}><AlertCircle size={16}/> {error}</div>}
        </div>
      )}

      {step === 'success' && (
        <div className="success-container">
          <CheckCircle size={64} color="#2ecc71" />
          <h2>Booking Confirmed!</h2>
          <p>Your booking for <strong>{selectedService.name}</strong> has been placed.</p>
          <p>We are notifying nearby professionals.</p>
          <button className="primary-btn" onClick={() => navigate('/housekeeping/home')}>Go to Home</button>
        </div>
      )}
    </div>
  );
};

export default BookingFlow;
