import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Car, User, MapPin, Phone, Mail, Plus, Trash2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../shared/api';

const CarServiceSetup = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [hasProfile, setHasProfile] = useState(false);
  const [formData, setFormData] = useState({
    // User Location
    city: '',
    address: '',
    
    // Emergency Contact
    emergency_contact_name: '',
    emergency_contact_phone: '',
    
    // Car Details
    brand: '',
    model: '',
    year: '',
    fuel_type: 'petrol',
    registration_number: '',
    is_default: true
  });

  const [cars, setCars] = useState([]);
  const [showCarForm, setShowCarForm] = useState(false);

  useEffect(() => {
    checkExistingProfile();
  }, []);

  const checkExistingProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/car/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data?.profile) {
        setHasProfile(true);
        // Redirect to home if profile exists
        navigate('/car-service/home');
      }
    } catch (error) {
      console.log('Profile check - user needs to setup:', error.message);
      setHasProfile(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const token = localStorage.getItem('token');
      
      // First setup user profile
      const profileData = {
        city: formData.city,
        address: formData.address,
        emergency_contact_name: formData.emergency_contact_name,
        emergency_contact_phone: formData.emergency_contact_phone
      };
      
      await api.post('/api/car/setup-profile', profileData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Then add the car
      const carData = {
        brand: formData.brand,
        model: formData.model,
        year: formData.year,
        fuel_type: formData.fuel_type,
        registration_number: formData.registration_number,
        is_default: formData.is_default
      };
      
      await api.post('/api/car/add-car', carData, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // Redirect to home after successful setup
      navigate('/car-service/home');
    } catch (error) {
      console.error('Setup error:', error);
      alert('Error setting up profile. Please try again.');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addCar = () => {
    if (formData.brand && formData.model && formData.year && formData.registration_number) {
      setCars(prev => [...prev, { ...formData, id: Date.now() }]);
      // Reset car form
      setFormData(prev => ({
        ...prev,
        brand: '',
        model: '',
        year: '',
        fuel_type: 'petrol',
        registration_number: '',
        is_default: false
      }));
      setShowCarForm(false);
    }
  };

  const removeCar = (carId) => {
    setCars(prev => prev.filter(car => car.id !== carId));
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Setting up your car service profile...</p>
      </div>
    );
  }

  return (
    <div className="car-service-setup">
      <div className="setup-container">
        <div className="setup-header">
          <Car size={48} />
          <h1>Complete Your Car Service Profile</h1>
          <p>We need some information to provide you with the best service</p>
        </div>

        <form onSubmit={handleSubmit} className="setup-form">
          {/* User Location Section */}
          <div className="form-section">
            <h2>Your Location</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="city">City *</label>
                <input
                  type="text"
                  id="city"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your city"
                />
              </div>
              
              <div className="form-group full-width">
                <label htmlFor="address">Address *</label>
                <textarea
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your complete address"
                  rows={3}
                />
              </div>
            </div>
          </div>

          {/* Emergency Contact Section */}
          <div className="form-section">
            <h2>Emergency Contact</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="emergency_contact_name">Contact Name *</label>
                <input
                  type="text"
                  id="emergency_contact_name"
                  name="emergency_contact_name"
                  value={formData.emergency_contact_name}
                  onChange={handleInputChange}
                  required
                  placeholder="Emergency contact person name"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="emergency_contact_phone">Contact Phone *</label>
                <input
                  type="tel"
                  id="emergency_contact_phone"
                  name="emergency_contact_phone"
                  value={formData.emergency_contact_phone}
                  onChange={handleInputChange}
                  required
                  placeholder="Emergency contact phone number"
                />
              </div>
            </div>
          </div>

          {/* Car Details Section */}
          <div className="form-section">
            <h2>Your Vehicle Details</h2>
            
            {/* Car Form */}
            <div className="car-form">
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="brand">Car Brand *</label>
                  <input
                    type="text"
                    id="brand"
                    name="brand"
                    value={formData.brand}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., Toyota, Honda, BMW"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="model">Car Model *</label>
                  <input
                    type="text"
                    id="model"
                    name="model"
                    value={formData.model}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., Camry, Civic, X5"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="year">Year *</label>
                  <input
                    type="number"
                    id="year"
                    name="year"
                    value={formData.year}
                    onChange={handleInputChange}
                    required
                    min="1990"
                    max={new Date().getFullYear() + 1}
                    placeholder="e.g., 2022"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="fuel_type">Fuel Type *</label>
                  <select
                    id="fuel_type"
                    name="fuel_type"
                    value={formData.fuel_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="petrol">Petrol</option>
                    <option value="diesel">Diesel</option>
                    <option value="electric">Electric</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="cng">CNG</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="registration_number">Registration Number *</label>
                  <input
                    type="text"
                    id="registration_number"
                    name="registration_number"
                    value={formData.registration_number}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., MH01AB1234"
                  />
                </div>
                
                <div className="form-group">
                  <label>
                    <input
                      type="checkbox"
                      name="is_default"
                      checked={formData.is_default}
                      onChange={(e) => setFormData(prev => ({...prev, is_default: e.target.checked}))}
                    />
                    Set as default vehicle
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="form-actions">
            <button type="submit" className="submit-btn">
              Complete Setup
            </button>
          </div>
        </form>
      </div>

      <style>{`
        .car-service-setup {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 2rem;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .setup-container {
          background: white;
          border-radius: 20px;
          padding: 3rem;
          max-width: 600px;
          width: 100%;
          box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        .setup-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .setup-header svg {
          color: #7c3aed;
          margin-bottom: 1rem;
        }

        .setup-header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .setup-header p {
          color: #6b7280;
          font-size: 1.1rem;
        }

        .setup-form {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .form-section {
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          padding: 1.5rem;
        }

        .form-section h2 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 1rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .form-group.full-width {
          grid-column: 1 / -1;
        }

        .form-group label {
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
          transition: all 0.2s;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
          outline: none;
          border-color: #7c3aed;
          box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
        }

        .form-group input[type="checkbox"] {
          width: auto;
          margin-right: 0.5rem;
        }

        .car-form {
          background: #f9fafb;
          padding: 1rem;
          border-radius: 8px;
        }

        .form-actions {
          display: flex;
          justify-content: center;
        }

        .submit-btn {
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          min-width: 200px;
        }

        .submit-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(124, 58, 237, 0.3);
        }

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .spinner {
          width: 50px;
          height: 50px;
          border: 4px solid rgba(255, 255, 255, 0.3);
          border-top: 4px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .car-service-setup {
            padding: 1rem;
          }
          
          .setup-container {
            padding: 2rem;
          }
          
          .form-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default CarServiceSetup;
