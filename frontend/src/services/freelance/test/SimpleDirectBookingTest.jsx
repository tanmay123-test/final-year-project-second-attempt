import React, { useState } from 'react';
import api from '../../../shared/api';

const SimpleDirectBookingTest = () => {
  const [message, setMessage] = useState('Loading...');
  const [bookings, setBookings] = useState([]);

  React.useEffect(() => {
    testAPI();
  }, []);

  const testAPI = async () => {
    try {
      setMessage('Testing API connection...');
      const response = await api.get('/api/freelancer/bookings/direct');
      console.log('API Response:', response.data);
      setMessage('✅ API working! Found ' + (response.data.bookings?.length || 0) + ' bookings');
      setBookings(response.data.bookings || []);
    } catch (error) {
      console.error('API Error:', error);
      setMessage('❌ API Error: ' + (error.response?.data?.message || error.message));
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧪 Simple Direct Booking Test</h1>
      
      <div style={{ 
        padding: '20px', 
        background: '#f0f8ff', 
        border: '1px solid #d0e8ff', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <strong>Status:</strong> {message}
      </div>

      {bookings.length > 0 && (
        <div>
          <h2>Bookings Found:</h2>
          {bookings.map((booking, index) => (
            <div key={booking.id} style={{
              padding: '15px',
              border: '1px solid #ddd',
              borderRadius: '8px',
              marginBottom: '10px',
              background: 'white'
            }}>
              <h3>Booking #{index + 1}</h3>
              <div>ID: {booking.id}</div>
              <div>Title: {booking.project_title || 'N/A'}</div>
              <div>Amount: ₹{(booking.amount || 0).toLocaleString()}</div>
              <div>Status: {booking.status || 'N/A'}</div>
              <div>Freelancer: {booking.freelancer_name || 'N/A'}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: '30px' }}>
        <button 
          onClick={testAPI}
          style={{
            padding: '10px 20px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Test Again
        </button>
      </div>

      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p><strong>Next Steps:</strong></p>
        <ol>
          <li>If API works, the issue is with the MyProjects component</li>
          <li>If API fails, check backend and network connection</li>
          <li>Check browser console (F12) for detailed errors</li>
        </ol>
      </div>
    </div>
  );
};

export default SimpleDirectBookingTest;
