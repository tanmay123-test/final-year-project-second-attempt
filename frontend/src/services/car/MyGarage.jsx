import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Car, Plus, Star, Edit, Trash2, Fuel, Calendar, 
  FileText, Check, X 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import api from '../../shared/api';

const MyGarage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingCar, setEditingCar] = useState(null);
  const [formData, setFormData] = useState({
    brand: '',
    model: '',
    year: '',
    fuel_type: '',
    registration_number: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchCars();
  }, []);

  const fetchCars = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/car/cars', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.data?.cars) {
        setCars(response.data.cars);
      }
    } catch (error) {
      console.error('Error fetching cars:', error);
      // Set empty array to prevent infinite loading
      setCars([]);
    } finally {
      setLoading(false);
    }
  };

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
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const data = {
        ...formData,
        year: parseInt(formData.year) || formData.year
      };

      let response;
      if (editingCar) {
        response = await api.put(`/api/car/cars/${editingCar.id}`, data, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } else {
        response = await api.post('/api/car/add-car', data, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }

      if (response.status === 200 || response.status === 201) {
        setSuccess(editingCar ? 'Car updated successfully!' : 'Car added successfully!');
        setShowAddForm(false);
        setEditingCar(null);
        setFormData({
          brand: '',
          model: '',
          year: '',
          fuel_type: '',
          registration_number: ''
        });
        fetchCars(); // Refresh the list
      }
    } catch (error) {
      setError(editingCar ? 'Failed to update car. Please try again.' : 'Failed to add car. Please try again.');
      console.error('Error saving car:', error);
    }
  };

  const handleEdit = (car) => {
    setEditingCar(car);
    setFormData({
      brand: car.brand,
      model: car.model,
      year: car.year.toString(),
      fuel_type: car.fuel_type,
      registration_number: car.registration_number
    });
    setShowAddForm(true);
  };

  const handleDelete = async (carId) => {
    if (!window.confirm('Are you sure you want to delete this car?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await api.delete(`/api/car/cars/${carId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      setCars(cars.filter(car => car.id !== carId));
      setSuccess('Car deleted successfully!');
    } catch (error) {
      setError('Failed to delete car. Please try again.');
      console.error('Error deleting car:', error);
    }
  };

  const handleSetDefault = async (carId) => {
    try {
      const token = localStorage.getItem('token');
      await api.put(`/api/car/cars/${carId}/set-default`, {}, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      setCars(cars.map(car => ({
        ...car,
        is_default: car.id === carId ? 1 : 0
      })));
      setSuccess('Default car updated successfully!');
    } catch (error) {
      setError('Failed to set default car. Please try again.');
      console.error('Error setting default car:', error);
    }
  };

  const resetForm = () => {
    setShowAddForm(false);
    setEditingCar(null);
    setFormData({
      brand: '',
      model: '',
      year: '',
      fuel_type: '',
      registration_number: ''
    });
    setError('');
    setSuccess('');
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading your garage...</p>
      </div>
    );
  }

  return (
    <div className="my-garage-container">
      <div className="garage-header">
        <h1>My Garage</h1>
        <button 
          onClick={() => setShowAddForm(true)}
          className="add-car-btn"
        >
          <Plus size={20} />
          Add Car
        </button>
      </div>

      {error && (
        <div className="error-message">
          <X size={20} />
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          <Check size={20} />
          {success}
        </div>
      )}

      <div className="cars-grid">
        {cars.map(car => (
          <div key={car.id} className="car-card">
            <div className="car-header">
              <div className="car-info">
                <h3>{car.brand} {car.model}</h3>
                <div className="car-meta">
                  <span className="year">
                    <Calendar size={16} />
                    {car.year}
                  </span>
                  <span className="fuel">
                    <Fuel size={16} />
                    {car.fuel_type}
                  </span>
                </div>
              </div>
              {car.is_default && (
                <div className="default-badge">
                  <Star size={16} />
                  <span>Default</span>
                </div>
              )}
            </div>
            
            <div className="car-details">
              <div className="detail-item">
                <span className="label">Registration:</span>
                <span className="value">{car.registration_number}</span>
              </div>
            </div>
            
            <div className="car-actions">
              {!car.is_default && (
                <button 
                  onClick={() => handleSetDefault(car.id)}
                  className="action-btn set-default-btn"
                  title="Set as default car"
                >
                  <Star size={16} />
                </button>
              )}
              <button 
                onClick={() => handleEdit(car)}
                className="action-btn edit-btn"
                title="Edit car"
              >
                <Edit size={16} />
              </button>
              <button 
                onClick={() => handleDelete(car.id)}
                className="action-btn delete-btn"
                title="Delete car"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {cars.length === 0 && (
        <div className="empty-garage">
          <Car size={60} />
          <h3>No cars in your garage</h3>
          <p>Add your first car to get started with car services</p>
          <button 
            onClick={() => setShowAddForm(true)}
            className="add-first-car-btn"
          >
            <Plus size={20} />
            Add Your First Car
          </button>
        </div>
      )}

      {/* Add/Edit Car Modal */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{editingCar ? 'Edit Car' : 'Add New Car'}</h2>
              <button onClick={resetForm} className="close-btn">
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="car-form">
              <div className="form-row">
                <div className="form-group">
                  <label>
                    <Car size={18} />
                    Brand
                  </label>
                  <input
                    type="text"
                    name="brand"
                    value={formData.brand}
                    onChange={handleInputChange}
                    placeholder="e.g., Toyota, Honda, BMW"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>
                    <Car size={18} />
                    Model
                  </label>
                  <input
                    type="text"
                    name="model"
                    value={formData.model}
                    onChange={handleInputChange}
                    placeholder="e.g., Camry, Civic, X5"
                    required
                  />
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>
                    <Calendar size={18} />
                    Year
                  </label>
                  <input
                    type="number"
                    name="year"
                    value={formData.year}
                    onChange={handleInputChange}
                    placeholder="e.g., 2022"
                    min="1900"
                    max={new Date().getFullYear() + 1}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>
                    <Fuel size={18} />
                    Fuel Type
                  </label>
                  <select
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
                <label>
                  <FileText size={18} />
                  Registration Number
                </label>
                <input
                  type="text"
                  name="registration_number"
                  value={formData.registration_number}
                  onChange={handleInputChange}
                  placeholder="e.g., MH01AB1234"
                  required
                />
              </div>
              
              <div className="form-actions">
                <button type="button" onClick={resetForm} className="cancel-btn">
                  Cancel
                </button>
                <button type="submit" className="submit-btn">
                  {editingCar ? 'Update Car' : 'Add Car'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style>{`
        .my-garage-container {
          min-height: 100vh;
          background: #f8f9fa;
          padding: 2rem;
        }

        .garage-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .garage-header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1f2937;
        }

        .add-car-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: #7c3aed;
          color: white;
          border: none;
          border-radius: 10px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }

        .add-car-btn:hover {
          background: #6d28d9;
        }

        .error-message, .success-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1rem;
        }

        .error-message {
          background: #fef2f2;
          color: #dc2626;
          border: 1px solid #fecaca;
        }

        .success-message {
          background: #f0fdf4;
          color: #16a34a;
          border: 1px solid #bbf7d0;
        }

        .cars-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .car-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          transition: transform 0.2s;
          position: relative;
        }

        .car-card:hover {
          transform: translateY(-2px);
        }

        .car-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .car-info h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.5rem;
        }

        .car-meta {
          display: flex;
          gap: 1rem;
        }

        .year, .fuel {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .default-badge {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          background: #fbbf24;
          color: #78350f;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .car-details {
          margin-bottom: 1rem;
        }

        .detail-item {
          display: flex;
          justify-content: space-between;
          padding: 0.5rem 0;
          border-bottom: 1px solid #f3f4f6;
        }

        .detail-item:last-child {
          border-bottom: none;
        }

        .label {
          font-weight: 500;
          color: #6b7280;
        }

        .value {
          font-weight: 600;
          color: #1f2937;
        }

        .car-actions {
          display: flex;
          gap: 0.5rem;
        }

        .action-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .set-default-btn {
          background: #fbbf24;
          color: #78350f;
        }

        .set-default-btn:hover {
          background: #f59e0b;
        }

        .edit-btn {
          background: #3b82f6;
          color: white;
        }

        .edit-btn:hover {
          background: #2563eb;
        }

        .delete-btn {
          background: #ef4444;
          color: white;
        }

        .delete-btn:hover {
          background: #dc2626;
        }

        .empty-garage {
          text-align: center;
          padding: 4rem 2rem;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .empty-garage h3 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1f2937;
          margin: 1rem 0 0.5rem;
        }

        .empty-garage p {
          color: #6b7280;
          margin-bottom: 2rem;
        }

        .add-first-car-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 1rem 2rem;
          background: #7c3aed;
          color: white;
          border: none;
          border-radius: 10px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
          margin: 0 auto;
        }

        .add-first-car-btn:hover {
          background: #6d28d9;
        }

        /* Modal Styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          max-width: 600px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .modal-header h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1f2937;
        }

        .close-btn {
          background: none;
          border: none;
          cursor: pointer;
          color: #6b7280;
          padding: 0.5rem;
          border-radius: 6px;
          transition: background 0.2s;
        }

        .close-btn:hover {
          background: #f3f4f6;
        }

        .car-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        .form-group label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .form-group input,
        .form-group select {
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #7c3aed;
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }

        .cancel-btn, .submit-btn {
          flex: 1;
          padding: 0.75rem;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .cancel-btn {
          background: white;
          color: #6b7280;
          border: 1px solid #e5e7eb;
        }

        .cancel-btn:hover {
          background: #f3f4f6;
        }

        .submit-btn {
          background: #7c3aed;
          color: white;
        }

        .submit-btn:hover {
          background: #6d28d9;
        }

        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 50vh;
          color: #7c3aed;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3e8ff;
          border-top: 4px solid #7c3aed;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .my-garage-container {
            padding: 1rem;
          }
          
          .garage-header {
            flex-direction: column;
            gap: 1rem;
            align-items: stretch;
          }
          
          .cars-grid {
            grid-template-columns: 1fr;
          }
          
          .form-row {
            grid-template-columns: 1fr;
          }
          
          .modal-content {
            padding: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default MyGarage;
