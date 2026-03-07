import React from 'react';
import { Link } from 'react-router-dom';
import { User, Briefcase } from 'lucide-react';

const Landing = () => {
  return (
    <div className="landing-container">
      <h1 className="landing-title">Welcome to ExpertEase</h1>
      <p className="landing-subtitle">Choose how you want to use the platform</p>
      
      <div className="selection-cards">
        <Link to="/login" className="selection-card">
          <div className="card-icon-wrapper">
            <User size={40} color="white" strokeWidth={1.5} />
          </div>
          <h2 className="card-title">Get Service</h2>
          <p className="card-desc">Find doctors, book appointments, and get expert advice.</p>
        </Link>
        
        <Link to="/provide-service" className="selection-card">
          <div className="card-icon-wrapper">
            <Briefcase size={40} color="white" strokeWidth={1.5} />
          </div>
          <h2 className="card-title">Provide Service</h2>
          <p className="card-desc">Join as a professional and offer your expertise.</p>
        </Link>
      </div>
    </div>
  );
};

export default Landing;
