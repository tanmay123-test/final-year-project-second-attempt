import React from 'react';
import { X, Calendar, DollarSign, Check, X as XIcon } from 'lucide-react';
import '../styles/ProjectDetailsModal.css';
import axios from 'axios';

const ProjectDetailsModal = ({ project, proposals, milestones, onClose, onAction }) => {
  if (!project) return null;

  const handleAccept = async (proposalId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/proposals/accept', { proposal_id: proposalId }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      onAction(); // Refetch data in parent
    } catch (error) {
      console.error('Error accepting proposal:', error);
    }
  };

  const handleReject = async (proposalId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/freelance/proposals/reject', { proposal_id: proposalId }, {
        headers: { Authorization: `Bearer ${token}` },
      });
      onAction(); // Refetch data in parent
    } catch (error) {
      console.error('Error rejecting proposal:', error);
    }
  };

  return (
    <div className="project-details-modal-overlay">
      <div className="project-details-modal-content">
        <button onClick={onClose} className="close-modal-btn">
          <X size={24} />
        </button>

        <div className="modal-header">
          <h2>{project.title}</h2>
          <div className="project-meta">
            <span><DollarSign size={16} /> ${project.budget}</span>
            <span><Calendar size={16} /> {new Date(project.deadline).toLocaleDateString()}</span>
            <span className="project-tag">Project</span>
          </div>
          <p className="project-description">{project.description}</p>
        </div>

        <div className="proposals-section">
          <h3>Proposals ({proposals.length})</h3>
          <div className="proposals-list">
            {proposals.map(proposal => (
              <div key={proposal.id} className="proposal-card">
                <div className="proposal-info">
                  <h4>{proposal.worker_name}</h4>
                  <p className="proposal-bid">${proposal.bid_amount} - {proposal.estimated_days} days</p>
                  <p className="proposal-summary">{proposal.cover_letter}</p>
                </div>
                <div className="proposal-actions">
                  <button className="btn-accept" onClick={() => handleAccept(proposal.id)}><Check size={16} /> Accept</button>
                  <button className="btn-reject" onClick={() => handleReject(proposal.id)}><XIcon size={16} /> Reject</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="milestones-section">
          <h3>Milestones</h3>
          <div className="milestones-list">
            {milestones.map(milestone => (
              <div key={milestone.id} className="milestone-item">
                <p>{milestone.description}</p>
                <span className={`milestone-status ${milestone.status.toLowerCase().replace(' ', '-')}`}>
                  {milestone.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="payment-summary">
          <DollarSign size={20} />
          <span>Payment: ${project.paid_amount || 0} / ${project.budget} released</span>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailsModal;
