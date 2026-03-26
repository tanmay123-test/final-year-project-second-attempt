import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../shared/api';

const BookMechanic = () => {
  const navigate = useNavigate();
  
  const [step, setStep] = useState('list'); // 'list' or 'details'
  const [mechanics, setMechanics] = useState([]);
  const [filteredMechanics, setFilteredMechanics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedService, setSelectedService] = useState('All Services');
  
  // Booking State
  const [selectedMechanic, setSelectedMechanic] = useState(null);
  const [bookingType, setBookingType] = useState('instant');
  const [issueDescription, setIssueDescription] = useState('');
  const [userCars, setUserCars] = useState([]);
  const [selectedCar, setSelectedCar] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const services = [
    'All Services',
    'Engine Repair',
    'Brake Service',
    'Electrical',
    'Battery',
    'Tyre'
  ];

  useEffect(() => {
    fetchMechanics();
    fetchUserCars();
  }, []);

  useEffect(() => {
    filterMechanics();
  }, [searchQuery, selectedService, mechanics]);

  const fetchMechanics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/car/mechanics/available');
      if (response.data?.mechanics) {
        setMechanics(response.data.mechanics);
      }
    } catch (error) {
      console.error('Error fetching mechanics:', error);
      setMechanics([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserCars = async () => {
    try {
      const response = await api.get('/api/car/cars');
      if (response.data?.cars && response.data.cars.length > 0) {
        setUserCars(response.data.cars);
        setSelectedCar(response.data.cars[0]); // Default to first car
      }
    } catch (error) {
      console.error('Error fetching user cars:', error);
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
    
    if (selectedService !== 'All Services') {
      filtered = filtered.filter(mechanic => 
        mechanic.specialization?.toLowerCase().includes(selectedService.toLowerCase()) ||
        mechanic.services?.some(s => s.toLowerCase().includes(selectedService.toLowerCase()))
      );
    }
    
    setFilteredMechanics(filtered);
  };

  const handleMechanicSelect = (mechanic) => {
    setSelectedMechanic(mechanic);
    setStep('details');
    window.scrollTo(0, 0);
  };

  const handleSubmitBooking = async () => {
    if (!selectedCar || !issueDescription) {
      alert('Please select a vehicle and describe your issue.');
      return;
    }

    try {
      setSubmitting(true);
      const bookingData = {
        mechanic_id: selectedMechanic.id,
        car_id: selectedCar.id,
        booking_type: bookingType,
        issue_description: issueDescription,
        service_fee: 450 // Real currency (Rupees)
      };

      const response = await api.post('/api/car/book-mechanic', bookingData);
      if (response.data?.success) {
        alert('Booking submitted successfully!');
        navigate('/car-service/home');
      }
    } catch (error) {
      console.error('Error submitting booking:', error);
      alert(error.response?.data?.error || 'Failed to submit booking. Please try again.');
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
    <div className="text-[#191c20] bg-surface min-h-screen font-body selection:bg-[#4d41df]/20">
      {step === 'list' ? (
        <main className="pt-12 pb-20 px-6 max-w-7xl mx-auto">
          {/* Back Navigation & Title Section */}
          <div className="mb-10 flex flex-col md:flex-row md:items-end md:justify-between gap-6">
            <div className="space-y-2">
              <button 
                onClick={() => navigate('/car-service/home')}
                className="flex items-center gap-2 text-[#4d41df] font-bold mb-4 hover:gap-3 transition-all group"
              >
                <span className="material-symbols-outlined transition-transform group-hover:-translate-x-1">arrow_back</span>
                <span>Back to Dashboard</span>
              </button>
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-[#191c20] leading-tight font-headline">
                Book a Mechanic
              </h1>
              <p className="text-lg text-[#464555] max-w-lg font-medium">Certified mechanics near you, on demand. Expert service delivered to your driveway.</p>
            </div>
            {/* Stats Boxes */}
            <div className="flex gap-4">
              <div className="bg-surface-container-low p-6 rounded-xl flex flex-col gap-1 min-w-[160px] border border-[#c7c4d8]/20">
                <span className="text-[#4d41df] font-black text-3xl font-headline">{mechanics.length}</span>
                <span className="text-[10px] font-bold uppercase tracking-widest text-[#777587]">Mechanics Online</span>
              </div>
              <div className="bg-surface-container-low p-6 rounded-xl flex flex-col gap-1 min-w-[160px] border border-[#c7c4d8]/20">
                <span className="text-[#ab3500] font-black text-3xl font-headline">12m</span>
                <span className="text-[10px] font-bold uppercase tracking-widest text-[#777587]">Avg Response</span>
              </div>
            </div>
          </div>

          {/* Search & Filter Bar */}
          <div className="bg-surface-container-lowest p-4 rounded-2xl shadow-[0_8px_24px_rgba(25,28,32,0.03)] flex flex-col md:flex-row gap-4 mb-12 border border-[#c7c4d8]/15">
            <div className="flex-1 relative">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#777587]">search</span>
              <input 
                className="w-full pl-12 pr-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-[#4d41df]/20 text-[#191c20] placeholder:text-[#777587] font-medium transition-all" 
                placeholder="Search by name or skill..." 
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="relative min-w-[200px]">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-[#777587]">filter_list</span>
              <select 
                className="w-full pl-12 pr-10 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-[#4d41df]/20 text-[#191c20] appearance-none cursor-pointer font-bold"
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

          {/* Mechanics Grid */}
          {filteredMechanics.length === 0 ? (
            <div className="bg-surface-container-low border-2 border-dashed border-[#c7c4d8]/30 rounded-3xl h-[400px] flex flex-col items-center justify-center text-center p-8">
              <div className="bg-surface-container-lowest p-6 rounded-full mb-6 shadow-sm">
                <span className="material-symbols-outlined text-6xl text-[#c7c4d8]">person_off</span>
              </div>
              <h3 className="text-2xl font-headline font-bold mb-2">No mechanics found</h3>
              <p className="text-[#464555] mb-8 max-w-xs font-medium">Try adjusting your search filters to find available experts near you.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {filteredMechanics.map((mechanic) => (
                <div key={mechanic.id} className="group bg-surface-container-lowest p-6 rounded-2xl flex flex-col sm:flex-row gap-6 hover:shadow-[0_12px_32px_rgba(25,28,32,0.06)] transition-all duration-300 border border-[#c7c4d8]/10">
                  <div className="relative shrink-0">
                    <div className="w-24 h-24 rounded-full border-4 border-surface-container-low overflow-hidden bg-slate-100">
                      <img 
                        alt={mechanic.name} 
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" 
                        src={mechanic.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(mechanic.name)}&background=4d41df&color=fff`}
                      />
                    </div>
                    <div className="absolute bottom-1 right-1 w-6 h-6 bg-[#00855d] rounded-full border-4 border-white flex items-center justify-center">
                      <div className="w-2.5 h-2.5 bg-[#85f8c4] rounded-full"></div>
                    </div>
                  </div>
                  <div className="flex-1 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-xl font-bold text-[#191c20] font-headline">{mechanic.name}</h3>
                        <p className="text-sm font-bold text-[#4d41df] tracking-tight">{mechanic.specialization || 'Master Mechanic'}</p>
                      </div>
                      <div className="bg-[#00855d]/10 text-[#006948] px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest border border-[#00855d]/20">
                        Available
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-[#464555] font-medium">
                      <div className="flex items-center gap-1">
                        <span className="material-symbols-outlined text-[18px] text-[#4d41df]">location_on</span>
                        <span>{mechanic.city || 'Chicago, IL'}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="material-symbols-outlined text-[18px] text-[#4d41df]">history</span>
                        <span>{mechanic.experience || '10'} yrs exp.</span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(mechanic.services || ['Engine Rebuild', 'Diagnostics', 'Brakes']).slice(0, 3).map((service, idx) => (
                        <span key={idx} className="bg-surface-container-low text-[#464555] text-[11px] px-3 py-1 rounded-full font-bold border border-[#c7c4d8]/20">
                          {service}
                        </span>
                      ))}
                    </div>
                    <div className="pt-2 flex items-center justify-between">
                      <div className="flex items-center gap-1">
                        <span className="material-symbols-outlined text-[#ab3500]" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                        <span className="font-bold text-[#191c20]">{mechanic.rating || '4.9'}</span>
                        <span className="text-[#777587] text-xs font-medium">({mechanic.reviews || '128'} reviews)</span>
                      </div>
                      <button 
                        onClick={() => handleMechanicSelect(mechanic)}
                        className="bg-gradient-to-br from-[#4d41df] to-[#675df9] text-white px-6 py-2.5 rounded-xl font-bold text-sm hover:scale-[1.05] active:scale-95 transition-all shadow-lg shadow-[#4d41df]/20"
                      >
                        Select Mechanic
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      ) : (
        <main className="pt-12 pb-20 px-6 max-w-5xl mx-auto">
          {/* Progress Indicator */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#4d41df]/30"></div>
              <div className="w-2 h-2 rounded-full bg-[#4d41df]"></div>
              <div className="w-2 h-2 rounded-full bg-[#4d41df]/30"></div>
            </div>
          </div>

          <div className="mb-10 text-center">
            <h1 className="text-4xl font-headline font-black tracking-tight text-[#191c20] mb-2">Service Details</h1>
            <p className="text-[#464555] font-medium">Help us understand what your vehicle needs.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            {/* Left Content: Booking Form */}
            <div className="lg:col-span-2 space-y-8">
              {/* Step 1: Booking Type */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#4d41df]/10 flex items-center justify-center text-[#4d41df] font-bold text-xs">01</div>
                  <h2 className="text-lg font-headline font-bold">Choose Booking Type</h2>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <button 
                    onClick={() => setBookingType('instant')}
                    className={`p-6 rounded-2xl border-2 transition-all text-left relative group ${
                      bookingType === 'instant' ? 'border-[#4d41df] bg-surface-container-lowest shadow-xl shadow-[#4d41df]/5' : 'border-[#c7c4d8]/20 bg-surface-container-lowest hover:border-[#4d41df]/30'
                    }`}
                  >
                    {bookingType === 'instant' && (
                      <div className="absolute top-4 right-4 text-[#4d41df]">
                        <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                      </div>
                    )}
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-4 transition-colors ${
                      bookingType === 'instant' ? 'bg-[#4d41df] text-white' : 'bg-surface-container-low text-[#464555]'
                    }`}>
                      <span className="material-symbols-outlined text-xl">bolt</span>
                    </div>
                    <h3 className="font-bold text-[#191c20] mb-1">Instant Book</h3>
                    <p className="text-xs text-[#464555] font-medium leading-relaxed">Mechanic arrives within 30-60 mins</p>
                  </button>

                  <button 
                    onClick={() => setBookingType('prebook')}
                    className={`p-6 rounded-2xl border-2 transition-all text-left relative group ${
                      bookingType === 'prebook' ? 'border-[#4d41df] bg-surface-container-lowest shadow-xl shadow-[#4d41df]/5' : 'border-[#c7c4d8]/20 bg-surface-container-lowest hover:border-[#4d41df]/30'
                    }`}
                  >
                    {bookingType === 'prebook' && (
                      <div className="absolute top-4 right-4 text-[#4d41df]">
                        <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                      </div>
                    )}
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-4 transition-colors ${
                      bookingType === 'prebook' ? 'bg-[#4d41df] text-white' : 'bg-surface-container-low text-[#464555]'
                    }`}>
                      <span className="material-symbols-outlined text-xl">calendar_today</span>
                    </div>
                    <h3 className="font-bold text-[#191c20] mb-1">Pre-Book</h3>
                    <p className="text-xs text-[#464555] font-medium leading-relaxed">Schedule for later today or tomorrow</p>
                  </button>
                </div>
              </div>

              {/* Step 2: Describe Issue */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#4d41df]/10 flex items-center justify-center text-[#4d41df] font-bold text-xs">02</div>
                  <h2 className="text-lg font-headline font-bold">Describe Your Issue</h2>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black tracking-widest text-[#777587] ml-1">The Problem</label>
                  <textarea 
                    value={issueDescription}
                    onChange={(e) => setIssueDescription(e.target.value)}
                    placeholder="Describe your vehicle issue... e.g. Strange knocking sound from front left wheel when braking at low speeds."
                    className="w-full bg-surface-container-low border-none rounded-2xl p-6 text-sm font-medium focus:ring-2 focus:ring-[#4d41df]/20 transition-all placeholder:text-[#777587]/60 min-h-[160px]"
                  />
                </div>
              </div>

              {/* Selected Vehicle */}
              <div className="bg-surface-container-low rounded-2xl p-6 border border-[#c7c4d8]/10">
                <div className="flex items-center justify-between mb-4">
                  <label className="text-[10px] uppercase font-black tracking-widest text-[#777587]">Select Vehicle</label>
                  <button 
                    onClick={() => navigate('/car-service/garage')}
                    className="text-[10px] uppercase font-black tracking-widest text-[#4d41df] hover:underline"
                  >
                    Add New Car
                  </button>
                </div>
                
                {userCars.length > 0 ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 gap-3">
                      {userCars.map(car => (
                        <button
                          key={car.id}
                          onClick={() => setSelectedCar(car)}
                          className={`flex items-center gap-4 p-4 rounded-xl border-2 transition-all text-left ${
                            selectedCar?.id === car.id 
                              ? 'border-[#4d41df] bg-surface-container-lowest shadow-sm' 
                              : 'border-[#c7c4d8]/10 bg-surface-container-low hover:border-[#4d41df]/30'
                          }`}
                        >
                          <div className={`w-12 h-10 rounded-lg flex items-center justify-center border ${
                            selectedCar?.id === car.id ? 'bg-[#4d41df]/10 text-[#4d41df] border-[#4d41df]/20' : 'bg-surface-container-lowest text-[#777587] border-[#c7c4d8]/20'
                          }`}>
                            <span className="material-symbols-outlined text-xl">directions_car</span>
                          </div>
                          <div className="flex-1">
                            <h4 className="font-bold text-[#191c20] text-sm">{car.brand} {car.model}</h4>
                            <p className="text-[10px] text-[#464555] font-medium uppercase tracking-wider">{car.registration_number}</p>
                          </div>
                          {selectedCar?.id === car.id && (
                            <span className="material-symbols-outlined text-[#4d41df]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-sm font-medium text-[#464555] mb-4">No vehicles in your garage</p>
                    <button 
                      onClick={() => navigate('/car-service/garage')}
                      className="bg-[#4d41df] text-white px-6 py-2 rounded-xl text-xs font-bold shadow-lg shadow-[#4d41df]/20"
                    >
                      Add Vehicle
                    </button>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <div className="pt-4 text-center space-y-4">
                <button 
                  onClick={handleSubmitBooking}
                  disabled={submitting || !selectedCar || !issueDescription}
                  className="w-full py-5 bg-gradient-to-br from-[#4d41df] to-[#675df9] text-white rounded-2xl font-black text-lg shadow-xl shadow-[#4d41df]/30 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:scale-100 disabled:shadow-none"
                >
                  {submitting ? 'Submitting...' : 'Submit Booking'}
                </button>
                <p className="text-xs text-[#777587] font-medium">You won't be charged until the service is complete.</p>
              </div>
            </div>

            {/* Right Sidebar: Assigned Specialist */}
            <div className="space-y-6">
              <div className="bg-surface-container-lowest rounded-3xl p-8 shadow-[0_20px_50px_rgba(25,28,32,0.06)] border border-[#c7c4d8]/10 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-surface-container-low rounded-full -mr-16 -mt-16 -z-0"></div>
                <div className="relative z-10">
                  <label className="text-[10px] uppercase font-black tracking-widest text-[#777587] mb-6 block">Assigned Specialist</label>
                  
                  <div className="flex items-center gap-4 mb-8">
                    <div className="w-16 h-16 rounded-2xl overflow-hidden bg-surface-container-low border-2 border-white shadow-sm">
                      <img 
                        src={selectedMechanic?.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedMechanic?.name)}&background=4d41df&color=fff`} 
                        alt={selectedMechanic?.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div>
                      <h3 className="text-xl font-headline font-black text-[#191c20]">{selectedMechanic?.name}</h3>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1 text-[#00855d]">
                          <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                          <span className="text-xs font-bold">{selectedMechanic?.rating || '4.9'}</span>
                        </div>
                        <span className="text-[#777587] text-[10px] font-bold">•</span>
                        <span className="text-[#777587] text-[10px] font-bold uppercase tracking-tighter">{selectedMechanic?.reviews || '124'} Jobs Done</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4 pt-6 border-t border-surface-container-low">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-[#464555]">Response Time</span>
                      <span className="text-xs font-bold text-[#191c20]">~8 mins</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-medium text-[#464555]">Distance</span>
                      <span className="text-xs font-bold text-[#191c20]">2.4 miles away</span>
                    </div>
                    <div className="flex justify-between items-center pt-4 border-t border-surface-container-low">
                      <span className="text-sm font-bold text-[#191c20]">Service Fee</span>
                      <span className="text-xl font-black text-[#4d41df]">₹450.00</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Satisfaction Guarantee */}
              <div className="bg-[#00855d]/5 rounded-2xl p-4 border border-[#00855d]/10 flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-[#00855d]/10 flex items-center justify-center text-[#006948]">
                  <span className="material-symbols-outlined text-xl" style={{ fontVariationSettings: "'FILL' 1" }}>verified_user</span>
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-[#006948] uppercase tracking-wider">Expert Satisfaction Guarantee</h4>
                  <p className="text-[9px] font-bold text-[#00855d] uppercase opacity-70">Fully Insured & Certified</p>
                </div>
              </div>

              <button 
                onClick={() => setStep('list')}
                className="w-full py-4 text-[#4d41df] font-bold text-sm hover:bg-[#4d41df]/5 rounded-2xl transition-all"
              >
                Choose another mechanic
              </button>
            </div>
          </div>
        </main>
      )}
    </div>
  );
};

export default BookMechanic;
