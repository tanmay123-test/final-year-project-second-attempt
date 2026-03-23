import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  Fuel,
  MapPin,
  Phone,
  Clock,
  Package,
  AlertCircle,
  CheckCircle,
  XCircle,
  Navigation,
  DollarSign,
  User,
  Calendar,
  Filter,
  RefreshCw,
  Search
} from 'lucide-react';
import { carService } from '../../shared/api';
import api from '../../shared/api';

const FuelDeliveryRequests = () => {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterFuelType, setFilterFuelType] = useState('all');
  const [acceptingRequest, setAcceptingRequest] = useState(null);
  const [rejectingRequest, setRejectingRequest] = useState(null);

  useEffect(() => {
    fetchRequests();
  }, []);

  // Set up periodic updates for new requests
  useEffect(() => {
    const interval = setInterval(() => {
      fetchRequests();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const workerId = localStorage.getItem('workerId');
      const workerData = localStorage.getItem('workerData');
      const workerToken = localStorage.getItem('workerToken');
      
      console.log('Debug - Requests Storage check:', {
        workerId,
        workerData: workerData ? 'present' : 'missing',
        workerToken: workerToken ? 'present' : 'missing'
      });
      
      if (!workerId) {
        // Try to get workerId from workerData as fallback
        if (workerData) {
          try {
            const parsedWorkerData = JSON.parse(workerData);
            if (parsedWorkerData.id) {
              console.log('Fallback: Using worker ID from workerData for requests:', parsedWorkerData.id);
              localStorage.setItem('workerId', parsedWorkerData.id.toString());
              // Continue with the fetched workerId
            } else {
              console.error('Worker ID not found in workerData for requests either');
              setError('Worker not authenticated - Please login again');
              setLoading(false);
              return;
            }
          } catch (e) {
            console.error('Error parsing workerData for requests:', e);
            setError('Worker not authenticated - Please login again');
            setLoading(false);
            return;
          }
        } else {
          console.error('Worker ID not found in localStorage for requests');
          setError('Worker not authenticated - Please login again');
          setLoading(false);
          return;
        }
      }

      const response = await api.get(`/api/fuel-delivery/queue/available?agent_id=${workerId}`);

      const data = response.data;

      if (data?.success && data.requests) {
        setRequests(data.requests);
      } else {
        setRequests([]);
      }
    } catch (err) {
      console.error('Failed to fetch requests:', err);
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRequest = async (request) => {
    try {
      setAcceptingRequest(request.request_id);
      const workerId = localStorage.getItem('workerId');
      
      const response = await api.post('/api/fuel-delivery/accept-request', {
        request_id: request.id,
        worker_id: workerId
      });
      
      const data = response.data;
      
      if (data?.success) {
        // Remove request from list and navigate to active delivery
        setRequests(prev => prev.filter(req => req.id !== request.id));
        navigate('/worker/car/fuel-delivery/active-delivery', { 
          state: { request: data.delivery } 
        });
      } else {
        setError(data.message || 'Failed to accept request');
        setAcceptingRequest(null);
      }
    } catch (err) {
      console.error('Failed to accept request:', err);
      setError('Failed to accept request');
      setAcceptingRequest(null);
    }
  };

  const handleRejectRequest = async (request) => {
    try {
      setRejectingRequest(request.id);
      const workerId = localStorage.getItem('workerId');
      
      const response = await api.post('/api/fuel-delivery/reject-request', {
        request_id: request.id,
        worker_id: workerId
      });
      
      const data = response.data;
      
      if (data?.success) {
        // Remove request from list
        setRequests(prev => prev.filter(req => req.id !== request.id));
      } else {
        setError(data.message || 'Failed to reject request');
      }
    } catch (err) {
      console.error('Failed to reject request:', err);
      setError('Failed to reject request');
    } finally {
      setRejectingRequest(null);
    }
  };

  const filteredRequests = requests.filter(request => {
    const matchesSearch = searchTerm === '' || 
      request.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.delivery_address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      request.fuel_type.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesPriority = filterPriority === 'all' || 
      (filterPriority === 'high' && request.priority_level >= 4) ||
      (filterPriority === 'medium' && request.priority_level >= 3 && request.priority_level < 4) ||
      (filterPriority === 'low' && request.priority_level < 3);
    
    const matchesFuelType = filterFuelType === 'all' || 
      request.fuel_type === filterFuelType;
    
    return matchesSearch && matchesPriority && matchesFuelType;
  });

  const getPriorityColor = (level) => {
    if (level >= 4) return 'text-red-600 bg-red-100';
    if (level >= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getPriorityIcon = (level) => {
    if (level >= 4) return AlertCircle;
    if (level >= 3) return Clock;
    return CheckCircle;
  };

  const getFuelIcon = (fuelType) => {
    return fuelType === 'Petrol' ? Fuel : Package;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-orange-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
          <p className="mt-4 text-orange-600">Loading fuel requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-orange-100">
      <style>{`
        .fuel-requests-page {
          min-height: 100vh;
          background: #f8f9fa;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
        }
        
        .header {
          background: white;
          padding: 16px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          max-width: 1200px;
          margin: 0 auto;
        }
        
        .header-left {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        
        .back-btn {
          padding: 8px;
          border-radius: 8px;
          border: none;
          background: #f8f9fa;
          cursor: pointer;
        }
        
        .back-btn:hover {
          background: #e9ecef;
        }
        
        .header-title {
          font-size: 24px;
          font-weight: bold;
          color: #333;
          margin: 0;
        }
        
        .header-subtitle {
          font-size: 14px;
          color: #666;
          margin: 0;
        }
        
        .refresh-btn {
          padding: 8px;
          border-radius: 8px;
          border: none;
          background: #f8f9fa;
          cursor: pointer;
        }
        
        .refresh-btn:hover {
          background: #e9ecef;
        }
        
        .filters-section {
          padding: 16px;
          max-width: 1200px;
          margin: 0 auto;
        }
        
        .filters-card {
          background: white;
          padding: 16px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .filters-grid {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 16px;
        }
        
        .search-input {
          width: 100%;
          padding: 8px 12px 8px 40px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 14px;
        }
        
        .search-wrapper {
          position: relative;
        }
        
        .search-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: #999;
        }
        
        .filter-select {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 14px;
        }
        
        .requests-section {
          padding: 0 16px 16px;
          max-width: 1200px;
          margin: 0 auto;
        }
        
        .requests-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        
        .request-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }
        
        .request-card:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .request-header {
          padding: 16px;
          border-bottom: 1px solid #f0f0f0;
        }
        
        .request-header-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }
        
        .request-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .request-icon {
          width: 40px;
          height: 40px;
          background: #fff3e0;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .request-title {
          font-size: 18px;
          font-weight: 600;
          color: #333;
          margin: 0;
        }
        
        .request-id {
          font-size: 12px;
          color: #666;
          margin: 0;
        }
        
        .priority-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 500;
        }
        
        .priority-high {
          background: #fee;
          color: #dc2626;
        }
        
        .priority-medium {
          background: #fef3c7;
          color: #d97706;
        }
        
        .priority-low {
          background: #dcfce7;
          color: #16a34a;
        }
        
        .request-details {
          padding: 16px;
        }
        
        .detail-item {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          font-size: 14px;
          color: #666;
        }
        
        .earnings-box {
          background: #f0fdf4;
          padding: 12px;
          border-radius: 8px;
          margin-bottom: 16px;
        }
        
        .earnings-text {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          color: #16a34a;
        }
        
        .action-buttons {
          display: flex;
          gap: 8px;
        }
        
        .accept-btn {
          flex: 1;
          padding: 8px 16px;
          background: #ff6b35;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
        }
        
        .accept-btn:hover {
          background: #e55a2b;
        }
        
        .accept-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .reject-btn {
          flex: 1;
          padding: 8px 16px;
          background: #dc2626;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
        }
        
        .reject-btn:hover {
          background: #b91c1c;
        }
        
        .reject-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .nav-btn {
          padding: 8px 16px;
          background: #f8f9fa;
          color: #666;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
        }
        
        .nav-btn:hover {
          background: #e9ecef;
        }
        
        .no-requests {
          background: white;
          padding: 48px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          text-align: center;
        }
        
        .no-requests-icon {
          width: 64px;
          height: 64px;
          color: #999;
          margin: 0 auto 16px;
        }
        
        .no-requests-title {
          font-size: 18px;
          font-weight: 600;
          color: #333;
          margin: 0 0 8px;
        }
        
        .no-requests-text {
          color: #666;
          margin: 0 0 16px;
        }
        
        .clear-filters-btn {
          padding: 8px 16px;
          background: #ff6b35;
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
        }
        
        .clear-filters-btn:hover {
          background: #e55a2b;
        }
        
        @media (max-width: 768px) {
          .requests-grid {
            grid-template-columns: 1fr;
          }
          
          .filters-grid {
            grid-template-columns: 1fr;
          }
          
          .action-buttons {
            flex-direction: column;
          }
        }
      `}</style>
      
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div className="header-left">
            <button
              onClick={() => navigate('/worker/car/fuel-delivery/home')}
              className="back-btn"
            >
              <ArrowLeft style={{ width: '24px', height: '24px' }} />
            </button>
            <div>
              <h1 className="header-title">Fuel Requests Queue</h1>
              <p className="header-subtitle">
                {filteredRequests.length} request{filteredRequests.length !== 1 ? 's' : ''} available
              </p>
            </div>
          </div>
          
          <button
            onClick={fetchRequests}
            className="refresh-btn"
            disabled={loading}
          >
            <RefreshCw 
              style={{ 
                width: '24px', 
                height: '24px',
                animation: loading ? 'spin 1s linear infinite' : 'none'
              }} 
            />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filters-card">
          <div className="filters-grid">
            {/* Search */}
            <div className="search-wrapper">
              <Search className="search-icon" style={{ width: '16px', height: '16px' }} />
              <input
                type="text"
                placeholder="Search by name, address, or fuel type..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>

            {/* Priority Filter */}
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Priorities</option>
              <option value="high">High Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="low">Low Priority</option>
            </select>

            {/* Fuel Type Filter */}
            <select
              value={filterFuelType}
              onChange={(e) => setFilterFuelType(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Fuel Types</option>
              <option value="Petrol">Petrol</option>
              <option value="Diesel">Diesel</option>
            </select>
          </div>
        </div>
      </div>

      {/* Requests List */}
      <div className="requests-section">
        {filteredRequests.length > 0 ? (
          <div className="requests-grid">
            {filteredRequests.map((request) => {
              const FuelIcon = getFuelIcon(request.fuel_type);
              const PriorityIcon = getPriorityIcon(request.priority_level);
              const priorityClass = request.priority_level >= 4 ? 'priority-high' : 
                                   request.priority_level >= 3 ? 'priority-medium' : 'priority-low';
              
              return (
                <div key={request.request_id} className="request-card">
                  <div className="request-header">
                    <div className="request-header-content">
                      <div className="request-info">
                        <div className="request-icon">
                          <FuelIcon style={{ width: '20px', height: '20px', color: '#ff6b35' }} />
                        </div>
                        <div>
                          <h3 className="request-title">{request.fuel_type}</h3>
                          <p className="request-id">Request ID: #{request.request_id}</p>
                        </div>
                      </div>
                      <div className={`priority-badge ${priorityClass}`}>
                        Priority {request.priority_level}
                      </div>
                    </div>
                  </div>

                  <div className="request-details">
                    <div className="detail-item">
                      <Package style={{ width: '16px', height: '16px' }} />
                      <span>Quantity: {request.quantity_liters} liters</span>
                    </div>
                    
                    <div className="detail-item">
                      <MapPin style={{ width: '16px', height: '16px' }} />
                      <span>{request.delivery_address}</span>
                    </div>
                    
                    <div className="detail-item">
                      <User style={{ width: '16px', height: '16px' }} />
                      <span>{request.user_name}</span>
                    </div>
                    
                    <div className="detail-item">
                      <Phone style={{ width: '16px', height: '16px' }} />
                      <span>{request.user_phone}</span>
                    </div>
                    
                    <div className="detail-item">
                      <Calendar style={{ width: '16px', height: '16px' }} />
                      <span>{request.created_at}</span>
                    </div>

                    <div className="earnings-box">
                      <div className="earnings-text">
                        <DollarSign style={{ width: '16px', height: '16px' }} />
                        <span>Estimated Earnings: ₹{request.estimated_earnings?.toFixed(2) || '0.00'}</span>
                      </div>
                    </div>

                    <div className="action-buttons">
                      <button
                        onClick={() => handleAcceptRequest(request)}
                        disabled={acceptingRequest === request.request_id || rejectingRequest === request.request_id}
                        className="accept-btn"
                      >
                        {acceptingRequest === request.request_id ? 'Accepting...' : 'Accept'}
                      </button>
                      
                      <button
                        onClick={() => handleRejectRequest(request)}
                        disabled={acceptingRequest === request.request_id || rejectingRequest === request.request_id}
                        className="reject-btn"
                      >
                        {rejectingRequest === request.request_id ? 'Rejecting...' : 'Reject'}
                      </button>
                      
                      <button
                        onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(request.delivery_address)}`, '_blank')}
                        className="nav-btn"
                      >
                        <Navigation style={{ width: '16px', height: '16px' }} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="no-requests">
            <Package className="no-requests-icon" />
            <h3 className="no-requests-title">No fuel requests available</h3>
            <p className="no-requests-text">
              {searchTerm || filterPriority !== 'all' || filterFuelType !== 'all'
                ? 'No requests match your current filters.'
                : 'There are no fuel delivery requests in the queue at the moment.'}
            </p>
            {(searchTerm || filterPriority !== 'all' || filterFuelType !== 'all') && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setFilterPriority('all');
                  setFilterFuelType('all');
                }}
                className="clear-filters-btn"
              >
                Clear Filters
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FuelDeliveryRequests;
