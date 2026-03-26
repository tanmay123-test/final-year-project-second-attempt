import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/DoctorLogin.css';

const DoctorLogin = () => {
  const [formData, setFormData] = useState({
    email: 'doctor@expertease.com',
    password: 'doctor123'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState('checking...');
  const navigate = useNavigate();

  // Check backend status on component mount
  React.useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/`);
      if (response.ok) {
        setBackendStatus('✅ Backend is running');
      } else {
        setBackendStatus('⚠️ Backend responding but may have issues');
      }
    } catch (error) {
      setBackendStatus('❌ Backend is not running - Please start the backend server');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    console.log('Attempting login with:', { email: formData.email, password: '***' });

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/doctor/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      console.log('Login response status:', response.status);
      
      const data = await response.json();
      console.log('Login response data:', data);

      if (response.ok) {
        // Store token
        localStorage.setItem('doctorToken', data.token);
        localStorage.setItem('doctorInfo', JSON.stringify({
          id: data.doctor_id,
          name: data.name,
          service: data.service,
          specialization: data.specialization
        }));
        
        console.log('Login successful, redirecting to dashboard...');
        // Redirect to healthcare dashboard instead of doctor dashboard
        navigate('/healthcare/home');
      } else {
        console.error('Login failed:', data.error);
        setError(data.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please make sure the backend server is running on localhost:5000');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="doctor-login-container">
      <div className="doctor-login-card">
        {/* Header */}
        <div className="doctor-login-header">
          <div className="doctor-login-logo">
            <span style={{ fontSize: '32px' }}>🏥</span>
          </div>
          <h1>Doctor Portal</h1>
          <p>Sign in to manage your practice</p>
          
          {/* Backend Status */}
          <div style={{ 
            marginTop: '10px', 
            padding: '8px 12px', 
            borderRadius: '6px', 
            fontSize: '12px',
            backgroundColor: backendStatus.includes('✅') ? '#d4edda' : backendStatus.includes('❌') ? '#f8d7da' : '#fff3cd',
            color: backendStatus.includes('✅') ? '#155724' : backendStatus.includes('❌') ? '#721c24' : '#856404',
            border: backendStatus.includes('✅') ? '1px solid #c3e6cb' : backendStatus.includes('❌') ? '1px solid #f5c6cb' : '1px solid #ffeaa7',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>{backendStatus}</span>
            <button 
              type="button"
              onClick={checkBackendStatus}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '10px',
                cursor: 'pointer',
                textDecoration: 'underline'
              }}
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Test Credentials Info */}
        <div style={{ 
          margin: '15px 0', 
          padding: '10px', 
          backgroundColor: '#e7f3ff', 
          borderRadius: '6px', 
          fontSize: '12px',
          border: '1px solid #b3d9ff'
        }}>
          <strong>🔑 Test Credentials:</strong><br/>
          Email: doctor@expertease.com<br/>
          Password: doctor123
        </div>

        {/* Form */}
        <form className="doctor-login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="doctor@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="doctor-login-btn"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Footer */}
        <div className="doctor-login-footer">
          <p>
            Don't have an account?{' '}
            <a href="/worker/healthcare/signup">Sign up</a>
          </p>
          <a href="/worker/healthcare/signup" className="signup-link">
            Create Doctor Account →
          </a>
        </div>
      </div>
    </div>
  );
};

export default DoctorLogin;
