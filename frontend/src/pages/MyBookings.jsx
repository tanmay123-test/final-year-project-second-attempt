import React, { useState, useEffect, useMemo } from 'react';
import {
  Fuel,
  MapPin,
  Calendar,
  Download,
  Wrench,
  Truck,
  Clock,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../shared/api';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all'); // 'all' | 'completed' | 'cancelled' | 'pending'
  const [filterService, setFilterService] = useState('all'); // 'all' | 'mechanic' | 'tow' | 'fuel'

  useEffect(() => {
    console.log('MyBookings component mounted');
    fetchAllBookings();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchAllBookings, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAllBookings = async () => {
    try {
      console.log('Fetching all bookings...');
      const [mechanicRes, towRes, fuelRes] = await Promise.allSettled([
        api.getUserAppointments().catch(err => {
          console.error('Mechanic API error:', err);
          return { data: { success: false, appointments: [] } };
        }),
        api.getUserTowBookings().catch(err => {
          console.error('Tow API error:', err);
          return { data: { success: false, bookings: [] } };
        }),
        api.getUserFuelDeliveryBookings().catch(err => {
          console.error('Fuel API error:', err);
          return { data: { success: false, bookings: [] } };
        })
      ]);

      console.log('API responses:', { mechanicRes, towRes, fuelRes });

      const allBookings = [];
      
      // Add mechanic bookings
      if (mechanicRes.status === 'fulfilled' && mechanicRes.value?.data?.success) {
        mechanicRes.value.data.appointments.forEach(apt => {
          allBookings.push({
            ...apt,
            service_type: 'mechanic',
            worker_name: apt.doctor_name || apt.worker_name,
            status: apt.status || 'pending',
            created_at: apt.appointment_date || apt.created_at,
            earnings: apt.estimated_cost || 0,
            quantity: '1 service',
            fuel_type: 'Mechanic Service',
            delivery_address: apt.clinic_address || apt.address,
            booking_id: apt.id
          });
        });
      }

      // Add tow truck bookings
      if (towRes.status === 'fulfilled' && towRes.value?.data?.success) {
        towRes.value.data.bookings.forEach(booking => {
          allBookings.push({
            ...booking,
            service_type: 'tow',
            worker_name: booking.worker_name || booking.driver_name,
            status: booking.status || 'pending',
            created_at: booking.created_at || booking.booking_date,
            earnings: booking.estimated_cost || 0,
            quantity: '1 service',
            fuel_type: 'Tow Service',
            delivery_address: booking.pickup_address || booking.address,
            booking_id: booking.id
          });
        });
      }

      // Add fuel delivery bookings
      if (fuelRes.status === 'fulfilled' && fuelRes.value?.data?.success) {
        fuelRes.value.data.bookings.forEach(booking => {
          allBookings.push({
            ...booking,
            service_type: 'fuel',
            worker_name: booking.worker_name || booking.station_name,
            status: booking.status || 'pending',
            created_at: booking.created_at || booking.booking_date,
            earnings: booking.earnings || booking.estimated_earnings || booking.total_cost || 0,
            quantity: booking.quantity_liters || booking.quantity || 0,
            fuel_type: booking.fuel_type || 'Not specified',
            delivery_address: booking.delivery_address || booking.address,
            booking_id: booking.id
          });
        });
      }

      // Sort by date (newest first)
      allBookings.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      console.log('Final bookings:', allBookings);
      setBookings(allBookings);

    } catch (err) {
      console.error('Failed to fetch bookings:', err);
      setBookings([]);
    } finally {
      setLoading(false);
    }
  };

  // Earnings by period from real history (completed only)
  const earningsByPeriod = useMemo(() => {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekStart = new Date(todayStart);
    weekStart.setDate(weekStart.getDate() - 7);
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    let today = 0, week = 0, month = 0, all = 0;
    const completed = bookings.filter((d) => (d.status || '').toLowerCase() === 'completed');
    completed.forEach((d) => {
      const earn = Number(d.earnings) || Number(d.estimated_cost) || 0;
      const dateStr = d.completed_at || d.created_at;
      if (!dateStr) {
        all += earn;
        return;
      }
      const dDate = new Date(dateStr);
      all += earn;
      if (dDate >= monthStart) month += earn;
      if (dDate >= weekStart) week += earn;
      if (dDate >= todayStart) today += earn;
    });

    return { today, week, month, all };
  }, [bookings]);

  const filteredBookings = useMemo(() => {
    let filtered = bookings;
    
    // Filter by service type
    if (filterService !== 'all') {
      filtered = filtered.filter((d) => d.service_type === filterService);
    }
    
    // Filter by status
    if (filterStatus === 'all') return filtered;
    if (filterStatus === 'completed') return filtered.filter((d) => (d.status || '').toLowerCase() === 'completed');
    if (filterStatus === 'cancelled') return filtered.filter((d) => (d.status || '').toLowerCase() === 'cancelled');
    if (filterStatus === 'pending') return filtered.filter((d) => (d.status || '').toLowerCase() === 'pending');
    return filtered;
  }, [bookings, filterStatus, filterService]);

  const formatDate = (dateString) => {
    if (!dateString) return '—';
    const d = new Date(dateString);
    return d.toISOString().slice(0, 10);
  };

  const formatQuantity = (quantity) => {
    if (typeof quantity === 'string' && quantity.includes('service')) {
      return quantity;
    }
    const n = Number(quantity);
    if (isNaN(n)) return '—';
    return `${n.toLocaleString('en-IN')} L`;
  };

  const formatRupee = (amount) => {
    const n = Number(amount);
    if (isNaN(n)) return '0';
    return n.toLocaleString('en-IN', { maximumFractionDigits: 0, minimumFractionDigits: 0 });
  };

  const getServiceIcon = (serviceType) => {
    switch (serviceType) {
      case 'mechanic': return <Wrench size={14} />;
      case 'tow': return <Truck size={14} />;
      case 'fuel': return <Fuel size={14} />;
      default: return <Clock size={14} />;
    }
  };

  const getServiceColor = (serviceType) => {
    switch (serviceType) {
      case 'mechanic': return '#3b82f6';
      case 'tow': return '#059669';
      case 'fuel': return '#f97316';
      default: return '#6b7280';
    }
  };

  const handleExport = () => {
    const rows = [
      ['Service Type', 'Worker Name', 'Location', 'Date', 'Details', 'Cost', 'Status'],
      ...filteredBookings.map((d) => [
        d.service_type || '—',
        d.worker_name || '—',
        d.delivery_address || '—',
        formatDate(d.created_at),
        `${d.fuel_type || d.quantity || '—'}`,
        formatRupee(d.earnings || d.estimated_cost || 0),
        (d.status || '').toLowerCase(),
      ]),
    ];
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `all-bookings-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const getStatusDisplay = (status) => {
    const s = (status || '').toLowerCase();
    if (s === 'completed') return 'Completed';
    if (s === 'cancelled') return 'Cancelled';
    if (s === 'pending') return 'Pending';
    return s || '—';
  };

  const getStatusColor = (status) => {
    const s = (status || '').toLowerCase();
    if (s === 'completed') return '#16a34a';
    if (s === 'cancelled') return '#dc2626';
    if (s === 'pending') return '#f59e0b';
    return '#6b7280';
  };

  if (loading) {
    return (
      <div className="history-screen history-loading">
        <div className="history-loading-spinner" />
        <p className="history-loading-text">Loading all bookings...</p>
      </div>
    );
  }

  // Test render
  console.log('MyBookings render - loading:', loading, 'bookings count:', bookings.length);

  return (
    <div className="history-screen">
      <style>{`
        .history-screen {
          min-height: 100vh;
          background: #f8f9fa;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 88px;
        }
        .history-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px;
        }
        .history-loading-spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #f0f0f0;
          border-top-color: #3b82f6;
          border-radius: 50%;
          animation: historySpin 0.8s linear infinite;
        }
        .history-loading-text { margin-top: 16px; color: #6b7280; font-size: 14px; }
        @keyframes historySpin { to { transform: rotate(360deg); } }

        .history-header {
          background: #fff;
          padding: 16px 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          box-shadow: 0 1px 3px rgba(0,0,0,0.06);
          position: sticky;
          top: 0;
          z-index: 10;
        }
        .history-header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .history-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #374151;
          font-weight: 700;
          font-size: 18px;
        }
        .history-logo svg { color: #3b82f6; flex-shrink: 0; }
        .history-title {
          font-size: 22px;
          font-weight: 700;
          color: #111827;
          margin: 4px 0 0 0;
        }
        .history-export-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          background: #fff;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          color: #374151;
          cursor: pointer;
        }
        .history-export-btn:hover { background: #f9fafb; border-color: #d1d5db; }

        .history-filters {
          padding: 16px 20px;
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
          align-items: center;
        }
        .history-filter-group {
          display: flex;
          gap: 8px;
          align-items: center;
        }
        .history-filter-label {
          font-size: 12px;
          font-weight: 500;
          color: #6b7280;
        }
        .history-filter-btn {
          padding: 8px 18px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          border: none;
          cursor: pointer;
          background: #e5e7eb;
          color: #4b5563;
          transition: all 0.2s;
        }
        .history-filter-btn:hover {
          background: #f3f4f6;
        }
        .history-filter-btn.active {
          background: #3b82f6;
          color: #fff;
          border-color: #3b82f6;
        }

        .history-earnings {
          padding: 20px 20px 16px;
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 12px;
        }
        .history-earnings-card {
          background: #f3f4f6;
          border-radius: 12px;
          padding: 14px 12px;
          text-align: left;
        }
        .history-earnings-amount {
          font-size: 18px;
          font-weight: 700;
          color: #111827;
        }
        .history-earnings-label {
          font-size: 12px;
          color: #6b7280;
          margin-top: 4px;
          font-weight: 500;
        }

        .history-list {
          padding: 0 20px 24px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .history-card {
          background: #fff;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.06);
          border: 1px solid #f3f4f6;
          transition: all 0.2s;
        }
        .history-card:hover {
          box-shadow: 0 4px 15px rgba(0,0,0,0.1);
          transform: translateY(-2px);
        }
        .history-card-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 8px;
        }
        .history-card-service {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 700;
          font-size: 16px;
          color: #111827;
        }
        .history-card-service svg {
          flex-shrink: 0;
        }
        .history-card-worker {
          font-size: 14px;
          color: #6b7280;
          margin-top: 2px;
        }
        .history-card-earnings {
          font-size: 16px;
          font-weight: 700;
          color: #16a34a;
        }
        .history-card-location {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: #6b7280;
          margin-bottom: 10px;
        }
        .history-card-location svg { flex-shrink: 0; color: #9ca3af; }
        .history-card-status {
          display: inline-block;
          padding: 4px 10px;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 10px;
          color: white;
        }
        .history-card-details {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 12px 16px;
          font-size: 13px;
          color: #6b7280;
        }
        .history-card-details span { display: inline-flex; align-items: center; gap: 4px; }
        .history-card-details svg { flex-shrink: 0; color: #9ca3af; }

        .history-empty {
          text-align: center;
          padding: 48px 24px;
          color: #6b7280;
          font-size: 15px;
        }

        @media (max-width: 768px) {
          .history-earnings {
            grid-template-columns: repeat(2, 1fr);
          }
          .history-filters {
            flex-direction: column;
            align-items: stretch;
          }
          .history-filter-group {
            justify-content: space-between;
          }
        }
      `}</style>

      {/* Header */}
      <header className="history-header">
        <div className="history-header-left">
          <div className="history-logo">
            <Calendar size={24} />
            <span>My Bookings</span>
          </div>
          <div>
            <h1 className="history-title">All Service Bookings</h1>
          </div>
        </div>
        <button type="button" className="history-export-btn" onClick={handleExport}>
          <Download size={18} />
          Export
        </button>
      </header>

      {/* Earnings summary */}
      <div className="history-earnings">
        <div className="history-earnings-card">
          <div className="history-earnings-amount">₹{formatRupee(earningsByPeriod.today)}</div>
          <div className="history-earnings-label">TODAY</div>
        </div>
        <div className="history-earnings-card">
          <div className="history-earnings-amount">₹{formatRupee(earningsByPeriod.week)}</div>
          <div className="history-earnings-label">THIS WEEK</div>
        </div>
        <div className="history-earnings-card">
          <div className="history-earnings-amount">₹{formatRupee(earningsByPeriod.month)}</div>
          <div className="history-earnings-label">THIS MONTH</div>
        </div>
        <div className="history-earnings-card">
          <div className="history-earnings-amount">₹{formatRupee(earningsByPeriod.all)}</div>
          <div className="history-earnings-label">ALL TIME</div>
        </div>
      </div>

      {/* Filters */}
      <div className="history-filters">
        <div className="history-filter-group">
          <span className="history-filter-label">Service:</span>
          <button
            type="button"
            className={`history-filter-btn ${filterService === 'all' ? 'active' : ''}`}
            onClick={() => setFilterService('all')}
          >
            All
          </button>
          <button
            type="button"
            className={`history-filter-btn ${filterService === 'mechanic' ? 'active' : ''}`}
            onClick={() => setFilterService('mechanic')}
          >
            <Wrench size={14} style={{ marginRight: '4px' }} />
            Mechanic
          </button>
          <button
            type="button"
            className={`history-filter-btn ${filterService === 'tow' ? 'active' : ''}`}
            onClick={() => setFilterService('tow')}
          >
            <Truck size={14} style={{ marginRight: '4px' }} />
            Tow
          </button>
          <button
            type="button"
            className={`history-filter-btn ${filterService === 'fuel' ? 'active' : ''}`}
            onClick={() => setFilterService('fuel')}
          >
            <Fuel size={14} style={{ marginRight: '4px' }} />
            Fuel
          </button>
        </div>
        <div className="history-filter-group">
          <span className="history-filter-label">Status:</span>
          <button
            type="button"
            className={`history-filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
            onClick={() => setFilterStatus('all')}
          >
            All
          </button>
          <button
            type="button"
            className={`history-filter-btn ${filterStatus === 'completed' ? 'active' : ''}`}
            onClick={() => setFilterStatus('completed')}
          >
            <CheckCircle2 size={14} style={{ marginRight: '4px' }} />
            Completed
          </button>
          <button
            type="button"
            className={`history-filter-btn ${filterStatus === 'cancelled' ? 'active' : ''}`}
            onClick={() => setFilterStatus('cancelled')}
          >
            <AlertCircle size={14} style={{ marginRight: '4px' }} />
            Cancelled
          </button>
          <button
            type="button"
            className={`history-filter-btn ${filterStatus === 'pending' ? 'active' : ''}`}
            onClick={() => setFilterStatus('pending')}
          >
            <Clock size={14} style={{ marginRight: '4px' }} />
            Pending
          </button>
        </div>
      </div>

      {/* Bookings list */}
      <div className="history-list">
        {filteredBookings.length === 0 ? (
          <div className="history-empty">No bookings to show.</div>
        ) : (
          filteredBookings.map((booking) => (
            <div key={booking.booking_id || booking.id || Math.random()} className="history-card">
              <div className="history-card-top">
                <div className="history-card-service" style={{ color: getServiceColor(booking.service_type) }}>
                  {getServiceIcon(booking.service_type)}
                  <span>{booking.service_type.charAt(0).toUpperCase() + booking.service_type.slice(1)} Service</span>
                </div>
                <div className="history-card-earnings">
                  ₹{formatRupee(booking.earnings || booking.estimated_cost || 0)}
                </div>
              </div>
              <div className="history-card-worker">
                {booking.worker_name || 'Worker not assigned'}
              </div>
              {(booking.delivery_address || booking.address) && (
                <div className="history-card-location">
                  <MapPin size={14} />
                  {booking.delivery_address || booking.address}
                </div>
              )}
              <div 
                className="history-card-status" 
                style={{ 
                  backgroundColor: getStatusColor(booking.status),
                  color: 'white'
                }}
              >
                {getStatusDisplay(booking.status)}
              </div>
              <div className="history-card-details">
                <span>
                  <Calendar size={14} />
                  {formatDate(booking.created_at)}
                </span>
                <span>
                  {getServiceIcon(booking.service_type)}
                  {booking.fuel_type || booking.quantity || '—'}
                </span>
                <span>{formatQuantity(booking.quantity)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MyBookings;
