import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../../frontend/src/context/AuthContext';
import { workerService } from '../../../../frontend/src/services/api';
import { 
  ChevronLeft, Plus, Trash2, Clock, Loader2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import './ProviderAvailability.css';

const ProviderAvailability = () => {
  const { worker } = useAuth();
  
  // State
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedTime, setSelectedTime] = useState('');
  const [daySlots, setDaySlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Generate time slots for dropdown (08:00 AM to 08:00 PM)
  const timeOptions = React.useMemo(() => {
    const slots = [];
    for (let i = 8; i <= 20; i++) {
      const hour = i > 12 ? i - 12 : i;
      const ampm = i >= 12 ? 'PM' : 'AM';
      slots.push(`${hour}:00 ${ampm}`);
      if (i !== 20) slots.push(`${hour}:30 ${ampm}`);
    }
    return slots;
  }, []);

  const getWorkerId = () => worker?.id || worker?.worker_id;

  // Fetch availability when date changes
  useEffect(() => {
    if (getWorkerId() && selectedDate) {
      fetchDayAvailability();
    }
  }, [worker, selectedDate]);

  const fetchDayAvailability = async () => {
    const workerId = getWorkerId();
    if (!workerId) return;

    setLoading(true);
    try {
      const res = await workerService.getAvailability(workerId, selectedDate);
      // Ensure we handle the response correctly based on API structure
      // API returns { availability: [{ time_slot: "10:00 AM", ... }, ...] }
      const slots = res.data.availability || [];
      // Sort slots by time
      const sortedSlots = slots.sort((a, b) => {
        const parseTime = (slotObj) => {
            const timeStr = slotObj.time_slot;
            if (!timeStr) return 0;
            const parts = timeStr.split(' ');
            if (parts.length < 2) return 0;
            const [time, mod] = parts;
            let [h, m] = time.split(':').map(Number);
            if (mod === 'PM' && h !== 12) h += 12;
            if (mod === 'AM' && h === 12) h = 0;
            return h * 60 + m;
        };
        return parseTime(a) - parseTime(b);
      });
      setDaySlots(sortedSlots);
    } catch (error) {
      console.error('Error fetching availability:', error);
      // If 404 or empty, just set empty slots
      setDaySlots([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSlot = async () => {
    if (!selectedTime) {
      showMessage('error', 'Please select a time');
      return;
    }

    // Check if already exists
    if (daySlots.some(s => s.time_slot === selectedTime)) {
      showMessage('error', 'Slot already added');
      return;
    }

    const workerId = getWorkerId();
    if (!workerId) return;

    setAdding(true);
    try {
      await workerService.addAvailability(workerId, selectedDate, selectedTime);
      showMessage('success', 'Slot added successfully');
      setSelectedTime(''); // Reset selection
      fetchDayAvailability(); // Refresh list
    } catch (error) {
      console.error('Error adding slot:', error);
      showMessage('error', 'Failed to add slot');
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveSlot = async (slotTime) => {
    const workerId = getWorkerId();
    if (!workerId) return;

    if (!window.confirm(`Remove slot ${slotTime}?`)) return;

    try {
      await workerService.removeAvailability(workerId, selectedDate, slotTime);
      showMessage('success', 'Slot removed');
      fetchDayAvailability();
    } catch (error) {
      console.error('Error removing slot:', error);
      showMessage('error', 'Failed to remove slot');
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };

  return (
    <div className="provider-availability-page">
      {/* Header Section with Purple Background */}
      <div className="availability-header">
        <div className="header-content">
            <Link to="/worker/housekeeping/dashboard" className="back-btn">
                <ChevronLeft size={24} color="white" />
            </Link>
            <div className="header-text">
                <h1>Availability</h1>
                <p>Manage your available dates and time slots</p>
            </div>
        </div>
      </div>

      <div className="availability-container">
        {/* Message Banner */}
        {message.text && (
            <div className={`message-banner ${message.type}`}>
            {message.text}
            </div>
        )}

        {/* Date Selection Card */}
        <div className="availability-card">
            <label className="card-label">Select Date</label>
            <div className="date-input-wrapper">
                <input 
                    type="date" 
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="date-input"
                />
            </div>
        </div>

        {/* Add Time Slot Card */}
        <div className="availability-card">
            <div className="card-header">
                <div className="icon-box">
                    <Plus size={20} color="#9333ea" />
                </div>
                <div>
                    <h3>Add Time Slot</h3>
                    <p className="card-subtitle">Add a new availability slot for {selectedDate}</p>
                </div>
            </div>
            
            <div className="add-slot-row">
                <select 
                    className="time-select"
                    value={selectedTime}
                    onChange={(e) => setSelectedTime(e.target.value)}
                >
                    <option value="">Select Time</option>
                    {timeOptions.map(time => (
                        <option key={time} value={time}>{time}</option>
                    ))}
                </select>
                <button 
                    className="add-btn"
                    onClick={handleAddSlot}
                    disabled={adding || !selectedTime}
                >
                    {adding ? <Loader2 className="spin" size={18} /> : 'Add Slot'}
                </button>
            </div>
        </div>

        {/* Current Availability Card */}
        <div className="availability-card">
            <div className="card-header">
                <div className="icon-box green">
                    <Clock size={20} color="#16a34a" />
                </div>
                <div>
                    <h3>Current Availability</h3>
                    <p className="card-subtitle">Your time slots for {selectedDate}</p>
                </div>
            </div>

            <div className="slots-container">
                {loading ? (
                    <div className="loading-state">
                        <Loader2 className="spin" size={30} color="#9333ea" />
                    </div>
                ) : daySlots.length > 0 ? (
                    <div className="slots-grid">
                        {daySlots.map((slot, index) => (
                            <div key={index} className="time-chip">
                                <span>{slot.time_slot}</span>
                                <button 
                                    className="remove-slot-btn"
                                    onClick={() => handleRemoveSlot(slot.time_slot)}
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-state">
                        <p>No slots added for this date.</p>
                    </div>
                )}
            </div>
        </div>
      </div>

    </div>
  );
};

export default ProviderAvailability;
