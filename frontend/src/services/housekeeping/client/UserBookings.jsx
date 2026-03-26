import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, MoreVertical, ArrowRight, Loader2, XCircle, Key, Copy, Home, Bot, User, Bell } from 'lucide-react';
import HousekeepingNavigation from '../components/HousekeepingNavigation';
import api, { housekeepingService } from '../../../services/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { housekeepingSocket } from '../../../services/housekeepingSocket';

const UserBookings = () => {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('upcoming');
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailsBooking, setDetailsBooking] = useState(null);
  const [copiedOTP, setCopiedOTP] = useState(null);

  const copyToClipboard = (text, bookingId) => {
    navigator.clipboard.writeText(text);
    setCopiedOTP(bookingId);
    setTimeout(() => setCopiedOTP(null), 2000);
  };

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  const fetchBookings = async () => {
    try {
      const response = await housekeepingService.getUserBookings();
      const data = response.data.bookings || [];
      // Map backend fields to frontend display fields if necessary
      const mapped = data.map(b => ({
        id: b.id,
        service: b.service_type || 'Service',
        provider: b.worker_name || 'Assigned Provider',
        date: `${b.booking_date || b.date || ''}, ${b.time_slot || b.time || ''}`,
        status: b.status.toLowerCase(), // Ensure lowercase for filtering
        price: b.price || 0,
        image: getServiceIcon(b.service_type),
        workerId: b.worker_id,
        address: b.address || '',
        otp: b.otp || null, // Include OTP if available
        started_at: b.started_at || null
      }));
      setBookings(mapped);
    } catch (error) {
      console.error('Failed to fetch bookings', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
    
    // Connect to WebSocket
    const userId = user?.user_id || user?.id; // Support both just in case
    if (userId) {
        housekeepingSocket.joinRoom('user', userId);

        const handleBookingUpdate = (data) => {
             console.log("Booking update received via socket:", data);
             fetchBookings();
        };

        housekeepingSocket.on('booking_update', handleBookingUpdate);

        return () => {
            housekeepingSocket.off('booking_update', handleBookingUpdate);
            housekeepingSocket.leaveRoom('user', userId);
        };
    }
  }, [user]);

  const handleCancel = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) return;
    try {
        await housekeepingService.cancelBooking(id);
        fetchBookings();
    } catch (error) {
        console.error('Failed to cancel booking', error);
        const msg = error.response?.data?.error || 'Failed to cancel booking';
        alert(msg);
    }
  };

  const getServiceIcon = (type) => {
    const icons = {
      'General Cleaning': '🏠',
      'Deep Cleaning': '✨',
      'Kitchen Cleaning': '🍳',
      'Bathroom Cleaning': '🚿', 
      'Sofa Cleaning': '🛋️',
      'Pest Control': '🐛'
    };
    return icons[type] || '🧹';
  };

  const filteredBookings = bookings.filter(b => {
    if (activeTab === 'upcoming') {
      return ['pending', 'requested', 'assigned', 'accepted', 'in_progress'].includes(b.status);
    } else {
      return ['completed', 'cancelled', 'declined'].includes(b.status);
    }
  });

  const getStatusColor = (status) => {
    if (['completed'].includes(status)) return { bg: '#F3F4F6', text: '#374151' }; // Gray
    if (['cancelled', 'declined'].includes(status)) return { bg: '#FEF2F2', text: '#DC2626' }; // Red
    if (['accepted', 'in_progress'].includes(status)) return { bg: '#EFF6FF', text: '#2563EB' }; // Blue
    if (['assigned'].includes(status)) return { bg: '#F3E5F5', text: '#8E44AD' }; // Purple
    return { bg: '#F9FAFB', text: '#6B7280' }; // Light Gray (Default/Requested/Pending)
  };

  if (loading) return <div style={{ padding: '20px', textAlign: 'center', color: '#8E44AD' }}>Loading bookings...</div>;

  return (
    <div className="hk-page-container" style={{ backgroundColor: '#F9FAFB', minHeight: '100vh', paddingBottom: '80px' }}>
      <div style={{ backgroundColor: '#8E44AD', padding: '20px 20px 40px 20px', borderBottomLeftRadius: '24px', borderBottomRightRadius: '24px', color: 'white' }}>
        <div className="breadcrumbs" style={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.85rem', marginBottom: '16px' }}>
          <span onClick={() => navigate('/services')} style={{ cursor: 'pointer' }}>Services</span> <span style={{ margin: '0 4px' }}>&gt;</span> <span style={{ color: 'white', fontWeight: '500' }}>Housekeeping</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <p style={{ margin: 0, opacity: 0.9, fontSize: '14px' }}>Your Bookings</p>
            <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>My Bookings</h1>
          </div>
          <div style={{ position: 'relative' }}>
            <Bell size={24} />
            <span style={{ position: 'absolute', top: -2, right: -2, width: '8px', height: '8px', backgroundColor: '#FF5252', borderRadius: '50%' }}></span>
          </div>
        </div>
      </div>

      <div style={{ 
        backgroundColor: 'white', 
        margin: '0 20px', 
        borderRadius: '16px', 
        padding: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        marginBottom: '20px',
        marginTop: '-30px'
      }}>
        <div style={{ display: 'flex', gap: '4px' }}>
          <button
            onClick={() => navigate('/housekeeping/home')}
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: 'transparent',
              color: '#6B7280',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#F3F4F6';
              e.target.style.color = '#8E44AD';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = '#6B7280';
            }}
          >
            <Home size={18} />
            Home
          </button>
          <button
            onClick={() => navigate('/housekeeping/ai-chat')}
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: 'transparent',
              color: '#6B7280',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#F3F4F6';
              e.target.style.color = '#8E44AD';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = '#6B7280';
            }}
          >
            <Bot size={18} />
            AI Care
          </button>
          <button
            onClick={() => navigate('/housekeeping/bookings')}
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: '#8E44AD',
              color: 'white',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            <Calendar size={18} />
            Bookings
          </button>
          <button
            onClick={() => navigate('/housekeeping/profile')}
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: 'transparent',
              color: '#6B7280',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#F3F4F6';
              e.target.style.color = '#8E44AD';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = 'transparent';
              e.target.style.color = '#6B7280';
            }}
          >
            <User size={18} />
            Profile
          </button>
        </div>
      </div>

      <div style={{ padding: '0 20px' }}>
        <div style={{ display: 'flex', backgroundColor: '#F3F4F6', borderRadius: '12px', padding: '4px', marginBottom: '20px' }}>
          <button 
            onClick={() => setActiveTab('upcoming')}
            style={{ 
              flex: 1, 
              padding: '10px', 
              borderRadius: '8px', 
              border: 'none', 
              backgroundColor: activeTab === 'upcoming' ? '#8E44AD' : 'transparent', 
              color: activeTab === 'upcoming' ? 'white' : '#6B7280',
              fontWeight: '600',
              fontSize: '14px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: activeTab === 'upcoming' ? '0 2px 4px rgba(142, 68, 173, 0.2)' : 'none'
            }}
          >
            Active
          </button>
          <button 
            onClick={() => setActiveTab('past')}
            style={{ 
              flex: 1, 
              padding: '10px', 
              borderRadius: '8px', 
              border: 'none', 
              backgroundColor: activeTab === 'past' ? '#8E44AD' : 'transparent', 
              color: activeTab === 'past' ? 'white' : '#6B7280',
              fontWeight: '600',
              fontSize: '14px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: activeTab === 'past' ? '0 2px 4px rgba(142, 68, 173, 0.2)' : 'none'
            }}
          >
            Past
          </button>
        </div>

        <div style={{ padding: '20px' }}>
          {filteredBookings.map(booking => {
            const colors = getStatusColor(booking.status);
            return (
              <div key={booking.id} style={{ backgroundColor: 'white', borderRadius: '16px', padding: '16px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', border: '1px solid #F3F4F6' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <div style={{ width: '48px', height: '48px', backgroundColor: '#F3E5F5', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', color: '#8E44AD' }}>
                      {booking.image}
                    </div>
                    <div>
                      <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: '700', color: '#1F2937' }}>{booking.provider}</h3>
                      <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>{booking.service}</p>
                    </div>
                  </div>
                  <span style={{ 
                    padding: '4px 12px', 
                    borderRadius: '12px', 
                    fontSize: '10px', 
                    fontWeight: 'bold', 
                    height: 'fit-content',
                    backgroundColor: colors.bg,
                    color: colors.text
                  }}>
                    {booking.status.toUpperCase()}
                  </span>
                </div>
                
                <div style={{ borderTop: '1px solid #F3F4F6', borderBottom: '1px solid #F3F4F6', padding: '12px 0', margin: '12px 0', display: 'flex', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#4B5563' }}>
                    <Calendar size={14} color="#8E44AD" />
                    <span>{booking.date}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#4B5563' }}>
                    <span style={{ fontWeight: 'bold', color: '#8E44AD', fontSize: '14px' }}>₹{booking.price}</span>
                  </div>
                </div>

                {/* OTP Section for Active Jobs */}
                {booking.status === 'in_progress' && booking.otp && (
                  <div style={{ 
                    backgroundColor: '#F8FAFC', 
                    border: '1px solid #E2E8F0', 
                    borderRadius: '12px', 
                    padding: '16px', 
                    margin: '12px 0',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        backgroundColor: '#8E44AD',
                        borderRadius: '8px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Key size={16} color="white" />
                      </div>
                      <div>
                        <span style={{ fontWeight: '700', color: '#1F2937', fontSize: '14px', display: 'block' }}>
                          Job Completion OTP
                        </span>
                        <span style={{ fontWeight: '400', color: '#6B7280', fontSize: '12px' }}>
                          Share this code with your service provider
                        </span>
                      </div>
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between', 
                      backgroundColor: 'white', 
                      padding: '16px', 
                      borderRadius: '8px', 
                      border: '2px dashed #CBD5E1'
                    }}>
                      <span style={{ 
                        fontSize: '24px', 
                        fontWeight: '700', 
                        color: '#1F2937', 
                        letterSpacing: '3px',
                        fontFamily: 'monospace'
                      }}>
                        {booking.otp}
                      </span>
                      <button 
                        onClick={() => copyToClipboard(booking.otp, booking.id)}
                        style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '6px', 
                          backgroundColor: '#8E44AD', 
                          color: 'white', 
                          border: 'none', 
                          padding: '10px 16px', 
                          borderRadius: '8px', 
                          fontSize: '12px', 
                          fontWeight: '600', 
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#7B3F99'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#8E44AD'}
                      >
                        <Copy size={14} />
                        {copiedOTP === booking.id ? 'Copied!' : 'Copy OTP'}
                      </button>
                    </div>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <button 
                    onClick={() => setDetailsBooking(booking)}
                    style={{ color: '#8E44AD', background: 'none', border: 'none', fontSize: '14px', fontWeight: '600', cursor: 'pointer' }}
                  >
                    View Details
                  </button>
                  
                  {['pending', 'requested', 'assigned'].includes(booking.status) && (
                    <button 
                      onClick={() => handleCancel(booking.id)}
                      style={{ backgroundColor: '#FEE2E2', color: '#DC2626', border: 'none', padding: '8px 16px', borderRadius: '8px', fontSize: '12px', fontWeight: '600', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                    >
                      <XCircle size={14} /> Cancel
                    </button>
                  )}

                  {['completed', 'cancelled', 'declined'].includes(booking.status) && (
                    <button style={{ backgroundColor: '#8E44AD', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '8px', fontSize: '12px', fontWeight: '500', cursor: 'pointer' }}>Book Again</button>
                  )}
                </div>
              </div>
            );
          })}

          {filteredBookings.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#6B7280' }}>
              <p>No {activeTab} bookings found.</p>
            </div>
          )}
        </div>
      </div>

      <HousekeepingNavigation />
      
      {detailsBooking && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', borderRadius: 16, width: '90%', maxWidth: 520, padding: 20, boxShadow: '0 10px 30px rgba(0,0,0,0.15)' }}>
            <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#1F2937' }}>{detailsBooking.provider}</h3>
            <p style={{ margin: '4px 0 12px 0', color: '#6B7280', fontSize: 13 }}>{detailsBooking.service}</p>
            <div style={{ display: 'grid', gap: 8, fontSize: 13, color: '#4B5563' }}>
              <div><strong>Date & Time:</strong> {detailsBooking.date}</div>
              {detailsBooking.address && <div><strong>Address:</strong> {detailsBooking.address}</div>}
              <div><strong>Status:</strong> {detailsBooking.status.toUpperCase()}</div>
              <div><strong>Price:</strong> ₹{detailsBooking.price}</div>
              
              {/* OTP in Details Modal */}
              {detailsBooking.status === 'in_progress' && detailsBooking.otp && (
                <div style={{ 
                  backgroundColor: '#F8FAFC', 
                  border: '1px solid #E2E8F0', 
                  borderRadius: '12px', 
                  padding: '16px', 
                  marginTop: '12px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <div style={{
                      width: '28px',
                      height: '28px',
                      backgroundColor: '#8E44AD',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <Key size={14} color="white" />
                    </div>
                    <div>
                      <span style={{ fontWeight: '700', color: '#1F2937', fontSize: '13px', display: 'block' }}>
                        Job Completion OTP
                      </span>
                      <span style={{ fontWeight: '400', color: '#6B7280', fontSize: '11px' }}>
                        Share this code with your service provider
                      </span>
                    </div>
                  </div>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between', 
                    backgroundColor: 'white', 
                    padding: '12px', 
                    borderRadius: '6px', 
                    border: '2px dashed #CBD5E1'
                  }}>
                    <span style={{ 
                      fontSize: '20px', 
                      fontWeight: '700', 
                      color: '#1F2937', 
                      letterSpacing: '2px',
                      fontFamily: 'monospace'
                    }}>
                      {detailsBooking.otp}
                    </span>
                    <button 
                      onClick={() => copyToClipboard(detailsBooking.otp, detailsBooking.id)}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '4px', 
                        backgroundColor: '#8E44AD', 
                        color: 'white', 
                        border: 'none', 
                        padding: '8px 12px', 
                        borderRadius: '6px', 
                        fontSize: '11px', 
                        fontWeight: '600', 
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseOver={(e) => e.target.style.backgroundColor = '#7B3F99'}
                      onMouseOut={(e) => e.target.style.backgroundColor = '#8E44AD'}
                    >
                      <Copy size={12} />
                      {copiedOTP === detailsBooking.id ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                </div>
              )}
            </div>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 16 }}>
              <button 
                onClick={() => setDetailsBooking(null)}
                style={{ backgroundColor: '#E5E7EB', color: '#374151', border: 'none', padding: '8px 16px', borderRadius: 8, fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserBookings;
