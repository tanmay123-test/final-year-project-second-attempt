import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import DoctorSearch from './pages/DoctorSearch';
import Booking from './pages/Booking';
import WorkerLogin from './pages/WorkerLogin';
import WorkerSignup from './pages/WorkerSignup';
import WorkerDashboard from './pages/WorkerDashboard';
import ServiceSelection from './pages/ServiceSelection';
import DoctorLogin from './pages/DoctorLogin';
import DoctorDashboard from './pages/DoctorDashboard';
import DoctorAvailability from './pages/DoctorAvailability';
import DoctorProfile from './pages/DoctorProfile';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Housekeeping Arrival Pages
import UserHome from '../../housekeeping/arrival/frontend/pages/UserHome';
import AIChat from '../../housekeeping/arrival/frontend/pages/AIChat';
import UserBookings from '../../housekeeping/arrival/frontend/pages/UserBookings';
import UserProfile from '../../housekeeping/arrival/frontend/pages/UserProfile';
import BookingFlow from '../../housekeeping/arrival/frontend/pages/BookingFlow';
import ProviderDashboard from '../../housekeeping/provider/frontend/pages/ProviderDashboard';
import ProviderSchedule from '../../housekeeping/provider/frontend/pages/ProviderSchedule';
import ProviderAvailability from '../../housekeeping/provider/frontend/pages/ProviderAvailability';
import ProviderEarnings from '../../housekeeping/provider/frontend/pages/ProviderEarnings';
import ProviderProfile from '../../housekeeping/provider/frontend/pages/ProviderProfile';
import ProviderPricing from '../../housekeeping/provider/frontend/pages/ProviderPricing';

import UserLayout from './components/UserLayout';

const ProtectedWorkerRoute = ({ children }) => {
  const { worker, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div>Loading...</div>;
  if (!worker) return <Navigate to="/worker/login" state={{ from: location }} replace />;
  return children;
};

const App = () => {
  return (
    <div className="app">
      <Navbar />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<Landing />} />
          
          {/* User Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          
          {/* Authenticated User Layout */}
          <Route element={<ProtectedRoute><UserLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/doctors" element={<DoctorSearch />} />
            <Route path="/book/:doctorId" element={<Booking />} />
            <Route path="/profile" element={<div style={{padding: '2rem'}}><h2>Profile Page</h2><p>Coming Soon</p></div>} />
          </Route>

          {/* Housekeeping Arrival Routes */}
          <Route path="/housekeeping/home" element={<ProtectedRoute><UserHome /></ProtectedRoute>} />
          <Route path="/housekeeping/ai-chat" element={<ProtectedRoute><AIChat /></ProtectedRoute>} />
          <Route path="/housekeeping/bookings" element={<ProtectedRoute><UserBookings /></ProtectedRoute>} />
          <Route path="/housekeeping/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
          <Route path="/housekeeping/explore" element={<ProtectedRoute><UserHome /></ProtectedRoute>} />
          <Route path="/housekeeping/booking/create" element={<ProtectedRoute><BookingFlow /></ProtectedRoute>} />

          {/* Service Selection (No Bottom Nav) */}
          <Route path="/services" element={<ProtectedRoute><ServiceSelection /></ProtectedRoute>} />

          {/* Worker Routes - Service Specific */}
          <Route path="/provide-service" element={<ServiceSelection mode="worker" />} />
          
          {/* Healthcare */}
          <Route path="/worker/healthcare/login" element={<DoctorLogin />} />
          <Route path="/worker/healthcare/signup" element={<WorkerSignup serviceType="healthcare" />} />
          <Route 
            path="/doctor/dashboard" 
            element={
              <ProtectedWorkerRoute>
                <DoctorDashboard />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/doctor/availability" 
            element={
              <ProtectedWorkerRoute>
                <DoctorAvailability />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/doctor/profile" 
            element={
              <ProtectedWorkerRoute>
                <DoctorProfile />
              </ProtectedWorkerRoute>
            } 
          />
          
          {/* Housekeeping */}
          <Route path="/worker/housekeeping/login" element={<WorkerLogin serviceType="housekeeping" />} />
          <Route path="/worker/housekeeping/signup" element={<WorkerSignup serviceType="housekeeping" />} />
          <Route 
            path="/worker/housekeeping/dashboard" 
            element={
              <ProtectedWorkerRoute>
                <ProviderDashboard />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/housekeeping/schedule" 
            element={
              <ProtectedWorkerRoute>
                <ProviderSchedule />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/housekeeping/availability" 
            element={
              <ProtectedWorkerRoute>
                <ProviderAvailability />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/housekeeping/earnings" 
            element={
              <ProtectedWorkerRoute>
                <ProviderEarnings />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/housekeeping/profile" 
            element={
              <ProtectedWorkerRoute>
                <ProviderProfile />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/housekeeping/pricing" 
            element={
              <ProtectedWorkerRoute>
                <ProviderPricing />
              </ProtectedWorkerRoute>
            } 
          />

          {/* Resource Management */}
          <Route path="/worker/resource/login" element={<WorkerLogin serviceType="resource" />} />
          <Route path="/worker/resource/signup" element={<WorkerSignup serviceType="resource" />} />

          {/* Car Services */}
          <Route path="/worker/car/login" element={<WorkerLogin serviceType="car" />} />
          <Route path="/worker/car/signup" element={<WorkerSignup serviceType="car" />} />

          {/* Money Management */}
          <Route path="/worker/money/login" element={<WorkerLogin serviceType="money" />} />
          <Route path="/worker/money/signup" element={<WorkerSignup serviceType="money" />} />

          {/* Legacy/Fallback Routes */}
          <Route path="/worker/login" element={<WorkerLogin serviceType="healthcare" />} />
          <Route path="/worker/signup" element={<WorkerSignup serviceType="healthcare" />} />
          
          <Route 
            path="/worker/dashboard" 
            element={
              <ProtectedWorkerRoute>
                <WorkerDashboard />
              </ProtectedWorkerRoute>
            } 
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;
