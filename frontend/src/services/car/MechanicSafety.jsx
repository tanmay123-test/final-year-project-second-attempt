import React from 'react';
import { useNavigate } from 'react-router-dom';

const MechanicSafety = () => {
  const navigate = useNavigate();
  
  return (
    <div className="safety">
      <h1>Safety</h1>
      <p>Safety guidelines and protocols will appear here</p>
    </div>
  );
};

export default MechanicSafety;
