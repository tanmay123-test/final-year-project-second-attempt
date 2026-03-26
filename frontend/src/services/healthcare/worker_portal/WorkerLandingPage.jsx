import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Stethoscope } from 'lucide-react';
import './WorkerPortal.css';

const WorkerLandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="wp-landing">
      <Stethoscope size={56} color="#ffffff" />
      <h1>ExpertEase</h1>
      <div className="wp-landing-sub">Worker Portal</div>
      <div className="wp-landing-tag">
        Manage your consultations, availability
        <br />
        and grow your practice
      </div>

      <div className="wp-landing-actions">
        <button className="wp-white-btn" onClick={() => navigate('/worker/signup')}>
          Sign Up as Healthcare Worker
        </button>
        <button className="wp-outline-btn" onClick={() => navigate('/worker/login')}>
          Log In to Dashboard
        </button>
      </div>

      <div className="wp-landing-link">
        Are you a patient?{' '}
        <button onClick={() => navigate('/')}>Go to App -&gt;</button>
      </div>
    </div>
  );
};

export default WorkerLandingPage;

