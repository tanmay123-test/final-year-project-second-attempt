import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { workerService, doctorService } from '../../../services/api';
import { useNavigate } from 'react-router-dom';
import DoctorBottomNav from '../../../components/DoctorBottomNav';
import { 
  Users, Clock, Calendar, TrendingUp, 
  Power, ChevronRight, Video, User, CheckCircle2, XCircle
} from 'lucide-react';

const DoctorDashboard = () => {
  const { worker, logout } = useAuth();
  const [isOnline, setIsOnline] = useState(true);
  const [doctorName, setDoctorName] = useState('');
  const [stats, setStats] = useState([
    { icon: Users, value: '0', label: "Today's Patients" },
    { icon: Clock, value: '0', label: "Pending Requests" },
    { icon: Calendar, value: '0', label: "Accepted" },
    { icon: TrendingUp, value: '0', label: "Total" },
  ]);
  const [appointments, setAppointments] = useState([]);
  const navigate = useNavigate();

  const fetchAll = async () => {
    if (!worker?.worker_id) return;
    try {
      const w = await doctorService.getDoctorById(worker.worker_id);
      const fullName = w.data.worker?.full_name || (worker.email?.split('@')[0] || 'Doctor');
      setDoctorName(fullName);
      const ap = await workerService.getAppointments(worker.worker_id);
      const list = ap.data.appointments || [];
      const mapped = list.map((a) => ({
        id: a.id,
        name: a.user_name || 'Patient',
        type: a.appointment_type === 'video' ? 'Video Call' : 'In-Person',
        symptom: a.patient_symptoms || '',
        time: a.time_slot || (a.booking_date ? (String(a.booking_date).split(' ')[1] || '') : ''),
        status: a.status || '',
        initial: (a.user_name || 'P').charAt(0).toUpperCase(),
        color: '#E8DAEF',
      }));
      setAppointments(mapped);

      const today = new Date().toISOString().slice(0, 10);
      const isToday = (bd) => (bd ? String(bd).startsWith(today) : false);
      const todayPatients = list.filter((a) => isToday(a.booking_date) && a.status !== 'completed').length;
      const pendingCount = list.filter((a) => a.status === 'pending').length;
      const acceptedCount = list.filter((a) => a.status === 'accepted').length;
      const totalCount = list.length;
      setStats([
        { icon: Users, value: String(todayPatients), label: "Today's Patients" },
        { icon: Clock, value: String(pendingCount), label: "Pending Requests" },
        { icon: Calendar, value: String(acceptedCount), label: "Accepted" },
        { icon: TrendingUp, value: String(totalCount), label: "Total" },
      ]);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchAll();
  }, [worker]);

  const respond = async (appointmentId, status) => {
    try {
      await workerService.respondToRequest({ appointment_id: appointmentId, status });
      fetchAll();
    } catch (e) {
      console.error('Respond failed', e);
      alert(e.response?.data?.error || 'Action failed');
    }
  };

  return (
    <div className="doctor-dashboard-container">
      {/* Header Section */}
      <div className="doctor-header">
        <div className="header-content">
          <div className="doctor-info">
            <span className="greeting">Good Morning 👋</span>
            <h1 className="doctor-name">Dr. {doctorName}</h1>
          </div>
          <div className="header-actions">
            <button 
              className={`status-toggle ${isOnline ? 'online' : 'offline'}`}
              onClick={() => setIsOnline(!isOnline)}
            >
              <Power size={16} />
              <span>{isOnline ? 'Online' : 'Offline'}</span>
              <span className="status-dot"></span>
            </button>
            <div className="profile-avatar">
              {(doctorName || 'S')[0]}
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon-wrapper">
              <stat.icon size={24} className="stat-icon" />
            </div>
            <div className="stat-info">
              <h3 className="stat-value">{stat.value}</h3>
              <p className="stat-label">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Today's Schedule */}
      <div className="schedule-section">
        <div className="section-header">
          <h2>Today's Schedule</h2>
          <button className="view-all-btn" onClick={() => navigate('/doctor/requests')}>
            View All <ChevronRight size={16} />
          </button>
        </div>

        <div className="appointments-list">
          {appointments.map((apt) => (
            <div key={apt.id} className="appointment-card">
              <div className="apt-avatar" style={{ backgroundColor: apt.color }}>
                {apt.initial}
              </div>
              <div className="apt-details">
                <h3 className="patient-name">{apt.name}</h3>
                <div className="apt-type">
                  {apt.type === 'Video Call' ? <Video size={14} /> : <User size={14} />}
                  <span>{apt.type}</span>
                </div>
                <p className="apt-symptom">{apt.symptom}</p>
              </div>
              <div className="apt-time-status">
                <span className="apt-time">{apt.time}</span>
                <span className="apt-status">{apt.status}</span>
              </div>
              {apt.status === 'pending' && (
                <div className="apt-actions">
                  <button className="btn-accept" onClick={() => respond(apt.id, 'accepted')}>
                    <CheckCircle2 size={16} /> Accept
                  </button>
                  <button className="btn-reject" onClick={() => respond(apt.id, 'rejected')}>
                    <XCircle size={16} /> Reject
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <DoctorBottomNav />

      <style>{`
        .doctor-dashboard-container {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 80px; /* Space for bottom nav */
        }

        .doctor-header {
          background: var(--medical-gradient);
          padding: 2rem 1.5rem 4rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
          box-shadow: 0 4px 20px rgba(142, 68, 173, 0.2);
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          max-width: 1200px;
          margin: 0 auto;
        }

        .greeting {
          font-size: 0.9rem;
          opacity: 0.9;
          margin-bottom: 0.25rem;
          display: block;
        }

        .doctor-name {
          font-size: 1.5rem;
          font-weight: 700;
          margin: 0;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .status-toggle {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          border: none;
          font-weight: 600;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .status-toggle.online {
          background: rgba(255, 255, 255, 0.2);
          color: white;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: var(--success-green);
        }

        .profile-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          color: white;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
          padding: 0 1.5rem;
          margin-top: -2.5rem;
          max-width: 1200px;
          margin-left: auto;
          margin-right: auto;
        }

        .stat-card {
          background: white;
          border-radius: 16px;
          padding: 1rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }

        .stat-icon-wrapper {
          background: #F4ECF7; /* Light purple tint */
          padding: 0.75rem;
          border-radius: 12px;
          color: var(--accent-blue);
        }

        .stat-value {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0;
        }

        .stat-label {
          font-size: 0.75rem;
          color: var(--text-secondary);
          margin: 0;
        }

        .schedule-section {
          padding: 1.5rem;
          max-width: 1200px;
          margin: 0 auto;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .section-header h2 {
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0;
        }

        .view-all-btn {
          background: none;
          border: none;
          color: var(--accent-blue);
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 0.25rem;
          cursor: pointer;
        }

        .appointments-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .appointment-card {
          background: white;
          border-radius: 16px;
          padding: 1rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
          position: relative;
        }

        .apt-avatar {
          width: 50px;
          height: 50px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.25rem;
          font-weight: 700;
          color: var(--accent-blue);
          flex-shrink: 0;
        }

        .apt-details {
          flex: 1;
        }

        .patient-name {
          font-size: 1rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 0.25rem 0;
        }

        .apt-type {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin-bottom: 0.25rem;
        }

        .apt-symptom {
          font-size: 0.8rem;
          color: var(--text-secondary);
          margin: 0;
          display: -webkit-box;
          -webkit-line-clamp: 1;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .apt-time-status {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 0.25rem;
        }

        .apt-time {
          font-weight: 700;
          color: var(--text-primary);
          font-size: 0.9rem;
        }

        .apt-status {
          background: #F4ECF7;
          color: var(--accent-blue);
          font-size: 0.7rem;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-weight: 600;
        }
        .apt-actions {
          display: flex;
          gap: 0.5rem;
          margin-left: auto;
        }
        .btn-accept, .btn-reject {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          border: 1px solid #E0E0E0;
          background: #F5F7FA;
          color: var(--text-primary);
          padding: 0.4rem 0.6rem;
          border-radius: 10px;
          cursor: pointer;
          font-weight: 600;
        }
        .btn-accept {
          border-color: #2ECC71;
          color: #2ECC71;
        }
        .btn-reject {
          border-color: #C0392B;
          color: #C0392B;
        }

        @media (min-width: 768px) {
          .stats-grid {
            grid-template-columns: repeat(4, 1fr);
          }
        }
      `}</style>
    </div>
  );
};

export default DoctorDashboard;
