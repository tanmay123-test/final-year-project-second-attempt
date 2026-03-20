import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, CreditCard, DollarSign, Calendar, Filter,
  Download, Search, TrendingUp, TrendingDown, CheckCircle,
  Clock, AlertCircle, FileText, Eye
} from 'lucide-react';

const MechanicPayments = () => {
  const navigate = useNavigate();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterMonth, setFilterMonth] = useState('all');
  const [selectedPayment, setSelectedPayment] = useState(null);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      const storedData = localStorage.getItem('workerData');
      const token = localStorage.getItem('workerToken');
      
      if (storedData && token) {
        const workerData = JSON.parse(storedData);
        const workerId = workerData.id || workerData.workerId || 7;
        
        try {
          const response = await fetch(`http://127.0.0.1:5000/api/car/service/worker/${workerId}/payments`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            setPayments(data.payments || data || []);
          } else {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
          }
        } catch (error) {
          console.log('🔄 Payments API not available, using sample data:', error.message);
          // Use realistic sample payment data
          const samplePayments = [
            {
              id: 1,
              jobId: 'JOB-2024-001',
              customerName: 'Rahul Sharma',
              serviceName: 'Engine Repair & Diagnostic',
              amount: 2500,
              status: 'completed',
              paymentStatus: 'paid',
              date: '2024-03-10',
              time: '14:30',
              paymentMethod: 'UPI',
              transactionId: 'TXN123456789',
              commission: 250,
              netEarning: 2250,
              customerRating: 5,
              customerFeedback: 'Excellent service, very professional!'
            },
            {
              id: 2,
              jobId: 'JOB-2024-002',
              customerName: 'Priya Patel',
              serviceName: 'Brake Service & Pad Replacement',
              amount: 1800,
              status: 'completed',
              paymentStatus: 'paid',
              date: '2024-03-08',
              time: '11:15',
              paymentMethod: 'Credit Card',
              transactionId: 'TXN123456790',
              commission: 180,
              netEarning: 1620,
              customerRating: 4,
              customerFeedback: 'Good work, reasonable pricing'
            },
            {
              id: 3,
              jobId: 'JOB-2024-003',
              customerName: 'Amit Kumar',
              serviceName: 'Complete Oil Change Service',
              amount: 800,
              status: 'completed',
              paymentStatus: 'pending',
              date: '2024-03-06',
              time: '09:45',
              paymentMethod: 'Cash',
              transactionId: null,
              commission: 80,
              netEarning: 720,
              customerRating: null,
              customerFeedback: null
            },
            {
              id: 4,
              jobId: 'JOB-2024-004',
              customerName: 'Sneha Reddy',
              serviceName: 'Tire Service & Alignment',
              amount: 2200,
              status: 'completed',
              paymentStatus: 'paid',
              date: '2024-03-03',
              time: '16:20',
              paymentMethod: 'UPI',
              transactionId: 'TXN123456791',
              commission: 220,
              netEarning: 1980,
              customerRating: 5,
              customerFeedback: 'Very satisfied with the service'
            },
            {
              id: 5,
              jobId: 'JOB-2024-005',
              customerName: 'Vikram Singh',
              serviceName: 'AC Repair & Recharge',
              amount: 1500,
              status: 'cancelled',
              paymentStatus: 'refunded',
              date: '2024-03-01',
              time: '13:00',
              paymentMethod: 'UPI',
              transactionId: 'TXN123456792',
              commission: 0,
              netEarning: 0,
              customerRating: null,
              customerFeedback: 'Job cancelled by customer'
            },
            {
              id: 6,
              jobId: 'JOB-2024-006',
              customerName: 'Anjali Nair',
              serviceName: 'Battery Replacement & Check',
              amount: 1200,
              status: 'completed',
              paymentStatus: 'paid',
              date: '2024-02-28',
              time: '10:30',
              paymentMethod: 'Credit Card',
              transactionId: 'TXN123456793',
              commission: 120,
              netEarning: 1080,
              customerRating: 4,
              customerFeedback: 'Prompt service, good pricing'
            },
            {
              id: 7,
              jobId: 'JOB-2024-007',
              customerName: 'Rohit Verma',
              serviceName: 'General Vehicle Inspection',
              amount: 600,
              status: 'completed',
              paymentStatus: 'paid',
              date: '2024-02-25',
              time: '15:45',
              paymentMethod: 'Cash',
              transactionId: null,
              commission: 60,
              netEarning: 540,
              customerRating: 5,
              customerFeedback: 'Thorough inspection, detailed report'
            },
            {
              id: 8,
              jobId: 'JOB-2024-008',
              customerName: 'Kavita Joshi',
              serviceName: 'Transmission Check & Service',
              amount: 3000,
              status: 'in_progress',
              paymentStatus: 'pending',
              date: '2024-02-22',
              time: '11:00',
              paymentMethod: null,
              transactionId: null,
              commission: 0,
              netEarning: 0,
              customerRating: null,
              customerFeedback: null
            }
          ];
          setPayments(samplePayments);
        }
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading payments:', error);
      setLoading(false);
    }
  };

  const filteredPayments = payments.filter(payment => {
    const matchesSearch = payment.customerName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         payment.jobId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         payment.serviceName?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || payment.paymentStatus === filterStatus;
    
    const matchesMonth = filterMonth === 'all' || 
                       (new Date(payment.date).toLocaleDateString('en-US', { month: 'long' }) === filterMonth);
    
    return matchesSearch && matchesStatus && matchesMonth;
  });

  const totalEarnings = payments
    .filter(p => p.paymentStatus === 'paid')
    .reduce((sum, p) => sum + p.netEarning, 0);

  const pendingAmount = payments
    .filter(p => p.paymentStatus === 'pending')
    .reduce((sum, p) => sum + p.amount, 0);

  const thisMonthEarnings = payments
    .filter(p => {
      const paymentDate = new Date(p.date);
      const thisMonth = new Date();
      return p.paymentStatus === 'paid' &&
             paymentDate.getMonth() === thisMonth.getMonth() && 
             paymentDate.getFullYear() === thisMonth.getFullYear();
    })
    .reduce((sum, p) => sum + p.netEarning, 0);

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return '#10B981';
      case 'pending': return '#F59E0B';
      case 'refunded': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'paid': return <CheckCircle size={16} />;
      case 'pending': return <Clock size={16} />;
      case 'refunded': return <AlertCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const downloadStatement = () => {
    // Generate CSV or PDF statement
    alert('Downloading payment statement...');
  };

  if (loading) {
    return (
      <div className="payments-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading payment history...</p>
        </div>
        <style>{`
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: #f8fafc;
          }
          .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #8B5CF6;
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
    <div className="payments-page">
      {/* Header */}
      <div className="payments-header">
        <div className="header-actions">
          <button className="back-button" onClick={() => navigate('/worker/car/mechanic/profile')}>
            <ArrowLeft size={20} />
            <span>Back to Profile</span>
          </button>
          <button className="download-button" onClick={downloadStatement}>
            <Download size={18} />
            <span>Download Statement</span>
          </button>
        </div>
        <h1>Payment History</h1>
      </div>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card total">
          <div className="card-icon">
            <DollarSign size={24} />
          </div>
          <div className="card-content">
            <div className="card-value">₹{totalEarnings.toLocaleString()}</div>
            <div className="card-label">Total Earnings</div>
          </div>
        </div>
        
        <div className="summary-card this-month">
          <div className="card-icon">
            <TrendingUp size={24} />
          </div>
          <div className="card-content">
            <div className="card-value">₹{thisMonthEarnings.toLocaleString()}</div>
            <div className="card-label">This Month</div>
          </div>
        </div>
        
        <div className="summary-card pending">
          <div className="card-icon">
            <Clock size={24} />
          </div>
          <div className="card-content">
            <div className="card-value">₹{pendingAmount.toLocaleString()}</div>
            <div className="card-label">Pending Amount</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search by customer, job ID, or service..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-controls">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="paid">Paid</option>
            <option value="pending">Pending</option>
            <option value="refunded">Refunded</option>
          </select>
          
          <select
            value={filterMonth}
            onChange={(e) => setFilterMonth(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Months</option>
            <option value="March">March 2024</option>
            <option value="February">February 2024</option>
            <option value="January">January 2024</option>
          </select>
        </div>
      </div>

      {/* Payments List */}
      <div className="payments-list">
        {filteredPayments.length === 0 ? (
          <div className="empty-state">
            <CreditCard size={48} className="empty-icon" />
            <h3>No payments found</h3>
            <p>Try adjusting your filters or search terms</p>
          </div>
        ) : (
          filteredPayments.map((payment) => (
            <div key={payment.id} className="payment-item">
              <div className="payment-header">
                <div className="job-info">
                  <span className="job-id">{payment.jobId}</span>
                  <span className="customer-name">{payment.customerName}</span>
                </div>
                <div className="payment-status">
                  <div 
                    className="status-badge" 
                    style={{ 
                      backgroundColor: getStatusColor(payment.paymentStatus),
                      color: 'white'
                    }}
                  >
                    {getStatusIcon(payment.paymentStatus)}
                    <span>{payment.paymentStatus.replace('_', ' ').toUpperCase()}</span>
                  </div>
                </div>
              </div>
              
              <div className="payment-details">
                <div className="service-info">
                  <span className="service-name">{payment.serviceName}</span>
                  <div className="date-time">
                    <Calendar size={14} />
                    <span>{new Date(payment.date).toLocaleDateString()} at {payment.time}</span>
                  </div>
                </div>
                
                <div className="amount-info">
                  <div className="amount-breakdown">
                    <div className="amount-row">
                      <span className="label">Total Amount:</span>
                      <span className="amount">₹{payment.amount.toLocaleString()}</span>
                    </div>
                    <div className="amount-row">
                      <span className="label">Commission (10%):</span>
                      <span className="commission">-₹{payment.commission.toLocaleString()}</span>
                    </div>
                    <div className="amount-row net">
                      <span className="label">Net Earning:</span>
                      <span className="net-amount">₹{payment.netEarning.toLocaleString()}</span>
                    </div>
                  </div>
                  
                  {payment.paymentMethod && (
                    <div className="payment-method">
                      <span className="method-label">Paid via:</span>
                      <span className="method-value">{payment.paymentMethod}</span>
                    </div>
                  )}
                </div>
              </div>
              
              {(payment.customerRating || payment.customerFeedback) && (
                <div className="customer-feedback">
                  <div className="rating-section">
                    <span className="rating-label">Customer Rating:</span>
                    <div className="rating-display">
                      <span className="rating-stars">{'⭐'.repeat(payment.customerRating || 0)}</span>
                      <span className="rating-number">({payment.customerRating || 0}/5)</span>
                    </div>
                  </div>
                  {payment.customerFeedback && (
                    <div className="feedback-section">
                      <span className="feedback-label">Feedback:</span>
                      <span className="feedback-text">"{payment.customerFeedback}"</span>
                    </div>
                  )}
                </div>
              )}
              
              <div className="payment-actions">
                <button 
                  className="view-details-btn"
                  onClick={() => setSelectedPayment(payment)}
                >
                  <Eye size={16} />
                  <span>View Details</span>
                </button>
                
                {payment.transactionId && (
                  <button className="receipt-btn">
                    <FileText size={16} />
                    <span>Receipt</span>
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Payment Details Modal */}
      {selectedPayment && (
        <div className="modal-overlay" onClick={() => setSelectedPayment(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Payment Details</h3>
              <button className="close-btn" onClick={() => setSelectedPayment(null)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="detail-row">
                <span className="detail-label">Job ID:</span>
                <span className="detail-value">{selectedPayment.jobId}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Customer:</span>
                <span className="detail-value">{selectedPayment.customerName}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Service:</span>
                <span className="detail-value">{selectedPayment.serviceName}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Date & Time:</span>
                <span className="detail-value">
                  {new Date(selectedPayment.date).toLocaleDateString()} at {selectedPayment.time}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Status:</span>
                <span 
                  className="detail-value status-badge"
                  style={{ backgroundColor: getStatusColor(selectedPayment.paymentStatus) }}
                >
                  {selectedPayment.paymentStatus.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Total Amount:</span>
                <span className="detail-value amount">₹{selectedPayment.amount.toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Commission:</span>
                <span className="detail-value commission">-₹{selectedPayment.commission.toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Net Earning:</span>
                <span className="detail-value net-earning">₹{selectedPayment.netEarning.toLocaleString()}</span>
              </div>
              {selectedPayment.paymentMethod && (
                <div className="detail-row">
                  <span className="detail-label">Payment Method:</span>
                  <span className="detail-value">{selectedPayment.paymentMethod}</span>
                </div>
              )}
              {selectedPayment.transactionId && (
                <div className="detail-row">
                  <span className="detail-label">Transaction ID:</span>
                  <span className="detail-value">{selectedPayment.transactionId}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        .payments-page {
          background-color: #f8fafc;
          min-height: 100vh;
          font-family: 'Inter', sans-serif;
        }

        .payments-header {
          background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
          padding: 1.5rem;
          color: white;
        }

        .header-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .back-button, .download-button {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .back-button:hover, .download-button:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .payments-header h1 {
          margin: 0;
          font-size: 1.5rem;
          font-weight: 700;
        }

        .summary-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
          padding: 1.5rem;
        }

        .summary-card {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .summary-card.total {
          border-left: 4px solid #10B981;
        }

        .summary-card.this-month {
          border-left: 4px solid #8B5CF6;
        }

        .summary-card.pending {
          border-left: 4px solid #F59E0B;
        }

        .card-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #F3F4F6;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .summary-card.total .card-icon {
          color: #10B981;
        }

        .summary-card.this-month .card-icon {
          color: #8B5CF6;
        }

        .summary-card.pending .card-icon {
          color: #F59E0B;
        }

        .card-content {
          flex: 1;
        }

        .card-value {
          font-size: 1.5rem;
          font-weight: 800;
          color: #1F2937;
          margin-bottom: 0.25rem;
        }

        .card-label {
          font-size: 0.9rem;
          color: #6B7280;
          font-weight: 600;
        }

        .filters-section {
          background: white;
          padding: 1.5rem;
          margin: 0 1.5rem 1.5rem;
          border-radius: 16px;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
          display: flex;
          gap: 1rem;
          align-items: center;
          flex-wrap: wrap;
        }

        .search-box {
          flex: 1;
          min-width: 300px;
          position: relative;
        }

        .search-icon {
          position: absolute;
          left: 1rem;
          top: 50%;
          transform: translateY(-50%);
          color: #6B7280;
        }

        .search-input {
          width: 100%;
          padding: 0.75rem 1rem 0.75rem 3rem;
          border: 1px solid #D1D5DB;
          border-radius: 8px;
          font-size: 1rem;
        }

        .search-input:focus {
          outline: none;
          border-color: #8B5CF6;
          box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }

        .filter-controls {
          display: flex;
          gap: 1rem;
        }

        .filter-select {
          padding: 0.75rem 1rem;
          border: 1px solid #D1D5DB;
          border-radius: 8px;
          font-size: 1rem;
          background: white;
        }

        .payments-list {
          padding: 0 1.5rem 2rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .empty-state {
          text-align: center;
          padding: 3rem;
          color: #6B7280;
        }

        .empty-icon {
          margin-bottom: 1rem;
          color: #D1D5DB;
        }

        .payment-item {
          background: white;
          border-radius: 16px;
          padding: 1.5rem;
          box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .payment-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }

        .job-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .job-id {
          font-size: 0.9rem;
          color: #6B7280;
          font-weight: 600;
        }

        .customer-name {
          font-size: 1.1rem;
          font-weight: 700;
          color: #1F2937;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .payment-details {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.5rem;
          margin-bottom: 1rem;
        }

        .service-info {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .service-name {
          font-size: 1rem;
          font-weight: 600;
          color: #1F2937;
        }

        .date-time {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #6B7280;
          font-size: 0.9rem;
        }

        .amount-info {
          text-align: right;
        }

        .amount-breakdown {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .amount-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .amount-row.net {
          border-top: 1px solid #E5E7EB;
          padding-top: 0.25rem;
          margin-top: 0.25rem;
        }

        .label {
          color: #6B7280;
          font-size: 0.9rem;
        }

        .amount {
          font-weight: 600;
          color: #1F2937;
        }

        .commission {
          color: #EF4444;
          font-weight: 600;
        }

        .net-amount {
          font-weight: 700;
          color: #10B981;
          font-size: 1.1rem;
        }

        .payment-method {
          margin-top: 0.5rem;
          font-size: 0.8rem;
          color: #6B7280;
        }

        .method-label {
          margin-right: 0.5rem;
        }

        .method-value {
          font-weight: 600;
        }

        .customer-feedback {
          background: #F9FAFB;
          border-radius: 8px;
          padding: 1rem;
          margin-bottom: 1rem;
        }

        .rating-section, .feedback-section {
          margin-bottom: 0.75rem;
        }

        .rating-label, .feedback-label {
          font-size: 0.8rem;
          color: #6B7280;
          font-weight: 600;
          display: block;
          margin-bottom: 0.25rem;
        }

        .rating-display {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .rating-stars {
          font-size: 1rem;
        }

        .rating-number {
          color: #6B7280;
          font-size: 0.9rem;
        }

        .feedback-text {
          color: #4B5563;
          font-style: italic;
        }

        .payment-actions {
          display: flex;
          gap: 0.75rem;
        }

        .view-details-btn, .receipt-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .view-details-btn {
          background: #8B5CF6;
          color: white;
          border: none;
        }

        .view-details-btn:hover {
          background: #7C3AED;
        }

        .receipt-btn {
          background: #F3F4F6;
          color: #4B5563;
          border: 1px solid #D1D5DB;
        }

        .receipt-btn:hover {
          background: #E5E7EB;
        }

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
          padding: 0;
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid #E5E7EB;
        }

        .modal-header h3 {
          margin: 0;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1F2937;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 1.5rem;
          color: #6B7280;
          cursor: pointer;
          padding: 0.25rem;
        }

        .modal-body {
          padding: 1.5rem;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 0;
          border-bottom: 1px solid #F3F4F6;
        }

        .detail-row:last-child {
          border-bottom: none;
        }

        .detail-label {
          font-size: 0.9rem;
          color: #6B7280;
          font-weight: 600;
        }

        .detail-value {
          font-size: 0.9rem;
          color: #1F2937;
          font-weight: 500;
        }

        .detail-value.amount {
          font-weight: 700;
          color: #1F2937;
        }

        .detail-value.commission {
          color: #EF4444;
        }

        .detail-value.net-earning {
          color: #10B981;
          font-weight: 700;
        }

        .detail-value.status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          color: white;
          font-size: 0.8rem;
          font-weight: 600;
        }

        @media (max-width: 768px) {
          .payment-details {
            grid-template-columns: 1fr;
          }
          
          .filters-section {
            flex-direction: column;
            align-items: stretch;
          }
          
          .filter-controls {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default MechanicPayments;
