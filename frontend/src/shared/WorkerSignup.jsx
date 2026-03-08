import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { doctorService, workerService, housekeepingService } from '../shared/api';
import { Stethoscope, Home, Car, Wallet, User, Mail, Phone, MapPin, Briefcase, Loader2, ChevronLeft, BadgeCheck, Lock, CreditCard } from 'lucide-react';

const SERVICE_CONFIG = {
  healthcare: { label: 'Healthcare', icon: Stethoscope, color: '#8E44AD' },
  housekeeping: { label: 'Housekeeping', icon: Home, color: '#8E44AD' },
  freelance: { label: 'Freelance Marketplace', icon: Briefcase, color: '#7c3aed' },
  car: { label: 'Car Services', icon: Car, color: '#9B59B6' },
  money: { label: 'Money Management', icon: Wallet, color: '#2ECC71' }
};

const WorkerSignup = ({ serviceType = 'healthcare' }) => {
  const config = SERVICE_CONFIG[serviceType] || SERVICE_CONFIG.healthcare;
  const ServiceIcon = config.icon;

  const isPurple = config.color === '#8E44AD';
  const bgStyle = { background: isPurple ? 'var(--medical-gradient)' : config.color };

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    specialization: '',
    experience: '',
    clinic_location: '',
    service: serviceType,
    license_number: '',
    password: '',
    aadhaar: '',
    skills: '',
    hourly_rate: '',
    bio: '',
    id_proof: ''
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
    } else if (serviceType === 'housekeeping') {
      const fetchServices = async () => {
        try {
          const res = await housekeepingService.getServices();
          // Extract service names from the response
          const services = res.data.services.map(s => s.name);
          setSpecializations(services);
        } catch (err) {
          console.error("Failed to load housekeeping services", err);
          // Fallback if API fails
          setSpecializations(['General Cleaning', 'Deep Cleaning', 'Kitchen Cleaning', 'Bathroom Cleaning']);
        }
      };
      fetchServices();
    }
  }, [serviceType]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSpecializationChange = (e) => {
    const { value, checked } = e.target;
    let currentSpecs = formData.specialization ? formData.specialization.split(',').filter(s => s) : [];
    
    if (checked) {
      if (!currentSpecs.includes(value)) {
        currentSpecs.push(value);
      }
    } else {
      currentSpecs = currentSpecs.filter(spec => spec !== value);
    }
    
    setFormData({ ...formData, specialization: currentSpecs.join(',') });
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
      } else if (serviceType === 'freelance') {
        // Direct call to freelance signup endpoint
        response = await axios.post('http://127.0.0.1:5000/worker/freelance/signup', payload);
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
           <div className="auth-icon" style={bgStyle}>
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
            {serviceType === 'freelance' && (
              <>
                <div className="input-group">
                  <label htmlFor="skills">Professional Skills</label>
                  <div className="input-wrapper">
                    <Briefcase className="input-icon" size={20} />
                    <input id="skills" name="skills" value={formData.skills} onChange={handleChange} required placeholder="React, Node.js, UI/UX" />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="hourly_rate">Hourly Rate (₹)</label>
                  <div className="input-wrapper">
                    <CreditCard className="input-icon" size={20} />
                    <input id="hourly_rate" type="number" name="hourly_rate" value={formData.hourly_rate} onChange={handleChange} required placeholder="1500" />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="bio">Professional Bio</label>
                  <div className="input-wrapper">
                    <User className="input-icon" size={20} />
                    <textarea id="bio" name="bio" value={formData.bio} onChange={handleChange} required placeholder="Describe your expertise..." style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb', minHeight: '80px' }} />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="aadhaar">Aadhaar Card Number</label>
                  <div className="input-wrapper">
                    <BadgeCheck className="input-icon" size={20} />
                    <input id="aadhaar" name="aadhaar" value={formData.aadhaar} onChange={handleChange} required placeholder="12-digit Aadhaar Number" />
                  </div>
                </div>

                <div className="input-group">
                  <label htmlFor="id_proof">Aadhaar Card Image (URL for now)</label>
                  <div className="input-wrapper">
                    <Mail className="input-icon" size={20} />
                    <input id="id_proof" name="id_proof" value={formData.id_proof} onChange={handleChange} placeholder="Upload to UI later or paste URL" />
                  </div>
                </div>
              </>
            )}

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

            {serviceType === 'housekeeping' && (
              <div className="input-group">
                <label>Specializations (Select all that apply)</label>
                <div 
                  className="input-wrapper" 
                  style={{ 
                    flexDirection: 'column', 
                    alignItems: 'flex-start', 
                    padding: '12px',
                    height: 'auto',
                    minHeight: '48px'
                  }}
                >
                  {specializations.length > 0 ? specializations.map(spec => (
                    <label key={spec} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', width: '100%', cursor: 'pointer', fontSize: '14px' }}>
                      <input
                        type="checkbox"
                        value={spec}
                        checked={formData.specialization ? formData.specialization.split(',').includes(spec) : false}
                        onChange={handleSpecializationChange}
                        style={{ marginRight: '10px', width: '16px', height: '16px', accentColor: config.color }}
                      />
                      {spec}
                    </label>
                  )) : <div style={{color: '#999'}}>Loading services...</div>}
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

            <button type="submit" className="btn-primary" disabled={loading} style={bgStyle}>
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Registering...</span>
                </>
              ) : (
                <span>Register</span>
              )}
            </button>
          </form>
        )}
        
        <div className="auth-footer">
          <p>
            Already registered? 
            <Link to={`/worker/${serviceType}/login`} className="auth-link" style={{ color: config.color }}>Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default WorkerSignup;
