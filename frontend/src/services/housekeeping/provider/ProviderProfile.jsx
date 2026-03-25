import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Phone, Mail, MapPin, DollarSign, LogOut } from 'lucide-react';
import api, { housekeepingService } from '../../../shared/api';
import { useAuth } from '../../../context/AuthContext';

const ProviderProfile = () => {
  const navigate = useNavigate();
  const { worker, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isServiceEnabled, setIsServiceEnabled] = useState(true);
  const [serviceConfigs, setServiceConfigs] = useState([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Mock fetch profile or use auth context
    setProfile({
        name: worker?.name || 'Ravi Kumar',
        phone: worker?.phone || '+91 98765 43210',
        email: worker?.email || 'ravi@expertease.com',
        status: 'Active',
        totalEarnings: '45,600',
        rating: 4.8,
        jobs: 234,
        specializations: ['Deep Cleaning', 'Kitchen', 'Bathroom']
    });
    const loadServices = async () => {
      try {
        const [allRes, myRes] = await Promise.all([
          housekeepingService.getServices(),
          housekeepingService.getWorkerServices()
        ]);
        const all = (allRes.data.services || []).map(s => ({
          id: s.id,
          name: s.name,
          description: s.description,
          price: s.price,
          active: false
        }));
        const mine = (myRes.data.services || []);
        const map = new Map(all.map(s => [s.id, s]));
        mine.forEach(ms => {
          const base = map.get(ms.id);
          if (base) {
            base.price = ms.price;
            base.active = !!ms.active;
          } else {
            map.set(ms.id, { id: ms.id, name: ms.name, description: ms.description, price: ms.price, active: !!ms.active });
          }
        });
        setServiceConfigs(Array.from(map.values()));
      } catch (e) {
      } finally {
        setLoading(false);
      }
    };
    loadServices();
  }, [worker]);

  const toggleService = (id) => {
    setServiceConfigs(prev => prev.map(s => s.id === id ? { ...s, active: !s.active } : s));
  };

  const changePrice = (id, value) => {
    const v = value.replace(/[^0-9.]/g, '');
    setServiceConfigs(prev => prev.map(s => s.id === id ? { ...s, price: v } : s));
  };

  const saveServices = async () => {
    setSaving(true);
    try {
      const payload = serviceConfigs
        .filter(s => s.active)
        .map(s => ({ service_id: s.id, price: parseFloat(s.price || 0), active: 1 }));
      await housekeepingService.saveWorkerServices(payload);
      alert('Services saved');
    } catch (e) {
      alert('Failed to save services');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/worker/login');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ backgroundColor: '#F9FAFB', minHeight: '100vh', paddingBottom: '80px' }}>
      {/* Header with Gradient */}
      <div style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)', padding: '40px 20px', borderBottomLeftRadius: '32px', borderBottomRightRadius: '32px', color: 'white', textAlign: 'center', marginBottom: '20px' }}>
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.2)', margin: '0 auto 16px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px', fontWeight: 'bold' }}>
          {profile.name.charAt(0)}
        </div>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: 'bold' }}>{profile.name}</h1>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', opacity: 0.9 }}>
          <span style={{ fontSize: '14px' }}>★ {profile.rating} • {profile.jobs} jobs</span>
        </div>
      </div>

      <div style={{ padding: '0 20px' }}>
        {/* Service Toggle Card */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '20px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>Housekeeping Service</h3>
            <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Enable to receive housekeeping jobs</p>
          </div>
          <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '48px', height: '24px' }}>
            <input 
              type="checkbox" 
              checked={isServiceEnabled} 
              onChange={() => setIsServiceEnabled(!isServiceEnabled)}
              style={{ opacity: 0, width: 0, height: 0 }}
            />
            <span style={{ 
              position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, 
              backgroundColor: isServiceEnabled ? '#8E44AD' : '#ccc', 
              transition: '.4s', borderRadius: '24px' 
            }}>
              <span style={{ 
                position: 'absolute', content: '""', height: '18px', width: '18px', left: isServiceEnabled ? '26px' : '3px', bottom: '3px', 
                backgroundColor: 'white', transition: '.4s', borderRadius: '50%' 
              }} />
            </span>
          </label>
        </div>

        {/* Service Pricing Entry */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '20px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>Service Pricing</h3>
          <p style={{ margin: '0 0 16px 0', fontSize: '12px', color: '#6B7280' }}>Configure per-size and custom area pricing</p>
          <button 
            onClick={() => navigate('/worker/housekeeping/pricing')}
            style={{ padding: '12px 16px', background: '#8E44AD', color: 'white', border: 'none', borderRadius: 8, fontWeight: 600, cursor: 'pointer', width: '100%' }}
          >
            Configure Pricing
          </button>
        </div>

        {/* Profile Details Card */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '20px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #F3F4F6', paddingBottom: '16px' }}>
            <span style={{ color: '#6B7280', fontSize: '14px' }}>Phone</span>
            <span style={{ fontWeight: '500', color: '#1F2937' }}>{profile.phone}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #F3F4F6', paddingBottom: '16px' }}>
            <span style={{ color: '#6B7280', fontSize: '14px' }}>Email</span>
            <span style={{ fontWeight: '500', color: '#1F2937' }}>{profile.email}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid #F3F4F6', paddingBottom: '16px' }}>
            <span style={{ color: '#6B7280', fontSize: '14px' }}>Status</span>
            <span style={{ fontWeight: '500', color: '#8E44AD' }}>{profile.status}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#6B7280', fontSize: '14px' }}>Total Earnings</span>
            <span style={{ fontWeight: 'bold', color: '#1F2937' }}>₹{profile.totalEarnings}</span>
          </div>
        </div>

        {/* Specializations Card */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '20px', marginBottom: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>Specializations</h3>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {profile.specializations.map((spec, index) => (
              <span key={index} style={{ backgroundColor: '#E0F2F1', color: '#00695C', padding: '6px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: '500' }}>
                {spec}
              </span>
            ))}
          </div>
        </div>

        {/* Sign Out Button */}
        <button 
          onClick={handleLogout}
          style={{ width: '100%', padding: '16px', backgroundColor: 'white', border: '1px solid #EF4444', color: '#EF4444', borderRadius: '12px', fontSize: '16px', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', cursor: 'pointer' }}
        >
          <LogOut size={20} />
          Sign Out
        </button>
      </div>

    </div>
  );
};

export default ProviderProfile;
