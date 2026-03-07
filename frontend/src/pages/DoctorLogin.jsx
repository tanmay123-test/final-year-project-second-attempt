import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Stethoscope, Loader2, ChevronLeft, Mail } from 'lucide-react';

const DoctorLogin = () => {
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
      navigate('/doctor/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to login. Please check your email.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container-wrapper">
      <div className="auth-container" style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', top: '1.5rem', left: '1.5rem' }}>
          <Link to="/provide-service" className="back-button-circle" style={{ 
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
           <div className="auth-icon" style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)' }}>
            <Stethoscope size={32} strokeWidth={2} color="white" />
          </div>
          <h2 className="auth-title">Doctor Portal</h2>
          <p className="auth-subtitle">
            Login with your registered email
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
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
          
          <button type="submit" className="btn-primary" disabled={loading} style={{ background: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)' }}>
            {loading ? <><Loader2 className="animate-spin" size={20} /> Verifying...</> : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Not registered as a doctor?{' '}
            <Link to="/worker/healthcare/signup" className="auth-link" style={{ color: '#8E44AD' }}>
              Apply here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default DoctorLogin;
