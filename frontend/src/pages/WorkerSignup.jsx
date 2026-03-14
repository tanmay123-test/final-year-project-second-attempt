import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { doctorService, workerService } from '../services/api';
import { Stethoscope, Home, Package, Car, Wallet, User, Mail, Phone, MapPin, Briefcase, Loader2, ChevronLeft, BadgeCheck, Lock } from 'lucide-react';

const SERVICE_CONFIG = {
  healthcare: { label: 'Healthcare', icon: Stethoscope, color: '#8E44AD' },
  housekeeping: { label: 'Housekeeping', icon: Home, color: '#E67E22' },
  resource: { label: 'Resource Management', icon: Package, color: '#3498DB' },
  car: { label: 'Car Services', icon: Car, color: '#9B59B6' },
  money: { label: 'Money Management', icon: Wallet, color: '#2ECC71' }
};

const WorkerSignup = ({ serviceType = 'healthcare' }) => {
  const config = SERVICE_CONFIG[serviceType] || SERVICE_CONFIG.healthcare;
  const ServiceIcon = config.icon;

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    specialization: '',
    experience: '',
    clinic_location: '',
    service: serviceType,
    license_number: '',
    password: ''
  });
  const [specializations, setSpecializations] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (serviceType === 'healthcare') {
      const fetchSpecs = async () => {
        try {
          const res = await doctorService.getSpecializations();
          setSpecializations(res.data.specializations);
        } catch (err) {
          console.error("Failed to load specializations", err);
        }
      };
      fetchSpecs();
    }
  }, [serviceType]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    
    try {
      const payload = { ...formData, service: serviceType };
      let response;
      if (serviceType === 'healthcare') {
        response = await workerService.registerHealthcare(payload);
      } else {
        response = await workerService.register(payload);
      }
      setSuccess(`Registration successful! Your ID is ${response.data.worker_id}.`);
      setTimeout(() => navigate(`/worker/${serviceType}/login`), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  const isHealthcare = serviceType === 'healthcare';

  return (
    <div className="auth-container-wrapper">
      <div className="auth-container" style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', top: '1.5rem', left: '1.5rem' }}>
          <Link to="/" className="back-button-circle" style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            width: '40px', 
            height: '40px', 
            borderRadius: '50%', 
            background: '#F5F7FA', 
            color: '#2C3E50',
            textDecoration: 'none'
          }}>
            <ChevronLeft size={24} />
          </Link>
        </div>

        <div className="auth-header" style={{ marginTop: '2rem' }}>
           <div className="auth-icon">
            <ServiceIcon size={32} strokeWidth={2} color="white" />
          </div>
          <h2 className="auth-title">
            {isHealthcare ? 'Join as a Doctor' : `Join as ${config.label} Pro`}
          </h2>
          <p className="auth-subtitle">
            {isHealthcare ? 'Register to provide healthcare services' : 'Create your account to start providing services'}
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        {!success && (
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="input-group">
              <label htmlFor="full_name">Full Name</label>
              <div className="input-wrapper">
                <User className="input-icon" size={20} />
                <input id="full_name" name="full_name" value={formData.full_name} onChange={handleChange} required placeholder={isHealthcare ? "Dr. John Doe" : "John Doe"} />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="email">Email</label>
              <div className="input-wrapper">
                <Mail className="input-icon" size={20} />
                <input id="email" type="email" name="email" value={formData.email} onChange={handleChange} required placeholder="doctor@example.com" />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="phone">Phone</label>
              <div className="input-wrapper">
                <Phone className="input-icon" size={20} />
                <input id="phone" type="tel" name="phone" value={formData.phone} onChange={handleChange} required placeholder="9876543210" />
              </div>
            </div>

            {serviceType === 'healthcare' && (
              <div className="input-group">
                <label htmlFor="specialization">Specialization</label>
                <div className="input-wrapper">
                  <Briefcase className="input-icon" size={20} />
                  <select id="specialization" name="specialization" value={formData.specialization} onChange={handleChange} required className="custom-select">
                    <option value="">Select specialization</option>
                    {specializations.map(spec => (
                      <option key={spec} value={spec}>{spec}</option>
                    ))}
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            )}

            <div className="input-group">
              <label htmlFor="experience">Experience (years)</label>
              <div className="input-wrapper">
                <Briefcase className="input-icon" size={20} />
                <input id="experience" type="number" name="experience" value={formData.experience} onChange={handleChange} required min="0" placeholder="5" />
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="clinic_location">{serviceType === 'healthcare' ? 'Clinic Location' : 'Base Location'}</label>
              <div className="input-wrapper">
                <MapPin className="input-icon" size={20} />
                <input id="clinic_location" name="clinic_location" value={formData.clinic_location} onChange={handleChange} placeholder={isHealthcare ? "Apollo Hospital, Delhi" : "City, Area"} />
              </div>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <><Loader2 className="animate-spin" size={20} /> Registering...</> : 'Register'}
            </button>
          </form>
        )}
        
        <div className="auth-footer">
          <p>
            Already registered? 
            <Link to={`/worker/${serviceType}/login`} className="auth-link">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default WorkerSignup;
