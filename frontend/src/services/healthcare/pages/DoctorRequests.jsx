import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { workerService } from '../../../services/api';
import DoctorBottomNav from '../../../components/DoctorBottomNav';
import { FileText, User, Calendar as CalendarIcon, RefreshCcw } from 'lucide-react';
import { Link } from 'react-router-dom';
 
const DoctorRequests = () => {
  const { worker } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
 
  const fetchRequests = async () => {
    if (!worker?.worker_id) return;
    setLoading(true);
    setError('');
    try {
      // fetch all appointments for full status visibility
      const res = await workerService.getAppointments(worker.worker_id);
      setRequests(res.data.appointments || []);
    } catch (e) {
      console.error('Failed to load requests', e);
      setError(e.response?.data?.error || 'Failed to load requests');
    } finally {
      setLoading(false);
    }
  };
 
  useEffect(() => {
    fetchRequests();
  }, [worker]);
 
  const formatType = (t) => t === 'video' ? 'VIDEO' : 'CLINIC';
  const pendingCount = requests.filter(r => r.status === 'pending').length;
  
  const respond = async (id, status) => {
    try {
      await workerService.respondToRequest({ appointment_id: id, status });
      fetchRequests();
    } catch (e) {
      alert(e.response?.data?.error || 'Failed to update request');
    }
  };
 
  return (
    <div className="doctor-requests-page">
      <div className="page-header">
        <div className="header-content">
          <FileText size={28} />
          <div>
            <h1 className="page-title">Requests</h1>
            <p className="page-subtitle">Pending Requests: {pendingCount}</p>
          </div>
        </div>
      </div>
 
      <div className="content-container">
        {error && <div className="message error">{error}</div>}
        {loading ? (
          <div className="loading">Loading requests...</div>
        ) : requests.length === 0 ? (
          <div className="empty">No pending requests</div>
        ) : (
          <div className="requests-list">
            {requests.map((r) => (
              <div key={r.id} className="request-card">
                <div className="request-title-row">
                  <h3 className="request-title">Appointment #{r.id}</h3>
                  <span className={`type-pill ${r.appointment_type === 'video' ? 'video' : 'clinic'}`}>
                    {formatType(r.appointment_type)}
                  </span>
                </div>
                <div className="request-row">
                  <User size={16} />
                  <span>Patient: {r.user_name}</span>
                </div>
                <div className="request-row">
                  <CalendarIcon size={16} />
                  <span>Date: {r.booking_date}</span>
                </div>
                <div className="symptoms-box">
                  Symptoms: {r.patient_symptoms || 'N/A'}
                </div>
                {r.status === 'pending' ? (
                  <div className="actions">
                    <button className="btn-accept" onClick={() => respond(r.id, 'accepted')}>Accept</button>
                    <button className="btn-reject" onClick={() => respond(r.id, 'rejected')}>Reject</button>
                  </div>
                ) : (
                  <div className={`status-pill ${r.status}`}>
                    {String(r.status || '').toUpperCase()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
 
        <button className="refresh-btn" onClick={fetchRequests}>
          <RefreshCcw size={18} /> Refresh
        </button>
      </div>
 
      <DoctorBottomNav />
 
      <style>{`
        .doctor-requests-page {
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
          gap: 0.75rem;
          max-width: 600px;
          margin: 0 auto;
        }
        .page-title {
          margin: 0;
          font-size: 1.4rem;
          font-weight: 700;
        }
        .page-subtitle {
          margin: 0;
          opacity: 0.9;
        }
        .content-container {
          padding: 1.5rem;
          max-width: 600px;
          margin: -2rem auto 0;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .message.error {
          background: #FADBD8;
          color: #C0392B;
          padding: 0.75rem 1rem;
          border-radius: 12px;
        }
        .loading, .empty {
          text-align: center;
          color: var(--text-secondary);
          padding: 2rem 0;
        }
        .requests-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .request-card {
          background: white;
          border-radius: 16px;
          padding: 1rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .request-title-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 0.5rem;
        }
        .request-title {
          margin: 0;
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        .type-pill {
          font-size: 0.75rem;
          font-weight: 700;
          padding: 0.25rem 0.5rem;
          border-radius: 999px;
          background: #F4ECF7;
          color: var(--primary-color, #7D3C98);
        }
        .type-pill.video {
          background: #E8DAEF;
        }
        .type-pill.clinic {
          background: #E8F8F5;
          color: #16A085;
        }
        .request-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: var(--text-secondary);
          font-size: 0.9rem;
          margin: 0.25rem 0;
        }
        .symptoms-box {
          margin-top: 0.5rem;
          background: #F5F7FA;
          border: 1px solid #E0E0E0;
          border-radius: 12px;
          padding: 0.75rem;
          color: var(--text-secondary);
          font-size: 0.9rem;
        }
        .refresh-btn {
          align-self: center;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: var(--primary-color, #7D3C98);
          color: white;
          border: none;
          padding: 0.75rem 1.25rem;
          border-radius: 12px;
          font-weight: 700;
          cursor: pointer;
          box-shadow: 0 6px 16px rgba(125,60,152,0.25);
        }
        .actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 0.75rem;
        }
        .btn-accept, .btn-reject {
          border: 1px solid #E0E0E0;
          background: #F5F7FA;
          color: var(--text-primary);
          padding: 0.5rem 0.75rem;
          border-radius: 10px;
          font-weight: 700;
          cursor: pointer;
        }
        .btn-accept { border-color: #2ECC71; color: #2ECC71; }
        .btn-reject { border-color: #C0392B; color: #C0392B; }
        .status-pill {
          margin-top: 0.75rem;
          display: inline-block;
          font-size: 0.75rem;
          font-weight: 700;
          padding: 0.25rem 0.5rem;
          border-radius: 999px;
          background: #F5F7FA;
          border: 1px solid #E0E0E0;
          color: var(--text-secondary);
        }
        .status-pill.accepted { background: #EAFAF1; border-color: #2ECC71; color: #2ECC71; }
        .status-pill.rejected { background: #FADBD8; border-color: #C0392B; color: #C0392B; }
      `}</style>
    </div>
  );
};
 
export default DoctorRequests;
