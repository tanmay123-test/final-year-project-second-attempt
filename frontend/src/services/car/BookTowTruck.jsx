import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../shared/api';

const BookTowTruck = () => {
  const navigate = useNavigate();
  const [towTruckOperators, setTowTruckOperators] = useState([]);
  const [filteredOperators, setFilteredOperators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState('All Services');
  const [selectedOperator, setSelectedOperator] = useState(null);
  const [bookingStep, setBookingStep] = useState('list');
  const [bookingData, setBookingData] = useState({
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }),
    location: '',
    dropoffLocation: '',
    vehicleType: 'Flatbed',
    vehicleCondition: 'Not Running',
    description: ''
  });
  const [submitting, setSubmitting] = useState(false);

  const services = [
    'All Services',
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
      setLoading(true);
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
    
    if (selectedService !== 'All Services') {
      filtered = filtered.filter(operator => 
        operator.services?.includes(selectedService) || 
        (operator.specialization && operator.specialization.includes(selectedService))
      );
    }
    
    setFilteredOperators(filtered);
  };

  const handleOperatorSelect = (operator) => {
    setSelectedOperator(operator);
    setBookingStep('details');
    window.scrollTo(0, 0);
  };

  const handleSubmitBooking = async (e) => {
    e.preventDefault();
    if (!bookingData.location || !bookingData.date || !bookingData.time) {
      alert('Please fill in all required fields.');
      return;
    }

    try {
      setSubmitting(true);
      // In a real app, you would send this to your backend
      // const response = await api.post('/api/car/tow/create-request', {
      //   operator_id: selectedOperator.id,
      //   ...bookingData
      // });
      
      // Simulating a successful booking
      setTimeout(() => {
        alert('Tow truck booking submitted successfully!');
        navigate('/car-service/my-bookings');
      }, 1000);
      
    } catch (error) {
      console.error('Error submitting booking:', error);
      alert('Failed to submit booking. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#4d41df]/20 border-t-[#4d41df]"></div>
      </div>
    );
  }

  return (
    <div className="bg-surface text-on-surface pb-32 font-body selection:bg-[#4d41df]/20">
      {bookingStep === 'list' ? (
        <main className="max-w-7xl mx-auto px-4 md:px-8 pt-8 space-y-12">
          {/* Service Banner */}
          <section className="relative overflow-hidden rounded-[1.5rem] md:rounded-[2.5rem] bg-gradient-to-br from-primary to-primary-container p-6 md:p-16 text-on-primary shadow-2xl">
            <div className="absolute top-0 right-0 w-1/2 h-full opacity-10 pointer-events-none hidden md:block">
              <span className="material-symbols-outlined text-[25rem] rotate-12 translate-x-12 translate-y-12">local_shipping</span>
            </div>
            <div className="relative z-10 max-w-2xl space-y-4 md:space-y-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20">
                <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>emergency</span>
                <span className="text-[10px] md:text-xs font-bold uppercase tracking-widest">Emergency Dispatch Active</span>
              </div>
              <h1 className="text-3xl md:text-7xl font-extrabold tracking-tight leading-none font-headline">
                Tow Truck Service
              </h1>
              <p className="text-base md:text-2xl text-primary-fixed-dim leading-relaxed max-w-lg font-medium opacity-90">
                24/7 Emergency towing for all vehicles. Expert operators at your location in minutes.
              </p>
              <div className="flex flex-wrap gap-4 pt-4">
                <button 
                  onClick={() => {
                    const el = document.getElementById('operators-section');
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }}
                  className="bg-surface-container-lowest text-primary px-6 md:px-10 py-3 md:py-5 rounded-2xl font-black text-base md:text-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all flex items-center gap-3 shadow-xl shadow-primary/20"
                >
                  Book Now
                  <span className="material-symbols-outlined text-xl md:text-2xl">arrow_forward</span>
                </button>
                <button className="bg-white/10 backdrop-blur-sm border border-white/20 text-white px-6 md:px-10 py-3 md:py-5 rounded-2xl font-black text-base md:text-xl hover:bg-white/20 active:scale-95 transition-all">
                  Learn More
                </button>
              </div>
            </div>
          </section>

          {/* Filters Section */}
          <div id="operators-section" className="bg-surface-container-lowest p-3 md:p-6 rounded-[1.5rem] shadow-[0_20px_50px_rgba(25,28,32,0.06)] flex flex-col md:flex-row gap-4 border border-[#c7c4d8]/15 sticky top-[100px] z-40 backdrop-blur-md bg-white/90">
            <div className="flex-1 relative">
              <span className="material-symbols-outlined absolute left-4 md:left-6 top-1/2 -translate-y-1/2 text-[#777587]">search</span>
              <input 
                className="w-full pl-12 md:pl-16 pr-6 py-3 md:py-5 bg-surface-container-low border-none rounded-2xl focus:ring-2 focus:ring-[#4d41df]/20 text-[#191c20] placeholder:text-[#777587] font-bold transition-all text-sm md:text-base" 
                placeholder="Search by name or location..." 
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="relative min-w-[200px]">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#777587]">filter_list</span>
              <select 
                className="w-full pl-12 pr-12 py-3 md:py-5 bg-surface-container-low border-none rounded-2xl focus:ring-2 focus:ring-[#4d41df]/20 text-[#191c20] appearance-none cursor-pointer font-black text-sm md:text-base"
                value={selectedService}
                onChange={(e) => setSelectedService(e.target.value)}
              >
                {services.map(service => (
                  <option key={service} value={service}>{service}</option>
                ))}
              </select>
              <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-[#777587] pointer-events-none">expand_more</span>
            </div>
          </div>

          <section className="space-y-8">
            <div className="flex justify-between items-end">
              <div className="space-y-2">
                <h2 className="text-3xl md:text-5xl font-black tracking-tight font-headline text-on-surface">Available Operators</h2>
                <p className="text-on-surface-variant font-bold text-base md:text-lg">Nearby operators ready to assist you right now.</p>
              </div>
            </div>

            {filteredOperators.length === 0 ? (
              <div className="py-24 text-center bg-surface-container-low rounded-[2.5rem] border-2 border-dashed border-outline-variant/30">
                <div className="max-w-xs mx-auto space-y-6">
                  <div className="w-24 h-24 bg-surface-container-lowest rounded-full flex items-center justify-center mx-auto shadow-inner">
                    <span className="material-symbols-outlined text-5xl text-outline-variant">search_off</span>
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-2xl font-black font-headline text-on-surface">No operators found</h3>
                    <p className="text-on-surface-variant text-sm font-bold leading-relaxed">We couldn't find any operators matching your criteria. Try expanding your search area.</p>
                  </div>
                  <button 
                    onClick={() => { setSearchQuery(''); setSelectedService('All Services'); }}
                    className="bg-primary/10 text-primary px-8 py-3 rounded-xl font-black hover:bg-primary/20 transition-all text-sm uppercase tracking-widest"
                  >
                    Clear Filters
                  </button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {filteredOperators.map((operator) => (
                  <div key={operator.id} className="group bg-surface-container-lowest rounded-3xl p-8 shadow-[0_20px_50px_rgba(25,28,32,0.04)] hover:shadow-[0_32px_64px_rgba(25,28,32,0.1)] hover:-translate-y-2 transition-all duration-500 border border-[#c7c4d8]/10 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-surface-container-low rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700 opacity-50"></div>
                    <div className="relative z-10">
                      <div className="flex justify-between items-start mb-8">
                        <div className="relative">
                          <div className="w-20 h-20 rounded-2xl overflow-hidden shadow-2xl border-2 border-white group-hover:rotate-3 transition-transform">
                            <img 
                              alt={operator.name} 
                              className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700 scale-110 group-hover:scale-100" 
                              src={operator.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(operator.name)}&background=4d41df&color=fff`} 
                            />
                          </div>
                          <div className="absolute -bottom-2 -right-2 w-6 h-6 bg-tertiary rounded-full border-4 border-white shadow-lg"></div>
                        </div>
                        <div className="flex flex-col items-end gap-3">
                          <div className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest border transition-colors ${
                            operator.is_online ? 'bg-secondary-container/10 text-secondary border-secondary/20' : 'bg-surface-container-low text-outline border-outline/20'
                          }`}>
                            {operator.is_online ? 'Emergency' : 'Offline'}
                          </div>
                          <div className="flex items-center gap-1.5 bg-amber-500/10 text-amber-600 px-3 py-1 rounded-lg border border-amber-500/20">
                            <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                            <span className="text-sm font-black">{operator.rating || '4.9'}</span>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-6">
                        <div>
                          <h3 className="text-2xl font-black font-headline text-on-surface group-hover:text-primary transition-colors">{operator.name}</h3>
                          <p className="text-on-surface-variant text-sm flex items-center gap-1.5 font-bold mt-1">
                            <span className="material-symbols-outlined text-base text-primary">location_on</span>
                            {operator.city || 'Available Nearby'}
                          </p>
                        </div>
                        <div className="flex items-center gap-4 py-5 border-y border-outline-variant/10">
                          <div className="w-12 h-12 bg-surface-container-low rounded-2xl flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-all duration-500">
                            <span className="material-symbols-outlined text-2xl">local_shipping</span>
                          </div>
                          <div>
                            <p className="text-[10px] text-on-surface-variant uppercase font-black tracking-widest opacity-60">Truck Type</p>
                            <p className="text-base font-black text-on-surface">{operator.specialization || 'Flatbed Tow Truck'}</p>
                          </div>
                        </div>
                        <button 
                          onClick={() => handleOperatorSelect(operator)}
                          className="w-full bg-surface-container-high text-on-surface py-4 rounded-2xl font-black text-sm uppercase tracking-widest group-hover:bg-primary group-hover:text-white group-hover:shadow-2xl group-hover:shadow-primary/30 transition-all active:scale-95 duration-300"
                        >
                          Select Operator
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      ) : (
        <main className="max-w-6xl mx-auto px-6 py-12 animate-fade-in">
          {/* Header Section: Operator Summary */}
          <section className="mb-12">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
              <div className="space-y-3">
                <button 
                  onClick={() => setBookingStep('list')}
                  className="flex items-center gap-2 text-primary font-black mb-4 hover:gap-4 transition-all group bg-primary/5 px-5 py-2 rounded-xl w-fit"
                >
                  <span className="material-symbols-outlined transition-transform group-hover:-translate-x-2">arrow_back</span>
                  <span className="uppercase tracking-widest text-[10px]">Change Operator</span>
                </button>
                <div className="space-y-1">
                  <span className="font-label text-[11px] font-bold uppercase tracking-widest text-secondary opacity-80">Confirming Specialist</span>
                  <h1 className="font-headline font-black text-5xl tracking-tighter text-on-surface">Book Your Tow</h1>
                </div>
              </div>
              
              <div className="bg-surface-container-lowest p-6 rounded-2xl shadow-[0_20px_50px_rgba(25,28,32,0.06)] flex items-center gap-6 border border-outline-variant/15 flex-1 md:max-w-md relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-24 h-24 bg-surface-container-low rounded-full -mr-12 -mt-12 opacity-50 group-hover:scale-150 transition-transform duration-700"></div>
                <div className="relative w-20 h-20 rounded-2xl overflow-hidden flex-shrink-0 shadow-lg border-2 border-white rotate-2 group-hover:rotate-0 transition-transform">
                  <img 
                    className="w-full h-full object-cover scale-110 group-hover:scale-100 transition-transform duration-500" 
                    src={selectedOperator?.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedOperator?.name)}&background=4d41df&color=fff`} 
                    alt={selectedOperator?.name}
                  />
                </div>
                <div className="flex-1 relative z-10">
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="font-headline font-black text-xl text-on-surface">{selectedOperator?.name || 'Roadside Titans Co.'}</h3>
                    <div className="flex items-center gap-1.5 bg-tertiary/10 text-tertiary px-2.5 py-1 rounded-lg text-xs font-black border border-tertiary/20">
                      <span className="material-symbols-outlined text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                      {selectedOperator?.rating || '4.9'}
                    </div>
                  </div>
                  <p className="text-on-surface-variant text-sm font-bold flex items-center gap-2 opacity-70">
                    <span className="material-symbols-outlined text-base text-primary">directions_car</span>
                    {selectedOperator?.specialization || 'Flatbed Specialist'}
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Asymmetric Layout: Form and Map Preview */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            {/* Booking Form Content (8 columns) */}
            <div className="lg:col-span-8 space-y-10">
              <div className="bg-surface-container-low p-10 rounded-[2.5rem] border border-outline-variant/10 shadow-sm">
                <form onSubmit={handleSubmitBooking} className="space-y-10">
                  {/* Location Inputs */}
                  <div className="grid grid-cols-1 gap-8">
                    <div className="space-y-3">
                      <label className="font-label text-[10px] font-black uppercase tracking-widest text-on-surface-variant ml-1 opacity-60">Pickup Location *</label>
                      <div className="relative flex items-center group">
                        <span className="material-symbols-outlined absolute left-5 text-primary transition-transform group-focus-within:scale-125">location_on</span>
                        <input 
                          required
                          className="w-full pl-14 pr-6 py-5 bg-surface-container-lowest border-0 rounded-2xl shadow-sm ring-1 ring-outline-variant/20 focus:ring-4 focus:ring-primary/10 transition-all font-body text-on-surface font-bold placeholder:text-outline/40" 
                          placeholder="Current Location or Enter Address" 
                          type="text"
                          value={bookingData.location}
                          onChange={(e) => setBookingData({...bookingData, location: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-3">
                      <label className="font-label text-[10px] font-black uppercase tracking-widest text-on-surface-variant ml-1 opacity-60">Drop-off Location *</label>
                      <div className="relative flex items-center group">
                        <span className="material-symbols-outlined absolute left-5 text-secondary transition-transform group-focus-within:scale-125">flag</span>
                        <input 
                          required
                          className="w-full pl-14 pr-6 py-5 bg-surface-container-lowest border-0 rounded-2xl shadow-sm ring-1 ring-outline-variant/20 focus:ring-4 focus:ring-primary/10 transition-all font-body text-on-surface font-bold placeholder:text-outline/40" 
                          placeholder="Destination Address" 
                          type="text"
                          value={bookingData.dropoffLocation}
                          onChange={(e) => setBookingData({...bookingData, dropoffLocation: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Dropdowns Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-3">
                      <label className="font-label text-[10px] font-black uppercase tracking-widest text-on-surface-variant ml-1 opacity-60">Vehicle Type</label>
                      <div className="relative">
                        <select 
                          className="w-full px-6 py-5 bg-surface-container-lowest border-0 rounded-2xl shadow-sm ring-1 ring-outline-variant/20 focus:ring-4 focus:ring-primary/10 appearance-none transition-all font-body text-on-surface font-black"
                          value={bookingData.vehicleType}
                          onChange={(e) => setBookingData({...bookingData, vehicleType: e.target.value})}
                        >
                          <option>Emergency Tow</option>
                          <option>Long Distance</option>
                          <option value="Flatbed">Flatbed</option>
                          <option>Motorcycle</option>
                          <option>Heavy Duty</option>
                        </select>
                        <span className="material-symbols-outlined absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-outline/60">expand_more</span>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <label className="font-label text-[10px] font-black uppercase tracking-widest text-on-surface-variant ml-1 opacity-60">Vehicle Condition</label>
                      <div className="relative">
                        <select 
                          className="w-full px-6 py-5 bg-surface-container-lowest border-0 rounded-2xl shadow-sm ring-1 ring-outline-variant/20 focus:ring-4 focus:ring-primary/10 appearance-none transition-all font-body text-on-surface font-black"
                          value={bookingData.vehicleCondition}
                          onChange={(e) => setBookingData({...bookingData, vehicleCondition: e.target.value})}
                        >
                          <option>Running</option>
                          <option value="Not Running">Not Running</option>
                          <option>Accident</option>
                        </select>
                        <span className="material-symbols-outlined absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-outline/60">expand_more</span>
                      </div>
                    </div>
                  </div>

                  {/* Notes */}
                  <div className="space-y-3">
                    <label className="font-label text-[10px] font-black uppercase tracking-widest text-on-surface-variant ml-1 opacity-60">Additional Notes</label>
                    <textarea 
                      className="w-full px-8 py-6 bg-surface-container-lowest border-0 rounded-3xl shadow-sm ring-1 ring-outline-variant/20 focus:ring-4 focus:ring-primary/10 transition-all font-body text-on-surface font-bold placeholder:text-outline/40 resize-none" 
                      placeholder="Any specific details about the issue or access..." 
                      rows="4"
                      value={bookingData.description}
                      onChange={(e) => setBookingData({...bookingData, description: e.target.value})}
                    ></textarea>
                  </div>

                  {/* Form Actions */}
                  <div className="flex flex-col sm:flex-row items-center gap-6 pt-6">
                    <button 
                      type="button"
                      onClick={() => setBookingStep('list')}
                      className="w-full sm:w-auto px-12 py-5 font-headline font-black text-primary rounded-2xl border-2 border-primary/10 hover:bg-primary/5 transition-all text-sm uppercase tracking-widest order-2 sm:order-1"
                    >
                      Cancel
                    </button>
                    <button 
                      type="submit"
                      disabled={submitting}
                      className="w-full sm:flex-1 py-5 font-headline font-black text-white bg-gradient-to-br from-primary to-primary-container rounded-2xl shadow-2xl shadow-primary/30 hover:scale-[1.02] active:scale-[0.98] transition-all text-sm uppercase tracking-widest order-1 sm:order-2 disabled:opacity-50"
                    >
                      {submitting ? 'Requesting...' : 'Request Tow Truck'}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Side Visual/Context (4 columns) */}
            <aside className="lg:col-span-4 space-y-8 lg:sticky lg:top-32">
              <div className="bg-surface-container-lowest rounded-[2.5rem] overflow-hidden border border-outline-variant/10 shadow-[0_32px_64px_rgba(25,28,32,0.1)] h-full flex flex-col">
                <div className="p-6 border-b border-outline-variant/5 bg-surface-container-low/30">
                  <span className="font-label text-[11px] font-black uppercase tracking-widest text-on-surface-variant opacity-60">Route Preview</span>
                </div>
                <div className="flex-1 min-h-[400px] w-full relative">
                  <img 
                    className="w-full h-full object-cover grayscale opacity-40" 
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuDoBBfck1GDNRI-cv3f-QSQu0AxCpDc78w1S1XFBkMowlfMdGLUSJ-s-HpmeJwnXEJx17O3uZMpfvKgb_T5d1DZ4NHYKsWymyzRSIZr9V0hsELJTjxDqjjtF9oqsswaQ1i0aNiU_An4GR3H7NbbMQu7j-_jZqT0PdyQ5y8IuIomfSXUeqKNwq6G9rkpd49DCbJSjI26L1_rCJdf3gIyQ3KD4y3p4Y8-KJ5-QTZ33D7bmXjSLHz4JXQOF0BFcerE0rZRZIXJ0apGJ5mQ" 
                    alt="Map Preview"
                  />
                  <div className="absolute inset-0 bg-primary/5 mix-blend-multiply"></div>
                  
                  {/* Map Overlays */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-primary/20 rounded-full animate-ping opacity-20"></div>
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-primary rounded-full shadow-2xl shadow-primary"></div>
                  
                  <div className="absolute inset-x-0 bottom-0 p-8 bg-gradient-to-t from-surface-container-lowest via-surface-container-lowest/90 to-transparent">
                    <div className="flex items-center gap-5">
                      <div className="bg-primary/10 p-4 rounded-2xl text-primary shadow-inner">
                        <span className="material-symbols-outlined text-3xl">route</span>
                      </div>
                      <div>
                        <div className="text-[10px] font-black text-on-surface-variant uppercase tracking-widest opacity-60">Estimated Arrival</div>
                        <div className="text-3xl font-headline font-black text-on-surface tracking-tighter">14-22 min</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="p-8 space-y-6 bg-surface-container-low/20">
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-tertiary/10 flex items-center justify-center text-tertiary shadow-sm">
                      <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>verified_user</span>
                    </div>
                    <div className="text-xs text-on-surface-variant leading-relaxed font-bold">
                      <span className="font-black text-on-surface block mb-1 uppercase tracking-widest text-[10px]">Insured Service</span> 
                      All tows by {selectedOperator?.name || 'Roadside Titans'} are covered by a $1M liability policy.
                    </div>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </main>
      )}
    </div>
  );
};

export default BookTowTruck;
