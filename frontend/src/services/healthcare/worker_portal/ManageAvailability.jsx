import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { Calendar, Clock, Plus, Trash2, Save } from 'lucide-react';
import '../styles/ManageAvailability.css';

const ManageAvailability = () => {
  const { worker } = useAuth();
  const [selectedDate, setSelectedDate] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [currentAvailability, setCurrentAvailability] = useState([]);

  const token = localStorage.getItem('token');
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // All possible time slots
  const allTimeSlots = [
    '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM', '02:00 PM', '02:30 PM',
    '03:00 PM', '03:30 PM', '04:00 PM', '04:30 PM'
  ];

  useEffect(() => {
    if (selectedDate) {
      fetchCurrentAvailability();
    }
  }, [selectedDate]);

  const fetchCurrentAvailability = async () => {
    try {
      const response = await fetch(`/healthcare/availability/${worker.id}?date=${selectedDate}`, { headers });
      if (response.ok) {
        const data = await response.json();
        setCurrentAvailability(data.available_slots || []);
        setAvailableSlots(data.available_slots || []);
      }
    } catch (err) {
      console.error('Failed to fetch availability:', err);
    }
  };

  const handleSlotToggle = (timeSlot) => {
    setAvailableSlots(prev => {
      if (prev.includes(timeSlot)) {
        return prev.filter(slot => slot !== timeSlot);
      } else {
        return [...prev, timeSlot];
      }
    });
  };

  const handleSaveAvailability = async () => {
    setSaving(true);
    setMessage('');
    
    try {
      const response = await fetch(`/healthcare/availability/${worker.id}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          date: selectedDate,
          time_slots: availableSlots
        })
      });

      if (response.ok) {
        setMessage('Availability saved successfully!');
        setCurrentAvailability(availableSlots);
      } else {
        setMessage('Failed to save availability');
      }
    } catch (err) {
      console.error('Failed to save availability:', err);
      setMessage('Failed to save availability');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="manage-availability-container">
      <div className="header">
        <h2>Manage Availability</h2>
        <p>Set your available time slots for patient appointments</p>
      </div>

      <div className="availability-form">
        <div className="form-group">
          <label>
            <Calendar size={20} />
            Select Date
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            max={new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
          />
        </div>

        {selectedDate && (
          <div className="slots-section">
            <div className="slots-header">
              <h3>
                <Clock size={20} />
                Available Time Slots
              </h3>
              <button
                className="select-all-btn"
                onClick={() => setAvailableSlots(allTimeSlots)}
              >
                Select All
              </button>
            </div>

            <div className="time-slots-grid">
              {allTimeSlots.map(timeSlot => (
                <button
                  key={timeSlot}
                  className={`slot-button ${availableSlots.includes(timeSlot) ? 'selected' : ''}`}
                  onClick={() => handleSlotToggle(timeSlot)}
                >
                  {timeSlot}
                </button>
              ))}
            </div>

            <div className="actions">
              <button
                className="save-btn"
                onClick={handleSaveAvailability}
                disabled={saving || availableSlots.length === 0}
              >
                <Save size={20} />
                {saving ? 'Saving...' : 'Save Availability'}
              </button>
              
              {availableSlots.length > 0 && (
                <button
                  className="clear-btn"
                  onClick={() => setAvailableSlots([])}
                >
                  <Trash2 size={20} />
                  Clear All
                </button>
              )}
            </div>
          </div>
        )}

        {message && (
          <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManageAvailability;
