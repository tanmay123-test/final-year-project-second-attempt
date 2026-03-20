import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { appointmentService } from '../shared/api';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const response = await appointmentService.getUserAppointments();
        setAppointments(response.data.appointments);
      } catch (error) {
        console.error('Failed to fetch appointments:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'accepted': return 'green';
      case 'pending': return 'orange';
      case 'completed': return 'blue';
      case 'rejected': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="dashboard-container">
      <h1>Welcome, {user?.user_name}</h1>
      
      <div className="dashboard-actions">
        <Link to="/doctors" className="btn-primary">Book New Appointment</Link>
      </div>

      <div className="appointments-section">
        <h2>Your Appointments</h2>
        {loading ? (
          <p>Loading appointments...</p>
        ) : appointments.length === 0 ? (
          <p>No appointments found.</p>
        ) : (
          <div className="appointments-list">
            {appointments.map((appt) => (
              <div key={appt.id} className="appointment-card">
                <div className="appt-header">
                  <span className={`status-badge ${getStatusColor(appt.status)}`}>
                    {appt.status}
                  </span>
                  <span className="appt-date">{appt.booking_date} {appt.time_slot}</span>
                </div>
                <div className="appt-details">
                  <p><strong>Doctor:</strong> {appt.doctor_name || 'Dr. Unknown'}</p> {/* Backend might need to join worker name */}
                  <p><strong>Type:</strong> {appt.appointment_type}</p>
                  <p><strong>Symptoms:</strong> {appt.patient_symptoms}</p>
                </div>
                {appt.appointment_type === 'video' && appt.status === 'accepted' && (
                  <button className="btn-secondary">Join Video Call</button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
