import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Clock, 
  MapPin, 
  Phone, 
  Calendar, 
  Car, 
  Wrench,
  User,
  AlertCircle,
  Filter,
  Search,
  DollarSign,
  Shield,
  TrendingUp
} from 'lucide-react';

const MechanicJobs = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // all, pending, accepted, rejected

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      // Get worker data from localStorage
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (!storedData || !token) {
        navigate('/worker/car/mechanic/login');
        return;
      }

      const workerData = JSON.parse(storedData);
      const workerId = workerData.id || workerData.workerId || 7;

      // Try to fetch real data from API
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/jobs`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setJobs(data.jobs || []);
        } else {
          throw new Error('API not available');
        }
      } catch (apiError) {
        console.log('API endpoints not available, using empty jobs list:', apiError.message);
        
        // Set empty jobs array - no hardcoded data
        setJobs([]);
        setError('No job requests available');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching jobs:', err.message);
      setError('Failed to load jobs');
      setJobs([]);
      setLoading(false);
    }
  };

  const handleAcceptJob = async (jobId) => {
    try {
      const token = localStorage.getItem('workerToken');
      
      // Update job status in local state immediately for better UX
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, status: 'accepted' }
            : job
        )
      );

      // Make API call to update status
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/jobs/${jobId}/accept`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          // If API call fails, revert the state
          setJobs(prevJobs => 
            prevJobs.map(job => 
              job.id === jobId 
                ? { ...job, status: 'pending' }
                : job
            )
          );
          console.error('Failed to accept job on server');
        }
      } catch (apiError) {
        console.log('API call failed, but local state updated:', apiError.message);
      }
    } catch (err) {
      console.error('Error accepting job:', err);
    }
  };

  const handleRejectJob = async (jobId) => {
    try {
      const token = localStorage.getItem('workerToken');
      
      // Update job status in local state immediately for better UX
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, status: 'rejected' }
            : job
        )
      );

      // Make API call to update status
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/jobs/${jobId}/reject`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          // If API call fails, revert the state
          setJobs(prevJobs => 
            prevJobs.map(job => 
              job.id === jobId 
                ? { ...job, status: 'pending' }
                : job
            )
          );
          console.error('Failed to reject job on server');
        }
      } catch (apiError) {
        console.log('API call failed, but local state updated:', apiError.message);
      }
    } catch (err) {
      console.error('Error rejecting job:', err);
    }
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.serviceType.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.carModel.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || job.status === filterStatus;
    
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status) => {
    switch(status) {
      case 'pending': return '#f59e0b';
      case 'accepted': return '#10b981';
      case 'rejected': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="jobs-loading">
        <div className="loading-spinner"></div>
        <p>Loading jobs...</p>
      </div>
    );
  }

  return (
    <div className="mechanic-jobs">
      {/* Header */}
      <div className="jobs-header">
        <div className="header-left">
          <button className="back-btn" onClick={() => navigate('/worker/car/mechanic/dashboard')}>
            <ArrowLeft size={20} />
          </button>
          <h1>Job Requests</h1>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-number">{filteredJobs.length}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{jobs.filter(j => j.status === 'pending').length}</span>
            <span className="stat-label">Pending</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{jobs.filter(j => j.status === 'accepted').length}</span>
            <span className="stat-label">Accepted</span>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="search-filter-bar">
        <div className="search-box">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search by customer, service, or car model..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-dropdown">
          <Filter size={20} className="filter-icon" />
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">All Jobs</option>
            <option value="pending">Pending</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Jobs List */}
      <div className="jobs-container">
        {filteredJobs.length === 0 ? (
          <div className="no-jobs">
            <AlertCircle size={48} />
            <h3>No jobs found</h3>
            <p>No job requests match your search criteria.</p>
          </div>
        ) : (
          filteredJobs.map(job => (
            <div key={job.id} className="job-card">
              {/* Job Header */}
              <div className="job-header">
                <div className="customer-info">
                  <div className="customer-name">
                    <User size={20} />
                    <span>{job.customerName}</span>
                  </div>
                  <div className="customer-contact">
                    <Phone size={16} />
                    <span>{job.customerPhone}</span>
                  </div>
                </div>
                <div className="job-badges">
                  <span 
                    className="status-badge" 
                    style={{ backgroundColor: getStatusColor(job.status) }}
                  >
                    {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                  </span>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(job.priority) }}
                  >
                    {job.priority.charAt(0).toUpperCase() + job.priority.slice(1)} Priority
                  </span>
                </div>
              </div>

              {/* Job Details */}
              <div className="job-details">
                <div className="detail-row">
                  <Car size={18} />
                  <span>{job.carModel}</span>
                </div>
                <div className="detail-row">
                  <Wrench size={18} />
                  <span>{job.serviceType}</span>
                </div>
                <div className="detail-row">
                  <MapPin size={18} />
                  <span>{job.customerLocation}</span>
                </div>
                <div className="detail-row">
                  <Calendar size={18} />
                  <span>{new Date(job.requestedTime).toLocaleString()}</span>
                </div>
              </div>

              {/* Description */}
              <div className="job-description">
                <p>{job.description}</p>
              </div>

              {/* Price Estimate */}
              <div className="price-estimate">
                <span className="estimate-label">Estimated Price:</span>
                <span className="estimate-value">{job.estimatedPrice}</span>
              </div>

              {/* Action Buttons */}
              {job.status === 'pending' && (
                <div className="job-actions">
                  <button 
                    className="accept-btn"
                    onClick={() => handleAcceptJob(job.id)}
                  >
                    <CheckCircle size={18} />
                    Accept Job
                  </button>
                  <button 
                    className="reject-btn"
                    onClick={() => handleRejectJob(job.id)}
                  >
                    <XCircle size={18} />
                    Reject Job
                  </button>
                </div>
              )}

              {job.status === 'accepted' && (
                <div className="accepted-message">
                  <CheckCircle size={20} />
                  <span>Job accepted - Contact customer to schedule service</span>
                </div>
              )}

              {job.status === 'rejected' && (
                <div className="rejected-message">
                  <XCircle size={20} />
                  <span>Job rejected</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-navigation">
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/dashboard')}>
          <ArrowLeft size={20} />
          <span>Dashboard</span>
        </div>
        <div className="nav-item active">
          <Wrench size={20} />
          <span>Jobs</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/active-jobs')}>
          <CheckCircle size={20} />
          <span>Active Jobs</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/performance')}>
          <TrendingUp size={20} />
          <span>Performance & Safety</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/slots')}>
          <Clock size={20} />
          <span>Slots</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/profile')}>
          <User size={20} />
          <span>Profile</span>
        </div>
      </div>

      <style>{`
        .mechanic-jobs {
          min-height: 100vh;
          background: #f3f4f6;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
        }

        .jobs-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          color: #6b7280;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #e5e7eb;
          border-top: 4px solid #8B5CF6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .jobs-header {
          background: white;
          padding: 1.5rem 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .back-btn {
          background: none;
          border: none;
          padding: 0.5rem;
          border-radius: 0.5rem;
          cursor: pointer;
          color: #6b7280;
          transition: all 0.2s ease;
        }

        .back-btn:hover {
          background: #f3f4f6;
          color: #8B5CF6;
        }

        .jobs-header h1 {
          margin: 0;
          color: #1f2937;
          font-size: 1.5rem;
          font-weight: 600;
        }

        .header-stats {
          display: flex;
          gap: 1.5rem;
        }

        .stat-item {
          text-align: center;
        }

        .stat-number {
          display: block;
          font-size: 1.25rem;
          font-weight: 700;
          color: #1f2937;
        }

        .stat-label {
          font-size: 0.75rem;
          color: #6b7280;
        }

        .search-filter-bar {
          background: white;
          padding: 1rem;
          display: flex;
          gap: 1rem;
          align-items: center;
          border-bottom: 1px solid #e5e7eb;
        }

        .search-box {
          flex: 1;
          position: relative;
          display: flex;
          align-items: center;
        }

        .search-icon {
          position: absolute;
          left: 1rem;
          color: #6b7280;
        }

        .search-box input {
          width: 100%;
          padding: 0.75rem 1rem 0.75rem 3rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .search-box input:focus {
          border-color: #8B5CF6;
        }

        .filter-dropdown {
          position: relative;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .filter-icon {
          color: #6b7280;
        }

        .filter-dropdown select {
          padding: 0.75rem 2rem 0.75rem 1rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          outline: none;
          cursor: pointer;
          background: white;
        }

        .jobs-container {
          padding: 1rem;
        }

        .no-jobs {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 4rem 2rem;
          text-align: center;
        }

        .no-jobs svg {
          color: #9ca3af;
          margin-bottom: 1rem;
        }

        .no-jobs h3 {
          color: #6b7280;
          margin: 0 0 0.5rem 0;
        }

        .no-jobs p {
          color: #9ca3af;
          margin: 0;
        }

        .job-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          margin-bottom: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .job-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .job-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .customer-info {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .customer-name {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 600;
          color: #1f2937;
        }

        .customer-contact {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #6b7280;
          font-size: 0.875rem;
        }

        .job-badges {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .status-badge, .priority-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
          color: white;
        }

        .job-details {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }

        .detail-row {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          color: #6b7280;
          font-size: 0.875rem;
        }

        .detail-row svg {
          flex-shrink: 0;
          color: #8B5CF6;
        }

        .job-description {
          background: #f8fafc;
          padding: 1rem;
          border-radius: 0.5rem;
          margin-bottom: 1rem;
        }

        .job-description p {
          margin: 0;
          color: #4b5563;
          font-size: 0.875rem;
          line-height: 1.5;
        }

        .price-estimate {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background: #f0f9ff;
          border-radius: 0.5rem;
          margin-bottom: 1rem;
        }

        .estimate-label {
          color: #6b7280;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .estimate-value {
          color: #1f2937;
          font-weight: 600;
          font-size: 1rem;
        }

        .job-actions {
          display: flex;
          gap: 1rem;
        }

        .accept-btn, .reject-btn {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          border: none;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .accept-btn {
          background: #10b981;
          color: white;
        }

        .accept-btn:hover {
          background: #059669;
          transform: translateY(-1px);
        }

        .reject-btn {
          background: #ef4444;
          color: white;
        }

        .reject-btn:hover {
          background: #dc2626;
          transform: translateY(-1px);
        }

        .accepted-message, .rejected-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          border-radius: 0.5rem;
          font-size: 0.875rem;
        }

        .accepted-message {
          background: #d1fae5;
          color: #065f46;
        }

        .rejected-message {
          background: #fee2e2;
          color: #991b1b;
        }

        .bottom-navigation {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: white;
          border-top: 1px solid #e5e7eb;
          display: flex;
          justify-content: space-around;
          align-items: center;
          padding: 0.5rem 0;
          z-index: 9999;
          box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
        }

        .nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
          cursor: pointer;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          transition: all 0.2s ease;
          min-width: 60px;
        }

        .nav-item:hover {
          background: #f8fafc;
          transform: translateY(-2px);
        }

        .nav-item.active {
          color: #8B5CF6;
        }

        .nav-item.active svg {
          color: #8B5CF6;
        }

        .nav-item svg {
          color: #6b7280;
          transition: color 0.2s ease;
        }

        .nav-item:hover svg {
          color: #8B5CF6;
        }

        .nav-item span {
          font-size: 0.75rem;
          font-weight: 500;
          color: #6b7280;
          transition: color 0.2s ease;
        }

        .nav-item.active span {
          color: #8B5CF6;
          font-weight: 600;
        }

        .nav-item:hover span {
          color: #8B5CF6;
        }

        @media (max-width: 768px) {
          .jobs-header {
            flex-direction: column;
            gap: 1rem;
            align-items: flex-start;
          }

          .header-stats {
            width: 100%;
            justify-content: space-around;
          }

          .search-filter-bar {
            flex-direction: column;
          }

          .search-box {
            width: 100%;
          }

          .job-actions {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicJobs;
