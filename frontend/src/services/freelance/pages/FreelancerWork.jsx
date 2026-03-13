import React, { useState, useEffect } from 'react';
import { Briefcase, CheckCircle, Clock, AlertCircle, MessageSquare, Send, Upload, ChevronDown, ChevronUp } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const FreelancerWork = () => {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeContractId, setActiveContractId] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchActiveWork();
  }, []);

  const fetchActiveWork = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/freelance/active-work', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContracts(response.data.contracts);
      if (response.data.contracts.length > 0) {
        setActiveContractId(response.data.contracts[0].id);
      }
    } catch (error) {
      console.error('Error fetching active work:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (contractId) => {
    if (!message.trim()) return;
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/messages', {
        contract_id: contractId,
        message: message
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage('');
      fetchActiveWork(); // Reload messages
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleSubmitMilestone = async (milestoneId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/milestones/submit', {
        milestone_id: milestoneId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchActiveWork(); // Reload milestones
    } catch (error) {
      console.error('Error submitting milestone:', error);
    }
  };

  const activeContract = contracts.find(c => c.id === activeContractId);

  return (
    <div className="work-container">
      <div className="section-header">
        <h2>My Work</h2>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your active projects...</p>
        </div>
      ) : contracts.length === 0 ? (
        <div className="empty-state">
          <Briefcase size={48} color="#cbd5e1" />
          <p>You don't have any active projects yet.</p>
        </div>
      ) : (
        <div className="work-layout">
          {/* Contracts Sidebar */}
          <aside className="contracts-list">
            {contracts.map(contract => (
              <div 
                key={contract.id} 
                className={`contract-item-card ${activeContractId === contract.id ? 'active' : ''}`}
                onClick={() => setActiveContractId(contract.id)}
              >
                <div className="contract-info-compact">
                  <h4>{contract.project_title}</h4>
                  <span className="status-pill-small">{contract.status}</span>
                </div>
              </div>
            ))}
          </aside>

          {/* Active Contract Details */}
          <main className="contract-details-view">
            {activeContract && (
              <>
                <div className="contract-header-row">
                  <div className="header-left">
                    <h3>{activeContract.project_title}</h3>
                    <span className="status-badge active-badge">
                      <Clock size={14} />
                      {activeContract.status}
                    </span>
                  </div>
                  <button className="mark-complete-btn">Mark Project Complete</button>
                </div>

                <div className="details-section">
                  <label>Project Details</label>
                  <p>{activeContract.project_description}</p>
                </div>

                <div className="milestones-section">
                  <label>Milestones</label>
                  <div className="milestones-list-new">
                    {activeContract.milestones?.map(m => (
                      <div key={m.id} className="milestone-card-row">
                        <div className="m-info">
                          <span className="m-title">{m.title}</span>
                          <span className={`m-status-badge ${m.status.toLowerCase()}`}>
                            {m.status}
                          </span>
                        </div>
                        {m.status === 'PENDING' && (
                          <button 
                            className="submit-m-btn"
                            onClick={() => handleSubmitMilestone(m.id)}
                          >
                            Submit
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="upload-deliverables-section">
                  <label>Upload Deliverables</label>
                  <div className="upload-dropzone-new">
                    <Upload size={32} />
                    <p>Drag & drop files or click to upload</p>
                  </div>
                  <button className="submit-milestone-btn-purple">
                    <CheckCircle size={18} />
                    Submit Milestone
                  </button>
                </div>

                <div className="chat-section-new">
                  <label>Messages</label>
                  <div className="messages-list-new">
                    {activeContract.messages?.map(msg => (
                      <div key={msg.id} className={`message-row ${msg.sender_id === activeContract.freelancer_id ? 'sent' : 'received'}`}>
                        <div className="message-bubble">
                          <p>{msg.message}</p>
                          <span className="msg-time">
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="message-input-row-new">
                    <input 
                      type="text" 
                      placeholder="Type your message..." 
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(activeContract.id)}
                    />
                    <button className="send-msg-btn-purple" onClick={() => handleSendMessage(activeContract.id)}>
                      <Send size={18} />
                    </button>
                  </div>
                </div>
              </>
            )}
          </main>
        </div>
      )}
    </div>
  );
};

export default FreelancerWork;
