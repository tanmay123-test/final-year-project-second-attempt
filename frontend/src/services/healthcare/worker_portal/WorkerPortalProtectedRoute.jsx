import React from 'react'
import { Navigate } from 'react-router-dom'

const WorkerPortalProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('workerToken')
  console.log('WorkerPortalProtectedRoute checking token:', token)
  if (!token) {
    console.log('No workerToken found - redirecting to login')
    return <Navigate to="/worker/healthcare/login" replace />
  }
  return children
}

export default WorkerPortalProtectedRoute

