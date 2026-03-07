import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { workerService } from '../shared/api';
import DoctorBottomNav from '../components/DoctorBottomNav';
import { 
  Calendar as CalendarIcon, Clock, Plus, Trash2, 
  ChevronLeft, AlertCircle, CheckCircle2, Loader2
} from 'lucide-react';
import { Link } from 'react-router-dom';

const DoctorAvailability = () => {
  const { worker } = useAuth();
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [availability, setAvailability] = useState([]);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState(false);
  const [newTimeSlot, setNewTimeSlot] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (worker?.worker_id) {
      fetchAvailability();
    }
  }, [worker, selectedDate]);

  const fetchAvailability = async () => {
    setLoading(true);
    try {
      const res = await workerService.getAvailability(worker.worker_id, selectedDate);
      // Backend returns { availability: [{date, time_slot}, ...] }
      setAvailability(res.data.availability || []);
    } catch (error) {
      console.error('Error fetching availability:', error);
      showMessage('error', 'Failed to load availability');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSlot = async (e) => {
    e.preventDefault();
    if (!newTimeSlot) return;

    setAdding(true);
    try {
      await workerService.addAvailability(worker.worker_id, selectedDate, newTimeSlot);
      showMessage('success', 'Time slot added successfully');
      setNewTimeSlot('');
      fetchAvailability();
    } catch (error) {
      console.error('Error adding slot:', error);
      showMessage('error', error.response?.data?.error || 'Failed to add time slot');
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveSlot = async (timeSlot) => {
    if (!window.confirm(`Are you sure you want to remove ${timeSlot}?`)) return;

    try {
      await workerService.removeAvailability(worker.worker_id, selectedDate, timeSlot);
      showMessage('success', 'Time slot removed');
      fetchAvailability();
    } catch (error) {
      console.error('Error removing slot:', error);
      showMessage('error', 'Failed to remove time slot');
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };

  // Helper to generate time options
  const timeOptions = [];
  for (let i = 8; i <= 20; i++) {
    const hour = i > 12 ? i - 12 : i;
    const ampm = i >= 12 ? 'PM' : 'AM';
    timeOptions.push(`${hour}:00 ${ampm}`);
    timeOptions.push(`${hour}:30 ${ampm}`);
  }

  return (
    <div className="availability-page">
      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <Link to="/doctor/dashboard" className="back-btn">
            <ChevronLeft size={24} />
          </Link>
          <div>
            <h1 className="page-title">Availability</h1>
            <p className="page-subtitle">Manage your available dates and time slots</p>
          </div>
        </div>
      </div>

      <div className="content-container">
        {/* Date Selection */}
        <div className="date-selector">
          <label className="section-label">Select Date</label>
          <div className="date-input-wrapper">
            <CalendarIcon className="input-icon" size={20} />
            <input 
              type="date" 
              value={selectedDate}
              min={new Date().toISOString().split('T')[0]}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="date-input"
            />
          </div>
        </div>

        {/* Message Alert */}
        {message.text && (
          <div className={`message-alert ${message.type}`}>
            {message.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
            <span>{message.text}</span>
          </div>
        )}

        {/* Add Slot Section */}
        <div className="card add-slot-card">
          <div className="card-header">
            <div className="icon-box add-icon">
              <Plus size={24} />
            </div>
            <div>
              <h3>Add Time Slot</h3>
              <p>Add a new availability slot for {selectedDate}</p>
            </div>
          </div>
          
          <form onSubmit={handleAddSlot} className="add-slot-form">
            <select 
              value={newTimeSlot}
              onChange={(e) => setNewTimeSlot(e.target.value)}
              className="time-select"
              required
            >
              <option value="">Select Time</option>
              {timeOptions.map(time => (
                <option 
                  key={time} 
                  value={time}
                  disabled={availability.some(s => s.time_slot === time)}
                >
                  {time} {availability.some(s => s.time_slot === time) ? '(Added)' : ''}
                </option>
              ))}
            </select>
            <button type="submit" className="btn-add" disabled={adding || !newTimeSlot}>
              {adding ? <Loader2 className="animate-spin" size={20} /> : 'Add Slot'}
            </button>
          </form>
        </div>

        {/* View Availability Section */}
        <div className="card view-slots-card">
          <div className="card-header">
            <div className="icon-box view-icon">
              <Clock size={24} />
            </div>
            <div>
              <h3>Current Availability</h3>
              <p>Your time slots for {selectedDate}</p>
            </div>
          </div>

          <div className="slots-list">
            {loading ? (
              <div className="loading-state">
                <Loader2 className="animate-spin" size={24} />
                <p>Loading slots...</p>
              </div>
            ) : availability.length === 0 ? (
              <div className="empty-state">
                <p>No slots added for this date.</p>
              </div>
            ) : (
              <div className="slots-grid">
                {availability.map((slot, index) => (
                  <div key={index} className="slot-item">
                    <span className="slot-time">{slot.time_slot}</span>
                    <button 
                      className="btn-remove"
                      onClick={() => handleRemoveSlot(slot.time_slot)}
                      title="Remove slot"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <DoctorBottomNav />

      <style>{`
        .availability-page {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 80px;
        }

        .page-header {
          background: var(--medical-gradient);
          padding: 2rem 1.5rem 3rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
          box-shadow: 0 4px 20px rgba(142, 68, 173, 0.2);
        }

        .header-content {
          display: flex;
          align-items: center;
          gap: 1rem;
          max-width: 600px;
          margin: 0 auto;
        }

        .back-btn {
          color: white;
          background: rgba(255, 255, 255, 0.2);
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }

        .back-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .page-title {
          font-size: 1.5rem;
          font-weight: 700;
          margin: 0;
        }

        .page-subtitle {
          font-size: 0.9rem;
          opacity: 0.9;
          margin: 0;
        }

        .content-container {
          padding: 1.5rem;
          max-width: 600px;
          margin: -2rem auto 0;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .date-selector {
          background: white;
          padding: 1rem;
          border-radius: 16px;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }

        .section-label {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
          display: block;
        }

        .date-input-wrapper {
          display: flex;
          align-items: center;
          background: #F5F7FA;
          border-radius: 12px;
          padding: 0.5rem 1rem;
        }

        .input-icon {
          color: var(--accent-blue);
          margin-right: 0.75rem;
        }

        .date-input {
          border: none;
          background: transparent;
          font-size: 1rem;
          color: var(--text-primary);
          width: 100%;
          outline: none;
          font-family: inherit;
        }

        .card {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }

        .card-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .icon-box {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .add-icon {
          background: #F4ECF7;
          color: var(--accent-blue);
        }

        .view-icon {
          background: #E8F8F5;
          color: var(--accent-teal);
        }

        .card-header h3 {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0 0 0.25rem 0;
        }

        .card-header p {
          font-size: 0.85rem;
          color: var(--text-secondary);
          margin: 0;
        }

        .add-slot-form {
          display: flex;
          gap: 1rem;
        }

        .time-select {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #E0E0E0;
          border-radius: 12px;
          font-size: 1rem;
          color: var(--text-primary);
          outline: none;
        }

        .time-select:focus {
          border-color: var(--accent-blue);
        }

        .btn-add {
          background: var(--medical-gradient);
          color: white;
          border: none;
          padding: 0 1.5rem;
          border-radius: 12px;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 100px;
        }

        .btn-add:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .slots-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
          gap: 0.75rem;
        }

        .slot-item {
          background: #F5F7FA;
          border: 1px solid #E0E0E0;
          border-radius: 12px;
          padding: 0.75rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
        }

        .slot-time {
          font-weight: 600;
          color: var(--text-primary);
          font-size: 0.9rem;
        }

        .btn-remove {
          background: #FDEBD0; /* Light orange/red tint */
          color: var(--error-red);
          border: none;
          width: 100%;
          padding: 0.4rem;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }

        .btn-remove:hover {
          background: #FADBD8;
        }

        .loading-state, .empty-state {
          text-align: center;
          padding: 2rem 0;
          color: var(--text-secondary);
        }

        .message-alert {
          padding: 1rem;
          border-radius: 12px;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .message-alert.success {
          background: #D5F5E3;
          color: #27AE60;
        }

        .message-alert.error {
          background: #FADBD8;
          color: #C0392B;
        }
      `}</style>
    </div>
  );
};

export default DoctorAvailability;
