import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import DoctorSearch from './services/healthcare/pages/DoctorSearch';
import Booking from './pages/Booking';
import WorkerLogin from './shared/WorkerLogin';
import WorkerSignup from './shared/WorkerSignup';
import WorkerDashboard from './pages/WorkerDashboard';
import ServiceSelection from './shared/ServiceSelection';
import DoctorLogin from './pages/DoctorLogin';
import DoctorAvailability from './pages/DoctorAvailability';
import DoctorProfile from './services/healthcare/DoctorProfile';
import HealthcareDashboard from './services/healthcare/pages/HealthcareDashboard';
import AppointmentsPage from './services/healthcare/pages/AppointmentsPage';
import AICareScreen from './services/healthcare/pages/AICareScreen';
import HealthcareProfile from './services/healthcare/pages/HealthcareProfile';
import MyCareScreen from './services/healthcare/pages/MyCareScreen';
import VideoConsultationsPage from './services/healthcare/pages/VideoConsultationsPage';
import { useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Housekeeping Arrival Pages
import UserHome from './services/housekeeping/arrival/UserHome';
import AIChat from './services/housekeeping/arrival/AIChat';
import AIAssistantPage from './services/housekeeping/AIAssistantPage';
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
import CarServiceUserLayout from './services/car/CarServiceUserLayout';
import HousekeepingClientLayout from './services/housekeeping/HousekeepingClientLayout';
import HousekeepingProviderLayout from './services/housekeeping/HousekeepingProviderLayout';

// Car Service Components
import CarServiceSetup from './services/car/CarServiceSetup';
import CarServiceHome from './services/car/CarServiceHome';
import BookMechanic from './services/car/BookMechanic';
import MyGarage from './services/car/MyGarage';
import BookTowTruck from './services/car/BookTowTruck';
import FuelDelivery from './services/car/FuelDelivery';

// Freelance Marketplace
import FreelanceHome from './services/freelance/client/FreelanceHome';
import ProjectDetailPage from './services/freelance/client/ProjectDetailPage';
import FreelancerProfileView from './services/freelance/client/FreelancerProfileView';
import ChatTestPage from './services/freelance/test/ChatTestPage';
import DirectBookingTest from './services/freelance/test/DirectBookingTest';
import SimpleDirectBookingTest from './services/freelance/test/SimpleDirectBookingTest';
import FreelancerDashboard from './services/freelance/worker/FreelancerDashboard';
import BrowseProjects from './services/freelance/worker/BrowseProjects';
import FreelancerProposals from './services/freelance/worker/FreelancerProposals';
import FreelancerWork from './services/freelance/worker/FreelancerWork';
import FreelanceWalletPage from './services/freelance/worker/FreelanceWalletPage';

// Finny Smart Transaction Tracker
import FinnyHomeScreen from './services/finny/pages/FinnyHomeScreen';
import QuickModePage from './services/finny/pages/QuickModePage';
import SummaryPage from './services/finny/pages/SummaryPage';
import AnalyticsPage from './services/finny/pages/AnalyticsPage';
import ChatModePage from './services/finny/pages/ChatModePage';
import BudgetPage from './services/finny/pages/BudgetPage';
import LoanPage from './services/finny/pages/LoanPage';
import GoalJarPage from './services/finny/pages/GoalJarPage';
import GoalJarDetailPage from './pages/finny/GoalJarDetailPage';
import AiCoachPage from './pages/finny/AiCoachPage';
import ChatFinancialAssistantPage from './services/finny/pages/ChatFinancialAssistantPage';
import AnalyticsDashboardPage from './services/finny/pages/AnalyticsDashboardPage';
import SmartBudgetPlannerPage from './services/finny/pages/SmartBudgetPlannerPage';
import CreateFinancialPlanPage from './services/finny/pages/CreateFinancialPlanPage';
import BudgetStatusPage from './services/finny/pages/BudgetStatusPage';
import BurnRatePage from './services/finny/pages/BurnRatePage';
import MonthlyReportPage from './services/finny/pages/MonthlyReportPage';
import BudgetGamificationPage from './services/finny/pages/BudgetGamificationPage';
import LeftoverManagementPage from './services/finny/pages/LeftoverManagementPage';
import SmartLoanAnalyzerPage from './services/finny/pages/SmartLoanAnalyzerPage';
import AnalyzeLoanPage from './services/finny/pages/AnalyzeLoanPage';
import CompareLoansPage from './services/finny/pages/CompareLoansPage';
import LoanImpactPage from './services/finny/pages/LoanImpactPage';
import EarlyRepaymentPage from './services/finny/pages/EarlyRepaymentPage';
import RepaymentSchedulePage from './services/finny/pages/RepaymentSchedulePage';
import LoanRiskPage from './services/finny/pages/LoanRiskPage';
import LoanHistoryPage from './services/finny/pages/LoanHistoryPage';
import FinnySidebarLayout from './services/finny/components/FinnySidebarLayout';

// Healthcare Doctor Dashboard
import DoctorDashboard from './services/healthcare/pages/DoctorDashboard';

// Car Services Worker Auth
import WorkerServiceSelection from './services/car/WorkerServiceSelection';
import MechanicAuth from './services/car/mechanic/MechanicAuth';
import FuelDeliveryAuth from './services/car/FuelDeliveryAuth';
import TowTruckAuth from './services/car/TowTruckAuth';
import AutomobileExpertAuth from './services/car/AutomobileExpertAuth';

// Car Services Dashboards
import CarServiceHomepage from './services/car/CarServiceHomepage';
import MechanicDashboard from './services/car/mechanic/MechanicDashboard';
import AutomobileExpertHomepage from './services/car/AutomobileExpertHomepage';
import AutomobileExpertRequests from './services/car/AutomobileExpertRequests';
import ActiveConsultation from './services/car/ActiveConsultation';
import AutomobileExpertConsultationMenu from './services/car/AutomobileExpertConsultationMenu';
import AutomobileExpertConsultationHistory from './services/car/AutomobileExpertConsultationHistory';
import AutomobileExpertPerformanceAnalytics from './services/car/AutomobileExpertPerformanceAnalytics';
import AutomobileExpertReputation from './services/car/AutomobileExpertReputation';
import AutomobileExpertReportUser from './services/car/AutomobileExpertReportUser';
import AutomobileExpertQueueStatus from './services/car/AutomobileExpertQueueStatus';
import MechanicJobs from './services/car/MechanicJobs';
import MechanicJobsQueue from './services/car/mechanic/MechanicJobsQueue';
import MechanicEarnings from './services/car/mechanic/MechanicEarnings';
import MechanicSettings from './services/car/mechanic/MechanicSettings';
import MechanicHistory from './services/car/mechanic/MechanicHistory';
import MechanicActiveJobs from './services/car/MechanicActiveJobs';
import MechanicPerformance from './services/car/MechanicPerformance';
import MechanicSlots from './services/car/MechanicSlots';
import MechanicProfile from './services/car/MechanicProfile';
import MechanicDetails from './services/car/MechanicDetails';
import MechanicPayments from './services/car/MechanicPayments';
import MechanicAnalytics from './services/car/MechanicAnalytics';
import MechanicSupport from './services/car/MechanicSupport';

// Fuel Delivery Components
import FuelDeliveryLayout from './services/car/FuelDeliveryLayout';
import FuelDeliveryHomepage from './services/car/FuelDeliveryHomepage';
import FuelDeliveryRequests from './services/car/FuelDeliveryRequests';
import FuelDeliveryActive from './services/car/FuelDeliveryActive';
import FuelDeliveryHistory from './services/car/FuelDeliveryHistory';
import FuelDeliveryPerformance from './services/car/FuelDeliveryPerformance';
import FuelDeliveryProfile from './services/car/FuelDeliveryProfile';
import MyBookings from './pages/MyBookings';
import AIMechanic from './pages/AIMechanic';

// Tow Truck Components
import TowTruckHomepage from './services/car/TowTruckHomepage';
import TowTruckDetails from './services/car/TowTruckDetails';
import WorkerLandingPage from './services/healthcare/worker_portal/WorkerLandingPage';
import WorkerSignupPage from './services/healthcare/worker_portal/WorkerSignupPage';
import WorkerLoginPage from './services/healthcare/worker_portal/WorkerLoginPage';
import WorkerDashboardPage from './services/healthcare/worker_portal/WorkerDashboardPage';
import WorkerPortalProtectedRoute from './services/healthcare/worker_portal/WorkerPortalProtectedRoute';
import experteaseELogo from './assets/expertease-e.png';

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
    } else if (location.pathname.startsWith('/freelancer/') || location.pathname.startsWith('/doctor/') || location.pathname.startsWith('/worker/housekeeping/')) {
      token = localStorage.getItem('token');
      // For these types, worker data might be in worker_id or user info
      const workerId = localStorage.getItem('worker_id');
      if (token && workerId) {
        workerData = JSON.stringify({ id: workerId, email: localStorage.getItem('worker_email') });
      }
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
  const location = useLocation();
  const [showStartupSplash, setShowStartupSplash] = useState(true);
  const isCarServiceUserRoute = location.pathname.startsWith('/car-service');
  const isHousekeepingRoute = location.pathname.startsWith('/housekeeping');
  const isWorkerRoute = location.pathname.startsWith('/worker') || 
                       location.pathname.startsWith('/freelancer/') || 
                       location.pathname.startsWith('/doctor/');

  const isFreelanceRoute = location.pathname.startsWith('/freelance');

  useEffect(() => {
    const timer = setTimeout(() => setShowStartupSplash(false), 3200);
    return () => clearTimeout(timer);
  }, []);

  if (showStartupSplash) {
    return (
      <div
        style={{
          minHeight: '100vh',
          background: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#5f49b8',
          flexDirection: 'row',
          gap: '16px',
        }}
      >
        <div
          style={{
            width: '92px',
            height: '92px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            filter: 'drop-shadow(0 10px 16px rgba(126, 89, 255, 0.2))',
          }}
        >
          <img
            src={experteaseELogo}
            alt="ExpertEase logo mark"
            style={{
              width: '86px',
              height: '86px',
              objectFit: 'contain',
            }}
          />
        </div>
        <div
          style={{
            fontSize: '52px',
            fontWeight: 700,
            lineHeight: 1,
            letterSpacing: '0.2px',
            color: '#5f49b8',
          }}
        >
          ExpertEase
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {!isCarServiceUserRoute && !isHousekeepingRoute && !isWorkerRoute && !isFreelanceRoute && <Navbar />}
      <div className={isCarServiceUserRoute || isHousekeepingRoute || isWorkerRoute || isFreelanceRoute ? "" : "main-content"}>
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
            
            {/* Finny Smart Transaction Tracker Routes */}
            <Route path="/finny" element={<ProtectedRoute><FinnySidebarLayout><FinnyHomeScreen /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/quick" element={<ProtectedRoute><FinnySidebarLayout><QuickModePage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/summary" element={<ProtectedRoute><FinnySidebarLayout><SummaryPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/analytics" element={<ProtectedRoute><FinnySidebarLayout><AnalyticsDashboardPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/chat" element={<ProtectedRoute><FinnySidebarLayout><ChatModePage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget" element={<ProtectedRoute><FinnySidebarLayout><SmartBudgetPlannerPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget/create-plan" element={<ProtectedRoute><FinnySidebarLayout><CreateFinancialPlanPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget/status" element={<ProtectedRoute><FinnySidebarLayout><BudgetStatusPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget/burn-rate" element={<ProtectedRoute><FinnySidebarLayout><BurnRatePage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget/report" element={<ProtectedRoute><FinnySidebarLayout><MonthlyReportPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget/gamification" element={<ProtectedRoute><FinnySidebarLayout><BudgetGamificationPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/budget/leftover" element={<ProtectedRoute><FinnySidebarLayout><LeftoverManagementPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan" element={<ProtectedRoute><FinnySidebarLayout><SmartLoanAnalyzerPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/analyze" element={<ProtectedRoute><FinnySidebarLayout><AnalyzeLoanPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/compare" element={<ProtectedRoute><FinnySidebarLayout><CompareLoansPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/impact" element={<ProtectedRoute><FinnySidebarLayout><LoanImpactPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/early-repayment" element={<ProtectedRoute><FinnySidebarLayout><EarlyRepaymentPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/schedule" element={<ProtectedRoute><FinnySidebarLayout><RepaymentSchedulePage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/risk" element={<ProtectedRoute><FinnySidebarLayout><LoanRiskPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/loan/history" element={<ProtectedRoute><FinnySidebarLayout><LoanHistoryPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/goals" element={<ProtectedRoute><FinnySidebarLayout><GoalJarPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/goal-jar" element={<ProtectedRoute><FinnySidebarLayout><GoalJarPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/goal-jar/:goalId" element={<ProtectedRoute><FinnySidebarLayout><GoalJarDetailPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/coach" element={<ProtectedRoute><FinnySidebarLayout><ChatFinancialAssistantPage /></FinnySidebarLayout></ProtectedRoute>} />
            <Route path="/finny/ai-coach" element={<ProtectedRoute><FinnySidebarLayout><AiCoachPage /></FinnySidebarLayout></ProtectedRoute>} />
          </Route>

          {/* Housekeeping Arrival Routes */}
          <Route element={<ProtectedRoute><HousekeepingClientLayout /></ProtectedRoute>}>
            <Route path="/housekeeping/home" element={<UserHome />} />
            <Route path="/housekeeping/ai-chat" element={<AIChat />} />
            <Route path="/housekeeping/ai-assistant" element={<AIAssistantPage />} />
            <Route path="/housekeeping/bookings" element={<UserBookings />} />
            <Route path="/housekeeping/profile" element={<UserProfile />} />
            <Route path="/housekeeping/explore" element={<UserHome />} />
            <Route path="/housekeeping/booking/create" element={<BookingFlow />} />
          </Route>

          {/* Service Selection */}
          <Route path="/services" element={<ProtectedRoute><ServiceSelection /></ProtectedRoute>} />
          <Route path="/provide-service" element={<ServiceSelection mode="worker" />} />
          
          {/* Car Service User Routes */}
          <Route element={<ProtectedRoute><CarServiceUserLayout /></ProtectedRoute>}>
            <Route path="/car-service/setup" element={<CarServiceSetup />} />
            <Route path="/car-service/home" element={<CarServiceHome />} />
            <Route path="/car-service/book-mechanic" element={<BookMechanic />} />
            <Route path="/car-service/garage" element={<MyGarage />} />
            <Route path="/car-service/book-tow-truck" element={<BookTowTruck />} />
            <Route path="/car-service/fuel-delivery" element={<FuelDelivery />} />
            <Route path="/car-service/my-bookings" element={<MyBookings />} />
            <Route path="/car-service/ai-mechanic" element={<AIMechanic />} />
            <Route path="/car-service" element={<CarServiceSetup />} />
          </Route>
          
          {/* Freelance Marketplace Routes */}
          <Route path="/freelance/home" element={<ProtectedRoute><FreelanceHome /></ProtectedRoute>} />
          <Route path="/freelance/project/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
          <Route path="/freelance/freelancer/:freelancerId" element={<ProtectedRoute><FreelancerProfileView /></ProtectedRoute>} />
          <Route path="/freelance/test-chat" element={<ProtectedRoute><ChatTestPage /></ProtectedRoute>} />
          <Route path="/freelance/test-direct-booking" element={<ProtectedRoute><DirectBookingTest /></ProtectedRoute>} />
          <Route path="/freelance/simple-test" element={<ProtectedRoute><SimpleDirectBookingTest /></ProtectedRoute>} />
          <Route path="/freelance/test-profile" element={<ProtectedRoute><FreelancerProfileView /></ProtectedRoute>} />

          {/* Healthcare User Routes */}
          <Route path="/healthcare/home" element={<ProtectedRoute><HealthcareDashboard /></ProtectedRoute>} />
          <Route path="/healthcare/explore" element={<ProtectedRoute><DoctorSearch /></ProtectedRoute>} />
          <Route path="/healthcare/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
          <Route path="/healthcare/ai-care" element={<ProtectedRoute><AICareScreen /></ProtectedRoute>} />
          <Route path="/healthcare/my-care" element={<ProtectedRoute><MyCareScreen /></ProtectedRoute>} />
          <Route path="/healthcare/video-consultations" element={<ProtectedRoute><VideoConsultationsPage /></ProtectedRoute>} />
          <Route path="/healthcare/profile" element={<ProtectedRoute><HealthcareProfile /></ProtectedRoute>} />
          
          {/* Healthcare Doctor Routes */}
          <Route path="/doctor/dashboard" element={<DoctorDashboard />} />
          <Route path="/doctor/availability" element={<DoctorDashboard />} />
          <Route path="/doctor/requests" element={<DoctorDashboard />} />
          <Route path="/doctor/appointments" element={<DoctorDashboard />} />
          <Route path="/doctor/profile" element={<DoctorDashboard />} />
          
          {/* Healthcare */}
          <Route path="/worker/healthcare/login" element={<DoctorLogin />} />
          <Route path="/worker/healthcare/signup" element={<WorkerSignupPage />} />
          
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
            path="/freelancer/browse" 
            element={
              <ProtectedWorkerRoute>
                <BrowseProjects />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/freelancer/proposals" 
            element={
              <ProtectedWorkerRoute>
                <FreelancerProposals />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/freelancer/work" 
            element={
              <ProtectedWorkerRoute>
                <FreelancerWork />
              </ProtectedWorkerRoute>
            } 
          />
          <Route 
            path="/freelancer/wallet" 
            element={
              <ProtectedWorkerRoute>
                <FreelanceWalletPage />
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
          
          {/* Housekeeping Provider Routes */}
          <Route path="/worker/housekeeping/login" element={<WorkerLogin serviceType="housekeeping" />} />
          <Route path="/worker/housekeeping/signup" element={<WorkerSignup serviceType="housekeeping" />} />
          <Route element={<ProtectedWorkerRoute><HousekeepingProviderLayout /></ProtectedWorkerRoute>}>
            <Route path="/worker/housekeeping/dashboard" element={<ProviderDashboard />} />
            <Route path="/worker/housekeeping/schedule" element={<ProviderSchedule />} />
            <Route path="/worker/housekeeping/availability" element={<ProviderAvailability />} />
            <Route path="/worker/housekeeping/earnings" element={<ProviderEarnings />} />
            <Route path="/worker/housekeeping/profile" element={<ProviderProfile />} />
            <Route path="/worker/housekeeping/pricing" element={<ProviderPricing />} />
          </Route>

          {/* Car Services */}
          <Route path="/worker/car/login" element={<WorkerLogin serviceType="car" />} />
          <Route path="/worker/car/signup" element={<WorkerSignup serviceType="car" />} />
          <Route path="/worker/car/services" element={<WorkerServiceSelection />} />

          {/* Mechanic Routes */}
          <Route path="/worker/car/mechanic/auth" element={<MechanicAuth />} />
          <Route path="/worker/car/mechanic/login" element={<MechanicAuth />} />
          <Route path="/worker/car/mechanic/signup" element={<MechanicAuth />} />
          <Route 
            path="/worker/car/mechanic/dashboard" 
            element={
              <ProtectedWorkerRoute>
                <MechanicDashboard />
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
            path="/worker/car/mechanic/jobs-queue" 
            element={
              <ProtectedWorkerRoute>
                <MechanicJobsQueue />
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
            path="/worker/car/mechanic/earnings" 
            element={
              <ProtectedWorkerRoute>
                <MechanicEarnings />
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
            path="/worker/car/mechanic/history" 
            element={
              <ProtectedWorkerRoute>
                <MechanicHistory />
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
          <Route path="/worker/car/automobile-expert/homepage" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertHomepage />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/requests" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertRequests />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/active" element={
            <ProtectedWorkerRoute>
              <ActiveConsultation />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/consultation-menu" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertConsultationMenu />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/consultation-history" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertConsultationHistory />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/performance-analytics" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertPerformanceAnalytics />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/reputation" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertReputation />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/report-user" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertReportUser />
            </ProtectedWorkerRoute>
          } />
          <Route path="/worker/car/automobile-expert/queue-status" element={
            <ProtectedWorkerRoute>
              <AutomobileExpertQueueStatus />
            </ProtectedWorkerRoute>
          } />

          {/* Resource Management */}
          <Route path="/worker/resource/login" element={<WorkerLogin serviceType="resource" />} />
          <Route path="/worker/resource/signup" element={<WorkerSignup serviceType="resource" />} />

          {/* Healthcare Worker Portal */}
          <Route path="/worker" element={<WorkerLandingPage />} />
          <Route path="/worker/login" element={<WorkerLoginPage />} />
          <Route path="/worker/signup" element={<WorkerSignupPage />} />
          <Route
            path="/worker/dashboard"
            element={
              <WorkerPortalProtectedRoute>
                <WorkerDashboardPage />
              </WorkerPortalProtectedRoute>
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
