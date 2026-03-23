import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../shared/api';

const MyGarage = () => {
  const navigate = useNavigate();
  // State Management
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    make: '',
    model: '',
    year: '',
    color: '',
    registration_number: ''
  });
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  // Fetch cars on mount
  useEffect(() => {
    fetchCars();
  }, []);

  const fetchCars = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/car/cars');
      if (response.data && response.data.cars) {
        setCars(response.data.cars);
      }
    } catch (error) {
      console.error('Failed to fetch cars:', error);
      showToast('Failed to load garage. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'registration_number' ? value.toUpperCase() : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    try {
      setSubmitting(true);
      const response = await api.post('/api/car/add-car', formData);
      
      if (response.data) {
        showToast('Vehicle registered successfully!', 'success');
        setFormData({ make: '', model: '', year: '', color: '', registration_number: '' });
        fetchCars(); // Refresh list
      }
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to add car';
      showToast(errorMsg, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 3000);
  };

  const handleDeleteClick = () => {
    showToast('Delete coming soon', 'success');
  };

  // Skeleton Card Component
  const SkeletonCard = () => (
    <div className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-sm animate-pulse flex flex-col h-[400px]">
      <div className="h-48 bg-slate-200"></div>
      <div className="p-6 space-y-4">
        <div className="h-8 bg-slate-200 rounded w-3/4"></div>
        <div className="h-4 bg-slate-200 rounded w-1/2"></div>
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100">
          <div className="space-y-2">
            <div className="h-3 bg-slate-200 rounded w-1/2"></div>
            <div className="h-4 bg-slate-200 rounded w-full"></div>
          </div>
          <div className="space-y-2">
            <div className="h-3 bg-slate-200 rounded w-1/2"></div>
            <div className="h-4 bg-slate-200 rounded w-full"></div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-[#f8f9ff] min-h-screen font-body text-[#191c20] selection:bg-[#4d41df]/20">
      {/* TopNavBar */}
      <header className="bg-[#f8f9ff]/80 backdrop-blur-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] fixed top-0 z-50 flex justify-between items-center w-full px-8 py-4 max-w-full border-b border-[#c7c4d8]/10">
        <div className="flex items-center gap-12">
          <span 
            onClick={() => navigate('/car-service/home')}
            className="text-2xl font-black text-[#4d41df] italic font-headline tracking-tight cursor-pointer"
          >
            Expertease
          </span>
          <nav className="hidden md:flex items-center gap-8">
            <a 
              onClick={(e) => { e.preventDefault(); navigate('/car-service/home'); }}
              className="text-slate-600 font-medium hover:text-[#4d41df] transition-colors duration-200 cursor-pointer" 
              href="#"
            >
              Services
            </a>
            <a className="text-slate-600 font-medium hover:text-[#4d41df] transition-colors duration-200" href="#">Pricing</a>
            <a className="text-slate-600 font-medium hover:text-[#4d41df] transition-colors duration-200" href="#">Fleet</a>
            <a className="text-slate-600 font-medium hover:text-[#4d41df] transition-colors duration-200" href="#">Support</a>
          </nav>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4 text-slate-500">
            <button className="material-symbols-outlined hover:text-[#4d41df] transition-colors">notifications</button>
            <button className="material-symbols-outlined hover:text-[#4d41df] transition-colors">settings</button>
          </div>
          <div className="w-10 h-10 rounded-full overflow-hidden bg-[#e7e8ee] ring-2 ring-[#4d41df]/10">
            <img alt="User profile" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuANxn1VI4zyT7hDN1FZXf5jwGeEx1OTa4r9zT2S2ijae44t5tNBeOx4JaFOReacmvqjvu3hceGFs8RjW0gR1ZUeeR7D6943q2jX-n3ZUM22D_UXgtUAbGJ-xrTl0DOEoYFrk4EjHGJ054znin6GKV9M4re69I_yTwMOLAqJG_O_eE6nih4ZfS0rd1UfMUNwF224rwF9YQoqYpqJOcI4x3SdG4QVbUu3LIomq5FR7gvKysbKQZ5SdFNCwKou2un53UBfw2pOJcwnn6Gy" />
          </div>
        </div>
      </header>

      <main className="pt-24 pb-32 px-6 lg:px-12 max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="text-5xl lg:text-6xl font-headline font-extrabold tracking-tight text-[#191c20] mb-2">My Garage</h1>
            <p className="text-[#464555] text-lg max-w-md font-medium">Manage your automotive fleet with professional-grade precision and history tracking.</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="bg-[#f2f3f9] px-4 py-2 rounded-xl flex items-center gap-3 border border-[#c7c4d8]/20">
              <span className="material-symbols-outlined text-[#4d41df]">directions_car</span>
              <span className="font-bold text-lg">{cars.length}</span>
              <span className="uppercase tracking-wider text-xs font-bold text-[#777587]">Vehicles</span>
            </div>
          </div>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Add New Car Form */}
          <div className="md:col-span-4 space-y-6">
            <div className="bg-white rounded-xl p-8 shadow-[0_12px_32px_rgba(25,28,32,0.04)] border border-[#c7c4d8]/15">
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-[#4d41df]/10 p-2 rounded-lg text-[#4d41df]">
                  <span className="material-symbols-outlined">add_circle</span>
                </div>
                <h2 className="text-xl font-headline font-bold">Add New Car</h2>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold tracking-widest text-[#777587] px-1">Make</label>
                  <input 
                    name="make"
                    value={formData.make}
                    onChange={handleInputChange}
                    className="w-full bg-[#f2f3f9] border-none rounded-lg focus:ring-2 focus:ring-[#4d41df]/20 transition-all placeholder:text-[#c7c4d8] py-3 px-4 text-sm font-medium" 
                    placeholder="e.g. Porsche" 
                    required 
                    type="text"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold tracking-widest text-[#777587] px-1">Model</label>
                    <input 
                      name="model"
                      value={formData.model}
                      onChange={handleInputChange}
                      className="w-full bg-[#f2f3f9] border-none rounded-lg focus:ring-2 focus:ring-[#4d41df]/20 transition-all placeholder:text-[#c7c4d8] py-3 px-4 text-sm font-medium" 
                      placeholder="911 Carrera" 
                      required 
                      type="text"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-bold tracking-widest text-[#777587] px-1">Year</label>
                    <input 
                      name="year"
                      value={formData.year}
                      onChange={handleInputChange}
                      className="w-full bg-[#f2f3f9] border-none rounded-lg focus:ring-2 focus:ring-[#4d41df]/20 transition-all placeholder:text-[#c7c4d8] py-3 px-4 text-sm font-medium" 
                      placeholder="2023" 
                      required 
                      type="number"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold tracking-widest text-[#777587] px-1">Color</label>
                  <input 
                    name="color"
                    value={formData.color}
                    onChange={handleInputChange}
                    className="w-full bg-[#f2f3f9] border-none rounded-lg focus:ring-2 focus:ring-[#4d41df]/20 transition-all placeholder:text-[#c7c4d8] py-3 px-4 text-sm font-medium" 
                    placeholder="Arctic Grey" 
                    required 
                    type="text"
                  />
                </div>
                <div className="space-y-1 pb-4">
                  <label className="text-[10px] uppercase font-bold tracking-widest text-[#777587] px-1">Registration Number</label>
                  <input 
                    name="registration_number"
                    value={formData.registration_number}
                    onChange={handleInputChange}
                    className="w-full bg-[#f2f3f9] border-none rounded-lg focus:ring-2 focus:ring-[#4d41df]/20 transition-all placeholder:text-[#c7c4d8] py-3 px-4 text-sm font-medium uppercase tracking-widest" 
                    placeholder="ABC-1234" 
                    required 
                    type="text"
                  />
                </div>
                <button 
                  disabled={submitting}
                  className="w-full py-4 bg-gradient-to-br from-[#4d41df] to-[#675df9] text-white rounded-xl font-bold shadow-lg shadow-[#4d41df]/20 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-70 disabled:scale-100" 
                  type="submit"
                >
                  {submitting ? 'Registering...' : 'Register Vehicle'}
                </button>
              </form>
            </div>
            {/* Small Info Card */}
            <div className="bg-[#ab3500] text-white rounded-xl p-6 relative overflow-hidden group">
              <div className="relative z-10">
                <span className="material-symbols-outlined text-4xl mb-2 opacity-80">verified_user</span>
                <h3 className="text-lg font-headline font-bold">Premium Protection</h3>
                <p className="text-sm opacity-90 mt-1">All registered vehicles are eligible for our 24/7 roadside assistance program.</p>
              </div>
              <div className="absolute -right-8 -bottom-8 opacity-10 group-hover:scale-110 transition-transform duration-500">
                <span className="material-symbols-outlined text-[120px]" style={{ fontVariationSettings: "'FILL' 1" }}>shield</span>
              </div>
            </div>
          </div>

          {/* Car List Area */}
          <div className="md:col-span-8">
            {loading ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SkeletonCard />
                <SkeletonCard />
                <SkeletonCard />
              </div>
            ) : cars.length === 0 ? (
              <div className="bg-[#f2f3f9] border-2 border-dashed border-[#c7c4d8]/30 rounded-3xl h-[400px] flex flex-col items-center justify-center text-center p-8">
                <div className="bg-white p-6 rounded-full mb-6 shadow-sm">
                  <span className="material-symbols-outlined text-6xl text-[#c7c4d8]">car_repair</span>
                </div>
                <h3 className="text-2xl font-headline font-bold mb-2">No cars in your garage yet.</h3>
                <p className="text-[#464555] mb-8 max-w-xs font-medium">Start your premium service journey by adding your first vehicle today.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {cars.map((car, index) => (
                  <div key={car.id || index} className="group bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col border border-[#c7c4d8]/10">
                    <div 
                      className="h-48 overflow-hidden relative"
                      style={{ background: `linear-gradient(135deg, ${car.color?.toLowerCase() === 'white' ? '#e2e8f0' : car.color || '#4d41df'} 0%, #1e293b 100%)` }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center opacity-20">
                        <span className="material-symbols-outlined text-[120px] text-white">directions_car</span>
                      </div>
                      <div className="absolute top-4 left-4">
                        <span className={`px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest backdrop-blur-md ${
                          car.status === 'Maintenance Due' 
                            ? 'bg-white/90 text-[#ab3500]' 
                            : 'bg-white/90 text-[#006948]'
                        }`}>
                          {car.status || 'Active'}
                        </span>
                      </div>
                      <div className="absolute top-4 right-4">
                        <button 
                          onClick={handleDeleteClick}
                          className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white hover:bg-red-500 hover:text-white transition-colors"
                        >
                          <span className="material-symbols-outlined text-lg">delete</span>
                        </button>
                      </div>
                    </div>
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-2xl font-headline font-extrabold leading-tight">{car.make} {car.model}</h3>
                          <p className="text-[#4d41df] font-bold tracking-tight">Variant • {car.year}</p>
                        </div>
                        <div className="bg-[#f2f3f9] px-2 py-1 rounded font-mono text-xs font-bold border border-[#c7c4d8]/20 uppercase tracking-wider">
                          {car.registration_number}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 border-t border-[#c7c4d8]/10 pt-4">
                        <div>
                          <p className="text-[10px] uppercase font-bold text-[#777587] tracking-wider">Color</p>
                          <p className="text-sm font-semibold">{car.color}</p>
                        </div>
                        <div>
                          <p className="text-[10px] uppercase font-bold text-[#777587] tracking-wider">Last Service</p>
                          <p className="text-sm font-semibold">{car.last_service_date || 'None'}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {/* Empty Placeholder for Grid Balance */}
                <div className="border-2 border-dashed border-[#c7c4d8]/15 rounded-xl flex items-center justify-center p-8 bg-[#f2f3f9] group/dashed hover:bg-[#eceef3] transition-colors cursor-pointer">
                  <div className="text-center group-hover/dashed:scale-110 transition-transform">
                    <span className="material-symbols-outlined text-4xl text-[#c7c4d8] mb-2">add_circle</span>
                    <p className="text-xs font-bold uppercase tracking-widest text-[#777587]">Add More</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Mobile BottomNavBar */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-2 bg-white/90 backdrop-blur-lg border-t border-[#c7c4d8]/15 shadow-[0_-4px_12px_rgba(25,28,32,0.04)] rounded-t-xl">
        <button 
          onClick={() => navigate('/car-service/home')}
          className="flex flex-col items-center justify-center text-[#4d41df] bg-[#4d41df]/10 rounded-xl px-4 py-1"
        >
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>home</span>
          <span className="text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Home</span>
        </button>
        <button 
          onClick={() => navigate('/car-service/my-bookings')}
          className="flex flex-col items-center justify-center text-slate-400"
        >
          <span className="material-symbols-outlined">car_repair</span>
          <span className="text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Bookings</span>
        </button>
        <button className="flex flex-col items-center justify-center text-slate-400">
          <span className="material-symbols-outlined">query_stats</span>
          <span className="text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Status</span>
        </button>
        <button className="flex flex-col items-center justify-center text-slate-400">
          <span className="material-symbols-outlined">menu</span>
          <span className="text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Menu</span>
        </button>
      </nav>

      {/* Mobile FAB */}
      <button className="md:hidden fixed bottom-24 right-6 w-14 h-14 bg-[#4d41df] text-white rounded-full shadow-lg flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-40">
        <span className="material-symbols-outlined text-3xl">add</span>
      </button>

      {/* Toast Notification */}
      {toast.show && (
        <div className={`fixed bottom-10 left-1/2 -translate-x-1/2 px-6 py-3 rounded-full text-white font-bold shadow-2xl z-[100] transition-all animate-bounce ${
          toast.type === 'success' ? 'bg-[#006948]' : 'bg-[#ba1a1a]'
        }`}>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">{toast.type === 'success' ? 'check_circle' : 'error'}</span>
            {toast.message}
          </div>
        </div>
      )}
    </div>
  );
};

export default MyGarage;
