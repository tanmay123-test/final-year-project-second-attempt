import React, { useState, useEffect, useMemo } from 'react';
import {
  Fuel,
  MapPin,
  Calendar,
  Download,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { fuelDeliveryService } from '../../shared/api';

const FuelDeliveryHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all'); // 'all' | 'completed' | 'cancelled'

  useEffect(() => {
    fetchHistory();
  }, []);

  useEffect(() => {
    const interval = setInterval(fetchHistory, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fuelDeliveryService.getUserFuelDeliveryBookings();
      if (!response.ok) {
        setHistory([]);
        setLoading(false);
        return;
      }
      const data = response.data;
      if (data.success && Array.isArray(data.bookings)) {
        setHistory(data.bookings);
      } else {
        setHistory([]);
      }
    } catch (err) {
      console.error('Failed to fetch fuel delivery history:', err);
      setHistory([]);
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
    const completed = history.filter((d) => (d.status || '').toLowerCase() === 'completed');
    completed.forEach((d) => {
      const earn = Number(d.earnings) || Number(d.estimated_earnings) || Number(d.total_cost) || 0;
      const dateStr = d.completed_at || d.created_at || d.booking_date;
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
  }, [history]);

  const filteredHistory = useMemo(() => {
    if (filterStatus === 'all') return history;
    if (filterStatus === 'completed') return history.filter((d) => (d.status || '').toLowerCase() === 'completed');
    if (filterStatus === 'cancelled') return history.filter((d) => (d.status || '').toLowerCase() === 'cancelled');
    return history;
  }, [history, filterStatus]);

  const formatDate = (dateString) => {
    if (!dateString) return '—';
    const d = new Date(dateString);
    return d.toISOString().slice(0, 10);
  };

  const formatQuantity = (liters) => {
    const n = Number(liters);
    if (isNaN(n)) return '—';
    return `${n.toLocaleString('en-IN')} L`;
  };

  const formatRupee = (amount) => {
    const n = Number(amount);
    if (isNaN(n)) return '0';
    return n.toLocaleString('en-IN', { maximumFractionDigits: 0, minimumFractionDigits: 0 });
  };

  const handleExport = () => {
    const rows = [
      ['Station / Worker', 'Location', 'Date', 'Fuel Type', 'Quantity', 'Total Cost', 'Status'],
      ...filteredHistory.map((d) => [
        d.worker_name || d.station_name || `Worker #${d.worker_id || d.id}`,
        d.delivery_address || d.address || '—',
        formatDate(d.completed_at || d.created_at || d.booking_date),
        d.fuel_type || '—',
        formatQuantity(d.quantity_liters || d.quantity),
        formatRupee(d.earnings || d.estimated_earnings || d.total_cost),
        (d.status || '').toLowerCase(),
      ]),
    ];
    const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `fuel-delivery-bookings-${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const getStatusDisplay = (status) => {
    const s = (status || '').toLowerCase();
    if (s === 'completed') return 'Completed';
    if (s === 'cancelled') return 'Cancelled';
    return s || '—';
  };

  if (loading) {
    return (
      <div className="history-screen history-loading">
        <div className="history-loading-spinner" />
        <p className="history-loading-text">Loading delivery history...</p>
      </div>
    );
  }

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
          border-top-color: #f97316;
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
        .history-logo svg { color: #f97316; flex-shrink: 0; }
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

        .history-filters {
          padding: 0 20px 16px;
          display: flex;
          gap: 10px;
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
        }
        .history-filter-btn.active {
          background: #f97316;
          color: #fff;
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
        }
        .history-card-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 8px;
        }
        .history-card-station {
          font-weight: 700;
          font-size: 16px;
          color: #111827;
        }
        .history-card-earnings {
          font-size: 16px;
          font-weight: 700;
          color: #f97316;
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
          background: #dcfce7;
          color: #166534;
        }
        .history-card-status.cancelled { background: #fee2e2; color: #991b1b; }
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
      `}</style>

      {/* Header */}
      <header className="history-header">
        <div className="history-header-left">
          <div className="history-logo">
            <Fuel size={24} />
            <span>FuelFleet</span>
          </div>
          <div>
            <h1 className="history-title">My Fuel Delivery Bookings</h1>
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
          Completed
        </button>
        <button
          type="button"
          className={`history-filter-btn ${filterStatus === 'cancelled' ? 'active' : ''}`}
          onClick={() => setFilterStatus('cancelled')}
        >
          Cancelled
        </button>
      </div>

      {/* Delivery history list */}
      <div className="history-list">
        {filteredHistory.length === 0 ? (
          <div className="history-empty">No delivery history to show.</div>
        ) : (
          filteredHistory.map((booking) => (
            <div key={booking.id || booking.booking_id || Math.random()} className="history-card">
              <div className="history-card-top">
                <div className="history-card-station">
                  {booking.worker_name || booking.station_name || `Worker #${booking.worker_id || booking.id}`}
                </div>
                <div className="history-card-earnings">
                  ₹{formatRupee(booking.earnings || booking.estimated_earnings || booking.total_cost)}
                </div>
              </div>
              {(booking.delivery_address || booking.address) && (
                <div className="history-card-location">
                  <MapPin size={14} />
                  {booking.delivery_address || booking.address}
                </div>
              )}
              <div className={`history-card-status ${(booking.status || '').toLowerCase() === 'cancelled' ? 'cancelled' : ''}`}>
                {getStatusDisplay(booking.status)}
              </div>
              <div className="history-card-details">
                <span>
                  <Calendar size={14} />
                  {formatDate(booking.completed_at || booking.created_at || booking.booking_date)}
                </span>
                <span>
                  <Fuel size={14} />
                  {booking.fuel_type || '—'}
                </span>
                <span>{formatQuantity(booking.quantity_liters || booking.quantity)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FuelDeliveryHistory;
