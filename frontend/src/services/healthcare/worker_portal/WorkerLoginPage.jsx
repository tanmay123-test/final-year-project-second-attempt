import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Stethoscope, Loader2, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import './WorkerPortal.css';

const WorkerLoginPage = () => {
  const navigate = useNavigate();
  const { workerLogin } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await workerLogin(email, password, 'healthcare');
      navigate('/worker/dashboard');
    } catch (err) {
      setError(err?.response?.data?.error || 'Worker not found. Please check your credentials or sign up.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wp-page">
      <div className="wp-mobile-shell">
        <div className="wp-dark-header">
          <div className="wp-header-row">
            <button className="wp-back-btn" onClick={() => navigate('/worker')}>
              <ArrowLeft size={18} />
            </button>
            <div className="wp-header-title">Doctor Login</div>
          </div>
        </div>

        <div className="wp-form-card wp-card" style={{ padding: 24 }}>
          <div style={{ width: 56, height: 56, margin: '0 auto', borderRadius: '50%', background: '#F5F3FF', color: '#8E44AD', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Stethoscope size={28} />
          </div>
          <h2 style={{ textAlign: 'center', color: '#0f172a', marginBottom: 4 }}>Welcome Back</h2>
          <p style={{ textAlign: 'center', fontSize: 13, color: '#64748b', marginTop: 0, marginBottom: 24 }}>Enter your registered email</p>

          <form onSubmit={onLogin}>
            <div className="wp-field">
              <label className="wp-label">Email Address</label>
              <div className="wp-input-wrap">
                <Mail className="wp-input-icon" size={18} />
                <input type="email" className="wp-input" placeholder="doctor@email.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
            </div>

            <div className="wp-field" style={{ marginTop: 16 }}>
              <label className="wp-label">Password</label>
              <div className="wp-input-wrap">
                <Lock className="wp-input-icon" size={18} />
                <input 
                  type={showPassword ? "text" : "password"} 
                  className="wp-input" 
                  placeholder="••••••••" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <button className="wp-primary-btn" style={{ marginTop: 20 }} type="submit" disabled={loading}>
              {loading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : 'Log In'}
            </button>
            {error ? <div className="wp-error-banner" style={{ margin: '12px 0 0' }}>{error}</div> : null}
          </form>

          <div style={{ marginTop: 14, fontSize: 14, color: '#64748b', textAlign: 'center' }}>
            New here?{' '}
            <button onClick={() => navigate('/worker/signup')} style={{ border: 'none', background: 'none', color: '#8E44AD', textDecoration: 'underline', cursor: 'pointer' }}>
              Register as a Doctor
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkerLoginPage;

