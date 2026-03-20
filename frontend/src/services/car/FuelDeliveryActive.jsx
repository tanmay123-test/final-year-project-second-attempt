import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  ArrowLeft,
  MapPin,
  Phone,
  DollarSign,
  User,
  MessageSquare,
  XCircle,
  Package
} from 'lucide-react';

const FuelDeliveryActive = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeDelivery, setActiveDelivery] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deliveryTime, setDeliveryTime] = useState(0);
  const [deliveryNote, setDeliveryNote] = useState('');
  const [showNoteInput, setShowNoteInput] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [cancelReason, setCancelReason] = useState('');
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    fetchActiveDelivery();
  }, []);

  const fetchActiveDelivery = async () => {
    try {
      setLoading(true);
      const workerId = localStorage.getItem('workerId');
      const workerData = localStorage.getItem('workerData');
      const workerToken = localStorage.getItem('workerToken');
      
      console.log('Debug - Storage check:', {
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
              console.log('Fallback: Using worker ID from workerData:', parsedWorkerData.id);
              localStorage.setItem('workerId', parsedWorkerData.id.toString());
              // Continue with the fetched workerId
            } else {
              console.error('Worker ID not found in workerData either');
              setError('Worker not authenticated - Please login again');
              setLoading(false);
              return;
            }
          } catch (e) {
            console.error('Error parsing workerData:', e);
            setError('Worker not authenticated - Please login again');
            setLoading(false);
            return;
          }
        } else {
          console.error('Worker ID not found in localStorage');
          setError('Worker not authenticated - Please login again');
          setLoading(false);
          return;
        }
      }

      // Fetch active delivery from backend
      const response = await fetch(`http://localhost:5000/api/fuel-delivery/active-delivery/${workerId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          // No active delivery
          setActiveDelivery(null);
        } else {
          throw new Error('Failed to fetch active delivery');
        }
      } else {
        const data = await response.json();
        if (data.success && data.delivery) {
          setActiveDelivery(data.delivery);
          // Set current step based on delivery status
          setCurrentStep(data.delivery.status === 'on_the_way' ? 1 : 
                       data.delivery.status === 'arrived' ? 2 : 3);
        } else {
          setActiveDelivery(null);
        }
      }
    } catch (error) {
      console.error('Error fetching active delivery:', error);
      setError('Failed to load active delivery');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '48px', 
            height: '48px', 
            border: '4px solid #f3f4f6', 
            borderTop: '4px solid #ff6b35', 
            borderRadius: '50%', 
            animation: 'spin 1s linear infinite',
            margin: '0 auto'
          }}></div>
          <p style={{ marginTop: '16px', color: '#6b7280' }}>Loading active delivery...</p>
        </div>
      </div>
    );
  }

  if (!activeDelivery) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <Package style={{ width: '64px', height: '64px', color: '#9ca3af', margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#111827', marginBottom: '8px' }}>No Active Delivery</h3>
          <p style={{ color: '#6b7280', marginBottom: '16px' }}>You don't have any active fuel deliveries at the moment.</p>
          <button
            onClick={() => navigate('/worker/car/fuel-delivery/requests')}
            style={{ padding: '8px 16px', background: '#ff6b35', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '500', cursor: 'pointer' }}
          >
            View Available Requests
          </button>
        </div>
      </div>
    );
  }

  // Button handlers
  const handleNavigate = () => {
    if (activeDelivery?.delivery_address) {
      window.open(`https://maps.google.com/?q=${encodeURIComponent(activeDelivery.delivery_address)}`, '_blank');
    }
  };

  const handleCancelDelivery = async () => {
    if (!window.confirm('Are you sure you want to cancel this delivery?')) {
      return;
    }

    try {
      setCancelling(true);
      const workerId = localStorage.getItem('workerId');
      
      const response = await fetch(`http://localhost:5000/api/fuel-delivery/queue/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worker_id: workerId,
          cancel_reason: 'Cancelled by worker'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Delivery cancelled successfully');
        navigate('/worker/car/fuel-delivery/home');
      } else {
        alert('Failed to cancel delivery: ' + data.message);
      }
    } catch (error) {
      console.error('Error cancelling delivery:', error);
      alert('Error cancelling delivery');
    } finally {
      setCancelling(false);
    }
  };

  const handleMarkAsArrived = async () => {
    if (currentStep >= 2) return;

    try {
      const workerId = localStorage.getItem('workerId');
      
      const response = await fetch(`http://localhost:5000/api/fuel-delivery/delivery/start-arrival`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worker_id: workerId,
          status: 'arrived'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setCurrentStep(2);
        alert('Status updated to Arrived');
      } else {
        alert('Failed to update status: ' + data.message);
      }
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Error updating status');
    }
  };

  const handleMarkAsDelivered = async () => {
    if (!window.confirm('Mark this delivery as complete?')) {
      return;
    }

    try {
      setCompleting(true);
      const workerId = localStorage.getItem('workerId');
      
      const response = await fetch(`http://localhost:5000/api/fuel-delivery/delivery/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          worker_id: workerId,
          delivery_note: deliveryNote
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert('Delivery completed successfully! Earnings added to your account.');
        navigate('/worker/car/fuel-delivery/home');
      } else {
        alert('Failed to complete delivery: ' + data.message);
      }
    } catch (error) {
      console.error('Error completing delivery:', error);
      alert('Error completing delivery');
    } finally {
      setCompleting(false);
    }
  };

  const handleViewDetails = () => {
    // Scroll to customer details section
    const element = document.querySelector('[data-section="customer-details"]');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleCallCustomer = () => {
    if (activeDelivery?.user_phone) {
      window.open(`tel:${activeDelivery.user_phone}`);
    }
  };

  const handleMessageCustomer = () => {
    const message = prompt(`Enter message for ${activeDelivery?.user_name}:`);
    if (message && activeDelivery?.user_phone) {
      // For mobile, this would open SMS app
      window.open(`sms:${activeDelivery.user_phone}?body=${encodeURIComponent(message)}`);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', paddingBottom: '80px' }}>
      <style>{`
        .active-delivery-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 16px;
        }
        
        @media (min-width: 768px) {
          .active-delivery-container {
            padding: 24px;
          }
        }
        
        .customer-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          margin-bottom: 16px;
        }
        
        .customer-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        
        .customer-title {
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }
        
        .customer-info {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 16px;
        }
        
        .info-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #666;
        }
        
        .tabs-container {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .tabs-header {
          display: flex;
          border-bottom: 1px solid #e5e7eb;
        }
        
        .tab {
          flex: 1;
          padding: 16px;
          text-align: center;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #666;
          transition: all 0.2s;
        }
        
        .tab.active {
          color: #ff6b35;
          border-bottom: 2px solid #ff6b35;
        }
        
        .tab-content {
          padding: 20px;
        }
        
        .order-details-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 16px;
        }
        
        .order-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;
          font-size: 14px;
        }
        
        .order-label {
          color: #666;
        }
        
        .order-value {
          font-weight: 600;
          color: #333;
        }
        
        .earnings-box {
          background: #f0fdf4;
          border: 1px solid #bbf7d0;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
        }
        
        .earnings-text {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 600;
          color: #16a34a;
        }
        
        .action-buttons {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }
        
        .btn {
          padding: 12px 16px;
          border: none;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          font-size: 14px;
        }
        
        .btn-primary {
          background: #ff6b35;
          color: white;
        }
        
        .btn-secondary {
          background: #f8f9fa;
          color: #666;
        }
        
        .btn-danger {
          background: #dc2626;
          color: white;
        }
        
        .location-info {
          padding: 16px;
          background: #f8f9fa;
          border-radius: 8px;
          margin-bottom: 16px;
        }
        
        .location-text {
          font-size: 14px;
          color: #666;
          line-height: 1.5;
        }
        
        .map-placeholder {
          height: 200px;
          background: #e5e7eb;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #6b7280;
          flex-direction: column;
          gap: 8px;
        }
      `}</style>
      
      <div className="active-delivery-container">
        {/* Header */}
        <div style={{ 
          background: 'white', 
          borderRadius: '12px', 
          padding: '24px', 
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#333', margin: '0 0 8px 0' }}>Active Delivery</h1>
            <p style={{ fontSize: '16px', color: '#666', margin: 0 }}>Request #{activeDelivery.request_id}</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button 
              onClick={handleNavigate}
              style={{ 
                padding: '10px 20px', 
                background: '#ff6b35', 
                border: 'none', 
                borderRadius: '8px', 
                color: 'white', 
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}>
              Navigate
            </button>
            <button 
              onClick={handleCancelDelivery}
              style={{ 
                padding: '10px 20px', 
                background: '#f8f9fa', 
                border: '1px solid #e5e7eb', 
                borderRadius: '8px', 
                color: '#666', 
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}>
              Cancel Delivery
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Left Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Delivery Progress */}
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '24px', 
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#333', margin: '0 0 20px 0' }}>Delivery Progress</h2>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: currentStep >= 1 ? '#ff6b35' : '#e5e7eb', 
                    color: currentStep >= 1 ? 'white' : '#6b7280',
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    marginBottom: '8px',
                    fontSize: '18px',
                    fontWeight: '600'
                  }}>
                    1
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '500', color: currentStep >= 1 ? '#ff6b35' : '#6b7280' }}>On the way</div>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: currentStep >= 2 ? '#ff6b35' : '#e5e7eb', 
                    color: currentStep >= 2 ? 'white' : '#6b7280',
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    marginBottom: '8px',
                    fontSize: '18px',
                    fontWeight: '600'
                  }}>
                    2
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '500', color: currentStep >= 2 ? '#ff6b35' : '#6b7280' }}>Arrived</div>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: currentStep >= 3 ? '#ff6b35' : '#e5e7eb', 
                    color: currentStep >= 3 ? 'white' : '#6b7280',
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    marginBottom: '8px',
                    fontSize: '18px',
                    fontWeight: '600'
                  }}>
                    3
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '500', color: currentStep >= 3 ? '#ff6b35' : '#6b7280' }}>Delivered</div>
                </div>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {currentStep === 1 && (
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button 
                      onClick={handleMarkAsArrived}
                      style={{ 
                        flex: 1, 
                        padding: '12px', 
                        background: '#ff6b35', 
                        border: 'none', 
                        borderRadius: '8px', 
                        color: 'white', 
                        fontSize: '14px',
                        fontWeight: '500',
                        cursor: 'pointer'
                      }}>
                      Mark as Arrived
                    </button>
                    <button 
                      onClick={handleViewDetails}
                      style={{ 
                        flex: 1, 
                        padding: '12px', 
                        background: '#f8f9fa', 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '8px', 
                        color: '#666', 
                        fontSize: '14px',
                        fontWeight: '500',
                        cursor: 'pointer'
                      }}>
                      View Details
                    </button>
                  </div>
                )}
                
                {currentStep === 2 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <textarea
                      placeholder="Add delivery notes (optional)"
                      value={deliveryNote}
                      onChange={(e) => setDeliveryNote(e.target.value)}
                      style={{ 
                        padding: '12px', 
                        border: '1px solid #e5e7eb', 
                        borderRadius: '8px', 
                        fontSize: '14px',
                        resize: 'vertical',
                        minHeight: '80px'
                      }}
                    />
                    <button 
                      onClick={handleMarkAsDelivered}
                      disabled={completing}
                      style={{ 
                        padding: '12px', 
                        background: '#16a34a', 
                        border: 'none', 
                        borderRadius: '8px', 
                        color: 'white', 
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: completing ? 'not-allowed' : 'pointer',
                        opacity: completing ? 0.7 : 1
                      }}>
                      {completing ? 'Completing...' : 'Mark as Delivered'}
                    </button>
                  </div>
                )}
                
                {currentStep === 3 && (
                  <div style={{ 
                    padding: '16px', 
                    background: '#f0fdf4', 
                    border: '1px solid #bbf7d0', 
                    borderRadius: '8px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#16a34a', marginBottom: '8px' }}>
                      ✓ Delivery Completed
                    </div>
                    <div style={{ fontSize: '14px', color: '#16a34a' }}>
                      Earnings have been added to your account
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Customer Details */}
            <div 
              data-section="customer-details"
              style={{ 
                background: 'white', 
                borderRadius: '12px', 
                padding: '24px', 
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
              }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#333', margin: '0 0 20px 0' }}>Customer Details</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: '#f8f9fa', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center' 
                  }}>
                    <User style={{ width: '24px', height: '24px', color: '#666' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>{activeDelivery.user_name}</div>
                    <div style={{ fontSize: '14px', color: '#666' }}>Customer</div>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: '#f8f9fa', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center' 
                  }}>
                    <Phone style={{ width: '24px', height: '24px', color: '#666' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>{activeDelivery.user_phone}</div>
                    <div style={{ fontSize: '14px', color: '#666' }}>Phone Number</div>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: '#f8f9fa', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <MapPin style={{ width: '24px', height: '24px', color: '#666' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '16px', fontWeight: '600', color: '#333', lineHeight: '1.4' }}>{activeDelivery.delivery_address}</div>
                    <div style={{ fontSize: '14px', color: '#666' }}>Delivery Address</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Order Details */}
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '24px', 
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#333', margin: '0 0 20px 0' }}>Order Details</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div style={{ 
                  padding: '16px', 
                  background: '#f8f9fa', 
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ fontSize: '12px', color: '#666', fontWeight: '500' }}>Fuel Type</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>{activeDelivery.fuel_type}</div>
                </div>
                
                <div style={{ 
                  padding: '16px', 
                  background: '#f8f9fa', 
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ fontSize: '12px', color: '#666', fontWeight: '500' }}>Quantity</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>{activeDelivery.quantity_liters} L</div>
                </div>
                
                <div style={{ 
                  padding: '16px', 
                  background: '#f8f9fa', 
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ fontSize: '12px', color: '#666', fontWeight: '500' }}>Priority</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>Level {activeDelivery.priority_level}</div>
                </div>
                
                <div style={{ 
                  padding: '16px', 
                  background: '#f8f9fa', 
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}>
                  <div style={{ fontSize: '12px', color: '#666', fontWeight: '500' }}>Time</div>
                  <div style={{ fontSize: '16px', fontWeight: '600', color: '#333' }}>{activeDelivery.created_at}</div>
                </div>
              </div>
              
              <div style={{ 
                background: '#f0fdf4', 
                border: '1px solid #bbf7d0', 
                borderRadius: '8px', 
                padding: '20px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ 
                    width: '48px', 
                    height: '48px', 
                    borderRadius: '50%', 
                    background: 'white', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center'
                  }}>
                    <DollarSign style={{ width: '24px', height: '24px', color: '#16a34a' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', color: '#16a34a', fontWeight: '500' }}>Estimated Earnings</div>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#16a34a' }}>₹{activeDelivery.estimated_earnings?.toFixed(2) || '0.00'}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Map */}
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '24px', 
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
              height: '400px'
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#333', margin: '0 0 20px 0' }}>Delivery Location</h2>
              <div style={{ 
                height: '300px', 
                background: '#e5e7eb', 
                borderRadius: '8px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: '#6b7280',
                flexDirection: 'column',
                gap: '12px'
              }}>
                <MapPin style={{ width: '48px', height: '48px' }} />
                <div style={{ fontSize: '16px' }}>Map View</div>
                <div style={{ fontSize: '14px' }}>Delivery location will be shown here</div>
              </div>
            </div>

            {/* Actions */}
            <div style={{ 
              background: 'white', 
              borderRadius: '12px', 
              padding: '24px', 
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#333', margin: '0 0 20px 0' }}>Quick Actions</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <button 
                  onClick={handleCallCustomer}
                  style={{ 
                    padding: '16px', 
                    background: '#ff6b35', 
                    border: 'none', 
                    borderRadius: '8px', 
                    color: 'white', 
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}>
                  <Phone style={{ width: '20px', height: '20px' }} />
                  Call Customer
                </button>
                
                <button 
                  onClick={handleMessageCustomer}
                  style={{ 
                    padding: '16px', 
                    background: '#f8f9fa', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '8px', 
                    color: '#666', 
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}>
                  <MessageSquare style={{ width: '20px', height: '20px' }} />
                  Message Customer
                </button>
                
                <button 
                  onClick={handleCancelDelivery}
                  style={{ 
                    padding: '16px', 
                    background: '#dc2626', 
                    border: 'none', 
                    borderRadius: '8px', 
                    color: 'white', 
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px'
                  }}>
                  <XCircle style={{ width: '20px', height: '20px' }} />
                  Cancel Delivery
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FuelDeliveryActive;
