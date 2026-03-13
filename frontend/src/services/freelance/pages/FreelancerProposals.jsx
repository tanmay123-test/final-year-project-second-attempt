import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, FileText, ChevronRight } from 'lucide-react';
import axios from 'axios';
import '../styles/FreelancerDashboard.css';

const FreelancerProposals = () => {
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/api/freelance/my-proposals', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProposals(response.data.proposals);
    } catch (error) {
      console.error('Error fetching proposals:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'ACCEPTED': return 'status-badge accepted-badge';
      case 'REJECTED': return 'status-badge rejected-badge';
      case 'PENDING': return 'status-badge pending-badge';
      default: return 'status-badge';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ACCEPTED': return <CheckCircle size={14} />;
      case 'REJECTED': return <XCircle size={14} />;
      case 'PENDING': return <AlertCircle size={14} />;
      default: return null;
    }
  };

  return (
    <div className="proposals-container">
      <div className="section-header">
        <h2>My Proposals</h2>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your proposals...</p>
        </div>
      ) : proposals.length === 0 ? (
        <div className="empty-state">
          <FileText size={48} color="#cbd5e1" />
          <p>You haven't submitted any proposals yet.</p>
        </div>
      ) : (
        <div className="proposals-list-new">
          {proposals.map(proposal => (
            <div key={proposal.id} className="proposal-card-row">
              <div className="proposal-main-info">
                <h3>{proposal.project_title}</h3>
                <div className="proposal-meta">
                  <span className="price">${proposal.proposed_price}</span>
                  <span className="divider">•</span>
                  <span className="time">{proposal.delivery_time}</span>
                </div>
              </div>
              <div className="proposal-status-action">
                <span className={getStatusBadgeClass(proposal.status)}>
                  {getStatusIcon(proposal.status)}
                  {proposal.status}
                </span>
                <button className="view-details-btn">
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FreelancerProposals;
