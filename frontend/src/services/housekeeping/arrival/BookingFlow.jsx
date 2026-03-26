import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { housekeepingService } from '../../../shared/api';
import { Calendar, Clock, MapPin, CheckCircle, AlertCircle, Home, Check, Plus, Minus, ArrowRight, ArrowLeft, Star } from 'lucide-react';
import '../../../pages/Housekeeping/Housekeeping.css';

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
    // Only fetch general recommendations if we haven't reached the slot selection yet
    if (step === 'details' && selectedService) {
       const fetchWorkers = () => {
           housekeepingService.getRecommendedWorkers(selectedService.name + `&_t=${new Date().getTime()}`)
             .then(res => {
                if (Array.isArray(res.data)) {
                   const newWorkers = res.data;
                   setRecommendedWorkers(newWorkers);
                   
                   setSelectedWorker(prevSelected => {
                       if (!prevSelected) return null;
                       const updated = newWorkers.find(w => w.id === prevSelected.id);
                       return updated ? updated : prevSelected;
                   });
                }
             })
             .catch(err => console.error("Failed to fetch recommended workers", err));
       };
       
       fetchWorkers();
       const interval = setInterval(fetchWorkers, 30000); // refresh every 30s
       return () => clearInterval(interval);
    }
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

  const [availableWorkers, setAvailableWorkers] = useState([]);

  const handleCheckAvailability = async () => {
    setLoading(true);
    setError(null);
    try {
      // Ensure date and time are set for instant booking if not picked
      const finalFormData = { ...formData };
      if (bookingType === 'instant') {
          if (!finalFormData.date) finalFormData.date = new Date().toISOString().split('T')[0];
          if (!finalFormData.time) finalFormData.time = 'Instant'; // Special marker for backend
      }

      const res = await housekeepingService.checkAvailability({
        service_type: selectedService.name,
        worker_id: selectedWorker?.id,
        booking_type: bookingType,
        ...finalFormData
      });
      
      // If a worker is already selected, we don't need to fetch a list of recommended workers
      if (!selectedWorker) {
        const workersRes = await housekeepingService.getRecommendedWorkers(
          `${selectedService.name}&date=${formData.date || ''}&time=${formData.time || ''}&booking_type=${bookingType}&address=${formData.address}`
        );
        setAvailableWorkers(workersRes.data || []);
      } else {
        // Just put the selected worker in the list for the confirmation screen
        setAvailableWorkers([selectedWorker]);
      }
      
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

  const handleConfirmBooking = async (workerId) => {
    setLoading(true);
    try {
      const totals = calculateTotal();
      await housekeepingService.confirmBooking({
        service_type: selectedService.name,
        worker_id: workerId,
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
                  <span className="price-tag">₹{service.price}</span>
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
                  <span className="price">+₹{addon.price}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="form-section">
            <label>Extra Hours (₹{EXTRA_HOUR_PRICE}/hr)</label>
            <div className="counter-control">
              <button onClick={() => setExtraHours(Math.max(0, extraHours - 1))}><Minus size={16}/></button>
              <span>{extraHours}</span>
              <button onClick={() => setExtraHours(extraHours + 1)}><Plus size={16}/></button>
            </div>
          </div>

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
              onClick={() => setBookingType('instant')}
              style={{
                  flex: 1,
                  border: bookingType === 'instant' ? '2px solid #8E44AD' : '1px solid #E5E7EB',
                  borderRadius: '12px',
                  padding: '24px',
                  cursor: 'pointer',
                  backgroundColor: bookingType === 'instant' ? '#F3E5F5' : 'white',
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
                  <span>₹{selectedService?.price}</span>
              </div>
              
              {(addOns.length > 0 || extraHours > 0) && (
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: '#666'}}>
                      <span>Add-ons</span>
                      <span>₹{
                          addOns.reduce((sum, id) => sum + (ADD_ONS.find(a => a.id === id)?.price || 0), 0) + 
                          (extraHours * EXTRA_HOUR_PRICE)
                      }</span>
                  </div>
              )}
              
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '16px', color: '#666'}}>
                  <span>Tax (18%)</span>
                  <span>₹{calculateTotal().tax.toFixed(2)}</span>
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
                  <span style={{color: '#2ECC71'}}>₹{calculateTotal().total.toFixed(2)}</span>
              </div>
          </div>

          <button 
             className="primary-btn"
             onClick={handleCheckAvailability}
             disabled={loading || !formData.address}
             style={{
                 width: '100%',
                 marginBottom: '24px',
                 justifyContent: 'center',
                 height: '56px',
                 fontSize: '1.1rem'
             }}
          >
             {loading ? <Loader2 className="spinner" /> : 'Check Availability'}
          </button>

          <div className="form-actions">
            <button className="secondary-btn" onClick={() => setStep('details')}>Back</button>
            <button className="primary-btn" onClick={() => setStep('schedule')}>Next <ArrowRight size={16}/></button>
          </div>
        </div>
      )}

      {step === 'schedule' && (
        <div className="step-content" style={{maxWidth: 720, margin: '0 auto'}}>
          <div style={{background: 'white', border: '1px solid #E5E7EB', borderRadius: 16, padding: 20, boxShadow: '0 10px 24px rgba(0,0,0,0.06)'}}>
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16}}>
              <h2 style={{margin: 0, fontSize: '1.25rem', fontWeight: 800, color: '#1F2937'}}>Schedule Service</h2>
              <span style={{padding: '6px 10px', background: '#F3E5F5', color: '#8E44AD', borderRadius: 999, fontSize: 12, fontWeight: 700}}>
                {bookingType === 'instant' ? 'Instant' : 'Scheduled'}
              </span>
            </div>
            
            {selectedWorker && !selectedWorker.is_online && (
              <div style={{padding: 12, background: '#FFF3E0', border: '1px solid #FFCC80', borderRadius: 12, marginBottom: 16, color: '#B45309', display: 'flex', alignItems: 'center', gap: 8}}>
                <AlertCircle size={16} />
                <span>{selectedWorker.name} is currently offline. Please select a time slot.</span>
              </div>
            )}

            <div style={{display: 'grid', gap: 16}}>
              <div>
                <label style={{display: 'block', fontWeight: 600, marginBottom: 8, color: '#374151'}}><MapPin size={16}/> Address</label>
                <input 
                  required 
                  type="text" 
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  placeholder="Enter your full address"
                  style={{width: '100%', padding: '12px 14px', borderRadius: 12, border: '1px solid #E5E7EB', outline: 'none'}}
                />
              </div>

              {bookingType === 'schedule' && (
                <div style={{display: 'grid', gridTemplateColumns: '1fr', gap: 16}}>
                  <div>
                    <label style={{display: 'block', fontWeight: 600, marginBottom: 8, color: '#374151'}}><Calendar size={16}/> Date</label>
                    <input 
                      required 
                      type="date" 
                      value={formData.date}
                      onChange={(e) => setFormData({...formData, date: e.target.value, time: ''})}
                      min={new Date().toISOString().split('T')[0]}
                      style={{width: '100%', padding: '12px 14px', borderRadius: 12, border: '1px solid #E5E7EB', outline: 'none'}}
                    />
                  </div>
                  
                  <div>
                    <label style={{display: 'block', fontWeight: 600, marginBottom: 8, color: '#374151'}}><Clock size={16}/> Available Time Slots</label>
                    {!formData.date ? (
                      <div style={{padding: 12, background: '#F9FAFB', border: '1px dashed #E5E7EB', borderRadius: 12, color: '#6B7280'}}>Please select a date first</div>
                    ) : fetchingSlots ? (
                      <div style={{padding: 12, background: '#F9FAFB', border: '1px dashed #E5E7EB', borderRadius: 12, color: '#6B7280'}}>Loading available slots...</div>
                    ) : (
                      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: 12}}>
                        {availableSlots.length > 0 ? availableSlots.map(slot => (
                          <button 
                            key={slot.time}
                            onClick={() => setFormData({...formData, time: slot.time})}
                            style={{
                              padding: '12px 10px',
                              borderRadius: 12,
                              border: formData.time === slot.time ? '2px solid #8E44AD' : '1px solid #E5E7EB',
                              background: formData.time === slot.time ? 'linear-gradient(135deg,#F3E5F5,#ffffff)' : 'white',
                              color: '#1F2937',
                              fontWeight: 600,
                              display: 'flex',
                              flexDirection: 'column',
                              alignItems: 'center',
                              gap: 4,
                              boxShadow: formData.time === slot.time ? '0 8px 16px rgba(142,68,173,0.15)' : 'none',
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                          >
                            <div>{slot.time}</div>
                            <div style={{fontSize: '0.75rem', opacity: 0.8}}>{slot.count} available</div>
                          </button>
                        )) : (
                          <div style={{padding: 12, background: '#F9FAFB', border: '1px dashed #E5E7EB', borderRadius: 12, color: '#6B7280'}}>No slots available for this date</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {bookingType === 'instant' && (
                <div style={{padding: 16, background: '#F3E5F5', border: '1px solid #8E44AD', borderRadius: 12, color: '#8E44AD', display: 'flex', alignItems: 'center', gap: 8}}>
                  <AlertCircle size={20} />
                  <p style={{margin: 0}}>
                    {selectedWorker 
                      ? `Request will be sent directly to ${selectedWorker.name}.` 
                      : "A professional will be assigned to you automatically."}
                  </p>
                </div>
              )}
            </div>

            <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 20}}>
              <button className="secondary-btn" onClick={() => setStep('type-selection')}>Back</button>
              <button 
                className="primary-btn" 
                onClick={handleCheckAvailability}
                disabled={
                  !formData.address || 
                  (bookingType === 'schedule' && (!selectedWorker || !formData.date || !formData.time))
                }
                title={bookingType === 'schedule' && !selectedWorker ? "Please select a professional first" : ""}
              >
                {loading ? 'Checking...' : 'Check Availability'}
              </button>
            </div>
            {error && <div className="error-msg" style={{marginTop: 12}}><AlertCircle size={16}/> {error}</div>}
          </div>
        </div>
      )}

      {step === 'confirm' && estimate && (
        <div className="step-content confirm-container" style={{ maxWidth: '500px', margin: '0 auto' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '24px', textAlign: 'center' }}>Confirm Your Booking</h2>
          
          <div className="summary-card" style={{ padding: '24px', borderRadius: '16px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
            <div className="summary-row" style={{ marginBottom: '12px' }}>
              <span style={{ color: '#666' }}>Service</span>
              <strong>{selectedService.name}</strong>
            </div>
            <div className="summary-row" style={{ marginBottom: '12px' }}>
              <span style={{ color: '#666' }}>Type</span>
              <strong>{bookingType === 'instant' ? 'Instant' : 'Schedule'}</strong>
            </div>
            {bookingType === 'schedule' && (
              <div className="summary-row" style={{ marginBottom: '12px' }}>
                <span style={{ color: '#666' }}>Date & Time</span>
                <strong>{formData.date} at {formData.time}</strong>
              </div>
            )}
            <div className="summary-row" style={{ marginBottom: '12px' }}>
              <span style={{ color: '#666' }}>Address</span>
              <strong>{formData.address}</strong>
            </div>

            {/* Display pre-selected worker info concisely if available */}
            {selectedWorker && (
              <div style={{ 
                marginTop: '16px', 
                padding: '12px', 
                backgroundColor: '#F3E5F5', 
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#E0E0E0', overflow: 'hidden' }}>
                  {selectedWorker.photo_url ? <img src={selectedWorker.photo_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', fontSize: '12px' }}>{selectedWorker.name[0]}</div>}
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 'bold' }}>{selectedWorker.name}</p>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#666' }}>⭐ {selectedWorker.rating} • Professional</p>
                </div>
              </div>
            )}
            
            <div className="divider" style={{ margin: '20px 0', borderTop: '1px dashed #E5E7EB' }}></div>
            
            <div className="summary-row total" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '1.1rem', fontWeight: '600' }}>Total Amount</span>
              <strong style={{ color: '#8E44AD', fontSize: '1.5rem' }}>₹{estimate.total.toFixed(2)}</strong>
            </div>

            <button 
              className="primary-btn" 
              onClick={() => handleConfirmBooking(selectedWorker?.id || availableWorkers[0]?.id)}
              disabled={loading || (!selectedWorker && availableWorkers.length === 0)}
              style={{ 
                width: '100%', 
                justifyContent: 'center', 
                padding: '14px', 
                marginTop: '24px',
                fontSize: '1.1rem',
                borderRadius: '12px'
              }}
            >
              {loading ? 'Processing...' : 'Confirm & Book Now'}
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '16px' }}>
            <button 
              className="secondary-btn" 
              onClick={() => setStep('schedule')} 
              style={{ border: 'none', background: 'none', color: '#666', textDecoration: 'underline' }}
            >
              Back to Schedule
            </button>
          </div>
          
          {error && <div className="error-msg" style={{ marginTop: '20px' }}><AlertCircle size={16} /> {error}</div>}
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
