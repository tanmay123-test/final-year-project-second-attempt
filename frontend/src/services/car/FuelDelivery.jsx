import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../shared/api';

const FuelDelivery = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [selectedFuel, setSelectedFuel] = useState('Petrol');
  const [quantity, setQuantity] = useState(20);
  const [location, setLocation] = useState('');
  const [agents, setAgents] = useState([]);
  const [activeRequest, setActiveRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ activeAgents: 0, avgEta: '18m' });

  useEffect(() => {
    fetchAgents();
  }, []);

  useEffect(() => {
    let interval;
    if (activeRequest && activeRequest.status !== 'COMPLETED') {
      interval = setInterval(async () => {
        try {
          const response = await api.get(`/api/fuel-delivery/requests/${activeRequest.id}/status`);
          if (response.data?.status) {
            setActiveRequest(prev => ({ ...prev, status: response.data.status }));
            if (response.data.status === 'COMPLETED') {
              clearInterval(interval);
            }
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 10000);
    }
    return () => clearInterval(interval);
  }, [activeRequest]);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/fuel-delivery/agents/available');
      const agentsList = response.data.agents || [];
      setAgents(agentsList);
      setStats({
        activeAgents: agentsList.length,
        avgEta: agentsList.length > 0 ? '15m' : 'N/A'
      });
    } catch (error) {
      console.error('Error fetching agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequest = async () => {
    if (!location || !quantity) {
      alert('Please provide location and quantity');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/api/fuel-delivery/requests/create', {
        fuel_type: selectedFuel,
        quantity: quantity,
        location: location,
        user_id: user?.user_id || user?.id
      });

      if (response.data?.success) {
        setActiveRequest({
          id: response.data.request_id,
          status: 'PENDING',
          agent: response.data.agent || null
        });
      }
    } catch (error) {
      console.error('Error creating fuel request:', error);
      alert('Failed to create fuel request');
    } finally {
      setLoading(false);
    }
  };

  const getStatusProgress = (status) => {
    const statuses = ['PENDING', 'ASSIGNED', 'EN_ROUTE', 'COMPLETED'];
    const index = statuses.indexOf(status);
    return ((index + 1) / statuses.length) * 100;
  };

  return (
    <div className="bg-surface font-body text-on-surface">
      {/* TopNavBar Shell */}
      <header className="bg-[#f8f9ff]/80 backdrop-blur-xl docked full-width top-0 z-50 shadow-[0_12px_32px_rgba(25,28,32,0.04)] fixed w-full">
        <nav className="flex justify-between items-center w-full px-8 py-4 max-w-full">
          <div className="flex items-center gap-12">
            <span className="text-2xl font-black text-[#4d41df] italic font-headline tracking-tight cursor-pointer" onClick={() => navigate('/car-service/home')}>Expertease</span>
            <div className="hidden md:flex gap-8">
              <a className="text-slate-600 font-medium font-headline hover:text-[#4d41df] transition-colors duration-200" href="#">Services</a>
              <a className="text-slate-600 font-medium font-headline hover:text-[#4d41df] transition-colors duration-200" href="#">Pricing</a>
              <a className="text-slate-600 font-medium font-headline hover:text-[#4d41df] transition-colors duration-200" href="#">Fleet</a>
              <a className="text-slate-600 font-medium font-headline hover:text-[#4d41df] transition-colors duration-200" href="#">Support</a>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-4">
              <button className="p-2 text-slate-600 hover:text-primary transition-colors">
                <span className="material-symbols-outlined">notifications</span>
              </button>
              <button className="p-2 text-slate-600 hover:text-primary transition-colors">
                <span className="material-symbols-outlined">settings</span>
              </button>
            </div>
            <div className="w-10 h-10 rounded-full bg-surface-container overflow-hidden border border-outline-variant/15">
              <img alt="User profile avatar" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCoU4osPojcG6jiTaW3snx8T38Db_DHWp6A8vintR_pj9p9Y9mGmE8Ar5SCp2Z6U8pqH4m_mumWVU0wTOyrsQt46Df5tJaH31CMc3IZuQBmpjuBMBZ5A8WeWeW48guJlnucJPAsWvRwHdU9VujzWQqCqaaoKV9bjb-JO5r-2TTzW_ACgNrmyZtnjjw75ypOF7ZH6BTwZVuFX1PNBnWrYRHluIdqFNEWzO8OFtAlnz2U-ypCswjx8PvDIjFpvJmSbXSrqws2Nfbfxsd6" />
            </div>
          </div>
        </nav>
      </header>

      <main className="pt-24 pb-20 px-4 md:px-8 max-w-7xl mx-auto min-h-screen">
        {/* Editorial Header Section */}
        <section className="mb-12 mt-8">
          <div className="flex flex-col md:flex-row justify-between items-end gap-6">
            <div className="max-w-2xl">
              <span className="text-secondary font-bold tracking-[0.05em] text-[11px] uppercase mb-3 block">Premium Roadside Assistance</span>
              <h1 className="text-5xl md:text-6xl font-headline font-extrabold tracking-tight text-on-surface leading-[1.1]">
                Fuel <span className="text-primary italic">Precision</span> Delivery.
              </h1>
              <p className="mt-6 text-lg text-on-surface-variant leading-relaxed font-medium">
                Running low on the road shouldn't be a crisis. Connect with certified fuel agents nearby and track your delivery in high-fidelity.
              </p>
            </div>
            <div className="flex gap-4">
              <div className="bg-surface-container-low px-6 py-4 rounded-xl">
                <span className="text-primary font-black text-2xl block">{stats.activeAgents}</span>
                <span className="text-xs font-bold uppercase tracking-wider text-outline">Agents Active</span>
              </div>
              <div className="bg-surface-container-low px-6 py-4 rounded-xl">
                <span className="text-tertiary font-black text-2xl block">{stats.avgEta}</span>
                <span className="text-xs font-bold uppercase tracking-wider text-outline">Avg ETA</span>
              </div>
            </div>
          </div>
        </section>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Request Form & Map */}
          <div className="lg:col-span-7 space-y-6">
            {/* Request Form Card */}
            <div className="bg-surface-container-lowest p-8 rounded-xl shadow-[0_12px_32px_rgba(25,28,32,0.04)]">
              <h2 className="text-2xl font-headline font-bold mb-8 flex items-center gap-3">
                <span className="material-symbols-outlined text-primary">local_gas_station</span>
                Request Fuel
              </h2>
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Fuel Type Selection */}
                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-widest text-outline mb-2">Fuel Type</label>
                    <div className="grid grid-cols-2 gap-3">
                      <button 
                        type="button"
                        onClick={() => setSelectedFuel('Petrol')}
                        className={`p-4 rounded-lg flex flex-col items-center gap-2 transition-all border-2 ${selectedFuel === 'Petrol' ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant/30 text-on-surface-variant hover:border-primary/50'}`}
                      >
                        <span className="material-symbols-outlined" style={{ fontVariationSettings: selectedFuel === 'Petrol' ? "'FILL' 1" : "'FILL' 0" }}>oil_barrel</span>
                        <span className="font-bold text-sm">Petrol</span>
                      </button>
                      <button 
                        type="button"
                        onClick={() => setSelectedFuel('Diesel')}
                        className={`p-4 rounded-lg flex flex-col items-center gap-2 transition-all border-2 ${selectedFuel === 'Diesel' ? 'border-primary bg-primary/5 text-primary' : 'border-outline-variant/30 text-on-surface-variant hover:border-primary/50'}`}
                      >
                        <span className="material-symbols-outlined" style={{ fontVariationSettings: selectedFuel === 'Diesel' ? "'FILL' 1" : "'FILL' 0" }}>propane_tank</span>
                        <span className="font-bold text-sm">Diesel</span>
                      </button>
                    </div>
                  </div>
                  {/* Quantity */}
                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-widest text-outline mb-2">Quantity (Liters)</label>
                    <div className="relative">
                      <input 
                        type="number" 
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        className="w-full bg-surface-container-low border-none rounded-lg p-4 font-bold text-lg focus:ring-2 focus:ring-primary transition-all" 
                        placeholder="20" 
                      />
                      <span className="absolute right-4 top-1/2 -translate-y-1/2 text-outline font-bold">LTR</span>
                    </div>
                  </div>
                </div>
                {/* Location */}
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-widest text-outline mb-2">Current Location</label>
                  <div className="relative group">
                    <input 
                      type="text" 
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="w-full bg-surface-container-low border-none rounded-lg p-4 pr-12 font-medium focus:ring-2 focus:ring-primary transition-all" 
                      placeholder="Enter address or pinpoint on map" 
                    />
                    <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-primary group-hover:scale-110 transition-transform">my_location</span>
                  </div>
                  <div className="mt-4 h-48 rounded-xl overflow-hidden relative">
                    <img className="w-full h-full object-cover brightness-90" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDCfDYQVg4SzVuF6OXXubuUVeKUYVQB0JHPYVmXt3-mHF-1au_HUvseYvNx-0rfitkWMKugRbfJ6VzBYYnBia2NZNZsbEMgofvHgCqTV5n5hX1Hz_Pb2rhDxQjUnaF9iBEZ302qSeTAfJCwZOOZLIyowc1UcrCciQc5Oj6zf9FodZ3oesBO7EME-IQhDOiDIwLck4ftpR-jY_vvO1rb9hZqZiJtoC7jh6JCG4qffTHOKNYmm_XWJZATzvszNi-yDHsGPz6H16UDN6ky" alt="Map" />
                    <div className="absolute inset-0 bg-primary/10 flex items-center justify-center">
                      <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-white shadow-xl animate-pulse">
                        <span className="material-symbols-outlined">location_on</span>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Submit */}
                <div className="pt-4">
                  <button 
                    type="button"
                    onClick={handleCreateRequest}
                    disabled={loading}
                    className="w-full bg-gradient-to-br from-primary to-primary-container text-on-primary py-5 rounded-xl font-bold text-lg shadow-lg hover:shadow-primary/25 transition-all active:scale-95 disabled:opacity-50"
                  >
                    {loading ? 'Processing...' : 'Create Fuel Request'}
                  </button>
                </div>
              </form>
            </div>

            {/* Live Status Tracking Card */}
            {activeRequest && (
              <div className="bg-surface-container-high/50 p-8 rounded-xl border border-primary/10">
                <div className="flex justify-between items-start mb-8">
                  <div>
                    <h3 className="text-xl font-headline font-bold">Delivery in Progress</h3>
                    <p className="text-sm text-on-surface-variant font-medium mt-1">Request ID: #{activeRequest.id}</p>
                  </div>
                  <span className="bg-secondary/10 text-secondary px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider">{activeRequest.status.replace('_', ' ')}</span>
                </div>
                
                <div className="relative py-10">
                  <div className="absolute top-[48px] left-0 w-full h-1 bg-outline-variant/30 rounded-full"></div>
                  <div 
                    className="absolute top-[48px] left-0 h-1 bg-primary rounded-full shadow-[0_0_8px_rgba(77,65,223,0.5)] transition-all duration-1000"
                    style={{ width: `${getStatusProgress(activeRequest.status)}%` }}
                  ></div>
                  <div className="relative flex justify-between">
                    <div className="flex flex-col items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ring-4 ring-surface-container-low ${['PENDING', 'ASSIGNED', 'EN_ROUTE', 'COMPLETED'].indexOf(activeRequest.status) >= 0 ? 'bg-primary text-white' : 'bg-surface-container-highest text-outline'}`}>
                        <span className="material-symbols-outlined text-sm">check</span>
                      </div>
                      <span className="text-[10px] font-bold uppercase text-outline">Received</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ring-4 ring-surface-container-low ${['ASSIGNED', 'EN_ROUTE', 'COMPLETED'].indexOf(activeRequest.status) >= 0 ? 'bg-primary text-white' : 'bg-surface-container-highest text-outline'}`}>
                        <span className="material-symbols-outlined text-sm">person</span>
                      </div>
                      <span className="text-[10px] font-bold uppercase text-outline">Assigned</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ring-4 ring-surface-container-low ${['EN_ROUTE', 'COMPLETED'].indexOf(activeRequest.status) >= 0 ? 'bg-primary text-white animate-bounce' : 'bg-surface-container-highest text-outline'}`}>
                        <span className="material-symbols-outlined text-sm">local_shipping</span>
                      </div>
                      <span className="text-[10px] font-bold uppercase text-outline">En Route</span>
                    </div>
                    <div className="flex flex-col items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ring-4 ring-surface-container-low ${activeRequest.status === 'COMPLETED' ? 'bg-primary text-white' : 'bg-surface-container-highest text-outline'}`}>
                        <span className="material-symbols-outlined text-sm">done_all</span>
                      </div>
                      <span className="text-[10px] font-bold uppercase text-outline">Complete</span>
                    </div>
                  </div>
                </div>

                {activeRequest.agent && (
                  <div className="mt-4 flex items-center gap-4 bg-white p-4 rounded-xl">
                    <div className="w-12 h-12 rounded-lg overflow-hidden bg-surface-variant">
                      <img src={activeRequest.agent.avatar || "https://lh3.googleusercontent.com/aida-public/AB6AXuARWvUEZH7IsIZjjVLXY87Y6D5a_udnVbyGe0cC5_2n-7AYgAMVOAvs3E-y056LP6gONZzH7Pcjw1pc4D5LN82qxA_Woxpv3wr4dEnWkYpQH6Zmed_vujWLln5NKfunb5I0JQMEQgZPezXXebAru_hpWnAACGdhDGYmGANQ9VeRHHiOCinGJ1Wcp0Ok7OOjxafZTmtejjMsVApQ6xJ-eNojf0P-sgkRlOv_dwpRguNqYXXmHlPfflj9KFaX9b7SEkxBClPT1WRZGnWl"} alt="Agent" className="w-full h-full object-cover" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-sm">{activeRequest.agent.name}</h4>
                      <p className="text-xs text-outline">{activeRequest.agent.vehicle || 'White Ford Transit'} • {activeRequest.agent.plate || 'AB-9201'}</p>
                    </div>
                    <button className="bg-surface-container-low p-2 rounded-lg text-primary">
                      <span className="material-symbols-outlined">call</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Nearby Agents */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-surface-container-low p-6 rounded-xl">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-headline font-bold">Nearby Agents</h2>
                <span className="text-xs text-primary font-bold hover:underline cursor-pointer">View All</span>
              </div>
              <div className="space-y-4">
                {agents.length === 0 ? (
                  <p className="text-center py-4 text-on-surface-variant text-sm">No agents nearby at the moment.</p>
                ) : (
                  agents.map((agent, index) => (
                    <div key={index} className="bg-surface-container-lowest p-4 rounded-xl flex items-center gap-4 group hover:shadow-md transition-all cursor-pointer">
                      <div className="w-14 h-14 rounded-lg overflow-hidden bg-surface-variant relative">
                        <img src={agent.avatar || `https://i.pravatar.cc/150?u=${agent.id}`} alt={agent.name} className="w-full h-full object-cover" />
                        <div className={`absolute bottom-1 right-1 w-3 h-3 rounded-full border-2 border-white ${agent.status === 'AVAILABLE' ? 'bg-tertiary' : 'bg-error'}`}></div>
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between">
                          <h4 className="font-bold group-hover:text-primary transition-colors">{agent.name}</h4>
                          <div className="flex items-center gap-1 text-secondary">
                            <span className="material-symbols-outlined text-[14px]" style={{ fontVariationSettings: "'FILL' 1" }}>star</span>
                            <span className="text-xs font-bold">{agent.rating || '4.8'}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${agent.is_fastest ? 'text-tertiary bg-tertiary/10' : 'text-outline-variant bg-surface-container'}`}>
                            {agent.is_fastest ? 'Fastest' : 'Standard'}
                          </span>
                          <span className="text-xs text-outline font-medium">{agent.distance || '0.8'} miles away</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Info Card */}
            <div className="bg-primary p-8 rounded-xl text-on-primary relative overflow-hidden group">
              <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-700">
                <span className="material-symbols-outlined text-9xl">verified</span>
              </div>
              <h3 className="text-xl font-headline font-bold mb-4">The Expertease Guarantee</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary-fixed-dim">verified</span>
                  <p className="text-sm font-medium">All agents are certified precision mechanics and safety-trained.</p>
                </li>
                <li className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary-fixed-dim">speed</span>
                  <p className="text-sm font-medium">Ultra-low response times with AI-optimized routing.</p>
                </li>
                <li className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-primary-fixed-dim">shield</span>
                  <p className="text-sm font-medium">Transparent pricing and spill-free delivery protocols.</p>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* BottomNavBar */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-2 bg-[#f8f9ff]/90 backdrop-blur-lg border-t border-[#c7c4d8]/15 shadow-[0_-4px_12px_rgba(25,28,32,0.04)]">
        <button onClick={() => navigate('/car-service/home')} className="flex flex-col items-center justify-center text-slate-400">
          <span className="material-symbols-outlined">home</span>
          <span className="font-['Inter'] text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Home</span>
        </button>
        <button onClick={() => navigate('/car-service/my-bookings')} className="flex flex-col items-center justify-center bg-[#4d41df]/10 text-[#4d41df] rounded-xl px-4 py-1">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>car_repair</span>
          <span className="font-['Inter'] text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Bookings</span>
        </button>
        <button className="flex flex-col items-center justify-center text-slate-400">
          <span className="material-symbols-outlined">query_stats</span>
          <span className="font-['Inter'] text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Status</span>
        </button>
        <button className="flex flex-col items-center justify-center text-slate-400">
          <span className="material-symbols-outlined">menu</span>
          <span className="font-['Inter'] text-[10px] uppercase tracking-[0.05em] font-bold mt-1">Menu</span>
        </button>
      </nav>
    </div>
  );
};

export default FuelDelivery;
