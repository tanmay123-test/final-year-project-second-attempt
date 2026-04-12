import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Stethoscope, Home, Briefcase, Car, Wallet, Mail, Loader2, ChevronLeft, Lock } from 'lucide-react';
import './WorkerLogin.css';

const SERVICE_CONFIG = {
  healthcare: { label: 'Healthcare', icon: Stethoscope, color: '#7C3AED' },
  housekeeping: { label: 'Housekeeping', icon: Home, color: '#7C3AED' },
  freelance: { label: 'Freelance Marketplace', icon: Briefcase, color: '#7C3AED' },
  car: { label: 'Car Services', icon: Car, color: '#7C3AED' },
  money: { label: 'Money Management', icon: Wallet, color: '#2ECC71' }
};

const WorkerLogin = ({ serviceType = 'healthcare' }) => {
  const config = SERVICE_CONFIG[serviceType] || SERVICE_CONFIG.healthcare;
  const ServiceIcon = config.icon;

  const isPurple = config.color === '#7C3AED';
  const bgStyle = { background: isPurple ? 'var(--medical-gradient)' : config.color };

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { workerLogin } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      // Use different login endpoints based on service type
      let loginUrl = 'http://localhost:5000/worker/login'
      if (serviceType === 'healthcare') {
        loginUrl = 'http://localhost:5000/worker/healthcare/login'
      }
      
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          password: password
        })
      })
      const data = await response.json()
      console.log('Login response:', data)
      console.log('Token received:', data.token)
      
      // Redirect to correct dashboard based on service type
      let dashboardPath = '/worker/dashboard'
      if (serviceType === 'housekeeping') {
        dashboardPath = '/worker/housekeeping/dashboard'
      } else if (serviceType === 'healthcare') {
        dashboardPath = '/worker/dashboard'
      } else if (serviceType === 'freelance') {
        dashboardPath = '/freelancer/dashboard'
      } else if (serviceType === 'car') {
        dashboardPath = '/worker/car/dashboard'
      } else if (serviceType === 'money') {
        dashboardPath = '/worker/money/dashboard'
      }
      
      console.log('Navigating to:', dashboardPath)
      
      if (data.token) {
        localStorage.setItem('workerToken', data.token)
        console.log('Token stored:', localStorage.getItem('workerToken'))
        localStorage.setItem('workerData', JSON.stringify(data.worker || {}))
        navigate(dashboardPath)
      } else {
        setError(data.error || 'Invalid email or password')
      }
    } catch (err) {
      setError('Cannot connect to server. Make sure backend is running.')
    } finally {
      setLoading(false)
    }
  }

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
            {isHealthcare ? 'Doctor Portal' : `${config.label} Login`}
          </h2>
          <p className="auth-subtitle">
            {isHealthcare ? 'Login with your registered email' : 'Access your dashboard to manage requests'}
          </p>
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleLogin} className="auth-form">
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
          
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={20} />
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </div>
          </div>
          
          <button 
            type="submit" 
            className="btn-primary" 
            disabled={loading}
            style={bgStyle}
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Signing in...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isHealthcare ? 'Not registered as a doctor? ' : 'New to ExpertEase? '}
            {isHealthcare ? (
              <span
                onClick={() => navigate('/worker/healthcare/signup')}
                style={{color:'#7C3AED', fontWeight:'600', cursor:'pointer'}}
              >
                Apply here
              </span>
            ) : (
              <Link to={`/worker/${serviceType}/signup`} className="auth-link" style={{ color: config.color }}>
                Join as a Provider
              </Link>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default WorkerLogin;
