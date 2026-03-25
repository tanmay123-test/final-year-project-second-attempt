import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Truck, Eye, EyeOff, User, Lock, Mail, Phone, AlertCircle, ArrowLeft } from 'lucide-react';
import api from '../../shared/api';

const TowTruckAuth = () => {
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
    city: '',
    experience: '',
    truck_type: 'Flatbed',
    truck_registration: '',
    truck_model: '',
    truck_capacity: 'Small Car',
    license_path: '',
    insurance_path: '',
    fitness_cert_path: '',
    pollution_cert_path: ''
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

    // Clear any existing tokens to avoid request interceptor interference
    localStorage.removeItem('token');
    localStorage.removeItem('workerToken');
    localStorage.removeItem('automobileExpertToken');

    try {
      const endpoint = isLogin ? 'login' : 'register';
      
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : {
            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            password: formData.password,
            city: formData.city,
            experience: formData.experience,
            truck_type: formData.truck_type,
            truck_registration: formData.truck_registration,
            truck_model: formData.truck_model,
            truck_capacity: formData.truck_capacity,
            license_path: formData.license_path || null,
            insurance_path: formData.insurance_path || null,
            fitness_cert_path: formData.fitness_cert_path || null,
            pollution_cert_path: formData.pollution_cert_path || null
          };

      const response = await api.post(`/api/tow-truck/${endpoint}`, payload);
      const data = response.data;

      if (data.success) {
        if (isLogin) {
          const operatorData = data.operator || data.worker;
          localStorage.setItem('workerToken', data.token);
          localStorage.setItem('workerData', JSON.stringify(operatorData));
          localStorage.setItem('workerId', operatorData.id.toString());
          
          setSuccess('Login successful! Redirecting...');
          setTimeout(() => {
            navigate('/worker/car/tow-truck/home');
          }, 1500);
        } else {
          setSuccess('Registration successful! You can now login.');
          setTimeout(() => {
            setIsLogin(true);
            setFormData({ ...formData, password: '', confirmPassword: '' });
          }, 3000);
        }
      } else {
        setError(data.error || 'Something went wrong');
      }
    } catch (error) {
      console.error('Auth error:', error);
      const message = error.response?.data?.error || error.response?.data?.message || 'Network error. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <style>{`
        .auth-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #059669 0%, #10b981 100%);
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
          background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
          box-shadow: 0 8px 25px rgba(167, 243, 208, 0.3);
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
          padding: 1rem 1.25rem;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          font-size: 1rem;
          transition: all 0.3s ease;
          background: rgba(255, 255, 255, 0.8);
          backdrop-filter: blur(10px);
        }
        
        .form-input:focus {
          outline: none;
          border-color: #059669;
          box-shadow: 0 0 0 4px rgba(5, 150, 105, 0.1);
          background: rgba(255, 255, 255, 0.95);
        }
        
        .form-input::placeholder {
          color: #9ca3af;
        }
        
        .input-icon {
          position: relative;
          display: flex;
          align-items: center;
        }
        
        .password-input-wrapper {
          position: relative;
        }
        
        .password-toggle {
          position: absolute;
          right: 1.25rem;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #6b7280;
          cursor: pointer;
          padding: 0.25rem;
          border-radius: 4px;
          transition: all 0.2s;
        }
        
        .password-toggle:hover {
          background: rgba(5, 150, 105, 0.1);
          color: #059669;
        }
        
        .auth-button {
          width: 100%;
          padding: 1rem 1.5rem;
          background: linear-gradient(135deg, #059669 0%, #047857 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.1rem;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
          margin-top: 1rem;
        }
        
        .auth-button::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s;
        }
        
        .auth-button:hover::before {
          left: 100%;
        }
        
        .auth-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(5, 150, 105, 0.3);
        }
        
        .auth-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
        
        .auth-toggle {
          text-align: center;
          margin-top: 2rem;
          color: #6b7280;
        }
        
        .auth-toggle a {
          color: #059669;
          text-decoration: none;
          font-weight: 600;
          cursor: pointer;
          transition: color 0.2s;
        }
        
        .auth-toggle a:hover {
          color: #047857;
          text-decoration: underline;
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
                <label className="form-label">City</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Your city"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Experience (years)</label>
                <input
                  type="number"
                  name="experience"
                  value={formData.experience}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Years of experience"
                  min="0"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Truck Type</label>
                <select
                  name="truck_type"
                  value={formData.truck_type}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                >
                  <option value="Flatbed">Flatbed</option>
                  <option value="Wheel Lift">Wheel Lift</option>
                  <option value="Heavy Duty">Heavy Duty</option>
                  <option value="Integrated">Integrated</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Truck Registration Number</label>
                <input
                  type="text"
                  name="truck_registration"
                  value={formData.truck_registration}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Truck registration number"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Truck Model</label>
                <input
                  type="text"
                  name="truck_model"
                  value={formData.truck_model}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Truck model"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Truck Capacity</label>
                <select
                  name="truck_capacity"
                  value={formData.truck_capacity}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                >
                  <option value="Small Car">Small Car</option>
                  <option value="SUV/Van">SUV/Van</option>
                  <option value="Heavy Vehicle">Heavy Vehicle</option>
                  <option value="Multiple Vehicles">Multiple Vehicles</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">License Path</label>
                <input
                  type="text"
                  name="license_path"
                  value={formData.license_path}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Path to driving license (optional)"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Insurance Path</label>
                <input
                  type="text"
                  name="insurance_path"
                  value={formData.insurance_path}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Path to insurance (optional)"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Fitness Certificate Path</label>
                <input
                  type="text"
                  name="fitness_cert_path"
                  value={formData.fitness_cert_path}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Path to fitness certificate (optional)"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Pollution Certificate Path</label>
                <input
                  type="text"
                  name="pollution_cert_path"
                  value={formData.pollution_cert_path}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Path to pollution certificate (optional)"
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

export default TowTruckAuth;
