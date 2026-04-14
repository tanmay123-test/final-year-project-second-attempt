import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Stethoscope,
  Award,
  MapPin,
  CheckCircle2,
} from 'lucide-react';
import api from '../../../shared/api';
import './WorkerPortal.css';
import './WorkerSignupResponsive.css';

const WorkerSignupPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successData, setSuccessData] = useState(null);
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    specialization: '',
    experience: '',
    clinic_location: '',
    license_number: '',
    password: '',
  });

  // Add these state variables
  const [profilePhoto, setProfilePhoto] = useState(null)
  const [aadhaarCard, setAadhaarCard] = useState(null)
  const [degreeCertificate, setDegreeCertificate] = useState(null)
  const [medicalLicense, setMedicalLicense] = useState(null)

  const onChange = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const formData = new FormData()
      formData.append('full_name', form.full_name)
      formData.append('email', form.email)
      formData.append('phone', form.phone)
      formData.append('specialization', form.specialization)
      formData.append('experience', form.experience)
      formData.append('clinic_location', form.clinic_location)
      formData.append('license_number', form.license_number)
      formData.append('password', form.password)
      formData.append('profile_photo', profilePhoto)
      formData.append('aadhaar', aadhaarCard)
      formData.append('degree_certificate', degreeCertificate)
      formData.append('medical_license', medicalLicense)

      const { data } = await api.post('/worker/healthcare/signup', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setSuccessData({
        worker_id: data.worker_id || data.id || data.worker?.worker_id,
        worker_token: data.token || data.worker_token || data.access_token,
      });
    } catch (err) {
      setError(err?.response?.data?.error || 'Failed to register worker.');
    } finally {
      setLoading(false);
    }
  };

  const onGoDashboard = () => {
    if (successData?.worker_id) localStorage.setItem('worker_id', String(successData.worker_id));
    if (successData?.worker_token) localStorage.setItem('worker_token', String(successData.worker_token));
    navigate('/worker/dashboard');
  };

  return (
    <div className="wp-page">
      <div className="wp-mobile-shell">
        <div className="wp-dark-header">
          <div className="wp-header-row">
            <button className="wp-back-btn" onClick={() => navigate('/worker/healthcare/login')}>
              <ArrowLeft size={18} />
            </button>
            <div className="wp-header-title">Register as Doctor</div>
          </div>
        </div>

        <div className="wp-form-card wp-card">
          {!successData ? (
            <form onSubmit={onSubmit}>
              <div className="wp-section-title">Personal Details</div>
              <div className="wp-field">
                <label className="wp-label">Full Name</label>
                <div className="wp-input-wrap">
                  <User className="wp-input-icon" size={18} />
                  <input className="wp-input" placeholder="Dr. Full Name" value={form.full_name} onChange={(e) => onChange('full_name', e.target.value)} required />
                </div>
              </div>
              <div className="wp-field">
                <label className="wp-label">Email Address</label>
                <div className="wp-input-wrap">
                  <Mail className="wp-input-icon" size={18} />
                  <input type="email" className="wp-input" placeholder="doctor@email.com" value={form.email} onChange={(e) => onChange('email', e.target.value)} required />
                </div>
              </div>
              <div className="wp-field">
                <label className="wp-label">Phone Number</label>
                <div className="wp-input-wrap">
                  <Phone className="wp-input-icon" size={18} />
                  <input type="tel" className="wp-input" placeholder="9999999999" value={form.phone} onChange={(e) => onChange('phone', e.target.value)} required />
                </div>
              </div>

              <div className="wp-section-title" style={{ marginTop: 20 }}>Professional Details</div>
              <div className="wp-field">
                <label className="wp-label">Specialization</label>
                <div className="wp-input-wrap">
                  <Stethoscope className="wp-input-icon" size={18} color="#9B59B6" />
                  <input className="wp-input" placeholder="e.g. Cardiologist, Dentist, General Physician" value={form.specialization} onChange={(e) => onChange('specialization', e.target.value)} required />
                </div>
              </div>
              <div className="wp-field">
                <label className="wp-label">Experience (Years)</label>
                <div className="wp-input-wrap">
                  <Award className="wp-input-icon" size={18} />
                  <input type="number" className="wp-input" placeholder="5" value={form.experience} onChange={(e) => onChange('experience', e.target.value)} required />
                </div>
              </div>
              <div className="wp-field">
                <label className="wp-label">Clinic Location</label>
                <div className="wp-input-wrap">
                  <MapPin className="wp-input-icon" size={18} />
                  <input className="wp-input" placeholder="e.g. Mumbai, Andheri West" value={form.clinic_location} onChange={(e) => onChange('clinic_location', e.target.value)} required />
                </div>
              </div>
              <div className="wp-field">
                <label className="wp-label">License Number</label>
                <div className="wp-input-wrap">
                  <Award className="wp-input-icon" size={18} />
                  <input className="wp-input" placeholder="Medical License Number" value={form.license_number} onChange={(e) => onChange('license_number', e.target.value)} required />
                </div>
              </div>
              <div className="wp-field">
                <label className="wp-label">Password</label>
                <div className="wp-input-wrap">
                  <User className="wp-input-icon" size={18} />
                  <input type="password" className="wp-input" placeholder="Create Password" value={form.password} onChange={(e) => onChange('password', e.target.value)} required />
                </div>
              </div>

              <div className="wp-section-title" style={{ marginTop: 20 }}>Document Upload</div>
              
              <div className="wp-field">
                <label className="wp-label">Profile Photo *</label>
                <input 
                  type="file" 
                  accept="image/*"
                  onChange={e => setProfilePhoto(e.target.files[0])}
                  className="wp-input"
                  required
                />
              </div>

              <div className="wp-field">
                <label className="wp-label">Aadhaar Card *</label>
                <input 
                  type="file" 
                  accept=".pdf,image/*"
                  onChange={e => setAadhaarCard(e.target.files[0])}
                  className="wp-input"
                  required
                />
              </div>

              <div className="wp-field">
                <label className="wp-label">Degree Certificate *</label>
                <input 
                  type="file" 
                  accept=".pdf,image/*"
                  onChange={e => setDegreeCertificate(e.target.files[0])}
                  className="wp-input"
                  required
                />
              </div>

              <div className="wp-field">
                <label className="wp-label">Medical License *</label>
                <input 
                  type="file" 
                  accept=".pdf,image/*"
                  onChange={e => setMedicalLicense(e.target.files[0])}
                  className="wp-input"
                  required
                />
              </div>

              <div className="wp-info-box">
                {'\u2713'} Registration submitted for admin approval.
                <br />
                You will be notified once your account is approved.
              </div>

              <button className="wp-primary-btn" type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Worker Account'}
              </button>
              {error ? <div className="wp-error-banner" style={{ margin: '10px 0 0' }}>{error}</div> : null}
            </form>
          ) : (
            <div style={{ textAlign: 'center', padding: '12px 0' }}>
              <div style={{ width: 56, height: 56, borderRadius: '50%', margin: '0 auto', background: '#DCFCE7', color: '#16A34A', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={28} />
              </div>
              <h2 style={{ margin: '14px 0 0', color: '#0f172a' }}>Registration Submitted!</h2>
              <div style={{ marginTop: 8, color: '#8E44AD', fontSize: 16, fontWeight: 600 }}>
                Worker ID: {successData.worker_id || 'N/A'}
              </div>
              <div style={{ marginTop: 8, color: '#F59E0B', fontSize: 14 }}>
                Status: ⏳ Pending Admin Approval
              </div>
              <div style={{ marginTop: 12, color: '#64748b', fontSize: 13 }}>
                Please wait for admin to review and approve your application.
              </div>
              <button className="wp-primary-btn" style={{ marginTop: 16 }} onClick={() => navigate('/worker/healthcare/login')}>
                Back to Login
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkerSignupPage;

