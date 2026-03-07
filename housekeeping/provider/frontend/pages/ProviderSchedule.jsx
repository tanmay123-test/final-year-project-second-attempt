import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Clock, Check, X, Navigation, Play, Calendar } from 'lucide-react';
import api from '../../../../frontend/src/services/api';
import ProviderBottomNav from '../components/ProviderBottomNav';
import OtpModal from '../components/OtpModal';

const ProviderSchedule = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('requests'); // 'requests', 'upcoming', 'active', 'history'
  const [otpModal, setOtpModal] = useState({ isOpen: false, bookingId: null });

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await api.get('/api/housekeeping/my-bookings');
      const allJobs = response.data.bookings || [];
      setJobs(allJobs);

      // Auto-switch tab if current tab is empty but others have jobs (only on initial load or if user hasn't manually switched)
      // For now, we'll just prioritize 'active' then 'upcoming' if 'requests' is empty
      const hasRequests = allJobs.some(j => ['REQUESTED', 'ASSIGNED'].includes((j.status || '').toUpperCase()));
      const hasActive = allJobs.some(j => ['IN_PROGRESS'].includes((j.status || '').toUpperCase()));
      const hasUpcoming = allJobs.some(j => ['ACCEPTED'].includes((j.status || '').toUpperCase()));

      if (!hasRequests) {
          if (hasActive) setActiveTab('active');
          else if (hasUpcoming) setActiveTab('upcoming');
      }

    } catch (error) {
      console.error('Failed to fetch jobs', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id, action) => {
    try {
      let endpoint = '/api/housekeeping/worker/update-status';
      let payload = { booking_id: id };

      if (action === 'accept') payload.status = 'ACCEPTED';
      else if (action === 'decline') payload.status = 'DECLINED';
      
      await api.post(endpoint, payload);
      fetchJobs(); // Refresh
      if (action === 'accept') setActiveTab('upcoming');
    } catch (error) {
      console.error(`Failed to ${action} job`, error);
      alert(`Failed to ${action} job`);
    }
  };

  const handleStartJob = async (id) => {
    try {
      await api.post('/api/housekeeping/worker/start-job', { booking_id: id });
      setActiveTab('active');
      fetchJobs();
    } catch (error) {
      console.error('Failed to start job', error);
      alert('Failed to start job. Please try again.');
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
        setActiveTab('history');
        fetchJobs();
        alert('Job completed successfully! 🎉');
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Verification failed');
    }
  };

  const getFilteredJobs = () => {
    if (activeTab === 'requests') {
        return jobs.filter(j => ['REQUESTED', 'ASSIGNED'].includes((j.status || '').toUpperCase()));
    } else if (activeTab === 'upcoming') {
        return jobs.filter(j => ['ACCEPTED'].includes((j.status || '').toUpperCase()));
    } else if (activeTab === 'active') {
        return jobs.filter(j => ['IN_PROGRESS'].includes((j.status || '').toUpperCase()));
    } else if (activeTab === 'history') {
        return jobs.filter(j => ['COMPLETED', 'DECLINED', 'CANCELLED'].includes((j.status || '').toUpperCase()));
    }
    return jobs;
  };

  const filteredJobs = getFilteredJobs();

  const getStatusBadge = (status) => {
    const styles = {
      'ASSIGNED': { bg: '#F3E5F5', color: '#8E44AD', label: 'Pending' },
      'REQUESTED': { bg: '#F3E5F5', color: '#8E44AD', label: 'Requested' },
      'ACCEPTED': { bg: '#E3F2FD', color: '#1565C0', label: 'Accepted' },
      'IN_PROGRESS': { bg: '#FFF3E0', color: '#EF6C00', label: 'In Progress' },
      'COMPLETED': { bg: '#E8F5E9', color: '#2E7D32', label: 'Completed' },
      'DECLINED': { bg: '#FFEBEE', color: '#C62828', label: 'Declined' },
      'CANCELLED': { bg: '#FFEBEE', color: '#C62828', label: 'Cancelled' }
    };
    return styles[status] || { bg: '#F5F5F5', color: '#616161', label: status };
  };

  return (
    <div style={{ paddingBottom: '80px', backgroundColor: '#F9FAFB', minHeight: '100vh' }}>
      <div style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)', padding: '20px', paddingBottom: '60px', borderBottomLeftRadius: '24px', borderBottomRightRadius: '24px', color: 'white' }}>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>My Schedule</h1>
      </div>

      <div style={{ marginTop: '-40px', padding: '0 20px' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', backgroundColor: 'white', borderRadius: '12px', padding: '4px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', marginBottom: '20px', overflowX: 'auto' }}>
            {['requests', 'upcoming', 'active', 'history'].map(tab => (
                <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    style={{
                        flex: 1,
                        padding: '10px 4px',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: activeTab === tab ? '#8E44AD' : 'transparent',
                        color: activeTab === tab ? 'white' : '#6B7280',
                        fontWeight: '600',
                        fontSize: '13px',
                        cursor: 'pointer',
                        textTransform: 'capitalize',
                        transition: 'all 0.2s',
                        whiteSpace: 'nowrap',
                        minWidth: '70px'
                    }}
                >
                    {tab === 'active' ? 'Active' : tab === 'requests' ? 'New' : tab}
                </button>
            ))}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filteredJobs.length > 0 ? (
            filteredJobs.map(job => {
              const badge = getStatusBadge(job.status);
              return (
                <div key={job.id} style={{ backgroundColor: 'white', borderRadius: '16px', padding: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #E0E0E0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <div style={{ fontSize: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: badge.bg, width: '40px', height: '40px', borderRadius: '12px' }}>
                        {/* Dynamic Icon based on service could go here */}
                        {job.service_type && job.service_type.toLowerCase().includes('kitchen') ? '🍳' : 
                         job.service_type && job.service_type.toLowerCase().includes('bathroom') ? '🚿' : '🧹'}
                      </div>
                      <div>
                        <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '600', color: '#1F2937' }}>{job.service_type || job.service}</h3>
                        <div style={{ fontSize: '12px', color: '#6B7280', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Calendar size={12} />
                          {job.booking_date} • {job.time_slot}
                        </div>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <MapPin size={12} />
                          {job.address}
                        </div>
                      </div>
                    </div>
                    <span style={{ 
                      backgroundColor: badge.bg, 
                      color: badge.color, 
                      padding: '4px 12px', 
                      borderRadius: '12px', 
                      fontSize: '10px', 
                      fontWeight: 'bold', 
                      height: 'fit-content' 
                    }}>
                      {badge.label}
                    </span>
                  </div>

                  {/* Action Buttons */}
                  {['ASSIGNED', 'REQUESTED'].includes((job.status || '').toUpperCase()) && (
                    <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                      <button 
                        onClick={() => handleAction(job.id, 'accept')}
                        style={{ flex: 1, padding: '10px', backgroundColor: '#8E44AD', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                      >
                        <Check size={16} /> Accept
                      </button>
                      <button 
                        onClick={() => handleAction(job.id, 'decline')}
                        style={{ flex: 1, padding: '10px', backgroundColor: 'white', color: '#EF4444', border: '1px solid #E5E7EB', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                      >
                        <X size={16} /> Reject
                      </button>
                    </div>
                  )}

                  {(job.status || '').toUpperCase() === 'ACCEPTED' && (
                    <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                      <button 
                        onClick={() => handleStartJob(job.id)}
                        style={{ flex: 1, padding: '12px', backgroundColor: '#059669', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 2px 4px rgba(5, 150, 105, 0.2)' }}
                      >
                        <Play size={16} fill="currentColor" />
                        Start Job
                      </button>
                      <button 
                        style={{ padding: '12px', backgroundColor: 'white', color: '#8E44AD', border: '1px solid #8E44AD', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                      >
                        <Navigation size={20} />
                      </button>
                    </div>
                  )}

                  {(job.status || '').toUpperCase() === 'IN_PROGRESS' && (
                    <div style={{ marginTop: '16px' }}>
                        <div style={{ backgroundColor: '#FFF3E0', padding: '10px', borderRadius: '8px', marginBottom: '12px', fontSize: '12px', color: '#B45309', display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <Clock size={14} />
                            <span>Job started at {new Date(job.started_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                        </div>
                        <button 
                            onClick={() => handleCompleteClick(job.id)}
                            style={{ width: '100%', padding: '12px', backgroundColor: '#8E44AD', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', boxShadow: '0 2px 4px rgba(142, 68, 173, 0.3)' }}
                        >
                            <Check size={18} />
                            Complete Job
                        </button>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#9CA3AF' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>📅</div>
                <p>No {activeTab.replace('_', ' ')} jobs found.</p>
            </div>
          )}
        </div>
      </div>

      <ProviderBottomNav />

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

export default ProviderSchedule;
