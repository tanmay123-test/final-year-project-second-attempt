import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Stethoscope, Home, Package, Car, Wallet, Mail, Loader2, ChevronLeft } from 'lucide-react';

const SERVICE_CONFIG = {
  healthcare: { label: 'Healthcare', icon: Stethoscope, color: '#8E44AD' },
  housekeeping: { label: 'Housekeeping', icon: Home, color: '#E67E22' },
  resource: { label: 'Resource Management', icon: Package, color: '#3498DB' },
  car: { label: 'Car Services', icon: Car, color: '#9B59B6' },
  money: { label: 'Money Management', icon: Wallet, color: '#2ECC71' }
};

const WorkerLogin = ({ serviceType = 'healthcare' }) => {
  const config = SERVICE_CONFIG[serviceType] || SERVICE_CONFIG.healthcare;
  const ServiceIcon = config.icon;

  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { workerLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await workerLogin(email);
      navigate('/worker/dashboard'); // Generic dashboard for now
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to login. Please check your email or approval status.');
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
            {isHealthcare ? 'Doctor Portal' : `${config.label} Login`}
          </h2>
          <p className="auth-subtitle">
            {isHealthcare ? 'Login with your registered email' : 'Access your dashboard to manage requests'}
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label htmlFor="email">{isHealthcare ? 'Email Address' : 'Registered Email'}</label>
            <div className="input-wrapper">
              <Mail className="input-icon" size={20} />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="doctor@example.com"
              />
            </div>
          </div>
          
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? <><Loader2 className="animate-spin" size={20} /> Verifying...</> : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isHealthcare ? 'Not registered as a doctor? ' : 'New to ExpertEase? '}
            <Link to={`/worker/${serviceType}/signup`} className="auth-link">
              {isHealthcare ? 'Apply here' : 'Join as a Provider'}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default WorkerLogin;
