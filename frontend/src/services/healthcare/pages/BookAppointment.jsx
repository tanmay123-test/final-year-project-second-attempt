import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import HealthcareBottomNav from '../components/HealthcareBottomNav';
import '../styles/BookAppointment.css';
import '../styles/healthcare-shared.css';

const BookAppointment = () => {
  const navigate = useNavigate();
  const { doctorId } = useParams();
  const { user } = useAuth();
  
  const [doctor, setDoctor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedTime, setSelectedTime] = useState('');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [slotsLoading, setSlotsLoading] = useState(false);

  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  useEffect(() => {
    fetchDoctorDetails();
  }, [doctorId]);

  useEffect(() => {
    if (selectedDate && doctor) {
      fetchAvailableSlots();
    }
  }, [selectedDate, doctor]);

  const fetchAvailableSlots = async () => {
    setSlotsLoading(true);
    console.log(`Fetching slots for doctor ${doctorId} on date ${selectedDate}`);
    try {
      const response = await fetch(`/healthcare/availability/${doctorId}?date=${selectedDate}`, { headers });
      console.log(`Response status: ${response.status}`);
      if (response.ok) {
        const data = await response.json();
        console.log('Available slots:', data);
        setAvailableSlots(data.available_slots || []);
      } else {
        console.error('Failed to fetch slots:', response.statusText);
      }
    } catch (err) {
      console.error('Failed to fetch available slots:', err);
      setAvailableSlots([]);
    } finally {
      setSlotsLoading(false);
    }
  };

  const fetchDoctorDetails = async () => {
    try {
      const response = await fetch(`/healthcare/doctors/${doctorId}`, { headers });
      if (response.ok) {
        const data = await response.json();
        setDoctor(data.doctor || data);
      }
    } catch (err) {
      console.error('Failed to fetch doctor details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!selectedDate || !selectedTime || !reason.trim()) {
      setError('Please fill all fields');
      return;
    }

    // Get patient ID from user object or localStorage fallback
    const patientId = user?.id || localStorage.getItem('user_id');
    
    if (!patientId) {
      setError('Please login to book appointment');
      return;
    }

    setBookingLoading(true);
    console.log('Starting booking with data:', {
      doctor_id: parseInt(doctorId),
      patient_id: patientId,
      date: selectedDate,
      time: selectedTime,
      reason: reason
    });
    
    try {
      const appointmentData = {
        doctor_id: parseInt(doctorId),
        patient_id: patientId,
        date: selectedDate,
        time: selectedTime,
        reason: reason,
        status: 'pending'
      };

      console.log('Sending appointment data:', appointmentData);
      const response = await fetch('/healthcare/appointments', {
        method: 'POST',
        headers,
        body: JSON.stringify(appointmentData)
      });

      console.log('Booking response status:', response.status);
      const responseData = await response.json();
      console.log('Booking response data:', responseData);

      if (response.ok) {
        setSuccess('Appointment booked successfully!');
        setTimeout(() => {
          navigate('/healthcare/appointments');
        }, 2000);
      } else {
        setError(responseData.error || 'Failed to book appointment');
      }
    } catch (err) {
      console.error('Booking error:', err);
      setError('Failed to book appointment');
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="healthcare-container">
        <div className="loading">Loading doctor details...</div>
      </div>
    );
  }

  if (!doctor) {
    return (
      <div className="healthcare-container">
        <div className="error">Doctor not found</div>
      </div>
    );
  }

  return (
    <div className="healthcare-container">
      <div className="healthcare-header">
        <button onClick={() => navigate(-1)} className="back-btn">← Back</button>
        <h1>Book Appointment</h1>
      </div>

      <div className="book-appointment-container">
        <div className="doctor-card">
          <div className="doctor-info">
            <h3>{doctor.full_name}</h3>
            <p className="specialization">{doctor.specialization}</p>
            <p className="experience">Experience: {doctor.experience || 'N/A'} years</p>
            <p className="rating">⭐ {doctor.rating || '4.5'}</p>
          </div>
        </div>

        <form onSubmit={handleBooking} className="booking-form">
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          <div className="form-group">
            <label>Select Date</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => {
              console.log('Date selected:', e.target.value);
              setSelectedDate(e.target.value);
              setSelectedTime(''); // Reset selected time when date changes
            }}
              min={new Date().toISOString().split('T')[0]}
              max={new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
              required
            />
          </div>

          <div className="form-group">
            <label>Select Time</label>
            {!selectedDate ? (
              <p className="info-text">Please select a date first to see available time slots</p>
            ) : slotsLoading ? (
              <p className="info-text">Loading available slots...</p>
            ) : availableSlots.length === 0 ? (
              <p className="info-text">No available slots for this date</p>
            ) : (
              <div className="time-slots">
                {availableSlots.map(time => (
                  <button
                    key={time}
                    type="button"
                    className={`time-slot ${selectedTime === time ? 'selected' : ''}`}
                    onClick={() => setSelectedTime(time)}
                  >
                    {time}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="form-group">
            <label>Reason for Visit</label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Please describe your symptoms or reason for visit..."
              rows="4"
              required
            />
          </div>

          <button type="submit" className="book-btn" disabled={bookingLoading}>
            {bookingLoading ? 'Booking...' : 'Book Appointment'}
          </button>
        </form>
      </div>

      <HealthcareBottomNav />
    </div>
  );
};

export default BookAppointment;
