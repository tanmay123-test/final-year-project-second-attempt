import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { appointmentService, videoService } from '../services/api';
import { Link } from 'react-router-dom';
import { CalendarDays, Stethoscope, Video, Clock, X, MessageCircle } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('upcoming');
  const [actionLoadingId, setActionLoadingId] = useState(null);

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

  const filtered = useMemo(() => {
    if (filter === 'completed') {
      return appointments.filter(a => (a.status || '').toLowerCase() === 'completed');
    }
    if (filter === 'cancelled') {
      return appointments.filter(a => ['cancelled','rejected'].includes((a.status || '').toLowerCase()));
    }
    return appointments.filter(a => !['completed','cancelled','rejected'].includes((a.status || '').toLowerCase()));
  }, [appointments, filter]);

  const joinVideo = (id) => {
    // Navigate to OTP join page as per design
    window.location.href = `/appointments/join/${id}`;
  };
  
  const cancel = async (id) => {
    const ok = window.confirm('Cancel this appointment?');
    if (!ok) return;
    try {
      setActionLoadingId(id);
      await appointmentService.cancelAppointment(id);
      setAppointments(prev => prev.map(a => a.id === id ? { ...a, status: 'cancelled' } : a));
    } catch (e) {
      alert('Cancel failed. This action may not be available.');
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="apt-page">
      <h1 className="title">My Appointments</h1>

      <div className="tabs">
        <button className={`tab ${filter==='upcoming'?'active':''}`} onClick={() => setFilter('upcoming')}>Upcoming</button>
        <button className={`tab ${filter==='completed'?'active':''}`} onClick={() => setFilter('completed')}>Completed</button>
        <button className={`tab ${filter==='cancelled'?'active':''}`} onClick={() => setFilter('cancelled')}>Cancelled</button>
      </div>

      {loading ? (
        <div className="skeleton-list">
          <div className="skeleton" />
          <div className="skeleton" />
          <div className="skeleton" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty">
          <CalendarDays size={28} />
          <p>No appointments found.</p>
          <Link to="/doctors" className="ghost">Browse Doctors</Link>
        </div>
      ) : (
        <div className="list">
          {filtered.map(appt => {
            const isVideo = appt.appointment_type === 'video';
            const canJoin = isVideo && ['accepted','confirmed','in_consultation'].includes(appt.status || '');
            const initial = (appt.doctor_name || 'Doctor').trim().charAt(0).toUpperCase();
            const spec = appt.specialization || 'General Physician';
            return (
              <div key={appt.id} className="card">
                <div className="top">
                  <div className="avatar">{initial}</div>
                  <div className="doc">
                    <div className="name">Dr. {appt.doctor_name || `#${appt.worker_id}`}</div>
                    <div className="spec">{spec}</div>
                    <div className="badges">
                      <span className="badge upcoming">Upcoming</span>
                    </div>
                  </div>
                </div>
                <div className="time">
                  <span className="when">
                    <CalendarDays size={16} />
                    <span>{appt.booking_date || 'TBD'}</span>
                  </span>
                  <span className="when">
                    <Clock size={16} />
                    <span>{appt.time_slot || ''}</span>
                  </span>
                </div>
                <div className="actions">
                  {isVideo ? (
                    <button className="primary" onClick={() => joinVideo(appt.id)} disabled={actionLoadingId===appt.id}>
                      <Video size={18} />
                      <span>Join Video</span>
                    </button>
                  ) : (
                    <button className="primary" onClick={() => alert('Chat coming soon')}>
                      <MessageCircle size={18} />
                      <span>Start Chat</span>
                    </button>
                  )}
                  <button className="cancel" onClick={() => cancel(appt.id)} disabled={actionLoadingId===appt.id}>
                    <X size={18} />
                    <span>Cancel</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <style>{`
        .apt-page{padding:1rem;max-width:900px;margin:0 auto}
        .title{font-size:1.4rem;margin:0 0 .75rem 0}
        .tabs{display:flex;gap:.5rem;background:#fff;border-radius:12px;padding:.4rem;border:1px solid #E5E7EB;box-shadow:0 4px 15px rgba(0,0,0,0.05)}
        .tab{flex:0 0 auto;border:none;background:transparent;padding:.5rem .9rem;border-radius:999px;cursor:pointer}
        .tab.active{background:#8E44AD;color:#fff}
        .skeleton-list{display:grid;gap:.75rem}
        .skeleton{height:84px;background:linear-gradient(90deg,#f3f4f6 25%,#e5e7eb 37%,#f3f4f6 63%);background-size:400% 100%;animation:shimmer 1.4s ease infinite;border-radius:14px}
        @keyframes shimmer{0%{background-position:100% 0}100%{background-position:0 0}}
        .empty{display:flex;flex-direction:column;align-items:center;gap:.5rem;color:#6B7280;background:white;padding:1.25rem;border-radius:16px}
        .empty .ghost{margin-top:.25rem;text-decoration:none;color:#8E44AD}
        .list{display:grid;gap:.75rem}
        .card{background:white;border-radius:20px;box-shadow:0 4px 18px rgba(0,0,0,0.06);padding:1rem}
        .top{display:flex;gap:.9rem;align-items:center}
        .avatar{width:48px;height:48px;border-radius:12px;background:#E9D5FF;display:flex;align-items:center;justify-content:center;font-weight:800;color:#6B21A8}
        .doc .name{font-weight:700}
        .doc .spec{color:#6B7280;font-size:.9rem}
        .badges{margin-top:.25rem}
        .badge.upcoming{background:#F4ECF7;color:#8E44AD;padding:.2rem .5rem;border-radius:10px;font-size:.75rem}
        .time{display:flex;gap:1rem;margin:.75rem 0;color:#4B5563}
        .when{display:inline-flex;align-items:center;gap:.35rem}
        .actions{display:flex;gap:.75rem;align-items:center}
        .primary{flex:1;display:inline-flex;align-items:center;justify-content:center;gap:.5rem;background:#8E44AD;color:#fff;border:none;border-radius:14px;padding:.8rem .9rem;cursor:pointer}
        .cancel{display:inline-flex;align-items:center;gap:.4rem;background:#fff;color:#111827;border:1px solid #E5E7EB;border-radius:14px;padding:.8rem .9rem;cursor:pointer}
      `}</style>
    </div>
  );
};

export default Dashboard;
