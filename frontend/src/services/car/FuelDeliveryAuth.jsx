import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Fuel, Eye, EyeOff, User, Lock, Mail, Phone, MapPin, AlertCircle, ArrowLeft } from 'lucide-react';
import { workerService } from '../../shared/api';
import api from '../../shared/api';

const FuelDeliveryAuth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    password: '',
    confirmPassword: '',
    city: '',
    vehicle_type: 'Bike',
    vehicle_number: '',
    vehicle_photo_path: '',
    rc_book_photo_path: '',
    pollution_certificate_path: '',
    fuel_contract_path: '',
    employee_proof_path: '',
    govt_id_path: '',
    safety_declaration_accepted: false
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

    if (!isLogin && !formData.safety_declaration_accepted) {
      setError('You must accept the safety guidelines to register.');
      setLoading(false);
      return;
    }

    try {
      if (isLogin) {
        // Use direct fetch for fuel delivery login
        try {
          const response = await api.post('/api/fuel-delivery/login', {
            email: formData.email,
            password: formData.password
          });
          
          console.log('Login response:', response); // Debug log
          
          if (response.data) {
            const data = response.data;
            console.log('Login data:', data);
            
            // Handle fuel delivery specific response structure
            if (data.success && data.agent) {
              // For fuel delivery, the agent data might not include a token
              // We'll store the agent data and create a mock token for now
              const agent = data.agent;
              
              // Check if there's a token in the response
              const token = data.token || 'fuel-delivery-token-' + Date.now();
              
              localStorage.setItem('workerToken', token);
              localStorage.setItem('workerData', JSON.stringify(agent));
              localStorage.setItem('workerId', agent.id.toString());
              
              // Verify data was stored correctly
              const storedData = localStorage.getItem('workerData');
              console.log('Stored worker data:', storedData);
              console.log('Stored worker ID:', agent.id);
              
              setSuccess('Login successful! Redirecting...');
              setTimeout(() => {
                navigate('/worker/car/fuel-delivery/home');
              }, 1500);
            } else {
              // Handle standard response structure
              const token = data.token || data.access_token;
              const worker = data.worker || data.user || data.data || data.agent;
              
              if (token && worker) {
                localStorage.setItem('workerToken', token);
                localStorage.setItem('workerData', JSON.stringify(worker));
                localStorage.setItem('workerId', worker.id.toString());
                
                const storedData = localStorage.getItem('workerData');
                console.log('Stored worker data:', storedData);
                console.log('Stored worker ID:', worker.id);
                
                setSuccess('Login successful! Redirecting...');
                setTimeout(() => {
                  navigate('/worker/car/fuel-delivery/home');
                }, 1500);
              } else {
                console.error('Missing token or worker in response:', data);
                setError('Invalid login response. Please try again.');
              }
            }
          } else {
            console.error('Login failed:', data);
            setError(data.message || data.error || 'Login failed. Please try again.');
          }
        } catch (apiError) {
          console.error('API Error:', apiError);
          setError('Login failed. Please check your credentials.');
        }
      } else {
        // Registration logic
        const payload = {
          name: formData.name,
          email: formData.email,
          phone_number: formData.phone_number,
          password: formData.password,
          city: formData.city,
          vehicle_type: formData.vehicle_type,
          vehicle_number: formData.vehicle_number,
          vehicle_photo_path: formData.vehicle_photo_path || null,
          rc_book_photo_path: formData.rc_book_photo_path || null,
          pollution_certificate_path: formData.pollution_certificate_path || null,
          fuel_contract_path: formData.fuel_contract_path || null,
          employee_proof_path: formData.employee_proof_path || null,
          govt_id_path: formData.govt_id_path || null,
          safety_declaration_accepted: formData.safety_declaration_accepted
        };

        const response = await api.post('/api/fuel-delivery/register', payload);

        const data = response.data;

        if (data) {
          setSuccess('Registration successful! Please wait for admin approval.');
          setTimeout(() => {
            setIsLogin(true);
            setFormData({ ...formData, password: '', confirmPassword: '' });
          }, 3000);
        } else {
          setError(data.message || data.error || 'Something went wrong');
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Network error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <style>{`
        .auth-container {
          min-height: calc(100vh - 80px);
          background: linear-gradient(135deg, #FED7AA 0%, #FDBA74 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1rem;
          position: relative;
          overflow: hidden;
        }
        
        .auth-container::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23ffffff" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="%23ffffff" opacity="0.1"/><circle cx="10" cy="50" r="0.5" fill="%23ffffff" opacity="0.1"/><circle cx="90" cy="90" r="0.5" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
          opacity: 0.3;
          pointer-events: none;
        }
        
        .auth-card {
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
          backdrop-filter: blur(20px);
          border-radius: 24px;
          box-shadow: 0 25px 50px -12px rgba(251, 146, 60, 0.25);
          padding: 3rem;
          width: 90%;
          max-width: 600px;
          z-index: 10;
          border: 2px solid rgba(251, 146, 60, 0.3);
          position: relative;
        }
        
        .auth-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(251, 146, 60, 0.05), rgba(251, 146, 60, 0.1));
          border-radius: 22px;
          z-index: -1;
        }
        
        .auth-header {
          text-align: center;
          margin-bottom: 2.5rem;
        }
        
        .auth-icon {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #FB923C 0%, #EA580C 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 2rem;
          box-shadow: 0 10px 30px rgba(251, 146, 60, 0.4);
          position: relative;
        }
        
        .auth-icon::before {
          content: '';
          position: absolute;
          top: -4px;
          left: -4px;
          right: -4px;
          bottom: -4px;
          background: linear-gradient(135deg, #FED7AA, #FDBA74);
          border-radius: 50%;
          z-index: -1;
          opacity: 0.5;
        }
        
        .auth-title {
          font-size: 2rem;
          font-weight: 800;
          color: #1f2937;
          margin-bottom: 0.5rem;
          background: linear-gradient(135deg, #EA580C, #FB923C);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        
        .auth-subtitle {
          color: #6b7280;
          font-size: 1rem;
          font-weight: 500;
        }
        
        .form-group {
          margin-bottom: 1.75rem;
        }
        
        .form-row {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }
        
        .input-wrapper .input-icon {
          position: absolute;
          left: 1rem;
          color: #9ca3af;
          pointer-events: none;
        }
        
        .form-label {
          display: block;
          margin-bottom: 0.75rem;
          font-weight: 600;
          color: #374151;
          font-size: 0.95rem;
        }
        
        .form-input {
          width: 100%;
          padding: 1rem 1.25rem;
          border: 2px solid rgba(251, 146, 60, 0.3);
          border-radius: 12px;
          font-size: 1rem;
          transition: all 0.3s ease;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
          backdrop-filter: blur(10px);
          color: #1f2937;
        }
        
        .form-input:focus {
          outline: none;
          border-color: #FB923C;
          box-shadow: 0 0 0 4px rgba(251, 146, 60, 0.2);
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.8));
        }
        
        .form-input::placeholder {
          color: #9ca3af;
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
          background: rgba(251, 146, 60, 0.1);
          color: #FB923C;
        }
        
        .submit-btn {
          width: 100%;
          padding: 1rem 1.5rem;
          background: linear-gradient(135deg, #FB923C 0%, #EA580C 100%);
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
        
        .submit-btn::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
          transition: left 0.5s;
        }
        
        .submit-btn:hover::before {
          left: 100%;
        }
        
        .submit-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(251, 146, 60, 0.3);
        }
        
        .submit-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
        
        .toggle-text {
          text-align: center;
          margin-top: 2rem;
          color: #6b7280;
        }
        
        .toggle-link {
          color: #FB923C;
          text-decoration: none;
          font-weight: 600;
          cursor: pointer;
          transition: color 0.2s;
        }
        
        .toggle-link:hover {
          color: #EA580C;
          text-decoration: underline;
        }
        
        .alert {
          padding: 1rem 1.25rem;
          border-radius: 12px;
          margin-bottom: 1.5rem;
          font-weight: 500;
          border-left: 4px solid;
        }
        
        .alert-success {
          background: rgba(34, 197, 94, 0.1);
          color: #166534;
          border-left-color: #22c55e;
        }
        
        .alert-error {
          background: rgba(239, 68, 68, 0.1);
          color: #dc2626;
          border-left-color: #ef4444;
        }
        
        .back-link {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          color: #FB923C;
          text-decoration: none;
          font-weight: 600;
          margin-bottom: 2rem;
          transition: all 0.2s;
          padding: 0.5rem 1rem;
          border-radius: 8px;
        }
        
        .back-link:hover {
          background: rgba(251, 146, 60, 0.1);
          transform: translateX(-4px);
        }
        
        .loading-spinner {
          display: inline-block;
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top: 2px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 0.5rem;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 640px) {
          .auth-card {
            padding: 2rem 1.5rem;
            margin: 1rem;
          }
          
          .auth-title {
            font-size: 1.75rem;
          }
          
          .auth-icon {
            width: 60px;
            height: 60px;
          }
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
        <div className="auth-header">
          <div className="auth-icon">
            <Fuel size={30} color="white" />
          </div>
          <h1 className="auth-title">
            {isLogin ? 'Fuel Delivery Login' : 'Fuel Delivery Signup'}
          </h1>
          <p className="auth-subtitle">
            {isLogin 
              ? 'Welcome back! Login to your account' 
              : 'Join our fuel delivery team'}
          </p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <div className="input-wrapper">
                <Mail size={18} className="input-icon" />
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
              <div className="input-wrapper">
                <Lock size={18} className="input-icon" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {!isLogin && (
              <>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <div className="input-wrapper">
                    <User size={18} className="input-icon" />
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
                  <div className="input-wrapper">
                    <Phone size={18} className="input-icon" />
                    <input
                      type="tel"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleInputChange}
                      className="form-input"
                      placeholder="Enter your phone number"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">City</label>
                  <div className="input-wrapper">
                    <MapPin size={18} className="input-icon" />
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
                </div>

                <div className="form-group">
                  <label className="form-label">Vehicle Type</label>
                  <div className="input-wrapper">
                    <Fuel size={18} className="input-icon" />
                    <select
                      name="vehicle_type"
                      value={formData.vehicle_type}
                      onChange={handleInputChange}
                      className="form-input"
                      required
                    >
                      <option value="Bike">Bike</option>
                      <option value="Van">Van</option>
                      <option value="Truck">Truck</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Vehicle Number</label>
                  <div className="input-wrapper">
                    <Fuel size={18} className="input-icon" />
                    <input
                      type="text"
                      name="vehicle_number"
                      value={formData.vehicle_number}
                      onChange={handleInputChange}
                      className="form-input"
                      placeholder="Vehicle registration number"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Confirm Password</label>
                  <div className="input-wrapper">
                    <Lock size={18} className="input-icon" />
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
              </>
            )}

            {!isLogin && (
              <div className="form-group" style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '1.5rem' }}>
                <input
                  type="checkbox"
                  id="safety_declaration"
                  name="safety_declaration_accepted"
                  checked={formData.safety_declaration_accepted}
                  onChange={handleInputChange}
                  style={{ width: '20px', height: '20px', marginTop: '4px', cursor: 'pointer' }}
                />
                <label htmlFor="safety_declaration" style={{ fontSize: '0.875rem', color: '#4b5563', lineHeight: '1.5', cursor: 'pointer' }}>
                  I accept the <strong>safety guidelines</strong> for fuel delivery operations and confirm all provided information is accurate.
                </label>
              </div>
            )}

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading && <span className="loading-spinner"></span>}
              {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
            </button>
          </div>
        </form>

        <div className="auth-footer">
          <div className="toggle-text">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              type="button"
              className="toggle-link"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setSuccess('');
              }}
            >
              {isLogin ? 'Sign up' : 'Login'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FuelDeliveryAuth;
