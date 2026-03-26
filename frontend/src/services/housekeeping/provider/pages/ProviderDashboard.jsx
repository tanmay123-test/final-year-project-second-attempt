import React, { useState, useEffect } from 'react';
import { Clock, MapPin, Calendar, Check, X, DollarSign, Briefcase, TrendingUp, CalendarDays, RefreshCw, LogOut, AlertTriangle, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api, { housekeepingService } from '../../../../frontend/src/services/api';
import { useAuth } from '../../../../frontend/src/context/AuthContext';
import { housekeepingSocket } from '../../../../frontend/src/services/housekeepingSocket';
import OtpModal from '../components/OtpModal';

const ProviderDashboard = () => {
  const navigate = useNavigate();
  const { worker, logout } = useAuth();
  const [isOnline, setIsOnline] = useState(true);
  const [requests, setRequests] = useState([]);
  const [activeJobs, setActiveJobs] = useState([]);
  const [upcomingJobs, setUpcomingJobs] = useState([]);
  const [otpModal, setOtpModal] = useState({ isOpen: false, bookingId: null });
  const [debugInfo, setDebugInfo] = useState({
    workerId: null,
    bookingsCount: 0,
    filteredCount: 0,
    lastSocketEvent: null,
    error: null,
    fetchStatus: 'idle'
  });
  const [stats, setStats] = useState({ 
    earningsToday: 1200, 
    earningsWeek: 4500, 
    jobsToday: 1 
  });

  const handleLogout = () => {
      logout();
      navigate('/worker/login');
  };

  const manualRefresh = () => {
      fetchBookings();
      fetchStatus();
      alert("Refreshed data from server.");
  };

  useEffect(() => {
    fetchBookings();
    fetchStatus();
    
    // Connect to WebSocket
    const workerId = worker?.id || worker?.worker_id;
    setDebugInfo(prev => ({ ...prev, workerId }));

    if (workerId) {
        console.log(`🔌 Connecting socket for worker: ${workerId}`);
        housekeepingSocket.joinRoom('worker', workerId);

        const handleNewBooking = (data) => {
            console.log("New booking received via socket:", data);
            setDebugInfo(prev => ({ ...prev, lastSocketEvent: `New Booking: ${data?.booking_id || 'unknown'}` }));
            // Refresh bookings to ensure data consistency and formatting
            fetchBookings();
            // Show notification
            alert("New Booking Request Received! 🔔"); 
        };

        const handleBookingUpdate = (data) => {
             console.log("Booking update received via socket:", data);
             setDebugInfo(prev => ({ ...prev, lastSocketEvent: `Update: ${data?.booking_id} -> ${data?.status}` }));
             fetchBookings();
        };

        housekeepingSocket.on('new_booking', handleNewBooking);
        housekeepingSocket.on('booking_update', handleBookingUpdate);

        return () => {
            housekeepingSocket.off('new_booking', handleNewBooking);
            housekeepingSocket.off('booking_update', handleBookingUpdate);
            housekeepingSocket.leaveRoom('worker', workerId);
        };
    }
  }, [worker]);

  const fetchStatus = async () => {
      try {
          const response = await housekeepingService.getWorkerStatus();
          setIsOnline(response.data.is_online);
      } catch (error) {
          console.error('Failed to fetch status', error);
      }
  };

  const fetchBookings = async () => {
    try {
      setDebugInfo(prev => ({ ...prev, fetchStatus: 'loading' }));
      console.log("Fetching worker bookings...");
      const response = await housekeepingService.getUserBookings();
      console.log("Raw worker bookings:", response.data);
      const allBookings = response.data.bookings || [];
      
      // Filter requests (Assigned/Requested to me but not yet accepted)
      const pending = allBookings.filter(b => {
          const s = (b.status || '').toUpperCase();
          return s === 'ASSIGNED' || s === 'REQUESTED';
      });
      
      const upcoming = allBookings.filter(b => (b.status || '').toUpperCase() === 'ACCEPTED');
      const active = allBookings.filter(b => (b.status || '').toUpperCase() === 'IN_PROGRESS');

      console.log("Pending requests:", pending);
      
      setDebugInfo(prev => ({ 
        ...prev, 
        bookingsCount: allBookings.length, 
        filteredCount: pending.length,
        fetchStatus: 'success'
      }));

      const mapJob = (job) => {
          let image = '🧹';
          const serviceType = job.service_type || job.service || 'General Cleaning';
          
          if (serviceType && typeof serviceType === 'string') {
              const lower = serviceType.toLowerCase();
              if (lower.includes('kitchen')) image = '🍳';
              else if (lower.includes('bathroom')) image = '🚽';
              else if (lower.includes('sofa')) image = '🛋️';
              else if (lower.includes('deep')) image = '✨';
          }
          
          return {
              ...job,
              service: serviceType,
              image: image,
              date: job.booking_date || job.date,
              time: job.time_slot || job.time
          };
      };

      setRequests(pending.map(mapJob));
      setUpcomingJobs(upcoming.map(mapJob));
      setActiveJobs(active.map(mapJob));
      
      // Calculate stats (Mock logic for demo matching screenshot)
      // Real implementation would aggregate from transaction history
    } catch (error) {
      console.error('Failed to fetch bookings', error);
      setRequests([]); 
    }
  };

  const toggleOnline = async () => {
      const newState = !isOnline;
      setIsOnline(newState);
      try {
          await housekeepingService.setWorkerStatus(newState);
      } catch (error) {
          console.error('Failed to update status', error);
          setIsOnline(!newState); // Revert on error
      }
  };

  const [processingId, setProcessingId] = useState(null);

  const handleAction = async (id, action) => {
    if (processingId) return;
    setProcessingId(id);
    try {
        const status = action === 'accept' ? 'ACCEPTED' : 'DECLINED';
        await housekeepingService.updateBookingStatus({
            booking_id: id,
            status: status
        });
        
        // Refresh list
        fetchBookings();
        alert(`Request ${action}ed!`);
    } catch (error) {
        console.error(`Failed to ${action} request`, error);
        alert(`Failed to ${action} request`);
    } finally {
        setProcessingId(null);
    }
  };

  const handleStartJob = async (id) => {
    if (processingId) return;
    setProcessingId(id);
    try {
      await api.post('/api/housekeeping/worker/start-job', { booking_id: id });
      fetchBookings();
      alert('Job started! OTP sent to user.');
    } catch (error) {
      console.error('Failed to start job', error);
      alert('Failed to start job. Please try again.');
    } finally {
      setProcessingId(null);
    }
  };

  const handleCompleteClick = (id) => {
    setOtpModal({ isOpen: true, bookingId: id });
  };

  const handleOtpSubmit = async (bookingId, otp) => {
    try {
        await api.post('/api/housekeeping/worker/complete-job', { 
            booking_id: bookingId,
            otp: otp
        });
        setOtpModal({ isOpen: false, bookingId: null });
        fetchBookings();
        alert('Job completed successfully! 🎉');
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Verification failed');
    }
  };

  return (
    <div className="provider-dashboard" style={{ backgroundColor: '#F9FAFB', minHeight: '100vh' }}>
      {/* Header with Gradient */}
      <div style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)', padding: '20px', borderBottomLeftRadius: '24px', borderBottomRightRadius: '24px', color: 'white', marginBottom: '20px', position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Worker Dashboard</h1>
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                <button 
                  onClick={() => navigate('/worker/housekeeping/availability')}
                  style={{ 
                    background: 'rgba(255, 255, 255, 0.2)', 
                    border: 'none', 
                    borderRadius: '8px', 
                    padding: '6px 12px', 
                    color: 'white', 
                    fontSize: '13px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '6px', 
                    cursor: 'pointer' 
                  }}
                >
                  <CalendarDays size={14} />
                  Availability
                </button>
                <button 
                  onClick={manualRefresh}
                  style={{ 
                    background: 'rgba(255, 255, 255, 0.2)', 
                    border: 'none', 
                    borderRadius: '8px', 
                    padding: '6px 12px', 
                    color: 'white', 
                    fontSize: '13px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '6px', 
                    cursor: 'pointer' 
                  }}
                >
                  <RefreshCw size={14} />
                  Refresh
                </button>
                 <button 
                  onClick={handleLogout}
                  style={{ 
                    background: 'rgba(255, 255, 255, 0.2)', 
                    border: 'none', 
                    borderRadius: '8px', 
                    padding: '6px 12px', 
                    color: 'white', 
                    fontSize: '13px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '6px', 
                    cursor: 'pointer' 
                  }}
                >
                  <LogOut size={14} />
                  Logout
                </button>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', opacity: 0.9 }}>{isOnline ? 'Online' : 'Offline'}</span>
            <label className="switch" style={{ position: 'relative', display: 'inline-block', width: '48px', height: '24px' }}>
              <input 
                type="checkbox" 
                checked={isOnline} 
                onChange={toggleOnline}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{ 
                position: 'absolute', cursor: 'pointer', top: 0, left: 0, right: 0, bottom: 0, 
                backgroundColor: 'rgba(255,255,255,0.3)', 
                transition: '.4s', borderRadius: '24px' 
              }}>
                <span style={{ 
                  position: 'absolute', content: '""', height: '18px', width: '18px', left: isOnline ? '26px' : '4px', bottom: '3px', 
                  backgroundColor: 'white', transition: '.4s', borderRadius: '50%' 
                }} />
              </span>
            </label>
          </div>
        </div>

        {/* Stats Cards Row */}
        <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '8px' }}>
          <div style={{ flex: 1, minWidth: '100px', backgroundColor: 'white', borderRadius: '16px', padding: '16px', color: '#1F2937' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#F3E5F5', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px', color: '#8E44AD' }}>
              <DollarSign size={16} />
            </div>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>₹{stats.earningsToday}</div>
            <div style={{ fontSize: '12px', color: '#6B7280' }}>Today</div>
          </div>
          <div style={{ flex: 1, minWidth: '100px', backgroundColor: 'white', borderRadius: '16px', padding: '16px', color: '#1F2937' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#F3E5F5', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px', color: '#8E44AD' }}>
              <TrendingUp size={16} />
            </div>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>₹{stats.earningsWeek}</div>
            <div style={{ fontSize: '12px', color: '#6B7280' }}>This Week</div>
          </div>
          <div style={{ flex: 1, minWidth: '100px', backgroundColor: 'white', borderRadius: '16px', padding: '16px', color: '#1F2937' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#F3E5F5', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '8px', color: '#8E44AD' }}>
              <Briefcase size={16} />
            </div>
            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>{stats.jobsToday}</div>
            <div style={{ fontSize: '12px', color: '#6B7280' }}>Jobs Today</div>
          </div>
        </div>
      </div>

      <div style={{ padding: '0 20px' }}>
        {/* Debug Info Panel */}
        <div style={{ 
          backgroundColor: '#FFF3CD', 
          border: '1px solid #FFEEBA', 
          color: '#856404', 
          padding: '10px', 
          borderRadius: '8px', 
          marginBottom: '16px',
          fontSize: '12px',
          fontFamily: 'monospace'
        }}>
          <strong>🔧 Debug Info:</strong>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px', marginTop: '4px' }}>
            <div>Worker ID: {debugInfo.workerId || 'Not Found'}</div>
            <div>Fetch Status: {debugInfo.fetchStatus}</div>
            <div>Total Bookings: {debugInfo.bookingsCount}</div>
            <div>Pending Requests: {debugInfo.filteredCount}</div>
            <div style={{ gridColumn: '1 / -1' }}>Last Socket Event: {debugInfo.lastSocketEvent || 'None'}</div>
            {debugInfo.error && <div style={{ gridColumn: '1 / -1', color: 'red' }}>Error: {debugInfo.error}</div>}
            
            {(debugInfo.bookingsCount === 0) && (
                <div style={{ gridColumn: '1 / -1', marginTop: '8px', padding: '8px', backgroundColor: '#FEF3C7', color: '#B45309', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px' }}>
                    <AlertTriangle size={14} />
                    <span>If testing User & Worker simultaneously, use Incognito for Worker to avoid session conflicts.</span>
                </div>
            )}
          </div>
        </div>

        <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#1F2937' }}>New Requests</h3>
        
        {/* Active Jobs Section */}
        {activeJobs.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '12px', color: '#EF6C00' }}>Active Jobs (In Progress)</h3>
            {activeJobs.map(job => (
              <div key={job.id} style={{ backgroundColor: 'white', borderRadius: '16px', padding: '16px', border: '1px solid #EF6C00', boxShadow: '0 4px 12px rgba(239, 108, 0, 0.1)', marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{ fontSize: '24px' }}>{job.image}</div>
                    <div>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>{job.service}</h4>
                      <div style={{ fontSize: '12px', color: '#6B7280' }}>Started at {new Date(job.started_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                      <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>{job.address}</div>
                    </div>
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#8E44AD' }}>₹{job.price}</div>
                </div>
                <button 
                  onClick={() => handleCompleteClick(job.id)}
                  style={{ width: '100%', padding: '12px', backgroundColor: '#8E44AD', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 2px 4px rgba(142, 68, 173, 0.3)' }}
                >
                  <Check size={18} />
                  Complete Job
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Upcoming Jobs Section */}
        {upcomingJobs.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '12px', color: '#1565C0' }}>Upcoming Jobs</h3>
            {upcomingJobs.map(job => (
              <div key={job.id} style={{ backgroundColor: 'white', borderRadius: '16px', padding: '16px', border: '1px solid #E0E0E0', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{ fontSize: '24px' }}>{job.image}</div>
                    <div>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>{job.service}</h4>
                      <div style={{ fontSize: '12px', color: '#6B7280' }}>{job.date} • {job.time}</div>
                      <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>{job.address}</div>
                    </div>
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#8E44AD' }}>₹{job.price}</div>
                </div>
                <button 
                  onClick={() => handleStartJob(job.id)}
                  disabled={processingId === job.id}
                  style={{ width: '100%', padding: '12px', backgroundColor: '#059669', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 2px 4px rgba(5, 150, 105, 0.2)', opacity: processingId === job.id ? 0.7 : 1 }}
                >
                  <Play size={16} fill="currentColor" />
                  {processingId === job.id ? 'Starting...' : 'Start Job'}
                </button>
              </div>
            ))}
          </div>
        )}

        {requests.length > 0 ? (
          requests.map(req => (
            <div key={req.id} style={{ backgroundColor: 'white', borderRadius: '16px', padding: '16px', border: '1px solid #E0E0E0', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ fontSize: '24px' }}>{req.image || '🧹'}</div>
                  <div>
                    <h4 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>{req.service}</h4>
                    <div style={{ fontSize: '12px', color: '#6B7280' }}>{req.date} • {req.time}</div>
                    <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>{req.address}</div>
                  </div>
                </div>
                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#8E44AD' }}>₹{req.price}</div>
              </div>
              
              <div style={{ display: 'flex', gap: '12px' }}>
                <button 
                  onClick={() => handleAction(req.id, 'accept')}
                  disabled={processingId === req.id}
                  style={{ 
                      flex: 1, 
                      padding: '10px', 
                      backgroundColor: processingId === req.id ? '#D1D5DB' : '#8E44AD', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '8px', 
                      fontWeight: '600', 
                      cursor: processingId === req.id ? 'not-allowed' : 'pointer', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      gap: '8px',
                      opacity: processingId === req.id ? 0.7 : 1
                  }}
                >
                  <Check size={16} />
                  {processingId === req.id ? 'Processing...' : 'Accept'}
                </button>
                <button 
                  onClick={() => handleAction(req.id, 'decline')}
                  disabled={processingId === req.id}
                  style={{ 
                      flex: 1, 
                      padding: '10px', 
                      backgroundColor: 'white', 
                      color: '#1F2937', 
                      border: '1px solid #E5E7EB', 
                      borderRadius: '8px', 
                      fontWeight: '600', 
                      cursor: processingId === req.id ? 'not-allowed' : 'pointer', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center', 
                      gap: '8px',
                      opacity: processingId === req.id ? 0.7 : 1
                  }}
                >
                  <X size={16} />
                  Decline
                </button>
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#6B7280' }}>
            No new requests at the moment.
          </div>
        )}
      </div>

      {/* OTP Modal */}
      {otpModal.isOpen && (
        <OtpModal 
            isOpen={otpModal.isOpen}
            bookingId={otpModal.bookingId}
            onClose={() => setOtpModal({ isOpen: false, bookingId: null })}
            onSubmit={(id, otp) => handleOtpSubmit(id, otp)}
        />
      )}
    </div>
  );
};

export default ProviderDashboard;
