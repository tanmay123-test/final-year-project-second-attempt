import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Phone, Mail, MapPin, Truck, Wrench, Clock, DollarSign, CheckCircle, AlertCircle, Power } from 'lucide-react';

const TowTruckDetails = () => {
  const navigate = useNavigate();
  const [workerData, setWorkerData] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get worker data from localStorage
    const storedWorkerData = localStorage.getItem('workerData');
    const storedToken = localStorage.getItem('workerToken');
    const storedWorkerId = localStorage.getItem('workerId');

    if (storedWorkerData && storedToken) {
      const worker = JSON.parse(storedWorkerData);
      setWorkerData(worker);
      setIsOnline(worker.is_online === 1);
    } else {
      navigate('/worker/car/tow-truck/login');
    }
    setLoading(false);
  }, [navigate]);

  const handleOnlineToggle = async () => {
    try {
      const workerId = localStorage.getItem('workerId');
      const response = await fetch(`http://localhost:5000/api/tow-truck/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operator_id: parseInt(workerId),
          is_online: !isOnline
        })
      });

      if (response.ok) {
        const result = await response.json();
        setIsOnline(!isOnline);
        // Update local storage
        const updatedWorkerData = { ...workerData, is_online: !isOnline ? 1 : 0 };
        setWorkerData(updatedWorkerData);
        localStorage.setItem('workerData', JSON.stringify(updatedWorkerData));
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('workerToken');
    localStorage.removeItem('workerData');
    localStorage.removeItem('workerId');
    navigate('/worker/car/tow-truck/login');
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '4px solid #e5e7eb', 
            borderTop: '4px solid #16a34a', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ marginTop: '16px', color: '#16a34a' }}>Loading details...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
      <style>{`
        .details-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .header-card {
          background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
          border-radius: 16px;
          padding: 24px;
          color: white;
          margin-bottom: 24px;
          box-shadow: 0 4px 20px rgba(22, 163, 74, 0.15);
        }
        
        .status-bar {
          width: 100%;
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 8px;
        }
        
        .status-fill {
          height: 100%;
          background: linear-gradient(90deg, #16a34a 0%, #22c55e 100%);
          border-radius: 4px;
          transition: width 0.3s ease;
        }
        
        .details-table {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
          margin-bottom: 24px;
        }
        
        .table-header {
          background: #f8fafc;
          padding: 16px 20px;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .table-row {
          padding: 16px 20px;
          border-bottom: 1px solid #f1f5f9;
          display: flex;
          align-items: center;
          transition: background-color 0.2s ease;
        }
        
        .table-row:hover {
          background-color: #f8fafc;
        }
        
        .table-row:last-child {
          border-bottom: none;
        }
        
        .table-label {
          font-weight: 600;
          color: #374151;
          min-width: 200px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .table-value {
          color: #6b7280;
          flex: 1;
        }
        
        .status-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
          margin-bottom: 24px;
        }
        
        .status-button {
          width: 100%;
          padding: 12px 20px;
          border-radius: 8px;
          border: none;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          font-size: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }
        
        .status-button.online {
          background: #16a34a;
          color: white;
        }
        
        .status-button.offline {
          background: #f3f4f6;
          color: #6b7280;
        }
        
        .status-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }
        
        .info-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
          border: 1px solid #e5e7eb;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      <div className="details-container">
        {/* Header Card */}
        <div className="header-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: '700', margin: '0 0 4px 0' }}>
                Tow Truck Operator Details
              </h1>
              <p style={{ fontSize: '14px', opacity: 0.9, margin: 0 }}>
                Professional information and status management
              </p>
            </div>
            <button 
              onClick={handleLogout}
              style={{ 
                background: 'rgba(255, 255, 255, 0.2)', 
                border: '1px solid rgba(255, 255, 255, 0.3)', 
                borderRadius: '6px', 
                padding: '8px 12px',
                color: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
                fontWeight: '500'
              }}
            >
              <User size={16} />
              Logout
            </button>
          </div>
          
          {/* Status Radius Bar */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{
              width: '100%',
              height: '8px',
              background: '#e5e7eb',
              borderRadius: '4px',
              overflow: 'hidden',
              marginBottom: '8px'
            }}>
              <div 
                style={{
                  height: '100%',
                  background: 'linear-gradient(90deg, #16a34a 0%, #22c55e 100%)',
                  borderRadius: '4px',
                  transition: 'width 0.3s ease',
                  width: isOnline ? '100%' : '0%'
                }}
              ></div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', opacity: 0.9 }}>
                {isOnline ? '🟢 Online and Available' : '🔴 Offline'}
              </span>
              <span style={{ fontSize: '12px', opacity: 0.9 }}>
                {isOnline ? '100%' : '0%'}
              </span>
            </div>
          </div>
        </div>

        {/* Details Table */}
        <div className="details-table">
          <div className="table-header">
            <User size={20} style={{ color: '#16a34a' }} />
            <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              Personal Information
            </span>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <User size={16} style={{ color: '#16a34a' }} />
              Full Name
            </div>
            <div className="table-value">{workerData?.name || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Mail size={16} style={{ color: '#16a34a' }} />
              Email Address
            </div>
            <div className="table-value">{workerData?.email || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Phone size={16} style={{ color: '#16a34a' }} />
              Phone Number
            </div>
            <div className="table-value">{workerData?.phone || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <MapPin size={16} style={{ color: '#16a34a' }} />
              City
            </div>
            <div className="table-value">{workerData?.city || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Wrench size={16} style={{ color: '#16a34a' }} />
              Experience
            </div>
            <div className="table-value">{workerData?.experience || 'N/A'} years</div>
          </div>
        </div>

        {/* Vehicle Information Table */}
        <div className="details-table">
          <div className="table-header">
            <Truck size={20} style={{ color: '#16a34a' }} />
            <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              Vehicle Information
            </span>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Truck size={16} style={{ color: '#16a34a' }} />
              Truck Type
            </div>
            <div className="table-value">{workerData?.truck_type || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Wrench size={16} style={{ color: '#16a34a' }} />
              Truck Model
            </div>
            <div className="table-value">{workerData?.truck_model || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <AlertCircle size={16} style={{ color: '#16a34a' }} />
              Registration Number
            </div>
            <div className="table-value">{workerData?.truck_registration || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <DollarSign size={16} style={{ color: '#16a34a' }} />
              Truck Capacity
            </div>
            <div className="table-value">{workerData?.truck_capacity || 'N/A'}</div>
          </div>
        </div>

        {/* Truck Details Table - Exact Match */}
        <div className="details-table">
          <div className="table-header">
            <Truck size={20} style={{ color: '#16a34a' }} />
            <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              Truck Details
            </span>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Truck size={16} style={{ color: '#16a34a' }} />
              Truck Type
            </div>
            <div className="table-value">{workerData?.truck_type || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <AlertCircle size={16} style={{ color: '#16a34a' }} />
              Truck Number
            </div>
            <div className="table-value">{workerData?.truck_registration || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <Wrench size={16} style={{ color: '#16a34a' }} />
              Truck Model
            </div>
            <div className="table-value">{workerData?.truck_model || 'N/A'}</div>
          </div>
          
          <div className="table-row">
            <div className="table-label">
              <DollarSign size={16} style={{ color: '#16a34a' }} />
              Truck Capacity
            </div>
            <div className="table-value">{workerData?.truck_capacity || 'N/A'}</div>
          </div>
        </div>

        {/* Status Toggle Card */}
        <div className="status-card">
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '8px' }}>
              Availability Status
            </h3>
            <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
              {isOnline 
                ? 'You are currently online and available for tow requests. Customers can see you in their search results.' 
                : 'You are currently offline and not receiving requests. Toggle to online to start accepting jobs.'
              }
            </p>
          </div>
          <button 
            onClick={handleOnlineToggle}
            className={`status-button ${isOnline ? 'online' : 'offline'}`}
          >
            <Power size={16} />
            {isOnline ? '🟢 Go Offline' : '🔴 Go Online'}
          </button>
        </div>

        {/* Quick Info Cards */}
        <div className="info-grid">
          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <CheckCircle size={20} style={{ color: '#16a34a' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Approval Status
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Account verification
                </p>
              </div>
            </div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#16a34a' }}>
              {workerData?.approval_status || 'PENDING'}
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <Clock size={20} style={{ color: '#16a34a' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Member Since
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Registration date
                </p>
              </div>
            </div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#16a34a' }}>
              {workerData?.created_at ? new Date(workerData.created_at).toLocaleDateString() : 'N/A'}
            </div>
          </div>

          <div className="info-card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px', 
                background: '#dcfce7', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <AlertCircle size={20} style={{ color: '#16a34a' }} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 2px 0' }}>
                  Account ID
                </h3>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: 0 }}>
                  Unique identifier
                </p>
              </div>
            </div>
            <div style={{ fontSize: '14px', fontWeight: '600', color: '#16a34a' }}>
              #{workerData?.id || 'N/A'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TowTruckDetails;
