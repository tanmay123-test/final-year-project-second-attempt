// Debug version to verify OTP colors are fixed
import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, MoreVertical, ArrowRight, Loader2, XCircle, Key, Copy } from 'lucide-react';
import HousekeepingNavigation from '../components/HousekeepingNavigation';
import api, { housekeepingService } from '../../../services/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { housekeepingSocket } from '../../../services/housekeepingSocket';

const UserBookingsDebug = () => {
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
      const mapped = data.map(b => ({
        id: b.id,
        service: b.service_type || 'Service',
        provider: b.worker_name || 'Assigned Provider',
        date: `${b.booking_date || b.date || ''}, ${b.time_slot || b.time || ''}`,
        status: b.status.toLowerCase(),
        price: b.price || 0,
        image: getServiceIcon(b.service_type),
        workerId: b.worker_id,
        address: b.address || '',
        otp: b.otp || null,
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
    
    const socket = housekeepingSocket;
    if (socket) {
      const handleBookingUpdate = (data) => {
        console.log('Booking update received:', data);
        fetchBookings();
      };
      
      socket.on('booking_update', handleBookingUpdate);
      return () => socket.off('booking_update', handleBookingUpdate);
    }
  }, []);

  const getServiceIcon = (serviceType) => {
    const icons = {
      'Deep Cleaning': '🧹',
      'Regular Cleaning': '🧽',
      'Kitchen Cleaning': '🍳',
      'Bathroom Cleaning': '🚿',
      'Window Cleaning': '🪟',
      'Laundry': '👕',
      'Dishwashing': '🍽️',
      'Organizing': '📦'
    };
    return icons[serviceType] || '🧹';
  };

  const getStatusColor = (status) => {
    // FIXED: No more green/yellow colors
    if (['completed'].includes(status)) return { bg: '#F3F4F6', text: '#374151' }; // Gray
    if (['cancelled', 'declined'].includes(status)) return { bg: '#FEF2F2', text: '#DC2626' }; // Red
    if (['accepted', 'in_progress'].includes(status)) return { bg: '#EFF6FF', text: '#2563EB' }; // Blue
    if (['assigned'].includes(status)) return { bg: '#F3E5F5', text: '#8E44AD' }; // Purple
    return { bg: '#F9FAFB', text: '#6B7280' }; // Light Gray
  };

  const filteredBookings = bookings.filter(b => {
    if (activeTab === 'upcoming') {
      return ['pending', 'requested', 'assigned', 'accepted', 'in_progress'].includes(b.status);
    } else {
      return ['completed', 'cancelled', 'declined'].includes(b.status);
    }
  });

  if (loading) return <div style={{ padding: '20px', textAlign: 'center', color: '#8E44AD' }}>Loading bookings...</div>;

  return (
    <div style={{ backgroundColor: '#F9FAFB', minHeight: '100vh', paddingBottom: '80px' }}>
      {/* Debug Header */}
      <div style={{ padding: '20px', backgroundColor: '#8E44AD', color: 'white' }}>
        <h1 style={{ margin: 0 }}>🔧 DEBUG VERSION - OTP Colors Fixed</h1>
        <p>Checking for remaining yellow/green colors...</p>
      </div>

      <div style={{ padding: '20px', backgroundColor: 'white', position: 'sticky', top: 0, zIndex: 10, borderBottom: '2px solid #F3E5F5' }}>
        <h1 style={{ margin: '0 0 20px 0', fontSize: '24px', fontWeight: 'bold', color: '#8E44AD' }}>My Bookings</h1>
        
        <div style={{ display: 'flex', backgroundColor: '#F3F4F6', borderRadius: '12px', padding: '4px' }}>
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
      </div>

      <div style={{ padding: '20px' }}>
        {filteredBookings.map(booking => {
          const colors = getStatusColor(booking.status);
          return (
            <div key={booking.id} style={{ 
              backgroundColor: 'white', 
              borderRadius: '16px', 
              padding: '20px', 
              marginBottom: '16px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
            }}>
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

              {/* PERFECT OTP DISPLAY - NO YELLOW/GREEN */}
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

      <HousekeepingNavigation />
    </div>
  );
};

export default UserBookingsDebug;
