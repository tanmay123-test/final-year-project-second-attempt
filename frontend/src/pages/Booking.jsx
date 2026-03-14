import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authService, appointmentService, doctorService } from '../shared/api.js';
import { useAuth } from '../context/AuthContext.jsx';
import { 
  ChevronLeft, Calendar, Clock, Video, MapPin, 
  User, AlertCircle, CheckCircle2, Star, ShieldCheck
} from 'lucide-react';

const Booking = () => {
  const { doctorId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [doctor, setDoctor] = useState(null);
  const [loadingDoctor, setLoadingDoctor] = useState(true);
  
  const [date, setDate] = useState('');
  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [insuranceProvider, setInsuranceProvider] = useState('');
  const [policyNumber, setPolicyNumber] = useState('');
  const [type, setType] = useState('clinic'); // clinic or video
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Generate next 7 days for date picker
  const generateDates = () => {
    const dates = [];
    const today = new Date();
    for (let i = 0; i < 7; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      dates.push({
        fullDate: d.toISOString().split('T')[0],
        dayName: d.toLocaleDateString('en-US', { weekday: 'short' }),
        dayNum: d.getDate(),
        month: d.toLocaleDateString('en-US', { month: 'short' })
      });
    }
    return dates;
  };

  const dates = generateDates();

  useEffect(() => {
    const fetchDoctor = async () => {
      try {
        const res = await doctorService.getDoctorById(doctorId);
        setDoctor(res.data.worker);
      } catch (err) {
        console.error('Error fetching doctor:', err);
        setError('Failed to load doctor details');
      } finally {
        setLoadingDoctor(false);
      }
    };

    if (doctorId) {
      fetchDoctor();
      // Default to today if date not set
      if (!date) setDate(new Date().toISOString().split('T')[0]);
    }
  }, [doctorId]);

  useEffect(() => {
    const fetchAvailability = async () => {
      if (!date || !doctorId) return;
      
      setLoadingSlots(true);
      try {
        // Only fetch slots for clinic visits or if backend requires it for video too
        // Assuming video availability is same as clinic for now, or open
        const res = await doctorService.getAvailability(doctorId, date);
        setSlots(res.data.availability || []);
        // Reset selected slot when date changes
        setSelectedSlot('');
      } catch (err) {
        console.error('Error fetching availability:', err);
      } finally {
        setLoadingSlots(false);
      }
    };

    fetchAvailability();
  }, [date, doctorId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSlot && type === 'clinic') {
      setError('Please select a time slot');
      return;
    }
    if (!symptoms) {
      setError('Please describe your symptoms');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const insuranceDetails = insuranceProvider || policyNumber 
        ? `Provider: ${insuranceProvider}, Policy: ${policyNumber}`
        : null;

      if (type === 'clinic') {
        await appointmentService.bookClinic({
          user_id: user.user_id,
          worker_id: doctorId,
          user_name: user.user_name,
          symptoms,
          date,
          time_slot: selectedSlot,
          insurance_details: insuranceDetails
        });
      } else {
        await appointmentService.bookVideo({
          user_id: user.user_id,
          worker_id: doctorId,
          user_name: user.user_name,
          symptoms,
          insurance_details: insuranceDetails
        });
      }
      
      setSuccess('Appointment booked successfully!');
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Booking failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingDoctor) {
    return (
      <div className="booking-page loading">
        <div className="spinner"></div>
        <p>Loading doctor details...</p>
      </div>
    );
  }

  if (!doctor) {
    return (
      <div className="booking-page error">
        <AlertCircle size={48} color="#E74C3C" />
        <h2>Doctor Not Found</h2>
        <button onClick={() => navigate(-1)} className="back-btn-text">Go Back</button>
      </div>
    );
  }

  return (
    <div className="booking-page">
      {/* Header */}
      <div className="page-header">
        <button onClick={() => navigate(-1)} className="back-btn">
          <ChevronLeft size={24} />
        </button>
        <h1>Book Appointment</h1>
      </div>

      <div className="booking-content">
        {/* Doctor Card */}
        <div className="doctor-card-booking">
          <div className="doctor-avatar">
            {doctor.name ? doctor.name[0].toUpperCase() : 'D'}
          </div>
          <div className="doctor-info">
            <h2 className="doctor-name">Dr. {doctor.name}</h2>
            <p className="doctor-spec">{doctor.specialization}</p>
            <div className="doctor-meta">
              <span className="worker-id">ID: {doctor.id}</span>
              <div className="rating">
                <Star size={14} fill="#F1C40F" color="#F1C40F" />
                <span>{doctor.rating || '4.9'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="form-section">
          <label className="section-label">
            <User size={18} /> Your Name
          </label>
          <input 
            type="text" 
            value={user?.user_name || ''} 
            readOnly 
            className="input-field readonly"
          />
        </div>

        {/* Appointment Type */}
        <div className="form-section">
          <label className="section-label">Appointment Type</label>
          <div className="type-selector">
            <button 
              className={`type-btn ${type === 'clinic' ? 'active' : ''}`}
              onClick={() => setType('clinic')}
            >
              <MapPin size={20} />
              <span>Clinic Visit</span>
            </button>
            <button 
              className={`type-btn ${type === 'video' ? 'active' : ''}`}
              onClick={() => setType('video')}
            >
              <Video size={20} />
              <span>Video Call</span>
            </button>
          </div>
        </div>

        {/* Date Selection */}
        <div className="form-section">
          <label className="section-label">
            <Calendar size={18} /> Select Date
          </label>
          <div className="date-scroll">
            {dates.map((d, index) => (
              <div 
                key={index} 
                className={`date-card ${date === d.fullDate ? 'active' : ''}`}
                onClick={() => setDate(d.fullDate)}
              >
                <span className="day-name">{d.dayName}</span>
                <span className="day-num">{d.dayNum}</span>
                <span className="month-name">{d.month}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Time Slot Selection */}
        {type === 'clinic' && (
          <div className="form-section">
            <label className="section-label">
              <Clock size={18} /> Select Time Slot
            </label>
            {loadingSlots ? (
              <div className="loading-slots">Loading availability...</div>
            ) : slots.length > 0 ? (
              <div className="slots-grid">
                {slots.map((slot, index) => (
                  <button
                    key={index}
                    className={`slot-btn ${selectedSlot === slot.time_slot ? 'active' : ''}`}
                    onClick={() => setSelectedSlot(slot.time_slot)}
                  >
                    {slot.time_slot}
                  </button>
                ))}
              </div>
            ) : (
              <div className="no-slots">No slots available for this date.</div>
            )}
          </div>
        )}

        {/* Insurance Verification */}
        <div className="form-section">
          <label className="section-label">
            <ShieldCheck size={18} /> Insurance Details
          </label>
          <div className="insurance-form">
            <input
              type="text"
              className="input-field"
              placeholder="Insurance Provider (Optional)"
              value={insuranceProvider}
              onChange={(e) => setInsuranceProvider(e.target.value)}
            />
            <input
              type="text"
              className="input-field"
              placeholder="Policy Number (Optional)"
              value={policyNumber}
              onChange={(e) => setPolicyNumber(e.target.value)}
            />
          </div>
          <div className="insurance-note">
            <AlertCircle size={14} />
            <span>We'll verify your insurance at the clinic.</span>
          </div>
        </div>

        {/* Symptoms */}
        <div className="form-section">
          <label className="section-label">Symptoms / Reason</label>
          <textarea
            className="input-field textarea"
            placeholder="Describe your symptoms or reason for visit..."
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            rows={4}
          ></textarea>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="message-box error">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}
        {success && (
          <div className="message-box success">
            <CheckCircle2 size={20} />
            <span>{success}</span>
          </div>
        )}

        {/* Submit Button */}
        <button 
          className="submit-btn"
          onClick={handleSubmit}
          disabled={submitting || (type === 'clinic' && !selectedSlot)}
        >
          {submitting ? 'Booking...' : 'Confirm Booking'}
        </button>
      </div>

      <style>{`
        .booking-page {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 2rem;
          font-family: 'Inter', sans-serif;
        }

        .booking-page.loading, .booking-page.error {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          gap: 1rem;
        }

        .page-header {
          background: white;
          padding: 1.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.05);
          position: sticky;
          top: 80px; /* Navbar height */
          z-index: 10;
        }

        .back-btn {
          background: #F5F7FA;
          border: none;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          color: var(--text-primary);
        }

        .page-header h1 {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
          color: var(--text-primary);
        }

        .booking-content {
          padding: 1.5rem;
          max-width: 600px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .doctor-card-booking {
          background: white;
          border-radius: 16px;
          padding: 1rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .doctor-avatar {
          width: 60px;
          height: 60px;
          border-radius: 16px;
          background: #E8DAEF;
          color: var(--primary-color);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .doctor-info {
          flex: 1;
        }

        .doctor-name {
          font-size: 1.1rem;
          font-weight: 700;
          margin: 0 0 0.25rem 0;
          color: var(--text-primary);
        }

        .doctor-spec {
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin: 0 0 0.5rem 0;
        }

        .doctor-meta {
          display: flex;
          align-items: center;
          gap: 1rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }

        .rating {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-weight: 600;
          color: var(--text-primary);
        }

        .form-section {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .section-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 600;
          color: var(--text-primary);
          font-size: 1rem;
        }

        .input-field {
          padding: 1rem;
          border: 1px solid #E0E0E0;
          border-radius: 12px;
          font-size: 1rem;
          font-family: inherit;
          width: 100%;
          outline: none;
          transition: border-color 0.2s;
        }

        .input-field:focus {
          border-color: var(--primary-color);
        }

        .insurance-form {
          display: flex;
          gap: 1rem;
        }

        .insurance-note {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin-top: 0.25rem;
        }

        .input-field.readonly {
          background: #F9FAFB;
          color: var(--text-secondary);
        }

        .type-selector {
          display: flex;
          gap: 1rem;
        }

        .type-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 1rem;
          background: white;
          border: 1px solid #E0E0E0;
          border-radius: 12px;
          cursor: pointer;
          font-weight: 600;
          color: var(--text-secondary);
          transition: all 0.2s;
        }

        .type-btn.active {
          border-color: var(--primary-color);
          background: #F4ECF7; /* Light purple */
          color: var(--primary-color);
        }

        .date-scroll {
          display: flex;
          gap: 0.75rem;
          overflow-x: auto;
          padding-bottom: 0.5rem;
          scrollbar-width: none; /* Firefox */
        }
        
        .date-scroll::-webkit-scrollbar {
          display: none; /* Chrome/Safari */
        }

        .date-card {
          min-width: 70px;
          background: white;
          border: 1px solid #E0E0E0;
          border-radius: 12px;
          padding: 0.75rem 0.5rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .date-card.active {
          background: var(--primary-color);
          border-color: var(--primary-color);
          color: white;
        }

        .date-card.active .day-name, 
        .date-card.active .day-num,
        .date-card.active .month-name {
          color: white;
        }

        .day-name {
          font-size: 0.8rem;
          color: var(--text-secondary);
          font-weight: 500;
        }

        .day-num {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
        }

        .month-name {
          font-size: 0.7rem;
          color: var(--text-secondary);
        }

        .slots-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.75rem;
        }

        .slot-btn {
          padding: 0.75rem;
          background: white;
          border: 1px solid #E0E0E0;
          border-radius: 8px;
          cursor: pointer;
          font-size: 0.9rem;
          color: var(--text-primary);
          transition: all 0.2s;
        }

        .slot-btn:hover {
          border-color: var(--primary-color);
        }

        .slot-btn.active {
          background: var(--primary-color);
          color: white;
          border-color: var(--primary-color);
        }

        .no-slots {
          text-align: center;
          color: var(--text-secondary);
          padding: 2rem;
          background: white;
          border-radius: 12px;
          border: 1px dashed #E0E0E0;
        }

        .message-box {
          padding: 1rem;
          border-radius: 12px;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 0.9rem;
        }

        .message-box.error {
          background: #FDEDEC;
          color: #E74C3C;
        }

        .message-box.success {
          background: #EAFAF1;
          color: #2ECC71;
        }

        .submit-btn {
          background: var(--primary-color);
          color: white;
          border: none;
          padding: 1.25rem;
          border-radius: 16px;
          font-size: 1.1rem;
          font-weight: 700;
          cursor: pointer;
          margin-top: 1rem;
          transition: background 0.2s;
        }

        .submit-btn:disabled {
          background: #BDC3C7;
          cursor: not-allowed;
        }

        .submit-btn:hover:not(:disabled) {
          opacity: 0.9;
        }
      `}</style>
    </div>
  );
};

export default Booking;
