import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Car, User, Phone, MapPin, Calendar, Fuel, FileText } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../shared/api';

const CarServiceSetup = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    city: '',
    address: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    brand: '',
    model: '',
    year: '',
    fuel_type: '',
    registration_number: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCheckingProfile, setIsCheckingProfile] = useState(true);

  // Check if user already has a car profile
  useEffect(() => {
    const checkProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await api.get('/api/car/profile', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        // If profile exists, redirect to car service home
        if (response.status === 200 && response.data?.profile) {
          navigate('/car-service/home');
          return;
        }
      } catch (err) {
        // If profile doesn't exist (404), continue to show setup form
        if (err.response?.status !== 404) {
          console.error('Error checking profile:', err);
        }
      } finally {
        setIsCheckingProfile(false);
      }
    };

    checkProfile();
  }, [navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Get token from localStorage (user is guaranteed to be logged in due to ProtectedRoute)
      const token = localStorage.getItem('token');

      const response = await api.post('/api/car/setup-profile', {
        ...formData,
        year: parseInt(formData.year) || formData.year
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.status === 200 || response.status === 201) {
        // Navigate to car service home after successful setup
        navigate('/car-service/home');
      }
    } catch (err) {
      setError('Failed to setup car service profile. Please try again.');
      console.error('Car service setup error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading while checking profile
  if (isCheckingProfile) {
    return (
      <div className="car-service-setup-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Checking your profile...</p>
        </div>
        <style>{`
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 50vh;
            color: white;
          }
          .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="car-service-setup-container">
      <div className="setup-header">
        <div className="header-icon">
          <Car size={40} strokeWidth={2} />
        </div>
        <h1>Car Service Setup</h1>
        <p>Set up your car details and emergency contact to get started</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="setup-form">
        {/* Location Information */}
        <div className="form-section">
          <h2>Location Information</h2>
          <div className="form-group">
            <label htmlFor="city">
              <MapPin size={18} />
              City
            </label>
            <input
              id="city"
              name="city"
              type="text"
              value={formData.city}
              onChange={handleInputChange}
              required
              placeholder="Enter your city"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="address">
              <MapPin size={18} />
              Address
            </label>
            <input
              id="address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleInputChange}
              required
              placeholder="Enter your complete address"
            />
          </div>
        </div>

        {/* Emergency Contact */}
        <div className="form-section">
          <h2>Emergency Contact</h2>
          <div className="form-group">
            <label htmlFor="emergency_contact_name">
              <User size={18} />
              Emergency Contact Name
            </label>
            <input
              id="emergency_contact_name"
              name="emergency_contact_name"
              type="text"
              value={formData.emergency_contact_name}
              onChange={handleInputChange}
              required
              placeholder="Enter emergency contact person's name"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="emergency_contact_phone">
              <Phone size={18} />
              Emergency Contact Phone
            </label>
            <input
              id="emergency_contact_phone"
              name="emergency_contact_phone"
              type="tel"
              value={formData.emergency_contact_phone}
              onChange={handleInputChange}
              required
              placeholder="Enter emergency contact phone number"
            />
          </div>
        </div>

        {/* Car Details */}
        <div className="form-section">
          <h2>Car Details</h2>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="brand">
                <Car size={18} />
                Brand
              </label>
              <input
                id="brand"
                name="brand"
                type="text"
                value={formData.brand}
                onChange={handleInputChange}
                required
                placeholder="e.g., Toyota, Honda, BMW"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="model">
                <Car size={18} />
                Model
              </label>
              <input
                id="model"
                name="model"
                type="text"
                value={formData.model}
                onChange={handleInputChange}
                required
                placeholder="e.g., Camry, Civic, X5"
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="year">
                <Calendar size={18} />
                Year
              </label>
              <input
                id="year"
                name="year"
                type="number"
                value={formData.year}
                onChange={handleInputChange}
                required
                placeholder="e.g., 2022"
                min="1900"
                max={new Date().getFullYear() + 1}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="fuel_type">
                <Fuel size={18} />
                Fuel Type
              </label>
              <select
                id="fuel_type"
                name="fuel_type"
                value={formData.fuel_type}
                onChange={handleInputChange}
                required
              >
                <option value="">Select fuel type</option>
                <option value="petrol">Petrol</option>
                <option value="diesel">Diesel</option>
                <option value="electric">Electric</option>
                <option value="hybrid">Hybrid</option>
                <option value="cng">CNG</option>
              </select>
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="registration_number">
              <FileText size={18} />
              Registration Number
            </label>
            <input
              id="registration_number"
              name="registration_number"
              type="text"
              value={formData.registration_number}
              onChange={handleInputChange}
              required
              placeholder="e.g., MH01AB1234"
            />
          </div>
        </div>

        <button 
          type="submit" 
          className="submit-btn"
          disabled={isLoading}
        >
          {isLoading ? 'Setting up...' : 'Complete Setup'}
        </button>
      </form>

      <style>{`
        .car-service-setup-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 2rem 1rem;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .setup-header {
          text-align: center;
          color: white;
          margin-bottom: 2rem;
          max-width: 500px;
        }

        .header-icon {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          width: 80px;
          height: 80px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          backdrop-filter: blur(10px);
        }

        .setup-header h1 {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
        }

        .setup-header p {
          font-size: 1rem;
          opacity: 0.9;
          margin: 0;
        }

        .setup-form {
          background: white;
          border-radius: 20px;
          padding: 2rem;
          width: 100%;
          max-width: 600px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }

        .form-section {
          margin-bottom: 2rem;
        }

        .form-section:last-child {
          margin-bottom: 0;
        }

        .form-section h2 {
          color: #333;
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 1rem;
          padding-bottom: 0.5rem;
          border-bottom: 2px solid #f0f0f0;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .form-group label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #555;
          font-weight: 500;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
        }

        .form-group input,
        .form-group select {
          width: 100%;
          padding: 0.75rem 1rem;
          border: 2px solid #e0e0e0;
          border-radius: 10px;
          font-size: 1rem;
          transition: border-color 0.3s;
          box-sizing: border-box;
        }

        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #667eea;
        }

        .submit-btn {
          width: 100%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 10px;
          padding: 1rem;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
          margin-top: 1rem;
        }

        .submit-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .submit-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .error-message {
          background: #ff4757;
          color: white;
          padding: 1rem;
          border-radius: 10px;
          margin-bottom: 1rem;
          text-align: center;
        }

        @media (max-width: 768px) {
          .form-row {
            grid-template-columns: 1fr;
            gap: 0;
          }
          
          .setup-form {
            padding: 1.5rem;
          }
          
          .setup-header h1 {
            font-size: 1.75rem;
          }
        }
      `}</style>
    </div>
  );
};

export default CarServiceSetup;
