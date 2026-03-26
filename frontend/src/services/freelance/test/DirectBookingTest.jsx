import React, { useState, useEffect } from 'react';
import api from '../../../shared/api';

const DirectBookingTest = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchBookings = async () => {
    setLoading(true);
    setError('');
    try {
      console.log('🧪 Testing direct booking API...');
      const response = await api.get('/api/freelancer/bookings/direct');
      console.log('✅ API Response:', response.data);
      setBookings(response.data.bookings || []);
    } catch (err) {
      console.error('❌ API Error:', err);
      setError(err.response?.data?.message || err.message || 'Failed to fetch bookings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧪 Direct Booking Test</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={fetchBookings}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Loading...' : 'Refresh Bookings'}
        </button>
      </div>

      {error && (
        <div style={{ 
          padding: '15px', 
          background: '#fee', 
          border: '1px solid #fcc', 
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      <div style={{ 
        padding: '15px', 
        background: '#f0f8ff', 
        border: '1px solid #d0e8ff', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <strong>📊 Debug Info:</strong>
        <br />
        • Bookings Count: {bookings.length}
        <br />
        • Loading: {loading.toString()}
        <br />
        • Error: {error || 'none'}
        <br />
        • API Endpoint: /api/freelancer/bookings/direct
      </div>

      <h2>Bookings ({bookings.length})</h2>
      
      {bookings.length === 0 ? (
        <div style={{ 
          padding: '40px', 
          textAlign: 'center', 
          background: '#f8f9fa', 
          borderRadius: '8px' 
        }}>
          <h3>No direct bookings found</h3>
          <p>Create a direct booking first to see it here.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '15px' }}>
          {bookings.map((booking, index) => (
            <div key={booking.id} style={{
              padding: '20px',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              background: 'white'
            }}>
              <h3>Booking #{index + 1}</h3>
              <div style={{ display: 'grid', gap: '8px', fontSize: '14px' }}>
                <div><strong>ID:</strong> {booking.id}</div>
                <div><strong>Title:</strong> {booking.project_title || 'N/A'}</div>
                <div><strong>Description:</strong> {booking.description || booking.project_description || 'N/A'}</div>
                <div><strong>Amount:</strong> ₹{(booking.amount || 0).toLocaleString()}</div>
                <div><strong>Status:</strong> {booking.status || 'N/A'}</div>
                <div><strong>Client:</strong> {booking.client_name || 'N/A'}</div>
                <div><strong>Freelancer:</strong> {booking.freelancer_name || 'N/A'}</div>
                <div><strong>Created:</strong> {new Date(booking.created_at).toLocaleString()}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: '30px', padding: '15px', background: '#fff3cd', borderRadius: '8px' }}>
        <h3>🔍 Testing Steps:</h3>
        <ol>
          <li>If you see no bookings, first create a direct booking:</li>
          <ul>
            <li>Go to <code>/freelance/home</code></li>
            <li>Click "Find Freelancers"</li>
            <li>Click "Book Now" on any freelancer</li>
            <li>Fill and submit the booking form</li>
          </ul>
          <li>Then come back to this test page and refresh</li>
          <li>Check browser console (F12) for detailed logs</li>
        </ol>
      </div>
    </div>
  );
};

export default DirectBookingTest;
