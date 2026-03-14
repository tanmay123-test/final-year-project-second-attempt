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
import DoctorRequests from './pages/DoctorRequests';
import DoctorProfile from './pages/DoctorProfile';
import DoctorProfileDetails from './pages/DoctorProfileDetails';
import DoctorSettings from './pages/DoctorSettings';
import DoctorAppointments from './pages/DoctorAppointments';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AICare from './pages/AiCare';
import Profile from './pages/Profile';
import VideoJoin from './pages/VideoJoin';

import UserLayout from './components/UserLayout';

<<<<<<< HEAD
=======
// Freelance Marketplace
import FreelanceHome from './services/freelance/pages/FreelanceHome';
import FreelancerDashboard from './services/freelance/pages/FreelancerDashboard';

// Finny Smart Transaction Tracker
import FinnyHomeScreen from './services/finny/pages/FinnyHomeScreen';
import QuickModePage from './services/finny/pages/QuickModePage';
import SummaryPage from './services/finny/pages/SummaryPage';
import AnalyticsPage from './services/finny/pages/AnalyticsPage';
import ChatModePage from './services/finny/pages/ChatModePage';
import ChatFinancialAssistantPage from './services/finny/pages/ChatFinancialAssistantPage';
import AnalyticsDashboardPage from './services/finny/pages/AnalyticsDashboardPage';

>>>>>>> 4eec942db43701c5f3b31ef6e6eee1f0c0988304
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
<<<<<<< HEAD
            <Route path="/profile" element={<Profile />} />
            <Route path="/appointments/join/:appointmentId" element={<VideoJoin />} />
            <Route path="/ai-care" element={<AICare />} />
=======
            <Route path="/profile" element={<div style={{padding: '2rem'}}><h2>Profile Page</h2><p>Coming Soon</p></div>} />
            
            {/* Finny Smart Transaction Tracker Routes */}
            <Route path="/finny" element={<ProtectedRoute><FinnyHomeScreen /></ProtectedRoute>} />
            <Route path="/finny/quick" element={<ProtectedRoute><QuickModePage /></ProtectedRoute>} />
            <Route path="/finny/summary" element={<ProtectedRoute><SummaryPage /></ProtectedRoute>} />
            <Route path="/finny/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
            <Route path="/finny/chat" element={<ProtectedRoute><ChatModePage /></ProtectedRoute>} />
>>>>>>> 4eec942db43701c5f3b31ef6e6eee1f0c0988304
          </Route>

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
            path="/doctor/requests" 
            element={
              <ProtectedWorkerRoute>
                <DoctorRequests />
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
          <Route 
            path="/doctor/profile/details" 
            element={
              <ProtectedWorkerRoute>
                <DoctorProfileDetails />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/doctor/settings" 
            element={
              <ProtectedWorkerRoute>
                <DoctorSettings />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/doctor/appointments" 
            element={
              <ProtectedWorkerRoute>
                <DoctorAppointments />
              </ProtectedWorkerRoute>
            } 
          />
          
          {/* Housekeeping */}
          <Route path="/worker/housekeeping/login" element={<WorkerLogin serviceType="housekeeping" />} />
          <Route path="/worker/housekeeping/signup" element={<WorkerSignup serviceType="housekeeping" />} />

          {/* Resource Management */}
          <Route path="/worker/resource/login" element={<WorkerLogin serviceType="resource" />} />
          <Route path="/worker/resource/signup" element={<WorkerSignup serviceType="resource" />} />

          {/* Car Services */}
          <Route path="/worker/car/login" element={<WorkerLogin serviceType="car" />} />
          <Route path="/worker/car/signup" element={<WorkerSignup serviceType="car" />} />

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
