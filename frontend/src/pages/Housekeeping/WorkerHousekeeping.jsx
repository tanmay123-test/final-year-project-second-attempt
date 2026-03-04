import React, { useState, useEffect } from 'react';
import { housekeepingService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import HousekeepingBottomNav from '../../components/HousekeepingBottomNav';
import { CheckCircle, Clock, MapPin, XCircle, Play, DollarSign, Home, Plus, Zap, Calendar } from 'lucide-react';
import './Housekeeping.css';

const WorkerHousekeeping = () => {
  const { worker } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [balance, setBalance] = useState(0.0);

  useEffect(() => {
    fetchBookings();
    fetchStatus();
    fetchBalance();

    // Poll for new bookings every 10 seconds
    const interval = setInterval(() => {
      fetchBookings();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await housekeepingService.getWorkerStatus();
      setIsOnline(res.data.is_online);
    } catch (err) {
      console.error("Failed to load status", err);
    }
  };

  const fetchBalance = async () => {
    try {
      const res = await housekeepingService.getWorkerBalance();
      setBalance(res.data.balance);
    } catch (err) {
      console.error("Failed to load balance", err);
    }
  };

  const toggleStatus = async () => {
    try {
      const newStatus = !isOnline;
      await housekeepingService.setWorkerStatus(newStatus);
      setIsOnline(newStatus);
    } catch (err) {
      alert("Failed to update status");
    }
  };

  const fetchBookings = async () => {
    try {
      console.log("Fetching worker bookings...");
      const res = await housekeepingService.getUserBookings(); // Same endpoint, backend differentiates by role
      console.log("Worker bookings fetched:", res.data.bookings);
      setBookings(res.data.bookings);
    } catch (err) {
      console.error("Failed to load bookings", err);
      setError("Failed to load bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (bookingId, newStatus) => {
    try {
      await housekeepingService.updateBookingStatus({
        booking_id: bookingId,
        status: newStatus
      });
      fetchBookings(); // Refresh list
      if (newStatus === 'COMPLETED') {
        fetchBalance(); // Refresh balance
      }
    } catch (err) {
      alert("Failed to update status: " + (err.response?.data?.error || err.message));
    }
  };

  if (loading) return <div className="housekeeping-container">Loading...</div>;

  return (
    <div className="housekeeping-container" style={{paddingBottom: '80px'}}>
      <div className="hk-header">
        <div>
          <h1>My Jobs</h1>
          <p>Manage your housekeeping assignments</p>
        </div>
        <div className="header-actions">
            <div className="wallet-badge">
                <DollarSign size={16} />
                <span>${balance.toFixed(2)}</span>
            </div>
            <div className="status-toggle">
              <label className="switch">
                <input type="checkbox" checked={isOnline} onChange={toggleStatus} />
                <span className="slider round"></span>
              </label>
              <span className="status-label">{isOnline ? 'Online' : 'Offline'}</span>
            </div>
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="bookings-list">
        {bookings.length === 0 ? (
          <div className="empty-state">No jobs assigned yet.</div>
        ) : (
          bookings.map(booking => {
            const addOns = booking.add_ons ? JSON.parse(booking.add_ons) : [];
            const isRequest = ['ASSIGNED', 'REQUESTED'].includes(booking.status);
            
            return (
              <div key={booking.id} className={`booking-card status-${booking.status.toLowerCase()}`}>
                <div className="booking-header">
                  <span className="booking-id">#{booking.id}</span>
                  <div style={{display: 'flex', gap: '0.5rem', alignItems: 'center'}}>
                    {booking.booking_type === 'instant' ? (
                      <span className="badge badge-instant"><Zap size={12}/> Instant</span>
                    ) : (
                      <span className="badge badge-schedule"><Calendar size={12}/> Scheduled</span>
                    )}
                    <span className={`status-badge ${booking.status.toLowerCase()}`}>{booking.status}</span>
                  </div>
                </div>
                
                <div className="booking-details">
                  <div className="detail-row">
                    <span className="label">Service:</span>
                    <span className="value">{booking.service_type}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label"><MapPin size={14}/> Address:</span>
                    <span className="value">{booking.address}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label"><Clock size={14}/> Schedule:</span>
                    <span className="value">{booking.booking_date} @ {booking.time_slot}</span>
                  </div>
                  {booking.home_size && (
                    <div className="detail-row">
                      <span className="label"><Home size={14}/> Size:</span>
                      <span className="value">{booking.home_size}</span>
                    </div>
                  )}
                  {addOns.length > 0 && (
                    <div className="detail-row">
                      <span className="label"><Plus size={14}/> Add-ons:</span>
                      <span className="value">{addOns.join(', ')}</span>
                    </div>
                  )}
                  <div className="detail-row">
                    <span className="label"><DollarSign size={14}/> Earnings:</span>
                    <span className="value">${booking.price}</span>
                  </div>
                </div>

                <div className="booking-actions">
                  {isRequest && (
                    <>
                      <button 
                        className="action-btn start-btn"
                        onClick={() => handleStatusUpdate(booking.id, 'ACCEPTED')}
                      >
                        <CheckCircle size={16}/> Accept Job
                      </button>
                      <button 
                        className="action-btn secondary-btn"
                        style={{backgroundColor: '#e74c3c', marginLeft: '0.5rem'}}
                        onClick={() => handleStatusUpdate(booking.id, 'DECLINED')}
                      >
                        <XCircle size={16}/> Decline
                      </button>
                    </>
                  )}

                  {booking.status === 'ACCEPTED' && (
                    <button 
                      className="action-btn start-btn"
                      onClick={() => handleStatusUpdate(booking.id, 'IN_PROGRESS')}
                    >
                      <Play size={16}/> Start Job
                    </button>
                  )}
                  
                  {booking.status === 'IN_PROGRESS' && (
                    <button 
                      className="action-btn complete-btn"
                      onClick={() => handleStatusUpdate(booking.id, 'COMPLETED')}
                    >
                      <CheckCircle size={16}/> Complete Job
                    </button>
                  )}

                  {booking.status === 'PENDING' && (
                     /* This shouldn't happen if auto-assigned, but just in case */
                     <span className="pending-msg">Awaiting Acceptance</span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default WorkerHousekeeping;
