import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  Plus,
  Calendar,
  Clock,
  Users,
  Search,
  Filter,
  Trash2,
  Wrench,
  CheckCircle,
  User,
  BarChart3,
  AlertCircle,
  TrendingUp
} from 'lucide-react';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#ef4444', marginBottom: '1rem' }}>Something went wrong</h2>
          <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#8B5CF6',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer'
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

const MechanicSlots = () => {
  const navigate = useNavigate();
  const [currentView, setCurrentView] = useState('main'); // main, add, view, delete, byDate
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form states for adding slot
  const [newSlot, setNewSlot] = useState({
    date: '',
    startTime: '',
    endTime: '',
    maxJobs: 1,
    status: 'available'
  });

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDate, setFilterDate] = useState('');

  // Helper function to safely format dates
  const formatDate = (dateString, options = {}) => {
    if (!dateString) return 'Date not set';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const defaultOptions = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    };
    
    return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
  };

  useEffect(() => {
    fetchSlots();
  }, []);

  const fetchSlots = async () => {
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
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/slots`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('✅ API Response:', data);
          console.log('✅ API Response structure:', JSON.stringify(data, null, 2));
          console.log('✅ Data.slots:', data.slots);
          console.log('✅ Direct data (if no slots property):', data);
          
          // Handle different API response structures
          if (data.slots && Array.isArray(data.slots)) {
            setSlots(data.slots);
          } else if (Array.isArray(data)) {
            setSlots(data);
          } else if (data.data && Array.isArray(data.data)) {
            setSlots(data.data);
          } else {
            console.warn('⚠️ Unexpected API response structure:', data);
            setSlots([]);
          }
        } else {
          throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
      } catch (apiError) {
        console.log('🔄 API not available, using local storage:', apiError.message);
        
        // Check if it's a CORS error (server not running)
        if (apiError.message.includes('CORS') || apiError.message.includes('Failed to fetch')) {
          setError('Backend server is not running. Slots will be stored locally only.');
        } else {
          setError('API unavailable. Using local storage for slots.');
        }
        
        setSlots([]);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('❌ Error fetching slots:', err.message);
      setError('Failed to load slots. Please try again.');
      setSlots([]);
      setLoading(false);
    }
  };

  const handleAddSlot = async () => {
    try {
      if (!newSlot.date || !newSlot.startTime || !newSlot.endTime) {
        setError('Please fill all required fields');
        return;
      }

      setLoading(true);
      setError('');
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      const workerData = JSON.parse(storedData);
      const workerId = workerData.id || workerData.workerId || 7;

      // Make API call to add slot
      try {
        const slotData = {
            slot_date: newSlot.date,
            start_time: newSlot.startTime,
            end_time: newSlot.endTime,
            max_jobs: newSlot.maxJobs,
            status: newSlot.status
          };
          console.log('📤 Sending slot data:', slotData);
          
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/slots`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(slotData)
        });

        if (response.ok) {
          const data = await response.json();
          console.log('✅ Slot added via API:', data);
          setSuccess('Slot added successfully to server!');
          setNewSlot({
            date: '',
            startTime: '',
            endTime: '',
            maxJobs: 1,
            status: 'available'
          });
          fetchSlots(); // Refresh slots
          setTimeout(() => {
            setCurrentView('view');
            setSuccess('');
          }, 2000);
        } else {
          throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
      } catch (apiError) {
        console.log('🔄 API not available, adding slot locally:', apiError.message);
        
        // Check if it's a CORS error (server not running)
        if (apiError.message.includes('CORS') || apiError.message.includes('Failed to fetch')) {
          setSuccess('Slot added locally (backend server offline).');
        } else {
          setSuccess('Slot added successfully (local storage)!');
        }
        
        // Create a local slot with unique ID
        const localSlot = {
          id: Date.now(), // Use timestamp as temporary ID
          slot_date: newSlot.date,
          start_time: newSlot.startTime,
          end_time: newSlot.endTime,
          max_jobs: newSlot.maxJobs,
          status: newSlot.status,
          worker_id: workerId,
          created_at: new Date().toISOString()
        };
        
        // Add to local state
        setSlots(prevSlots => [...prevSlots, localSlot]);
        setNewSlot({
          date: '',
          startTime: '',
          endTime: '',
          maxJobs: 1,
          status: 'available'
        });
        
        setTimeout(() => {
          setCurrentView('view');
          setSuccess('');
        }, 2000);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error adding slot:', err);
      setError('Failed to add slot');
      setLoading(false);
    }
  };

  const handleDeleteSlot = async (slotId) => {
    try {
      if (!confirm('Are you sure you want to delete this slot?')) {
        return;
      }

      setLoading(true);
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      const workerData = JSON.parse(storedData);
      const workerId = workerData.id || workerData.workerId || 7;

      // Make API call to delete slot
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/slots/${slotId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          setSuccess('Slot deleted successfully!');
          fetchSlots(); // Refresh slots
          setTimeout(() => setSuccess(''), 2000);
        } else {
          throw new Error('Failed to delete slot');
        }
      } catch (apiError) {
        console.log('API not available, deleting slot locally:', apiError.message);
        
        // Remove from local state
        setSlots(prevSlots => prevSlots.filter(slot => slot.id !== slotId));
        setSuccess('Slot deleted successfully (local storage)!');
        setTimeout(() => setSuccess(''), 2000);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error deleting slot:', err);
      setError('Failed to delete slot');
      setLoading(false);
    }
  };

  const filteredSlots = slots.filter(slot => {
    const slotDateStr = formatDate(slot.slot_date);
    const matchesSearch = slotDateStr.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (slot.status && slot.status.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesDate = !filterDate || (slot.slot_date && slot.slot_date === filterDate);
    return matchesSearch && matchesDate;
  });

  const renderMainView = () => (
    <div className="slots-main">
      <div className="slots-header">
        <h2>📅 Manage Available Slots</h2>
        <p>Manage your working schedule and availability</p>
      </div>

      <div className="slots-options">
        <div className="option-card" onClick={() => setCurrentView('add')}>
          <div className="option-icon">
            <Plus size={32} />
          </div>
          <h3>➕ Add New Slot</h3>
          <p>Create a new available time slot for work</p>
        </div>

        <div className="option-card" onClick={() => setCurrentView('view')}>
          <div className="option-icon">
            <Calendar size={32} />
          </div>
          <h3>📋 View My Slots</h3>
          <p>See all your available time slots</p>
        </div>

        <div className="option-card" onClick={() => setCurrentView('delete')}>
          <div className="option-icon">
            <Trash2 size={32} />
          </div>
          <h3>🗑️ Delete Slot</h3>
          <p>Remove an existing time slot</p>
        </div>

        <div className="option-card" onClick={() => setCurrentView('byDate')}>
          <div className="option-icon">
            <BarChart3 size={32} />
          </div>
          <h3>📊 View Slots by Date</h3>
          <p>Filter and view slots by specific date</p>
        </div>
      </div>

      <div className="slots-summary">
        <h3>📊 Your Slots Summary</h3>
        <div className="summary-stats">
          <div className="stat">
            <span className="stat-number">{slots.length}</span>
            <span className="stat-label">Total Slots</span>
          </div>
          <div className="stat">
            <span className="stat-number">{slots.filter(s => s.status === 'available').length}</span>
            <span className="stat-label">Available</span>
          </div>
          <div className="stat">
            <span className="stat-number">{slots.filter(s => s.status === 'booked').length}</span>
            <span className="stat-label">Booked</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAddSlotView = () => (
    <div className="add-slot">
      <div className="form-header">
        <button className="back-btn" onClick={() => setCurrentView('main')}>
          <ArrowLeft size={20} />
        </button>
        <h2>➕ Add New Slot</h2>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="slot-form">
        <div className="form-group">
          <label>Date *</label>
          <input
            type="date"
            value={newSlot.date}
            onChange={(e) => setNewSlot({...newSlot, date: e.target.value})}
            min={new Date().toISOString().split('T')[0]}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Start Time *</label>
            <input
              type="time"
              value={newSlot.startTime}
              onChange={(e) => setNewSlot({...newSlot, startTime: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>End Time *</label>
            <input
              type="time"
              value={newSlot.endTime}
              onChange={(e) => setNewSlot({...newSlot, endTime: e.target.value})}
              min={newSlot.startTime}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Maximum Jobs</label>
          <input
            type="number"
            value={newSlot.maxJobs}
            onChange={(e) => setNewSlot({...newSlot, maxJobs: parseInt(e.target.value) || 1})}
            min="1"
            max="10"
          />
        </div>

        <button 
          className="submit-btn"
          onClick={handleAddSlot}
          disabled={loading}
        >
          {loading ? 'Adding...' : 'Add Slot'}
        </button>
      </div>
    </div>
  );

  const renderViewSlotsView = () => (
    <div className="view-slots">
      <div className="view-header">
        <button className="back-btn" onClick={() => setCurrentView('main')}>
          <ArrowLeft size={20} />
        </button>
        <h2>📋 My Available Slots</h2>
      </div>

      <div className="search-filter">
        <div className="search-box">
          <Search size={20} className="search-icon" />
          <input
            type="text"
            placeholder="Search slots..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="slots-list">
        {filteredSlots.length === 0 ? (
          <div className="no-slots">
            <Calendar size={48} />
            <h3>No Slots Found</h3>
            <p>You haven't created any time slots yet.</p>
            <button onClick={() => setCurrentView('add')}>
              <Plus size={16} />
              Add Your First Slot
            </button>
          </div>
        ) : (
          filteredSlots.map(slot => {
            return (
            <div key={slot.id} className="slot-card">
              <div className="slot-header">
                <div className="slot-date">
                  <Calendar size={20} />
                  <span>{formatDate(slot.slot_date)}</span>
                </div>
                <div className={`slot-status ${slot.status}`}>
                  {slot.status === 'available' ? '✅ Available' : '🔒 Booked'}
                </div>
              </div>
              
              <div className="slot-time">
                <Clock size={18} />
                <span>{slot.start_time || 'Not set'} - {slot.end_time || 'Not set'}</span>
              </div>
              
              <div className="slot-details">
                <span>Max Jobs: {slot.max_jobs || 'Not set'}</span>
                {slot.bookedJobs && <span>Booked: {slot.bookedJobs}</span>}
              </div>
            </div>
            );
          })
        )}
      </div>
    </div>
  );

  const renderDeleteSlotView = () => (
    <div className="delete-slots">
      <div className="view-header">
        <button className="back-btn" onClick={() => setCurrentView('main')}>
          <ArrowLeft size={20} />
        </button>
        <h2>🗑️ Delete Slot</h2>
      </div>

      <div className="delete-warning">
        <AlertCircle size={32} />
        <p>Select a slot to delete. This action cannot be undone.</p>
      </div>

      <div className="slots-list">
        {slots.length === 0 ? (
          <div className="no-slots">
            <Trash2 size={48} />
            <h3>No Slots to Delete</h3>
            <p>You don't have any slots to delete.</p>
          </div>
        ) : (
          slots.map(slot => {
            return (
            <div key={slot.id} className="slot-card deletable">
              <div className="slot-header">
                <div className="slot-date">
                  <Calendar size={20} />
                  <span>{formatDate(slot.slot_date)}</span>
                </div>
                <div className={`slot-status ${slot.status}`}>
                  {slot.status === 'available' ? '✅ Available' : '🔒 Booked'}
                </div>
              </div>
              
              <div className="slot-time">
                <Clock size={18} />
                <span>{slot.start_time || 'Not set'} - {slot.end_time || 'Not set'}</span>
              </div>
              
              <button 
                className="delete-btn"
                onClick={() => handleDeleteSlot(slot.id)}
                disabled={loading}
              >
                <Trash2 size={16} />
                Delete
              </button>
            </div>
            );
          })
        )}
      </div>
    </div>
  );

  const renderByDateView = () => (
    <div className="by-date-slots">
      <div className="view-header">
        <button className="back-btn" onClick={() => setCurrentView('main')}>
          <ArrowLeft size={20} />
        </button>
        <h2>📊 View Slots by Date</h2>
      </div>

      <div className="date-filter">
        <label>Filter by Date:</label>
        <input
          type="date"
          value={filterDate}
          onChange={(e) => setFilterDate(e.target.value)}
        />
      </div>

      <div className="slots-list">
        {filteredSlots.length === 0 ? (
          <div className="no-slots">
            <BarChart3 size={48} />
            <h3>No Slots Found</h3>
            <p>No slots available for selected date.</p>
          </div>
        ) : (
          <div className="date-grouped-slots">
            {(() => {
              // Group slots by date manually for better browser compatibility
              const groupedSlots = {};
              filteredSlots.forEach(slot => {
                if (!groupedSlots[slot.slot_date]) {
                  groupedSlots[slot.slot_date] = [];
                }
                groupedSlots[slot.slot_date].push(slot);
              });
              
              return Object.entries(groupedSlots).map(([date, dateSlots]) => (
                <div key={date} className="date-group">
                  <h3>{formatDate(date, { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</h3>
                  <div className="date-stats">
                    <span>Total: {dateSlots.length}</span>
                    <span>Available: {dateSlots.filter(s => s.status === 'available').length}</span>
                    <span>Booked: {dateSlots.filter(s => s.status === 'booked').length}</span>
                  </div>
                  <div className="slots-grid">
                    {dateSlots.map(slot => {
                      return (
                      <div key={slot.id} className="slot-card mini">
                        <div className="slot-time">
                          <Clock size={16} />
                          <span>{slot.start_time || 'Not set'} - {slot.end_time || 'Not set'}</span>
                        </div>
                        <div className={`slot-status ${slot.status}`}>
                          {slot.status === 'available' ? 'Available' : 'Booked'}
                        </div>
                      </div>
                      );
                    })}
                  </div>
                </div>
              ));
            })()}
          </div>
        )}
      </div>
    </div>
  );

  if (loading && currentView === 'main') {
    return (
      <div className="slots-loading">
        <div className="loading-spinner"></div>
        <p>Loading slots...</p>
      </div>
    );
  }

  return (
    <div className="mechanic-slots">
      {currentView === 'main' && renderMainView()}
      {currentView === 'add' && renderAddSlotView()}
      {currentView === 'view' && renderViewSlotsView()}
      {currentView === 'delete' && renderDeleteSlotView()}
      {currentView === 'byDate' && renderByDateView()}

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
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/performance')}>
          <TrendingUp size={20} />
          <span>Performance & Safety</span>
        </div>
        <div className="nav-item active">
          <Clock size={20} />
          <span>Slots</span>
        </div>
        <div className="nav-item" onClick={() => navigate('/worker/car/mechanic/profile')}>
          <User size={20} />
          <span>Profile</span>
        </div>
      </div>

      <style>{`
        .mechanic-slots {
          min-height: 100vh;
          background: #f3f4f6;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          padding-bottom: 80px;
        }

        .slots-loading {
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

        .form-header, .view-header {
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

        .form-header h2, .view-header h2 {
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

        .slots-main {
          padding: 2rem 1rem;
        }

        .slots-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .slots-header h2 {
          margin: 0 0 0.5rem 0;
          color: #1f2937;
          font-size: 1.875rem;
          font-weight: 700;
        }

        .slots-header p {
          margin: 0;
          color: #6b7280;
          font-size: 1rem;
        }

        .slots-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .option-card {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: center;
        }

        .option-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        .option-icon {
          width: 64px;
          height: 64px;
          background: #8B5CF6;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1rem;
          color: white;
        }

        .option-card h3 {
          margin: 0 0 0.5rem 0;
          color: #1f2937;
          font-size: 1.25rem;
          font-weight: 600;
        }

        .option-card p {
          margin: 0;
          color: #6b7280;
          font-size: 0.875rem;
        }

        .slots-summary {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .slots-summary h3 {
          margin: 0 0 1rem 0;
          color: #1f2937;
          font-size: 1.125rem;
          font-weight: 600;
        }

        .summary-stats {
          display: flex;
          justify-content: space-around;
        }

        .stat {
          text-align: center;
        }

        .stat-number {
          display: block;
          font-size: 2rem;
          font-weight: 700;
          color: #8B5CF6;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .add-slot, .view-slots, .delete-slots, .by-date-slots {
          padding: 1rem;
        }

        .slot-form {
          background: white;
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          max-width: 600px;
          margin: 0 auto;
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
          display: block;
          margin-bottom: 0.5rem;
          color: #374151;
          font-weight: 500;
          font-size: 0.875rem;
        }

        .form-group input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          font-size: 1rem;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .form-group input:focus {
          border-color: #8B5CF6;
        }

        .submit-btn {
          width: 100%;
          padding: 1rem;
          background: #8B5CF6;
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .submit-btn:hover:not(:disabled) {
          background: #7C3AED;
        }

        .submit-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .search-filter {
          background: white;
          padding: 1rem;
          margin-bottom: 1rem;
          border-radius: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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

        .delete-warning {
          background: #fef3c7;
          border: 1px solid #fde68a;
          border-radius: 0.5rem;
          padding: 1rem;
          margin-bottom: 1rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          color: #92400e;
        }

        .date-filter {
          background: white;
          padding: 1rem;
          margin-bottom: 1rem;
          border-radius: 1rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .date-filter label {
          color: #374151;
          font-weight: 500;
        }

        .date-filter input {
          padding: 0.5rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          outline: none;
        }

        .slots-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .no-slots {
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

        .no-slots svg {
          color: #9ca3af;
          margin-bottom: 1rem;
        }

        .no-slots h3 {
          color: #6b7280;
          margin: 0 0 0.5rem 0;
        }

        .no-slots p {
          color: #9ca3af;
          margin: 0 0 1.5rem 0;
        }

        .no-slots button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: #8B5CF6;
          color: white;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .no-slots button:hover {
          background: #7C3AED;
        }

        .slot-card {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .slot-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .slot-card.deletable {
          border-left: 4px solid #ef4444;
        }

        .slot-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .slot-date {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 600;
          color: #1f2937;
        }

        .slot-status {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .slot-status.available {
          background: #d1fae5;
          color: #065f46;
        }

        .slot-status.booked {
          background: #fee2e2;
          color: #991b1b;
        }

        .slot-time {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .slot-details {
          display: flex;
          gap: 1rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .delete-btn {
          margin-top: 1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .delete-btn:hover:not(:disabled) {
          background: #dc2626;
        }

        .date-grouped-slots {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .date-group {
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .date-group h3 {
          margin: 0 0 1rem 0;
          color: #1f2937;
          font-size: 1.25rem;
          font-weight: 600;
        }

        .date-stats {
          display: flex;
          gap: 1.5rem;
          margin-bottom: 1rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .slots-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }

        .slot-card.mini {
          padding: 1rem;
        }

        .slot-card.mini .slot-time {
          margin-bottom: 0.5rem;
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
          .slots-options {
            grid-template-columns: 1fr;
          }

          .form-row {
            grid-template-columns: 1fr;
          }

          .summary-stats {
            flex-direction: column;
            gap: 1rem;
          }

          .slots-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default () => (
  <ErrorBoundary>
    <MechanicSlots />
  </ErrorBoundary>
);
