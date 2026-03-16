import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { doctorService } from '../../../services/api';
import DoctorBottomNav from '../../../components/DoctorBottomNav';
import { ChevronLeft, User, Star, ShieldCheck } from 'lucide-react';

const DoctorProfileDetails = () => {
  const navigate = useNavigate();
  const { worker } = useAuth();
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      if (!worker?.worker_id) return;
      try {
        const res = await doctorService.getDoctorById(worker.worker_id);
        setDoc(res.data.worker || {});
      } catch (e) {
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [worker]);

  const displayName = doc?.full_name || doc?.name || (worker?.email || 'Doctor');
  const statusLabel = String(doc?.status || 'Pending');
  const isApproved = statusLabel.toLowerCase() === 'approved';

  return (
    <div className="doctor-details-page">
      <div className="details-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <ChevronLeft size={20} />
          <span>Back</span>
        </button>
        <div className="title-row">
          <User size={22} className="title-icon" />
          <h1>Doctor Profile</h1>
        </div>
      </div>

      <div className="content-wrap">
        <div className="details-card">
          <div className="row">
            <span className="label">Name</span>
            <span className="value">{displayName}</span>
          </div>
          <div className="row">
            <span className="label">Email</span>
            <span className="value">{doc?.email || worker?.email || '—'}</span>
          </div>
          <div className="row">
            <span className="label">Specialization</span>
            <span className="value">{doc?.specialization || '—'}</span>
          </div>
          <div className="row">
            <span className="label">Experience</span>
            <span className="value">{doc?.experience ? `${doc.experience} years` : '—'}</span>
          </div>
          <div className="row">
            <span className="label">Clinic Location</span>
            <span className="value">{doc?.clinic_location || '—'}</span>
          </div>
          <div className="row">
            <span className="label">Rating</span>
            <span className="value rating">
              <Star size={16} color="#F1C40F" fill="#F1C40F" />
              <span>{doc?.rating || '4.9'}</span>
            </span>
          </div>
          <div className="row">
            <span className="label">Worker ID</span>
            <span className="value">{doc?.id ? `DOC${String(doc.id).padStart(3, '0')}` : '—'}</span>
          </div>
          <div className="row">
            <span className="label">Verification</span>
            <span className={`value status ${isApproved ? 'approved' : 'pending'}`}>
              {isApproved ? <ShieldCheck size={16} /> : null}
              <span>{statusLabel.charAt(0).toUpperCase() + statusLabel.slice(1)}</span>
            </span>
          </div>
        </div>
      </div>

      <DoctorBottomNav />

      <style>{`
        .doctor-details-page {
          background-color: var(--background-light);
          min-height: 100vh;
          padding-bottom: 90px;
          font-family: 'Inter', sans-serif;
        }
        .details-header {
          background: var(--medical-gradient);
          padding: 1.5rem 1.5rem 2rem;
          border-bottom-left-radius: 30px;
          border-bottom-right-radius: 30px;
          color: white;
        }
        .back-btn {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          background: transparent;
          border: none;
          color: white;
          cursor: pointer;
          margin-bottom: 0.75rem;
        }
        .title-row {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .title-row h1 {
          font-size: 1.25rem;
          font-weight: 700;
          margin: 0;
        }
        .title-icon {
          opacity: 0.9;
        }
        .content-wrap {
          padding: 1.5rem;
          margin-top: -1.25rem;
        }
        .details-card {
          background: white;
          border-radius: 20px;
          padding: 1rem 1.25rem;
          box-shadow: var(--shadow-sm);
        }
        .row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          padding: 0.75rem 0;
          border-bottom: 1px solid #EEF2F7;
          align-items: center;
        }
        .row:last-child {
          border-bottom: none;
        }
        .label {
          color: var(--text-secondary);
          font-weight: 600;
        }
        .value {
          text-align: right;
          color: var(--text-primary);
          font-weight: 600;
        }
        .rating {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          justify-content: flex-end;
        }
        .status {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          justify-content: flex-end;
        }
        .status.approved {
          color: #27AE60;
        }
        .status.pending {
          color: #E67E22;
        }
        @media (min-width: 768px) {
          .content-wrap {
            max-width: 640px;
            margin: -1.25rem auto 0;
          }
        }
      `}</style>
    </div>
  );
};

export default DoctorProfileDetails;
