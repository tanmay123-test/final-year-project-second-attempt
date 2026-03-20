import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  CheckCircle,
  Clock,
  MapPin,
  Phone,
  Calendar,
  Car,
  Wrench,
  User,
  AlertCircle,
  Search,
  Filter,
  MessageCircle,
  Navigation,
  TrendingUp,
  Shield
} from 'lucide-react';

const MechanicActiveJobs = () => {
  const navigate = useNavigate();
  const [activeJobs, setActiveJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchActiveJobs();
  }, []);

  const fetchActiveJobs = async () => {
    try {
      setLoading(true);
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
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/active-jobs`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setActiveJobs(data.activeJobs || []);
        } else {
          throw new Error('API not available');
        }
      } catch (apiError) {
        console.log('API endpoints not available, using empty active jobs list:', apiError.message);
        
        // Set empty active jobs array - no hardcoded data
        setActiveJobs([]);
        setError('No active jobs available');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching active jobs:', err.message);
      setError('Failed to load active jobs');
      setActiveJobs([]);
      setLoading(false);
    }
  };

  const handleCompleteJob = async (jobId) => {
    try {
      const token = localStorage.getItem('workerToken');
      
      // Update job status in local state immediately for better UX
      setActiveJobs(prevJobs => 
        prevJobs.map(job => 
          job.id === jobId 
            ? { ...job, status: 'completed' }
            : job
        )
      );

      // Make API call to update status
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/jobs/${jobId}/complete`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          // If API call fails, revert the state
          setActiveJobs(prevJobs => 
            prevJobs.map(job => 
              job.id === jobId 
                ? { ...job, status: 'accepted' }
                : job
            )
          );
          console.error('Failed to complete job on server');
        }
      } catch (apiError) {
        console.log('API call failed, but local state updated:', apiError.message);
      }
    } catch (err) {
      console.error('Error completing job:', err);
    }
  };

  const filteredActiveJobs = activeJobs.filter(job => {
    const matchesSearch = job.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.serviceType.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.carModel.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  const getStatusColor = (status) => {
    switch(status) {
      case 'accepted': return '#10b981';
      case 'in-progress': return '#f59e0b';
      case 'completed': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getStatusText = (status) => {
    switch(status) {
      case 'accepted': return 'Accepted - Ready to Start';
      case 'in-progress': return 'In Progress';
      case 'completed': return 'Completed';
      default: return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="active-jobs-loading">
        <div className="loading-spinner"></div>
        <p>Loading active jobs...</p>
      </div>
    );
  }

  return (
    <div className="mechanic-active-jobs">
      {/* Header */}
      <div className="jobs-header">
        <div className="header-left">
          <button className="back-btn" onClick={() => navigate('/worker/car/mechanic/dashboard')}>
            <ArrowLeft size={20} />
          </button>
          <h1>Active Jobs</h1>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-number">{filteredActiveJobs.length}</span>
            <span className="stat-label">Active</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{activeJobs.filter(j => j.status === 'in-progress').length}</span>
            <span className="stat-label">In Progress</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{activeJobs.filter(j => j.status === 'accepted').length}</span>
            <span className="stat-label">Pending Start</span>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-bar">
        <div className="search-box">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search active jobs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Active Jobs List */}
      <div className="jobs-container">
        {filteredActiveJobs.length === 0 ? (
          <div className="no-jobs">
            <CheckCircle size={48} />
            <h3>No Active Jobs</h3>
            <p>You don't have any active jobs at the moment. Check the Jobs section to accept new requests.</p>
          </div>
        ) : (
          filteredActiveJobs.map(job => (
            <div key={job.id} className="active-job-card">
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
                <div className="job-status">
                  <span 
                    className="status-badge" 
                    style={{ backgroundColor: getStatusColor(job.status) }}
                  >
                    {getStatusText(job.status)}
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

              {/* Price */}
              <div className="price-estimate">
                <span className="estimate-label">Price:</span>
                <span className="estimate-value">{job.estimatedPrice}</span>
              </div>

              {/* Action Buttons */}
              <div className="job-actions">
                {job.status === 'accepted' && (
                  <div className="action-buttons">
                    <button className="start-job-btn">
                      <Clock size={18} />
                      Start Job
                    </button>
                    <button className="contact-btn">
                      <MessageCircle size={18} />
                      Contact
                    </button>
                    <button className="navigate-btn">
                      <Navigation size={18} />
                      Navigate
                    </button>
                  </div>
                )}

                {job.status === 'in-progress' && (
                  <div className="action-buttons">
                    <button 
                      className="complete-btn"
                      onClick={() => handleCompleteJob(job.id)}
                    >
                      <CheckCircle size={18} />
                      Complete Job
                    </button>
                    <button className="contact-btn">
                      <MessageCircle size={18} />
                      Contact
                    </button>
                  </div>
                )}

                {job.status === 'completed' && (
                  <div className="completed-message">
                    <CheckCircle size={20} />
                    <span>Job completed successfully</span>
                  </div>
                )}
              </div>
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
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/jobs')}>
          <Wrench size={20} />
          <span>Jobs</span>
        </div>
        <div className="nav-item active">
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
        .mechanic-active-jobs {
          min-height: 100vh;
          background: #f3f4f6;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
        }

        .active-jobs-loading {
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

        .search-bar {
          background: white;
          padding: 1rem;
          border-bottom: 1px solid #e5e7eb;
        }

        .search-box {
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
          color: #10b981;
          margin-bottom: 1rem;
        }

        .no-jobs h3 {
          color: #1f2937;
          margin: 0 0 0.5rem 0;
        }

        .no-jobs p {
          color: #6b7280;
          margin: 0;
        }

        .active-job-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          margin-bottom: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border-left: 4px solid #10b981;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .active-job-card:hover {
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

        .job-status {
          flex-shrink: 0;
        }

        .status-badge {
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
          background: #f0f9ff;
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
          background: #f0fdf4;
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
          margin-top: 1rem;
        }

        .action-buttons {
          display: flex;
          gap: 0.75rem;
          flex-wrap: wrap;
        }

        .start-job-btn, .complete-btn {
          flex: 1;
          min-width: 120px;
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

        .start-job-btn {
          background: #f59e0b;
          color: white;
        }

        .start-job-btn:hover {
          background: #d97706;
          transform: translateY(-1px);
        }

        .complete-btn {
          background: #10b981;
          color: white;
        }

        .complete-btn:hover {
          background: #059669;
          transform: translateY(-1px);
        }

        .contact-btn, .navigate-btn {
          flex: 1;
          min-width: 100px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          border: 1px solid #e5e7eb;
          background: white;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .contact-btn:hover, .navigate-btn:hover {
          background: #f8fafc;
          border-color: #8B5CF6;
          color: #8B5CF6;
          transform: translateY(-1px);
        }

        .completed-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background: #f3f4f6;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          color: #6b7280;
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

          .action-buttons {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicActiveJobs;
