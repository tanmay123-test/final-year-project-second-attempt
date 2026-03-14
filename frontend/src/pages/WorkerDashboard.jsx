import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { appointmentService } from '../services/api';

const WorkerDashboard = () => {
  const { worker } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (worker?.worker_id) {
      fetchAppointments();
    }
  }, [worker]);

  const fetchAppointments = async () => {
    try {
      // API expects worker_id
      const res = await appointmentService.getWorkerAppointments(worker.worker_id);
      setAppointments(res.data.appointments);
    } catch (error) {
      console.error("Failed to fetch appointments", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (appointmentId, status) => {
    try {
      await appointmentService.respondToAppointment({
        appointment_id: appointmentId,
        status: status
      });
      fetchAppointments(); // Refresh list
    } catch (error) {
      console.error("Failed to update status", error);
    }
  };

  if (!worker) return <div>Access Denied</div>;

  return (
    <div className="dashboard-container">
      <h1>Provider Dashboard</h1>
      <div className="card-desc" style={{ marginBottom: '2rem' }}>
        Welcome back, {worker.email} ({worker.specialization})
      </div>

      <h2>Appointment Requests</h2>
      {loading ? (
        <p>Loading...</p>
      ) : appointments.length === 0 ? (
        <p>No appointments found.</p>
      ) : (
        <div className="appointments-grid">
          {appointments.map(appt => (
            <div key={appt.id} className="appointment-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <span className={`status-badge ${appt.status}`}>{appt.status}</span>
                <span style={{ fontSize: '0.9rem', color: '#666' }}>{appt.booking_date} {appt.time_slot}</span>
              </div>
              
              <h3>{appt.user_name}</h3>
              <p><strong>Symptoms:</strong> {appt.patient_symptoms || appt.symptoms}</p>
              <p><strong>Type:</strong> {appt.appointment_type}</p>
              
              {appt.status === 'pending' && (
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                  <button 
                    className="btn-primary" 
                    style={{ background: 'var(--success-green)' }}
                    onClick={() => handleStatusChange(appt.id, 'accepted')}
                  >
                    Accept
                  </button>
                  <button 
                    className="btn-secondary" 
                    style={{ borderColor: 'var(--error-red)', color: 'var(--error-red)' }}
                    onClick={() => handleStatusChange(appt.id, 'rejected')}
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkerDashboard;
