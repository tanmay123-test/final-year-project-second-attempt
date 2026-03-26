import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/DoctorLogin.css';

const DoctorLogin = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

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

    try {
      const response = await fetch('http://localhost:5000/doctor/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Store token
        localStorage.setItem('doctorToken', data.token);
        localStorage.setItem('doctorInfo', JSON.stringify({
          id: data.doctor_id,
          name: data.name,
          service: data.service,
          specialization: data.specialization
        }));
        
        // Redirect to doctor dashboard
        navigate('/doctor/dashboard');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
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
