import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

const WorkerPortalProtectedRoute = ({ children }) => {
  const location = useLocation();
  const workerToken = localStorage.getItem('worker_token');

  if (!workerToken) {
    return <Navigate to="/worker/login" state={{ from: location }} replace />;
  }
  return children;
};

export default WorkerPortalProtectedRoute;

