import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Wrench, Settings, Bell, LogOut, ChevronLeft, User, Clock, CheckCircle, DollarSign, Star, Fuel, Battery, Zap, Shield } from 'lucide-react';

const MechanicDashboard = () => {
  const navigate = useNavigate();
  
  const workerData = {
    name: 'Mechanic',
    email: 'mechanic@example.com'
  };
  
  const stats = {
    activeJobs: 3,
    completedJobs: 47,
    earnings: 12580,
    rating: 4.8
  };

  const services = [
    { id: 1, name: 'General Repair', icon: Wrench, price: '₹500-2000', duration: '1-3 hours', color: '#3B82F6' },
    { id: 2, name: 'Engine Diagnosis', icon: Settings, price: '₹800-3000', duration: '2-4 hours', color: '#EF4444' },
    { id: 3, name: 'Battery Service', icon: Battery, price: '₹300-1500', duration: '30 min - 2 hours', color: '#10B981' },
    { id: 4, name: 'Fuel System', icon: Fuel, price: '₹600-2500', duration: '1-3 hours', color: '#F59E0B' },
    { id: 5, name: 'Electrical Systems', icon: Zap, price: '₹400-2000', duration: '1-2 hours', color: '#8B5CF6' },
    { id: 6, name: 'Brake Service', icon: Shield, price: '₹800-3000', duration: '1-3 hours', color: '#EC4899' }
  ];

  const handleLogout = () => {
    localStorage.clear();
    navigate('/worker/car/login');
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Header */}
      <div style={{ backgroundColor: 'white', padding: '16px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => navigate('/worker/car/homepage')}
              style={{ padding: '8px', border: 'none', borderRadius: '6px', backgroundColor: '#f3f4f6', cursor: 'pointer' }}
            >
              <ChevronLeft size={20} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', backgroundColor: '#3b82f6', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Wrench size={20} color="white" />
              </div>
              <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0, color: '#1f2937' }}>Mechanic Dashboard</h1>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button style={{ padding: '8px', border: 'none', borderRadius: '6px', backgroundColor: '#f3f4f6', cursor: 'pointer' }}>
              <Bell size={20} />
            </button>
            <button style={{ padding: '8px', border: 'none', borderRadius: '6px', backgroundColor: '#f3f4f6', cursor: 'pointer' }}>
              <Settings size={20} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingLeft: '16px', borderLeft: '1px solid #e5e7eb' }}>
              <div style={{ width: '40px', height: '40px', backgroundColor: '#e5e7eb', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <User size={20} />
              </div>
              <div>
                <p style={{ fontSize: '14px', fontWeight: '600', margin: 0, color: '#1f2937' }}>
                  {workerData.name}
                </p>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  {workerData.email}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              style={{ padding: '8px', border: 'none', borderRadius: '6px', backgroundColor: '#fef2f2', cursor: 'pointer', color: '#dc2626' }}
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
        {/* Welcome Section */}
        <div style={{ marginBottom: '32px' }}>
          <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#1f2937' }}>
            Welcome back, {workerData.name}!
          </h2>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>
            Manage your repair services and track your performance
          </p>
        </div>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '40px' }}>
          <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '56px', height: '56px', backgroundColor: '#dbeafe', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '20px' }}>
                <Clock size={28} color="#3b82f6" />
              </div>
              <div>
                <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#1f2937' }}>{stats.activeJobs}</p>
                <p style={{ color: '#6b7280', margin: 0 }}>Active Jobs</p>
              </div>
            </div>
          </div>

          <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '56px', height: '56px', backgroundColor: '#d1fae5', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '20px' }}>
                <CheckCircle size={28} color="#10b981" />
              </div>
              <div>
                <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#1f2937' }}>{stats.completedJobs}</p>
                <p style={{ color: '#6b7280', margin: 0 }}>Completed</p>
              </div>
            </div>
          </div>

          <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '56px', height: '56px', backgroundColor: '#fef3c7', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '20px' }}>
                <DollarSign size={28} color="#f59e0b" />
              </div>
              <div>
                <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#1f2937' }}>₹{stats.earnings}</p>
                <p style={{ color: '#6b7280', margin: 0 }}>Earnings</p>
              </div>
            </div>
          </div>

          <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ width: '56px', height: '56px', backgroundColor: '#e9d5ff', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '20px' }}>
                <Star size={28} color="#8b5cf6" />
              </div>
              <div>
                <p style={{ fontSize: '28px', fontWeight: 'bold', margin: 0, color: '#1f2937' }}>⭐ {stats.rating}</p>
                <p style={{ color: '#6b7280', margin: 0 }}>Rating</p>
              </div>
            </div>
          </div>
        </div>

        {/* Services Section */}
        <div>
          <h3 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#1f2937' }}>Your Services</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            {services.map((service) => {
              const Icon = service.icon;
              return (
                <div key={service.id} style={{ backgroundColor: 'white', padding: '28px', borderRadius: '16px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', transition: 'transform 0.2s', cursor: 'pointer' }}>
                  <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '20px' }}>
                    <div style={{ width: '56px', height: '56px', backgroundColor: service.color + '20', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={28} style={{ color: service.color }} />
                    </div>
                    <span style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937', backgroundColor: service.color + '10', padding: '6px 12px', borderRadius: '8px' }}>
                      {service.price}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '12px', color: '#1f2937', margin: '0 0 12px 0' }}>
                    {service.name}
                  </h3>
                  <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: '1.5', marginBottom: '16px', margin: '0 0 16px 0' }}>
                    Professional {service.name.toLowerCase()} with quality parts and expert service
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ color: '#6b7280', fontSize: '14px', display: 'flex', alignItems: 'center' }}>
                      <Clock size={16} style={{ marginRight: '6px' }} />
                      {service.duration}
                    </span>
                    <button style={{ color: service.color, backgroundColor: 'transparent', border: `1px solid ${service.color}`, padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', fontSize: '14px' }}>
                      View Details
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MechanicDashboard;
