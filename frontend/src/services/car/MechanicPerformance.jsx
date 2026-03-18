import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  TrendingUp,
  Star,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Award,
  AlertTriangle,
  Shield,
  Phone,
  MapPin,
  Calendar,
  BarChart3,
  Activity,
  Zap,
  Users,
  DollarSign,
  Wrench
} from 'lucide-react';

const MechanicPerformance = () => {
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, panic, incident, reports, alerts
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Performance data state
  const [performanceData, setPerformanceData] = useState({
    rating: 5.0,
    total_jobs: 0,
    completed_jobs: 0,
    cancelled_jobs: 0,
    acceptance_rate: 0,
    completion_rate: 0,
    avg_response_time: 0
  });

  // Tips data state
  const [tipsData, setTipsData] = useState({
    performance_level: 'Average',
    tips: []
  });

  // Safety data state
  const [safetyReports, setSafetyReports] = useState([]);
  const [panicAlerts, setPanicAlerts] = useState([]);

  // Form states
  const [incidentForm, setIncidentForm] = useState({
    incident_type: '',
    description: '',
    job_id: null
  });

  const [panicForm, setPanicForm] = useState({
    location: '',
    job_id: null
  });

  useEffect(() => {
    fetchPerformanceData();
    fetchSafetyReports();
    fetchPanicAlerts();
  }, []);

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (!storedData || !token) {
        navigate('/worker/car/mechanic/login');
        return;
      }

      // Try to fetch real data from API
      try {
        const response = await fetch('http://127.0.0.1:5000/api/car/mechanic/performance', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setPerformanceData(data.performance || performanceData);
          setTipsData(data.tips || tipsData);
        } else {
          throw new Error('API not available');
        }
      } catch (apiError) {
        console.log('API not available, using default performance data:', apiError.message);
        // Use default data
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching performance data:', err);
      setError('Failed to load performance data');
      setLoading(false);
    }
  };

  const fetchSafetyReports = async () => {
    try {
      const token = localStorage.getItem('workerToken');
      
      try {
        const response = await fetch('http://127.0.0.1:5000/api/car/mechanic/safety-reports', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setSafetyReports(data.reports || []);
        }
      } catch (apiError) {
        console.log('Safety reports API not available:', apiError.message);
      }
    } catch (err) {
      console.error('Error fetching safety reports:', err);
    }
  };

  const fetchPanicAlerts = async () => {
    try {
      const token = localStorage.getItem('workerToken');
      
      try {
        const response = await fetch('http://127.0.0.1:5000/api/car/mechanic/panic-alerts', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setPanicAlerts(data.alerts || []);
        } else {
          throw new Error('API not available');
        }
      } catch (apiError) {
        console.log('Panic alerts API not available, using local storage:', apiError.message);
        
        // Load panic alerts from local storage
        const storedAlerts = localStorage.getItem('panicAlerts');
        if (storedAlerts) {
          setPanicAlerts(JSON.parse(storedAlerts));
        }
      }
    } catch (err) {
      console.error('Error fetching panic alerts:', err);
    }
  };

  const sendPanicAlert = async () => {
    try {
      if (!confirm('Are you sure you want to send panic alert? This will immediately notify admin for help.')) {
        return;
      }

      setLoading(true);
      const token = localStorage.getItem('workerToken');
      
      try {
        const response = await fetch('http://127.0.0.1:5000/api/car/mechanic/panic-alert', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(panicForm)
        });

        if (response.ok) {
          const data = await response.json();
          setSuccess('Panic alert sent successfully! Admin has been notified.');
          setPanicForm({ location: '', job_id: null });
          fetchPanicAlerts();
          setTimeout(() => setSuccess(''), 3000);
        } else {
          throw new Error('Failed to send panic alert');
        }
      } catch (apiError) {
        console.log('Panic alert API not available, saving locally:', apiError.message);
        
        // Create local panic alert
        const newAlert = {
          id: Date.now(),
          location: panicForm.location || 'Unknown location',
          status: 'PENDING',
          created_at: new Date().toISOString(),
          resolved_at: null
        };
        
        // Save to local storage
        const storedAlerts = localStorage.getItem('panicAlerts');
        const alerts = storedAlerts ? JSON.parse(storedAlerts) : [];
        alerts.push(newAlert);
        localStorage.setItem('panicAlerts', JSON.stringify(alerts));
        
        setPanicAlerts(alerts);
        setSuccess('Panic alert sent (local storage). Admin would be notified in production.');
        setPanicForm({ location: '', job_id: null });
        setTimeout(() => setSuccess(''), 3000);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error sending panic alert:', err);
      setError('Failed to send panic alert');
      setLoading(false);
    }
  };

  const reportIncident = async () => {
    try {
      if (!incidentForm.incident_type || !incidentForm.description) {
        setError('Please fill all required fields');
        return;
      }

      setLoading(true);
      const token = localStorage.getItem('workerToken');
      
      try {
        const response = await fetch('http://127.0.0.1:5000/api/car/mechanic/report-incident', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(incidentForm)
        });

        if (response.ok) {
          const data = await response.json();
          setSuccess('Incident reported successfully!');
          setIncidentForm({ incident_type: '', description: '', job_id: null });
          fetchSafetyReports();
          setTimeout(() => setSuccess(''), 3000);
        } else {
          throw new Error('Failed to report incident');
        }
      } catch (apiError) {
        console.log('Incident report API not available, simulating:', apiError.message);
        setSuccess('Incident reported (local simulation). Report would be saved in production.');
        setIncidentForm({ incident_type: '', description: '', job_id: null });
        setTimeout(() => setSuccess(''), 3000);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error reporting incident:', err);
      setError('Failed to report incident');
      setLoading(false);
    }
  };

  const renderDashboard = () => (
    <div className="performance-dashboard">
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* Performance Metrics */}
      <div className="metrics-section">
        <h3>📈 Performance Metrics</h3>
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">
              <Star size={24} />
            </div>
            <div className="metric-content">
              <div className="metric-value">{performanceData.rating.toFixed(1)}</div>
              <div className="metric-label">Rating</div>
              <div className="metric-sublabel">out of 5.0</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <CheckCircle size={24} />
            </div>
            <div className="metric-content">
              <div className="metric-value">{(performanceData.completion_rate * 100).toFixed(1)}%</div>
              <div className="metric-label">Completion Rate</div>
              <div className="metric-sublabel">jobs completed</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <Target size={24} />
            </div>
            <div className="metric-content">
              <div className="metric-value">{(performanceData.acceptance_rate * 100).toFixed(1)}%</div>
              <div className="metric-label">Acceptance Rate</div>
              <div className="metric-sublabel">jobs accepted</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <Clock size={24} />
            </div>
            <div className="metric-content">
              <div className="metric-value">{performanceData.avg_response_time.toFixed(1)}s</div>
              <div className="metric-label">Avg Response</div>
              <div className="metric-sublabel">response time</div>
            </div>
          </div>
        </div>

        <div className="job-stats">
          <div className="stat-item">
            <div className="stat-number">{performanceData.total_jobs}</div>
            <div className="stat-label">Total Jobs</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{performanceData.completed_jobs}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{performanceData.cancelled_jobs}</div>
            <div className="stat-label">Cancelled</div>
          </div>
        </div>
      </div>

      {/* Performance Tips */}
      <div className="tips-section">
        <h3>💡 Performance Tips</h3>
        <div className="performance-level">
          <span className="level-badge">{tipsData.performance_level}</span>
        </div>
        <div className="tips-list">
          {tipsData.tips.length > 0 ? (
            tipsData.tips.map((tip, index) => (
              <div key={index} className="tip-item">
                <Zap size={16} />
                <span>{tip}</span>
              </div>
            ))
          ) : (
            <div className="no-tips">
              <p>Keep up the good work! More tips will appear as you complete more jobs.</p>
            </div>
          )}
        </div>
      </div>

      {/* Safety Tools */}
      <div className="safety-section">
        <h3>🛡️ Safety Tools</h3>
        <div className="safety-grid">
          <div className="safety-card panic" onClick={() => setCurrentView('panic')}>
            <div className="safety-icon">
              <AlertTriangle size={32} />
            </div>
            <h4>🚨 Panic Alert</h4>
            <p>Send emergency alert for immediate help</p>
          </div>

          <div className="safety-card incident" onClick={() => setCurrentView('incident')}>
            <div className="safety-icon">
              <Shield size={32} />
            </div>
            <h4>📝 Report Incident</h4>
            <p>Report safety incidents or issues</p>
          </div>

          <div className="safety-card reports" onClick={() => setCurrentView('reports')}>
            <div className="safety-icon">
              <BarChart3 size={32} />
            </div>
            <h4>📋 Safety Reports</h4>
            <p>View your incident reports history</p>
          </div>

          <div className="safety-card alerts" onClick={() => setCurrentView('alerts')}>
            <div className="safety-icon">
              <Phone size={32} />
            </div>
            <h4>📋 Panic Alerts</h4>
            <p>View your panic alerts history</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPanicAlert = () => (
    <div className="panic-alert">
      <div className="section-header">
        <button className="back-btn" onClick={() => setCurrentView('dashboard')}>
          <ArrowLeft size={20} />
        </button>
        <h2>🚨 Panic Alert</h2>
      </div>

      <div className="panic-warning">
        <AlertTriangle size={48} />
        <h3>Emergency Alert System</h3>
        <p>This will immediately notify admin for help. Use only in emergency situations.</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="panic-form">
        <div className="form-group">
          <label>Current Location (optional)</label>
          <input
            type="text"
            placeholder="Enter your current location"
            value={panicForm.location}
            onChange={(e) => setPanicForm({...panicForm, location: e.target.value})}
          />
        </div>

        <button 
          className="panic-btn"
          onClick={sendPanicAlert}
          disabled={loading}
        >
          {loading ? 'Sending Alert...' : '🚨 Send Panic Alert'}
        </button>
      </div>
    </div>
  );

  const renderIncidentReport = () => (
    <div className="incident-report">
      <div className="section-header">
        <button className="back-btn" onClick={() => setCurrentView('dashboard')}>
          <ArrowLeft size={20} />
        </button>
        <h2>📝 Report Incident</h2>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="incident-form">
        <div className="form-group">
          <label>Incident Type *</label>
          <select
            value={incidentForm.incident_type}
            onChange={(e) => setIncidentForm({...incidentForm, incident_type: e.target.value})}
          >
            <option value="">Select incident type</option>
            <option value="Unsafe location">Unsafe location</option>
            <option value="Fraud customer">Fraud customer</option>
            <option value="Payment dispute">Payment dispute</option>
            <option value="Threat">Threat</option>
            <option value="Fake booking">Fake booking</option>
          </select>
        </div>

        <div className="form-group">
          <label>Description *</label>
          <textarea
            placeholder="Describe the incident in detail..."
            value={incidentForm.description}
            onChange={(e) => setIncidentForm({...incidentForm, description: e.target.value})}
            rows={4}
          />
        </div>

        <button 
          className="submit-btn"
          onClick={reportIncident}
          disabled={loading}
        >
          {loading ? 'Reporting...' : '📝 Report Incident'}
        </button>
      </div>
    </div>
  );

  const renderSafetyReports = () => (
    <div className="safety-reports">
      <div className="section-header">
        <button className="back-btn" onClick={() => setCurrentView('dashboard')}>
          <ArrowLeft size={20} />
        </button>
        <h2>📋 Safety Reports</h2>
      </div>

      <div className="reports-list">
        {safetyReports.length === 0 ? (
          <div className="no-reports">
            <Shield size={48} />
            <h3>No Safety Reports</h3>
            <p>You haven't reported any incidents yet.</p>
          </div>
        ) : (
          safetyReports.map((report) => (
            <div key={report.id} className="report-card">
              <div className="report-header">
                <span className="report-id">Report #{report.id}</span>
                <span className="report-status">{report.status}</span>
              </div>
              <div className="report-type">
                <AlertTriangle size={16} />
                <span>{report.incident_type}</span>
              </div>
              <div className="report-description">
                {report.description}
              </div>
              <div className="report-date">
                <Calendar size={14} />
                <span>{new Date(report.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="reports-summary">
        <div className="summary-stat">
          <span className="summary-number">{safetyReports.length}</span>
          <span className="summary-label">Total Reports</span>
        </div>
      </div>
    </div>
  );

  const renderPanicAlerts = () => (
    <div className="panic-alerts">
      <div className="section-header">
        <button className="back-btn" onClick={() => setCurrentView('dashboard')}>
          <ArrowLeft size={20} />
        </button>
        <h2>📋 Panic Alerts</h2>
      </div>

      <div className="alerts-list">
        {panicAlerts.length === 0 ? (
          <div className="no-alerts">
            <Phone size={48} />
            <h3>No Panic Alerts</h3>
            <p>You haven't sent any panic alerts yet.</p>
          </div>
        ) : (
          panicAlerts.map((alert) => (
            <div key={alert.id} className="alert-card">
              <div className="alert-header">
                <span className="alert-id">Alert #{alert.id}</span>
                <span className={`alert-status ${alert.status.toLowerCase()}`}>
                  {alert.status}
                </span>
              </div>
              <div className="alert-location">
                <MapPin size={16} />
                <span>{alert.location}</span>
              </div>
              <div className="alert-date">
                <Calendar size={14} />
                <span>{new Date(alert.created_at).toLocaleDateString()}</span>
              </div>
              {alert.resolved_at && (
                <div className="alert-resolved">
                  <CheckCircle size={14} />
                  <span>Resolved: {new Date(alert.resolved_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <div className="alerts-summary">
        <div className="summary-stat">
          <span className="summary-number">{panicAlerts.length}</span>
          <span className="summary-label">Total Alerts</span>
        </div>
      </div>
    </div>
  );

  if (loading && currentView === 'dashboard') {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading performance data...</p>
      </div>
    );
  }

  return (
    <div className="mechanic-performance">
      {currentView === 'dashboard' && renderDashboard()}
      {currentView === 'panic' && renderPanicAlert()}
      {currentView === 'incident' && renderIncidentReport()}
      {currentView === 'reports' && renderSafetyReports()}
      {currentView === 'alerts' && renderPanicAlerts()}

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
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/active-jobs')}>
          <CheckCircle size={20} />
          <span>Active Jobs</span>
        </div>
        <div className="nav-item active">
          <TrendingUp size={20} />
          <span>Performance & Safety</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/slots')}>
          <Clock size={20} />
          <span>Slots</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/profile')}>
          <Users size={20} />
          <span>Profile</span>
        </div>
      </div>

      <style>{`
        .mechanic-performance {
          min-height: 100vh;
          background: #f8fafc;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
        }

        .loading-container {
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

        .section-header {
          background: white;
          padding: 1.5rem 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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

        .section-header h2 {
          margin: 0;
          color: #1f2937;
          font-size: 1.5rem;
          font-weight: 600;
        }

        .error-message, .success-message {
          margin: 1rem;
          padding: 0.75rem;
          border-radius: 0.5rem;
          font-size: 0.875rem;
        }

        .error-message {
          background: #fee2e2;
          color: #991b1b;
          border: 1px solid #fecaca;
        }

        .success-message {
          background: #d1fae5;
          color: #065f46;
          border: 1px solid #a7f3d0;
        }

        .performance-dashboard {
          padding: 2rem 1rem;
        }

        .dashboard-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .dashboard-header h2 {
          margin: 0 0 0.5rem 0;
          color: #1f2937;
          font-size: 1.875rem;
          font-weight: 700;
        }

        .dashboard-header p {
          margin: 0;
          color: #6b7280;
          font-size: 1rem;
        }

        .metrics-section {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin-bottom: 2rem;
        }

        .metrics-section h3 {
          margin: 0 0 1.5rem 0;
          color: #1f2937;
          font-size: 1.25rem;
          font-weight: 600;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .metric-card {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1.5rem;
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          border-radius: 1rem;
          color: white;
        }

        .metric-icon {
          width: 48px;
          height: 48px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .metric-content {
          flex: 1;
        }

        .metric-value {
          font-size: 2rem;
          font-weight: 700;
          line-height: 1;
        }

        .metric-label {
          font-size: 0.875rem;
          opacity: 0.9;
          margin-top: 0.25rem;
        }

        .metric-sublabel {
          font-size: 0.75rem;
          opacity: 0.7;
        }

        .job-stats {
          display: flex;
          justify-content: space-around;
          padding-top: 1.5rem;
          border-top: 1px solid #e5e7eb;
        }

        .stat-item {
          text-align: center;
        }

        .stat-number {
          display: block;
          font-size: 1.5rem;
          font-weight: 700;
          color: #8B5CF6;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #6b7280;
          margin-top: 0.25rem;
        }

        .tips-section {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          margin-bottom: 2rem;
        }

        .tips-section h3 {
          margin: 0 0 1rem 0;
          color: #1f2937;
          font-size: 1.25rem;
          font-weight: 600;
        }

        .performance-level {
          margin-bottom: 1rem;
        }

        .level-badge {
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 600;
        }

        .tips-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .tip-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: #f8fafc;
          border-radius: 0.5rem;
          color: #4b5563;
        }

        .tip-item svg {
          color: #8B5CF6;
          flex-shrink: 0;
        }

        .no-tips {
          text-align: center;
          padding: 2rem;
          color: #6b7280;
        }

        .safety-section {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .safety-section h3 {
          margin: 0 0 1.5rem 0;
          color: #1f2937;
          font-size: 1.25rem;
          font-weight: 600;
        }

        .safety-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .safety-card {
          padding: 1.5rem;
          border-radius: 1rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s ease;
          border: 2px solid transparent;
        }

        .safety-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .safety-card.panic {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
        }

        .safety-card.incident {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
        }

        .safety-card.reports {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          color: white;
        }

        .safety-card.alerts {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
        }

        .safety-icon {
          width: 64px;
          height: 64px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
        }

        .safety-card h4 {
          margin: 0 0 0.5rem 0;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .safety-card p {
          margin: 0;
          font-size: 0.875rem;
          opacity: 0.9;
        }

        .panic-alert, .incident-report, .safety-reports, .panic-alerts {
          padding: 1rem;
        }

        .panic-warning {
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
          padding: 2rem;
          border-radius: 1rem;
          text-align: center;
          margin-bottom: 2rem;
        }

        .panic-warning svg {
          margin-bottom: 1rem;
        }

        .panic-warning h3 {
          margin: 0 0 1rem 0;
          font-size: 1.5rem;
          font-weight: 600;
        }

        .panic-warning p {
          margin: 0;
          opacity: 0.9;
        }

        .panic-form, .incident-form {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          color: #374151;
          font-weight: 500;
          font-size: 0.875rem;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          font-size: 1rem;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
          border-color: #8B5CF6;
        }

        .panic-btn {
          width: 100%;
          padding: 1rem;
          background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .panic-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        }

        .submit-btn {
          width: 100%;
          padding: 1rem;
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .submit-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #7C3AED 0%, #6d28d9 100%);
        }

        .submit-btn:disabled,
        .panic-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .reports-list, .alerts-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .no-reports, .no-alerts {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 4rem 2rem;
          text-align: center;
          background: white;
          border-radius: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .no-reports svg, .no-alerts svg {
          color: #9ca3af;
          margin-bottom: 1rem;
        }

        .no-reports h3, .no-alerts h3 {
          color: #6b7280;
          margin: 0 0 0.5rem 0;
        }

        .no-reports p, .no-alerts p {
          color: #9ca3af;
          margin: 0;
        }

        .report-card, .alert-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          transition: transform 0.2s ease;
        }

        .report-card:hover, .alert-card:hover {
          transform: translateY(-2px);
        }

        .report-header, .alert-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .report-id, .alert-id {
          font-weight: 600;
          color: #1f2937;
        }

        .report-status, .alert-status {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .report-status {
          background: #e5e7eb;
          color: #6b7280;
        }

        .alert-status {
          background: #e5e7eb;
          color: #6b7280;
        }

        .alert-status.resolved {
          background: #d1fae5;
          color: #065f46;
        }

        .report-type, .alert-location {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          color: #6b7280;
        }

        .report-description {
          color: #4b5563;
          margin-bottom: 1rem;
          line-height: 1.5;
        }

        .report-date, .alert-date, .alert-resolved {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          color: #9ca3af;
        }

        .alert-resolved {
          color: #065f46;
        }

        .reports-summary, .alerts-summary {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          text-align: center;
        }

        .summary-stat {
          display: inline-block;
        }

        .summary-number {
          display: block;
          font-size: 2rem;
          font-weight: 700;
          color: #8B5CF6;
        }

        .summary-label {
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
          .metrics-grid {
            grid-template-columns: 1fr;
          }

          .safety-grid {
            grid-template-columns: 1fr;
          }

          .job-stats {
            flex-direction: column;
            gap: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicPerformance;
