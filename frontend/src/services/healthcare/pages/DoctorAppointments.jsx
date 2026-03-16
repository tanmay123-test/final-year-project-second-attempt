import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { workerService, videoService } from '../../../services/api';
import DoctorBottomNav from '../../../components/DoctorBottomNav';
import { Calendar as CalendarIcon, CheckCircle2, Video, MessageSquare, RefreshCcw, User, FileText } from 'lucide-react';
 
const DoctorAppointments = () => {
  const { worker } = useAuth();
  const [upcoming, setUpcoming] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
 
  const fetchData = async () => {
    if (!worker?.worker_id) return;
    setLoading(true);
    setError('');
    try {
      const all = await workerService.getAppointments(worker.worker_id);
      const list = (all.data.appointments || []).filter(a => a.status === 'accepted');
      const today = new Date().toISOString().slice(0,10);
      const isUpcoming = (bd) => bd && String(bd) >= today;
      setUpcoming(list.filter(a => isUpcoming(a.booking_date)));
    } catch (e) {
      console.error('Failed to load appointments', e);
      setError(e.response?.data?.error || 'Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };
 
  useEffect(() => {
    fetchData();
  }, [worker]);
 
  const startVideo = async (id) => {
    const otp = window.prompt('Enter OTP to start video call');
    if (!otp) return;
    try {
      const res = await videoService.startVideo(id, otp);
      const link = res.data?.meeting_link;
      if (link) window.open(link, '_blank');
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to start video');
    }
  };
 
  const joinVideo = async (id) => {
    try {
      const res = await videoService.getVideoLink(id);
      const link = res.data?.video_link;
      if (link) window.open(link, '_blank');
    } catch (e) {
      alert(e.response?.data?.error || 'Unable to join. Is payment done and consultation started?');
    }
  };
 
  const completeAppointment = async (id, type) => {
    try {
      if (type === 'video') {
        await videoService.endVideo(id);
      } else {
        await workerService.respondToRequest({ appointment_id: id, status: 'completed' });
      }
      fetchData();
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to complete appointment');
    }
  };
 
  return (
    <div className="doctor-appointments-page">
      <div className="page-header">
        <div className="header-content">
          <FileText size={28} />
          <div>
            <h1 className="page-title">Appointments</h1>
          </div>
        </div>
      </div>
 
      <div className="content-container">
        {error && <div className="message error">{error}</div>}
        {loading ? (
          <div className="loading">Loading...</div>
        ) : (
          <>
            <h2 className="section-heading">Upcoming Schedule</h2>
            <div className="list">
              {upcoming.map((a) => (
                <div key={a.id} className="card">
                  <div className="card-body">
                    <div className="avatar"><User size={24} /></div>
                    <div className="content">
                      <div className="title-row">
                        <h3 className="title">
                          <CheckCircle2 size={18} color="#2ECC71" />
                          Appointment #{a.id}
                        </h3>
                        <span className={`pill ${a.appointment_type === 'video' ? 'video' : 'clinic'}`}>
                          {a.appointment_type === 'video' ? 'VIDEO' : 'CLINIC'}
                        </span>
                      </div>
                      <div className="status-line">Patient: {a.user_name}</div>
                      <div className="info-line">
                        <CalendarIcon size={16} /> {a.booking_date} • {a.patient_symptoms}
                      </div>
                    </div>
                  </div>
                  <div className="actions">
                    <button className="action-btn" onClick={() => startVideo(a.id)}>
                      <Video size={16} /> Start Video Call (OTP)
                    </button>
                    <button className="action-btn" onClick={() => joinVideo(a.id)}>
                      <Video size={16} /> Join Video Call
                    </button>
                    <button className="action-btn" onClick={() => completeAppointment(a.id, a.appointment_type)}>
                      <CheckCircle2 size={16} /> Complete Appointment
                    </button>
                    <button className="action-btn" onClick={() => alert('Messages view coming soon')}>
                      <MessageSquare size={16} /> View Messages
                    </button>
                  </div>
                </div>
              ))}
            </div>
 
            
 
            <button className="refresh-btn" onClick={fetchData}>
              <RefreshCcw size={18} /> Refresh
            </button>
          </>
        )}
      </div>
 
      <DoctorBottomNav />
 
      <style>{`
        .doctor-appointments-page {
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
          box-shadow: 0 4px 20px rgba(142,68,173,0.2);
        }
        .header-content {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          max-width: 600px;
          margin: 0 auto;
        }
        .page-title { margin: 0; font-size: 1.4rem; font-weight: 700; }
        .content-container {
          padding: 1.5rem;
          max-width: 600px;
          margin: -2rem auto 0;
        }
        .section-heading {
          margin: 0.5rem 0 0.75rem;
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        .list { display: flex; flex-direction: column; gap: 1rem; }
        .card {
          background: white;
          border-radius: 20px;
          padding: 1rem;
          box-shadow: 0 10px 24px rgba(0,0,0,0.06);
        }
        .card-body {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .avatar {
          width: 56px;
          height: 56px;
          border-radius: 16px;
          background: #E8DAEF;
          color: var(--primary-color, #7D3C98);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        .content { flex: 1; }
        .title-row { display: flex; align-items: center; justify-content: space-between; }
        .title { margin: 0; font-weight: 700; display: flex; gap: 0.5rem; align-items: center; }
        .pill {
          font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.5rem; border-radius: 999px;
          background: #F4ECF7; color: var(--primary-color, #7D3C98);
        }
        .pill.video { background: #E8DAEF; }
        .pill.clinic { background: #E8F8F5; color: #16A085; }
        .pill.done { background: #EAFAF1; color: #2ECC71; }
        .status-line { color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem; }
        .info-line { display: flex; align-items: center; gap: 0.5rem; color: var(--text-secondary); font-size: 0.9rem; margin: 0.25rem 0; }
        .actions { display: grid; grid-template-columns: 1fr; gap: 0.5rem; margin-top: 0.75rem; }
        .action-btn {
          display: flex; align-items: center; gap: 0.5rem;
          background: #F5F7FA; border: 1px solid #E0E0E0; color: var(--text-primary);
          padding: 0.75rem; border-radius: 12px; cursor: pointer;
        }
        .refresh-btn {
          margin: 1rem auto; display: flex; align-items: center; gap: 0.5rem;
          background: var(--primary-color, #7D3C98); color: white; border: none;
          padding: 0.75rem 1.25rem; border-radius: 12px; font-weight: 700; cursor: pointer;
          box-shadow: 0 6px 16px rgba(125,60,152,0.25);
        }
        .message.error { background: #FADBD8; color: #C0392B; padding: 0.75rem 1rem; border-radius: 12px; }
        .loading { text-align: center; color: var(--text-secondary); padding: 2rem 0; }
      `}</style>
    </div>
  );
};
 
export default DoctorAppointments;
