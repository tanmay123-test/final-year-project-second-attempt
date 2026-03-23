import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../shared/api';

const CarServiceHome = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [cars, setCars] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Set user name
        if (user) {
          setUserName(user.user_name || user.name || 'User');
        }

        // Fetch cars
        try {
          const carResponse = await api.get('/api/car/cars');
          if (carResponse.data?.cars) {
            setCars(carResponse.data.cars);
          }
        } catch (err) {
          console.error('Error fetching cars:', err);
        }

        // Fetch bookings
        try {
          const bookingsResponse = await api.get('/api/car/jobs');
          if (bookingsResponse.data?.jobs) {
            setBookings(bookingsResponse.data.jobs);
          }
        } catch (err) {
          console.error('Error fetching bookings:', err);
        }
      } catch (error) {
        console.error('General error fetching home data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary/20 border-t-primary"></div>
      </div>
    );
  }

  return (
    <div className="bg-surface font-body text-on-surface">
      {/* TopNavBar */}
      <nav className="bg-[#f8f9ff]/80 dark:bg-[#191c20]/80 backdrop-blur-xl fixed top-0 z-50 flex justify-between items-center w-full px-8 py-4 max-w-full shadow-[0_12px_32px_rgba(25,28,32,0.04)]">
        <div className="flex items-center gap-8">
          <span className="text-2xl font-black text-primary dark:text-[#675df9] italic font-headline cursor-pointer" onClick={() => navigate('/services')}>Expertease</span>
          <div className="hidden md:flex gap-6 items-center">
            <a className="text-slate-600 dark:text-slate-400 font-medium hover:text-primary transition-colors duration-200" href="#">Services</a>
            <a className="text-slate-600 dark:text-slate-400 font-medium hover:text-primary transition-colors duration-200" href="#">Pricing</a>
            <a className="text-slate-600 dark:text-slate-400 font-medium hover:text-primary transition-colors duration-200" href="#">Fleet</a>
            <a className="text-slate-600 dark:text-slate-400 font-medium hover:text-primary transition-colors duration-200" href="#">Support</a>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 text-slate-600 dark:text-slate-400 hover:text-primary transition-colors">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="p-2 text-slate-600 dark:text-slate-400 hover:text-primary transition-colors">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <div className="w-10 h-10 rounded-full bg-surface-container-high overflow-hidden border border-outline-variant/15">
            <img className="w-full h-full object-cover" alt="User profile avatar" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC2FVEsyOBRK5UUHT1TPVrU8Sl6ovcImYlJu90T59-ZKF1VGt6VHn5ASOkThdxeikc1onK_m205zf8s9vrxdUjOqIjy124SV4Dgu5Jn6Bet6Ta9XIWVPz9AxlgjItBDeid9NV199cLEhFwNM3zylRSe-XKIBGWm1qlQzXEKhLYYWHRbGaqA0r8g9PTZ6lSvWPTgrA_hj7aDBQYn3zSk43KxQTddB59GMQHlbThaZC3PUzGzKSv0tKWg0dkm8mb3Tm3KZ0Ak_ta7PMuN"/>
          </div>
        </div>
      </nav>

      <main className="pt-24 pb-32 px-6 md:px-12 max-w-7xl mx-auto">
        {/* Welcome Banner */}
        <section className="mb-12 relative overflow-hidden rounded-xl bg-primary px-8 py-16 text-on-primary">
          <div className="relative z-10 max-w-2xl">
            <h1 className="font-headline text-4xl md:text-5xl font-extrabold tracking-tight mb-4">Welcome back, {userName}!</h1>
            <p className="text-on-primary/80 text-lg leading-relaxed mb-8">
              {cars.length > 0 
                ? `Your ${cars[0].brand} ${cars[0].model} is ready for its next checkup. Schedule a session with our premium experts today.`
                : "Your vehicle's health is our priority. Add your first car to get started with our premium diagnostics."}
            </p>
            <div className="flex gap-4">
              <button 
                onClick={() => navigate('/car-service/book-mechanic')}
                className="bg-surface-container-lowest text-primary font-bold px-6 py-3 rounded-lg hover:bg-surface-bright transition-all active:scale-95 shadow-lg"
              >
                Schedule Checkup
              </button>
              <button 
                onClick={() => navigate('/car-service/my-bookings')}
                className="bg-primary-container text-on-primary-container font-bold px-6 py-3 rounded-lg hover:opacity-90 transition-all border border-white/10"
              >
                View Reports
              </button>
            </div>
          </div>
          <div className="absolute top-0 right-0 w-1/2 h-full opacity-10 pointer-events-none">
            <span className="material-symbols-outlined text-[20rem] absolute -right-20 -top-20" style={{ fontVariationSettings: "'FILL' 1" }}>directions_car</span>
          </div>
        </section>

        {/* Premium Services Grid */}
        <section className="mb-16">
          <h2 className="font-headline text-2xl font-extrabold text-on-surface mb-8 tracking-tight">Premium Services</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Card 1: Mechanic */}
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] group hover:shadow-xl transition-all border border-outline-variant/10">
              <div className="w-14 h-14 bg-primary/10 rounded-lg flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-3xl">build</span>
              </div>
              <h3 className="font-headline text-xl font-bold mb-2">Mechanic</h3>
              <p className="text-on-surface-variant text-sm mb-6 leading-relaxed">Full engine diagnostic, suspension repairs, and brake services by certified pros.</p>
              <button 
                onClick={() => navigate('/car-service/book-mechanic')}
                className="w-full bg-primary py-3 rounded-lg text-on-primary font-bold text-sm tracking-wide hover:bg-primary-container transition-colors"
              >
                Book Now
              </button>
            </div>

            {/* Card 2: Fuel Delivery */}
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] group hover:shadow-xl transition-all border border-outline-variant/10">
              <div className="w-14 h-14 bg-secondary/10 rounded-lg flex items-center justify-center text-secondary mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-3xl">local_gas_station</span>
              </div>
              <h3 className="font-headline text-xl font-bold mb-2">Fuel Delivery</h3>
              <p className="text-on-surface-variant text-sm mb-6 leading-relaxed">Stranded? We deliver high-grade fuel directly to your location in minutes.</p>
              <button 
                onClick={() => navigate('/car-service/fuel-delivery')}
                className="w-full bg-primary py-3 rounded-lg text-on-primary font-bold text-sm tracking-wide hover:bg-primary-container transition-colors"
              >
                Book Now
              </button>
            </div>

            {/* Card 3: Tow Truck */}
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] group hover:shadow-xl transition-all border border-outline-variant/10">
              <div className="w-14 h-14 bg-on-surface/5 rounded-lg flex items-center justify-center text-on-surface mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-3xl">auto_towing</span>
              </div>
              <h3 className="font-headline text-xl font-bold mb-2">Tow Truck</h3>
              <p className="text-on-surface-variant text-sm mb-6 leading-relaxed">24/7 emergency towing with flatbed options for luxury and electric vehicles.</p>
              <button 
                onClick={() => navigate('/car-service/book-tow-truck')}
                className="w-full bg-primary py-3 rounded-lg text-on-primary font-bold text-sm tracking-wide hover:bg-primary-container transition-colors"
              >
                Book Now
              </button>
            </div>

            {/* Card 4: Automobile Expert */}
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] group hover:shadow-xl transition-all border border-outline-variant/10">
              <div className="w-14 h-14 bg-tertiary/10 rounded-lg flex items-center justify-center text-tertiary mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined text-3xl">psychology</span>
              </div>
              <h3 className="font-headline text-xl font-bold mb-2">Automobile Expert</h3>
              <p className="text-on-surface-variant text-sm mb-6 leading-relaxed">Pre-purchase inspections and expert consulting for performance tuning.</p>
              <button 
                onClick={() => navigate('/car-service/ask-expert')}
                className="w-full bg-primary py-3 rounded-lg text-on-primary font-bold text-sm tracking-wide hover:bg-primary-container transition-colors"
              >
                Book Now
              </button>
            </div>
          </div>
        </section>

        {/* Two Column Layout for Garage and History */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* My Garage Section */}
          <section className="lg:col-span-2">
            <div className="flex items-center justify-between mb-8">
              <h2 className="font-headline text-2xl font-extrabold text-on-surface tracking-tight">My Garage</h2>
              <button 
                onClick={() => navigate('/car-service/garage')}
                className="text-primary font-bold text-sm hover:underline"
              >
                Add New Car
              </button>
            </div>
            
            {cars.length === 0 ? (
              <div className="bg-surface-container-low rounded-xl p-12 text-center border-2 border-dashed border-outline-variant/30">
                <span className="material-symbols-outlined text-6xl text-on-surface-variant mb-4 opacity-20">directions_car</span>
                <p className="text-on-surface-variant">No cars in your garage yet. Add one to get personalized service suggestions.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {cars.map((car, index) => (
                  <div key={index} className="bg-surface-container-low rounded-xl p-6 flex flex-col md:flex-row items-center gap-8 border border-transparent hover:border-outline-variant/20 transition-all">
                    <div className="w-full md:w-48 h-32 rounded-lg bg-surface-container-highest overflow-hidden flex items-center justify-center">
                      <span className="material-symbols-outlined text-5xl text-on-surface-variant">directions_car</span>
                    </div>
                    <div className="flex-grow text-center md:text-left">
                      <div className="flex flex-col md:flex-row md:items-center gap-2 mb-2">
                        <h4 className="text-xl font-bold">{car.brand} {car.model}</h4>
                        <span className="bg-tertiary/10 text-tertiary text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider self-center">
                          {car.fuel_type || 'Regular'}
                        </span>
                      </div>
                      <p className="text-on-surface-variant text-sm mb-4">Plate: {car.registration_number || 'N/A'}</p>
                      <div className="flex justify-center md:justify-start gap-3">
                        <button className="text-xs font-bold uppercase tracking-widest text-primary border border-primary/20 px-4 py-2 rounded-lg hover:bg-primary/5 transition-colors">Diagnostics</button>
                        <button className="text-xs font-bold uppercase tracking-widest text-on-surface-variant border border-outline-variant/30 px-4 py-2 rounded-lg hover:bg-surface-container-high transition-colors">History</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Booking History Section */}
          <section className="lg:col-span-1">
            <h2 className="font-headline text-2xl font-extrabold text-on-surface mb-8 tracking-tight">Booking History</h2>
            <div className="bg-surface-container-lowest rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)] p-6 space-y-6">
              {bookings.length === 0 ? (
                <div className="text-center py-8">
                  <span className="material-symbols-outlined text-4xl text-on-surface-variant mb-2 opacity-20">history</span>
                  <p className="text-xs text-on-surface-variant">No booking history available yet.</p>
                </div>
              ) : (
                bookings.slice(0, 5).map((booking, index) => (
                  <div key={index} className="flex items-start gap-4 pb-6 border-b border-outline-variant/10 last:border-0">
                    <div className="p-2 bg-surface-container-low rounded-lg text-primary">
                      <span className="material-symbols-outlined">{booking.service_type === 'Fuel' ? 'local_gas_station' : 'build'}</span>
                    </div>
                    <div className="flex-grow">
                      <div className="flex justify-between items-start mb-1">
                        <p className="font-bold text-sm">{booking.service_type || 'Car Service'}</p>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-tighter ${
                          booking.status === 'Completed' ? 'bg-tertiary/10 text-tertiary' : 'bg-secondary-container/15 text-secondary'
                        }`}>
                          {booking.status || 'Pending'}
                        </span>
                      </div>
                      <p className="text-xs text-on-surface-variant">{booking.car_model || 'Vehicle'} • {new Date(booking.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))
              )}
              <button 
                onClick={() => navigate('/car-service/my-bookings')}
                className="w-full text-center text-sm font-bold text-primary py-2 hover:bg-primary/5 rounded-lg transition-colors"
              >
                View All History
              </button> 
            </div> 
          </section> 
        </div> 
      </main> 

      {/* BottomNavBar for Mobile */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-2 bg-[#f8f9ff]/90 dark:bg-[#191c20]/90 backdrop-blur-lg rounded-t-xl shadow-[0_-4px_12px_rgba(25,28,32,0.04)] border-t border-[#c7c4d8]/15"> 
        <button onClick={() => navigate('/car-service/home')} className="flex flex-col items-center justify-center bg-primary/10 text-primary rounded-xl px-4 py-1 active:scale-90 duration-150"> 
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>home</span> 
          <span className="font-label text-[10px] uppercase tracking-[0.05em] font-bold">Home</span> 
        </button> 
        <button onClick={() => navigate('/car-service/my-bookings')} className="flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 hover:bg-primary/5 active:scale-90 duration-150"> 
          <span className="material-symbols-outlined">car_repair</span> 
          <span className="font-label text-[10px] uppercase tracking-[0.05em] font-bold">Bookings</span> 
        </button> 
        <button className="flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 hover:bg-primary/5 active:scale-90 duration-150"> 
          <span className="material-symbols-outlined">query_stats</span> 
          <span className="font-label text-[10px] uppercase tracking-[0.05em] font-bold">Status</span> 
        </button> 
        <button className="flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 hover:bg-primary/5 active:scale-90 duration-150"> 
          <span className="material-symbols-outlined">menu</span> 
          <span className="font-label text-[10px] uppercase tracking-[0.05em] font-bold">Menu</span> 
        </button> 
      </nav> 
    </div>
  );
};

export default CarServiceHome;
