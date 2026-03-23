import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Eye, EyeOff, User, Lock, Mail, Phone, AlertCircle, ArrowLeft, Award } from 'lucide-react';
import api from '../../shared/api';

const AutomobileExpertAuth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    experience_years: '',
    area_of_expertise: 'Engine',
    certificate_path: '',
    worker_type: 'automobile_expert'
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const endpoint = isLogin ? 'login' : 'signup';
      
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : {
            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            password: formData.password,
            experience_years: formData.experience_years,
            area_of_expertise: formData.area_of_expertise,
            certificate_path: formData.certificate_path,
            worker_type: formData.worker_type
          };

      const response = await api.post(`/api/automobile-expert/${endpoint}`, payload);

      const data = response.data;

      if (response.data) {
        if (isLogin) {
          console.log('AutomobileExpertAuth - Login response:', data);
          // The backend returns individual fields, not wrapped in a worker object
          const expertData = {
            id: data.worker_id,
            name: data.name,
            email: data.email,
            area_of_expertise: data.area_of_expertise,
            experience_years: data.experience_years,
            status: data.status,
            is_online: 0, // Default to offline
            approval_status: data.status
          };
          console.log('AutomobileExpertAuth - Storing expert data:', expertData);
          localStorage.setItem('automobileExpertToken', data.token);
          localStorage.setItem('automobileExpertData', JSON.stringify(expertData));
          setSuccess('Login successful! Redirecting...');
          setTimeout(() => {
            navigate('/worker/car/automobile-expert/home');
          }, 1500);
        } else {
          setSuccess('Registration successful! Please wait for admin approval.');
          setTimeout(() => {
            setIsLogin(true);
            setFormData({ ...formData, password: '', confirmPassword: '' });
          }, 3000);
        }
      } else {
        setError(data.message || data.error || 'Something went wrong');
      }
    } catch (error) {
      console.error('Auth error:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <style>{`
        .auth-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #DDD6FE 0%, #C4B5FD 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1rem;
          position: relative;
        }
        .auth-card {
          background: white;
          border-radius: 20px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.1);
          padding: 2rem;
          width: 90%;
          max-width: 600px;
          margin: 0 auto;
          z-index: 10;
        }
        .auth-header {
          text-align: center;
          margin-bottom: 2rem;
        }
        .auth-icon {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #DDD6FE 0%, #C4B5FD 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
          box-shadow: 0 8px 25px rgba(196, 181, 253, 0.3);
        }
        .auth-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }
        .auth-subtitle {
          color: #6b7280;
          font-size: 0.9rem;
        }
        .form-group {
          margin-bottom: 1.5rem;
        }
        .form-label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #374151;
        }
        .form-input {
          width: 100%;
          padding: 0.75rem 1rem;
          border: 1px solid #e5e7eb;
          border-radius: 10px;
          font-size: 0.95rem;
          transition: all 0.3s;
          pointer-events: auto !important;
          user-select: text !important;
          -webkit-user-select: text !important;
          -moz-user-select: text !important;
          -ms-user-select: text !important;
        }
        .form-input:focus {
          outline: none;
          border-color: #10b981;
          box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }
        .password-toggle {
          position: absolute;
          right: 1rem;
          top: 50%;
          transform: translateY(-50%);
          cursor: pointer;
          color: #6b7280;
        }
        .auth-button {
          width: 100%;
          padding: 0.875rem;
          background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        .auth-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
        }
        .auth-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
        }
        .auth-toggle {
          text-align: center;
          margin-top: 1.5rem;
          color: #6b7280;
        }
        .auth-toggle a {
          color: #10b981;
          text-decoration: none;
          font-weight: 600;
        }
        .error-message {
          background: #fef2f2;
          color: #dc2626;
          padding: 0.75rem;
          border-radius: 8px;
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }
        .success-message {
          background: #f0fdf4;
          color: #16a34a;
          padding: 0.75rem;
          border-radius: 8px;
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }

        .input-icon {
          position: relative;
        }
      `}</style>

      {/* Back Button */}
      <button 
        type="button" 
        className="back-button"
        onClick={() => navigate('/worker/car/services')}
        style={{ position: 'absolute', top: '2rem', left: '2rem', zIndex: 10, background: 'rgba(255, 255, 255, 0.2)', border: '1px solid rgba(255, 255, 255, 0.3)', borderRadius: '50%', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1f2937', cursor: 'pointer', backdropFilter: 'blur(10px)' }}
      >
        <ArrowLeft size={20} />
      </button>

      <div className="auth-card">

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <div className="input-icon">
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter your full name"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <div className="input-icon">
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="form-input"
                    placeholder="Enter your phone number"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Experience (years)</label>
                <input
                  type="number"
                  name="experience_years"
                  value={formData.experience_years}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Years of experience"
                  min="0"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Area of Expertise</label>
                <select
                  name="area_of_expertise"
                  value={formData.area_of_expertise}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                >
                  <option value="Engine">Engine</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Diagnostic">Diagnostic</option>
                  <option value="General">General</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Certificate Path</label>
                <input
                  type="text"
                  name="certificate_path"
                  value={formData.certificate_path}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Path to your certificate (optional)"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="input-icon">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="input-icon">
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="form-input"
                placeholder="Enter your password"
                required
              />
              <div className="password-toggle" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </div>
            </div>
          </div>

          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <div className="input-icon">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Confirm your password"
                  required
                />
              </div>
            </div>
          )}

          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>

        <div className="auth-toggle">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <a href="#" onClick={(e) => {
            e.preventDefault();
            setIsLogin(!isLogin);
            setError('');
            setSuccess('');
          }}>
            {isLogin ? 'Sign up' : 'Login'}
          </a>
        </div>
      </div>
    </div>
  );
};

export default AutomobileExpertAuth;
