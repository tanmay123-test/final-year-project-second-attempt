import React, { useState, useEffect } from 'react';
import { Search, Bell, MapPin, Star, Clock, X } from 'lucide-react';
import HousekeepingNavigation from '../components/HousekeepingNavigation';
import { useNavigate } from 'react-router-dom';
import api from '../../../services/api';
import { useAuth } from '../../../context/AuthContext';

const UserHome = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [services, setServices] = useState([]);
  const [topCleaners, setTopCleaners] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState(null);
  
  // Debounce search query
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 500);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  // Icon mapping helper
  const getServiceStyle = (name) => {
    const styles = {
      'General Cleaning': { icon: '🏠', color: '#E8F5E9' },
      'Deep Cleaning': { icon: '✨', color: '#FFF8E1' },
      'Kitchen Cleaning': { icon: '🍳', color: '#FFF3E0' },
      'Bathroom Cleaning': { icon: '🚿', color: '#E3F2FD' },
      'Sofa Cleaning': { icon: '🛋️', color: '#F3E5F5' },
      'Pest Control': { icon: '🐛', color: '#FBE9E7' }
    };
    return styles[name] || { icon: '🧹', color: '#F5F5F5' };
  };

  useEffect(() => {
     const fetchServices = async () => {
       try {
         const params = {};
         if (debouncedSearchQuery) params.search = debouncedSearchQuery;
         if (selectedSpecialization) params.specialization = selectedSpecialization;

         const response = await api.get('/api/housekeeping/services', { params });
         const servicesData = response.data.services || response.data; // Handle wrapped or direct array
         if (Array.isArray(servicesData)) {
            const mappedServices = servicesData.map(s => ({
              ...s,
              ...getServiceStyle(s.name)
            }));
            setServices(mappedServices);
         }
         
         if (response.data.top_cleaners) {
            setTopCleaners(response.data.top_cleaners.map(c => ({
              id: c.id,
              name: c.name || c.full_name,
              role: c.role || c.specialization || 'Housekeeping Specialist',
              rating: c.rating || 4.8,
              exp: c.experience ? `${c.experience} yrs` : 'New',
              location: c.clinic_location || c.location || 'Bangalore',
              price: c.price || 500,
              color: '#8E44AD',
              is_online: c.is_online // Use backend status
            })));
         }
       } catch (error) {
        console.error('Failed to fetch services', error);
        // Fallback to mock if API fails
        setServices([
          { name: 'Full Home', icon: '🏠', color: '#E8F5E9' },
          { name: 'Kitchen', icon: '🍳', color: '#FFF3E0' },
          { name: 'Bathroom', icon: '🚿', color: '#E3F2FD' },
          { name: 'Sofa', icon: '🛋️', color: '#F3E5F5' },
          { name: 'Pest Control', icon: '🐛', color: '#FBE9E7' },
          { name: 'Mini', icon: '✨', color: '#FFF8E1' },
        ]);
      }
    };

    fetchServices();
    // Poll for real-time updates every 15 seconds
    const interval = setInterval(fetchServices, 15000);
    return () => clearInterval(interval);
  }, [debouncedSearchQuery, selectedSpecialization]);

  // Filter Logic (Handled by Backend for cleaners, Client-side for services)
  const filteredServices = services.filter(service => 
    searchQuery === '' || service.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredCleaners = topCleaners; // Already filtered by backend

  const handleSpecializationClick = (specName) => {
    if (selectedSpecialization === specName) {
      setSelectedSpecialization(null); // Deselect
    } else {
      setSelectedSpecialization(specName); // Select
    }
  };

  return (
    <div className="hk-page-container" style={{ backgroundColor: '#F9FAFB', minHeight: '100vh', paddingBottom: '80px' }}>
      {/* Header Section */}
      <div style={{ backgroundColor: '#8E44AD', padding: '20px 20px 40px 20px', borderBottomLeftRadius: '24px', borderBottomRightRadius: '24px', color: 'white' }}>
        <div className="breadcrumbs" style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.85rem', marginBottom: '16px' }}>
          <span onClick={() => navigate('/services')} style={{ cursor: 'pointer' }}>Services</span> <span style={{ margin: '0 4px' }}>&gt;</span> <span style={{ color: 'white', fontWeight: '500' }}>Housekeeping</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <p style={{ margin: 0, opacity: 0.9, fontSize: '14px' }}>Welcome back 👋</p>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>{user?.username || 'Guest'}</h1>
          </div>
          <div style={{ position: 'relative' }}>
            <Bell size={24} />
            <span style={{ position: 'absolute', top: -2, right: -2, width: '8px', height: '8px', backgroundColor: '#FF5252', borderRadius: '50%' }}></span>
          </div>
        </div>

        {/* Search Bar - refreshed pill style */}
        <div style={{ backgroundColor: 'white', padding: '12px 16px', borderRadius: '999px', display: 'flex', alignItems: 'center', gap: '10px', boxShadow: '0 6px 20px rgba(0,0,0,0.08)' }}>
          <Search size={20} color="#8E44AD" />
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for cleaners, services, or locations..." 
            style={{ background: 'transparent', border: 'none', color: '#1F2937', width: '100%', outline: 'none' }}
          />
          {searchQuery && (
            <X 
              size={20} 
              color="#6B7280" 
              style={{ cursor: 'pointer' }} 
              onClick={() => setSearchQuery('')}
            />
          )}
        </div>
      </div>

      <div style={{ padding: '0 20px', marginTop: '-30px' }}>
        
        {/* Specializations */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>Specializations</h2>
            {selectedSpecialization && (
              <span 
                style={{ fontSize: '12px', color: '#8E44AD', fontWeight: '500', cursor: 'pointer' }}
                onClick={() => setSelectedSpecialization(null)}
              >
                Clear Filter
              </span>
            )}
          </div>
          <div style={{ display: 'flex', gap: '20px', overflowX: 'auto', paddingBottom: '8px', scrollbarWidth: 'none' }}>
            {filteredServices.map((spec, index) => {
              const isSelected = selectedSpecialization === spec.name;
              return (
                <div 
                  key={index} 
                  onClick={() => handleSpecializationClick(spec.name)}
                  style={{ 
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    minWidth: '200px',
                    padding: '18px',
                    background: 'white',
                    borderRadius: '24px',
                    boxShadow: '0 12px 30px rgba(0,0,0,0.06)',
                    cursor: 'pointer', 
                    position: 'relative',
                    opacity: selectedSpecialization && !isSelected ? 0.5 : 1,
                    transform: isSelected ? 'scale(1.05)' : 'scale(1)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{
                    width: '40px',
                    height: '40px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '26px',
                    marginBottom: '10px'
                  }}>
                    {spec.icon}
                  </div>
                  <span style={{ 
                    fontSize: '14px',
                    color: isSelected ? '#8E44AD' : '#111827',
                    fontWeight: 600,
                    textAlign: 'center'
                  }}>
                    {spec.name}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Top Cleaners */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>
              {selectedSpecialization ? `${selectedSpecialization} Specialists` : 'Top Cleaners'}
            </h2>
            <span style={{ fontSize: '12px', color: '#8E44AD', fontWeight: '500' }}>See All</span>
          </div>
          
          {filteredCleaners.length > 0 ? (
            filteredCleaners.map(cleaner => (
              <div key={cleaner.id} style={{ backgroundColor: 'white', borderRadius: '16px', padding: '16px', marginBottom: '16px', border: '1px solid #EEF2F7', boxShadow: '0 6px 18px rgba(0,0,0,0.06)' }}>
                <div style={{ display: 'flex', gap: '16px', marginBottom: '12px', alignItems: 'center' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '12px', backgroundColor: cleaner.color, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '18px', fontWeight: 'bold', position: 'relative' }}>
                    {cleaner.name.charAt(0)}
                    {cleaner.is_online && (
                      <span style={{ position: 'absolute', bottom: -2, right: -2, width: '10px', height: '10px', backgroundColor: '#2ECC71', border: '2px solid white', borderRadius: '50%' }} title="Online"></span>
                    )}
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#1F2937' }}>{cleaner.name}</h3>
                    <p style={{ margin: '4px 0 6px 0', fontSize: '12px', color: '#6B7280' }}>{cleaner.role}</p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: '#6B7280' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Star size={12} fill="#F59E0B" color="#F59E0B" />
                        <span style={{ color: '#1F2937', fontWeight: 600 }}>{cleaner.rating}</span>
                        <span style={{ color: '#9CA3AF' }}>·</span>
                        <span>45 reviews</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Clock size={12} />
                        <span>{cleaner.exp}</span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px', fontSize: '12px', color: '#6B7280' }}>
                      <MapPin size={12} />
                      <span>{cleaner.location}</span>
                    </div>
                  </div>
                </div>
                <div style={{ borderTop: '1px solid #F3F4F6', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '16px', fontWeight: 700, color: '#8E44AD' }}>₹{cleaner.price}<span style={{ fontSize: '12px', color: '#9CA3AF', fontWeight: 'normal' }}> / visit</span></span>
                  <button 
                    onClick={() => navigate('/housekeeping/booking/create', { state: { worker: cleaner } })}
                    style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)', color: 'white', border: 'none', padding: '10px 18px', borderRadius: '999px', fontSize: '14px', fontWeight: 700, boxShadow: '0 8px 16px rgba(142, 68, 173, 0.25)' }}
                  >
                    Book Now
                  </button>
                </div>
              </div>
            ))
          ) : (
             <div style={{ textAlign: 'center', padding: '40px 0', color: '#6B7280' }}>
               <Search size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
               <p>No professionals found matching your criteria.</p>
               <button 
                 onClick={() => {setSearchQuery(''); setSelectedSpecialization(null);}}
                 style={{ marginTop: '12px', background: 'none', border: 'none', color: '#8E44AD', fontWeight: '600', cursor: 'pointer' }}
               >
                 Clear Filters
               </button>
             </div>
          )}
        </div>
      </div>
      <HousekeepingNavigation />
    </div>
  );
};

export default UserHome;
