import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import DoctorSearch from './services/healthcare/DoctorSearch';
import Booking from './pages/Booking';
import WorkerLogin from './shared/WorkerLogin';
import WorkerSignup from './shared/WorkerSignup';
import WorkerDashboard from './pages/WorkerDashboard';
import ServiceSelection from './shared/ServiceSelection';
import DoctorLogin from './pages/DoctorLogin';
import DoctorDashboard from './services/healthcare/DoctorDashboard';
import DoctorAvailability from './pages/DoctorAvailability';
import DoctorProfile from './services/healthcare/DoctorProfile';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Housekeeping Arrival Pages
import UserHome from './services/housekeeping/arrival/UserHome';
import AIChat from './services/housekeeping/arrival/AIChat';
import UserBookings from './services/housekeeping/arrival/UserBookings';
import UserProfile from './services/housekeeping/arrival/UserProfile';
import BookingFlow from './services/housekeeping/arrival/BookingFlow';
import ProviderDashboard from './services/housekeeping/provider/ProviderDashboard';
import ProviderSchedule from './services/housekeeping/provider/ProviderSchedule';
import ProviderAvailability from './services/housekeeping/provider/ProviderAvailability';
import ProviderEarnings from './services/housekeeping/provider/ProviderEarnings';
import ProviderProfile from './services/housekeeping/provider/ProviderProfile';
import ProviderPricing from './services/housekeeping/provider/ProviderPricing';

import UserLayout from './components/UserLayout';

// Freelance Marketplace
import FreelanceHome from './services/freelance/pages/FreelanceHome';
import FreelancerDashboard from './services/freelance/pages/FreelancerDashboard';

// Car Services Worker Auth
import WorkerServiceSelection from './services/car/WorkerServiceSelection';
import MechanicAuth from './services/car/MechanicAuth';
import FuelDeliveryAuth from './services/car/FuelDeliveryAuth';
import TowTruckAuth from './services/car/TowTruckAuth';
import AutomobileExpertAuth from './services/car/AutomobileExpertAuth';

// Car Services Dashboards
import CarServiceHomepage from './services/car/CarServiceHomepage';
import AutomobileExpertHomepage from './services/car/AutomobileExpertHomepage';
import MechanicJobs from './services/car/MechanicJobs';
import MechanicActiveJobs from './services/car/MechanicActiveJobs';
import MechanicPerformance from './services/car/MechanicPerformance';
import MechanicSlots from './services/car/MechanicSlots';
import MechanicProfile from './services/car/MechanicProfile';
import MechanicDetails from './services/car/MechanicDetails';
import MechanicPayments from './services/car/MechanicPayments';
import MechanicAnalytics from './services/car/MechanicAnalytics';
import MechanicSettings from './services/car/MechanicSettings';
import MechanicSupport from './services/car/MechanicSupport';

// Fuel Delivery Components
import FuelDeliveryLayout from './services/car/FuelDeliveryLayout';
import FuelDeliveryHomepage from './services/car/FuelDeliveryHomepage';
import FuelDeliveryRequests from './services/car/FuelDeliveryRequests';
import FuelDeliveryActive from './services/car/FuelDeliveryActive';
import FuelDeliveryHistory from './services/car/FuelDeliveryHistory';
import FuelDeliveryPerformance from './services/car/FuelDeliveryPerformance';
import FuelDeliveryProfile from './services/car/FuelDeliveryProfile';

// Tow Truck Components
import TowTruckHomepage from './services/car/TowTruckHomepage';
import TowTruckDetails from './services/car/TowTruckDetails';

const ProtectedWorkerRoute = ({ children }) => {
  const [worker, setWorker] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // Check if worker is logged in via localStorage (support multiple worker types)
    let token = null;
    let workerData = null;
    
    // Check for different worker types
    if (location.pathname.startsWith('/worker/car/automobile-expert')) {
      token = localStorage.getItem('automobileExpertToken');
      workerData = localStorage.getItem('automobileExpertData');
    } else {
      token = localStorage.getItem('workerToken');
      workerData = localStorage.getItem('workerData');
    }
    
    // Debug logging
    console.log('ProtectedWorkerRoute - Path:', location.pathname);
    console.log('ProtectedWorkerRoute - Token exists:', !!token);
    console.log('ProtectedWorkerRoute - WorkerData exists:', !!workerData);
    
    if (token && workerData) {
      try {
        // Check if workerData is valid JSON before parsing
        if (workerData && workerData !== 'undefined' && workerData !== 'null') {
          const parsedData = JSON.parse(workerData);
          if (parsedData && typeof parsedData === 'object') {
            console.log('ProtectedWorkerRoute - Setting worker data:', parsedData);
            setWorker(parsedData);
          } else {
            console.error('Invalid workerData object in localStorage');
            // Clear invalid data
            if (location.pathname.startsWith('/worker/car/automobile-expert')) {
              localStorage.removeItem('automobileExpertToken');
              localStorage.removeItem('automobileExpertData');
            } else {
              localStorage.removeItem('workerToken');
              localStorage.removeItem('workerData');
            }
          }
        } else {
          console.error('Invalid workerData in localStorage');
          // Clear invalid data
          if (location.pathname.startsWith('/worker/car/automobile-expert')) {
            localStorage.removeItem('automobileExpertToken');
            localStorage.removeItem('automobileExpertData');
          } else {
            localStorage.removeItem('workerToken');
            localStorage.removeItem('workerData');
          }
        }
      } catch (error) {
        console.error('Error parsing worker data:', error);
        // Clear corrupted data
        if (location.pathname.startsWith('/worker/car/automobile-expert')) {
          localStorage.removeItem('automobileExpertToken');
          localStorage.removeItem('automobileExpertData');
        } else {
          localStorage.removeItem('workerToken');
          localStorage.removeItem('workerData');
        }
      }
    } else {
      console.log('ProtectedWorkerRoute - No authentication data found');
    }
    setLoading(false);
  }, [location.pathname]);

  if (loading) return <div>Loading...</div>;
  if (!worker) {
    // Check if current path is a fuel delivery path and redirect accordingly
    if (location.pathname.startsWith('/worker/car/fuel-delivery')) {
      return <Navigate to="/worker/car/fuel-delivery/login" state={{ from: location }} replace />;
    }
    // Check if current path is a tow truck path and redirect accordingly
    if (location.pathname.startsWith('/worker/car/tow-truck')) {
      return <Navigate to="/worker/car/tow-truck/login" state={{ from: location }} replace />;
    }
    // Check if current path is an automobile expert path and redirect accordingly
    if (location.pathname.startsWith('/worker/car/automobile-expert')) {
      return <Navigate to="/worker/car/automobile-expert/login" state={{ from: location }} replace />;
    }
    return <Navigate to="/worker/login" state={{ from: location }} replace />;
  }
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
          
          {/* Freelance Marketplace Routes */}
          <Route path="/freelance/home" element={<ProtectedRoute><FreelanceHome /></ProtectedRoute>} />

          {/* Worker Routes - Service Specific */}
          <Route path="/provide-service" element={<ServiceSelection mode="worker" />} />
          
          {/* Healthcare */}
          <Route path="/worker/healthcare/login" element={<DoctorLogin />} />
          <Route path="/worker/healthcare/signup" element={<WorkerSignup serviceType="healthcare" />} />
          
          {/* Freelance */}
          <Route path="/worker/freelance/login" element={<WorkerLogin serviceType="freelance" />} />
          <Route path="/worker/freelance/signup" element={<WorkerSignup serviceType="freelance" />} />
          <Route 
            path="/freelancer/dashboard" 
            element={
              <ProtectedWorkerRoute>
                <FreelancerDashboard />
              </ProtectedWorkerRoute>
            } 
          />
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

          {/* Car Services */}
          <Route path="/worker/car/login" element={<WorkerLogin serviceType="car" />} />
          <Route path="/worker/car/signup" element={<WorkerSignup serviceType="car" />} />
          <Route path="/worker/car/services" element={<WorkerServiceSelection />} />

          {/* Car Services Homepage */}
          <Route 
            path="/worker/car/homepage" 
            element={
              <ProtectedWorkerRoute>
                <CarServiceHomepage />
              </ProtectedWorkerRoute>
            } 
          />

          {/* Mechanic Routes */}
          <Route path="/worker/car/mechanic/login" element={<MechanicAuth />} />
          <Route path="/worker/car/mechanic/signup" element={<MechanicAuth />} />
          <Route 
            path="/worker/car/mechanic/dashboard" 
            element={
              <ProtectedWorkerRoute>
                <CarServiceHomepage />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/jobs" 
            element={
              <ProtectedWorkerRoute>
                <MechanicJobs />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/active-jobs" 
            element={
              <ProtectedWorkerRoute>
                <MechanicActiveJobs />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/performance" 
            element={
              <ProtectedWorkerRoute>
                <MechanicPerformance />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/slots" 
            element={
              <ProtectedWorkerRoute>
                <MechanicSlots />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/profile" 
            element={
              <ProtectedWorkerRoute>
                <MechanicProfile />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/details" 
            element={
              <ProtectedWorkerRoute>
                <MechanicDetails />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/payments" 
            element={
              <ProtectedWorkerRoute>
                <MechanicPayments />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/analytics" 
            element={
              <ProtectedWorkerRoute>
                <MechanicAnalytics />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/settings" 
            element={
              <ProtectedWorkerRoute>
                <MechanicSettings />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/worker/car/mechanic/support" 
            element={
              <ProtectedWorkerRoute>
                <MechanicSupport />
              </ProtectedWorkerRoute>
            } 
          />

          {/* Fuel Delivery Routes */}
          <Route path="/worker/car/fuel-delivery/login" element={<FuelDeliveryAuth />} />
          <Route path="/worker/car/fuel-delivery/signup" element={<FuelDeliveryAuth />} />
          {/* Fuel Delivery: shared bottom nav on every screen */}
          <Route
            path="/worker/car/fuel-delivery"
            element={
              <ProtectedWorkerRoute>
                <FuelDeliveryLayout />
              </ProtectedWorkerRoute>
            }
          >
            <Route index element={<Navigate to="home" replace />} />
            <Route path="home" element={<FuelDeliveryHomepage />} />
            <Route path="requests" element={<FuelDeliveryRequests />} />
            <Route path="active-delivery" element={<FuelDeliveryActive />} />
            <Route path="history" element={<FuelDeliveryHistory />} />
            <Route path="performance" element={<FuelDeliveryPerformance />} />
            <Route path="profile" element={<FuelDeliveryProfile />} />
          </Route>

          {/* Tow Truck Routes */}
          <Route path="/worker/car/tow-truck/login" element={<TowTruckAuth />} />
          <Route path="/worker/car/tow-truck/signup" element={<TowTruckAuth />} />
          <Route path="/worker/car/tow-truck/home" element={
            <ProtectedWorkerRoute>
              <TowTruckHomepage />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/tow-truck/details" element={
            <ProtectedWorkerRoute>
              <TowTruckDetails />
            </ProtectedWorkerRoute>
          } />

          {/* Automobile Expert Routes */}
          <Route path="/worker/car/automobile-expert/login" element={<AutomobileExpertAuth />} />
          <Route path="/worker/car/automobile-expert/signup" element={<AutomobileExpertAuth />} />
          <Route path="/worker/car/automobile-expert/home" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertHomepage />
            </ProtectedWorkerRoute>
          } />

          {/* Resource Management */}
          <Route path="/worker/resource/login" element={<WorkerLogin serviceType="resource" />} />
          <Route path="/worker/resource/signup" element={<WorkerSignup serviceType="resource" />} />

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
