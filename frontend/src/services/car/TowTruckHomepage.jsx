import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';
import { styled, keyframes } from '../../stitches.config';
import api from '../../shared/api';
import { 
  LayoutDashboard, 
  ListChecks, 
  Wallet, 
  History, 
  Settings, 
  HelpCircle, 
  LogOut, 
  Bell, 
  Search,
  Truck,
  Timer,
  Navigation,
  Check,
  Cog,
  MapPin,
  Phone,
  ArrowRight,
  User,
  MoreVertical,
  CheckCircle,
  X
} from 'lucide-react';

// Animations
const pulse = keyframes({
  '0%, 100%': { opacity: 1 },
  '50%': { opacity: 0.5 },
});

// Styled Components
const DashboardContainer = styled('div', {
  minHeight: '100vh',
  display: 'flex',
  background: '#f7f9fb',
  fontFamily: '$body',
});

const TopNav = styled('header', {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  height: '64px',
  background: 'rgba(255, 255, 255, 0.8)',
  backdropFilter: 'blur(12px)',
  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  paddingX: '12px',
  zIndex: 100,
  '@md': { paddingX: '24px' },
});

const Brand = styled('span', {
  fontSize: '24px',
  fontWeight: 'bold',
  color: '#7c3aed',
  fontFamily: '$heading',
  letterSpacing: '-0.05em',
});

const SearchBar = styled('div', {
  display: 'none',
  '@md': {
    display: 'flex',
    alignItems: 'center',
    background: '#f2f4f6',
    borderRadius: 'full',
    padding: '8px 16px',
    width: '384px',
    gap: '8px',
    marginLeft: '32px',
  },
});

const SearchInput = styled('input', {
  background: 'transparent',
  border: 'none',
  fontSize: '14px',
  width: '100%',
  '&:focus': { outline: 'none' },
});

const HeaderRight = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '24px',
});

const OnlineBadge = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  background: '#f2f4f6',
  padding: '6px 12px',
  borderRadius: 'full',
});

const StatusText = styled('span', {
  fontSize: '12px',
  fontWeight: 'bold',
  color: '#4a4455',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
});

const ToggleBtn = styled('button', {
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  color: '#00746a',
  variants: {
    online: {
      true: { color: '#00746a' },
      false: { color: '#64748B' },
    },
  },
});

const Avatar = styled('img', {
  width: '40px',
  height: '40px',
  borderRadius: 'full',
  objectFit: 'cover',
  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
});

const Sidebar = styled('aside', {
  display: 'none',
  '@md': {
    display: 'flex',
    flexDirection: 'column',
    width: '256px',
    background: '#f8fafc',
    height: '100vh',
    position: 'fixed',
    top: 0,
    left: 0,
    padding: '96px 16px 32px',
    zIndex: 50,
  },
});

const SidebarProfile = styled('div', {
  paddingX: '16px',
  marginBottom: '32px',
});

const ProfileName = styled('h2', {
  fontSize: '20px',
  fontWeight: '900',
  color: '#7c3aed',
  fontFamily: '$heading',
});

const ProfileRole = styled('p', {
  fontSize: '12px',
  fontWeight: '500',
  color: '#64748B',
});

const Nav = styled('nav', {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
});

const NavItem = styled('a', {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  padding: '12px 16px',
  borderRadius: '8px',
  fontSize: '14px',
  fontWeight: '500',
  color: '#4a4455',
  transition: 'all 0.2s',
  cursor: 'pointer',
  textDecoration: 'none',
  '&:hover': {
    color: '#7c3aed',
    transform: 'translateX(4px)',
  },
  variants: {
    active: {
      true: {
        background: 'white',
        color: '#7c3aed',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        fontWeight: 'bold',
      },
    },
  },
});

const SidebarFooter = styled('div', {
  paddingTop: '24px',
  borderTop: '1px solid rgba(0,0,0,0.05)',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
});

const Main = styled('main', {
  marginLeft: 0,
  padding: '80px 16px 40px',
  flex: 1,
  '@md': { marginLeft: '256px', padding: '96px 40px 40px' },
});

const ContentWrapper = styled('div', {
  maxWidth: '1280px',
  margin: '0 auto',
});

const WelcomeSection = styled('section', {
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
  marginBottom: '40px',
  '@md': { flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'space-between' },
});

const StatsRow = styled('div', {
  display: 'flex',
  gap: '12px',
  width: '100%',
  overflowX: 'auto',
  paddingBottom: '8px',
  scrollbarWidth: 'none',
  '&::-webkit-scrollbar': { display: 'none' },
  '@md': { gap: '16px', overflowX: 'visible', paddingBottom: 0 },
});

const MiniStatCard = styled('div', {
  flex: '0 0 200px',
  background: 'white',
  padding: '16px',
  borderRadius: '12px',
  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  borderLeft: '4px solid',
  '@md': { flex: 1, padding: '20px', gap: '16px' },
  variants: {
    color: {
      tertiary: { borderLeftColor: '#005952' },
      primary: { borderLeftColor: '#630ed4' },
    },
  },
});

const IconBox = styled('div', {
  padding: '8px',
  borderRadius: '8px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  variants: {
    bg: {
      tertiary: { background: '#89f5e7', color: '#005049' },
      primary: { background: '#eaddff', color: '#5a00c6' },
    },
  },
});

const DashboardGrid = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1fr',
  gap: '32px',
  '@lg': { gridTemplateColumns: 'repeat(12, 1fr)' },
});

const LeftCol = styled('div', {
  gridColumn: 'span 12',
  '@lg': { gridColumn: 'span 8' },
  display: 'flex',
  flexDirection: 'column',
  gap: '32px',
});

const RightCol = styled('div', {
  gridColumn: 'span 12',
  '@lg': { gridColumn: 'span 4' },
  display: 'flex',
  flexDirection: 'column',
  gap: '32px',
});

const ActiveJobCard = styled('div', {
  background: 'white',
  borderRadius: '12px',
  overflow: 'hidden',
  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  display: 'flex',
  flexDirection: 'column',
});

const CardHeader = styled('div', {
  padding: '24px',
  borderBottom: '1px solid rgba(0,0,0,0.05)',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
});

const JobBadge = styled('span', {
  padding: '4px 12px',
  background: '#89f5e7',
  color: '#005049',
  fontSize: '12px',
  fontWeight: 'bold',
  borderRadius: 'full',
  textTransform: 'uppercase',
});

const MapArea = styled('div', {
  height: '240px',
  background: '#e2e8f0',
  position: 'relative',
  '@md': { height: '320px' },
});

const MapImage = styled('div', {
  width: '100%',
  height: '100%',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  filter: 'grayscale(0.2)',
});

const MapOverlay = styled('div', {
  position: 'absolute',
  bottom: '12px',
  left: '12px',
  right: '12px',
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(4px)',
  padding: '12px',
  borderRadius: '12px',
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
  '@sm': { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: '16px', bottom: '16px', left: '16px', right: '16px' },
});

const Stepper = styled('div', {
  display: 'flex', 
  justifyContent: 'space-between',
  position: 'relative',
  paddingX: '8px',
  paddingY: '24px',
  width: '100%',
  overflowX: 'auto',
  scrollbarWidth: 'none',
  '&::-webkit-scrollbar': { display: 'none' },
  '@sm': { paddingX: '16px', paddingY: '32px', overflowX: 'visible' },
  '&::before': {
    content: '""',
    position: 'absolute', 
    top: '44px',
    left: '40px',
    right: '40px',
    height: '2px',
    background: '#f2f4f6',
    zIndex: 0,
    '@sm': { top: '52px' },
  },
});

const StepFill = styled('div', {
  position: 'absolute',
  top: '44px',
  left: '40px',
  height: '2px',
  background: '#005952',
  zIndex: 1,
  transition: 'width 0.3s ease',
  '@sm': { top: '52px' },
});

const Step = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '8px',
  zIndex: 2,
  minWidth: '80px',
  flexShrink: 0,
  '@sm': { minWidth: '96px', gap: '12px' },
});

const StepIcon = styled('div', {
  width: '32px',
  height: '32px',
  borderRadius: 'full',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  '@sm': { width: '40px', height: '40px' },
  variants: {
    status: {
      completed: { background: '#005952', color: 'white' },
      active: { background: '#005952', color: 'white', ring: '4px solid #89f5e7' },
      pending: { background: '#f2f4f6', color: '#7b7487' },
    },
  },
});

const StepLabel = styled('span', {
  fontSize: '10px',
  fontWeight: 'bold',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  textAlign: 'center',
  variants: {
    active: {
      true: { color: '#005952' },
      false: { color: '#7b7487' },
    },
  },
});

const JobFooter = styled('div', {
  padding: '32px',
  display: 'grid',
  gridTemplateColumns: '1fr',
  '@md': { gridTemplateColumns: '1fr 1fr' },
  gap: '32px',
});

const LocationFlow = styled('div', {
  display: 'flex',
  gap: '16px',
});

const FlowIndicator = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  paddingTop: '4px',
});

const Dot = styled('div', {
  width: '10px',
  height: '10px',
  borderRadius: 'full',
  variants: {
    type: {
      pickup: { border: '2px solid #630ed4' },
      drop: { background: '#005952' },
    },
  },
});

const Line = styled('div', {
  width: '2px',
  height: '48px',
  background: 'rgba(204, 195, 216, 0.3)',
  margin: '4px 0',
});

const ActionBtn = styled('button', {
  height: '56px',
  background: 'linear-gradient(to right, #005952, #00746a)',
  color: 'white',
  borderRadius: '12px',
  fontWeight: 'bold',
  border: 'none',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '12px',
  boxShadow: '0 10px 15px -3px rgba(0, 89, 82, 0.2)',
  transition: 'transform 0.2s',
  '&:hover': { transform: 'scale(1.02)' },
});

const PendingSection = styled('div', {
  background: '#f2f4f6',
  padding: '4px',
  borderRadius: '16px',
});

const SectionTitle = styled('h3', {
  padding: '12px 16px',
  fontSize: '18px',
  fontWeight: 'bold',
  fontFamily: '$heading',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
});

const CountBadge = styled('span', {
  background: '#630ed4',
  color: 'white',
  fontSize: '10px',
  padding: '2px 8px',
  borderRadius: 'full',
});

const RequestCard = styled('div', {
  background: 'white',
  padding: '16px',
  borderRadius: '12px',
  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  marginBottom: '12px',
  cursor: 'pointer',
  transition: 'all 0.2s',
  '&:hover': { transform: 'translateX(4px)', borderLeft: '4px solid #005952' },
});

const GoalCard = styled('div', {
  background: '#630ed4',
  padding: '24px',
  borderRadius: '16px',
  color: 'white',
  boxShadow: '0 10px 25px rgba(99, 14, 212, 0.2)',
});

const ProgressBar = styled('div', {
  width: '100%',
  height: '8px',
  background: 'rgba(255,255,255,0.2)',
  borderRadius: 'full',
  overflow: 'hidden',
  marginTop: '16px',
});

const ProgressFill = styled('div', {
  height: '100%',
  background: 'white',
  borderRadius: 'full',
  transition: 'width 0.5s ease',
});

const MobileNav = styled('nav', {
  '@md': { display: 'none' },
  position: 'fixed',
  bottom: 0,
  left: 0,
  right: 0,
  height: '64px',
  background: 'white',
  boxShadow: '0 -4px 12px rgba(0,0,0,0.05)',
  display: 'flex',
  justifyContent: 'space-around',
  alignItems: 'center',
  zIndex: 100,
});

const MobileNavItem = styled('a', {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '2px',
  color: '#64748B',
  textDecoration: 'none',
  variants: {
    active: {
      true: { color: '#7c3aed', fontWeight: 'bold' },
    },
  },
});

const Toast = styled('div', {
  position: 'fixed',
  bottom: '80px',
  right: '24px',
  padding: '12px 24px',
  borderRadius: '8px',
  color: 'white',
  fontWeight: 'bold',
  zIndex: 1000,
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  variants: {
    type: {
      success: { background: '#005952' },
      error: { background: '#ba1a1a' },
    },
  },
});

const TowTruckHomepage = () => {
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [activeJob, setActiveJob] = useState(null);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [stats, setStats] = useState({
    truckStatus: 'Flatbed Heavy',
    shiftTime: '06h 42m',
    weeklyGoal: 1420,
    target: 2000
  });
  const [workerProfile, setWorkerProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const workerId = localStorage.getItem('workerId');
  const token = localStorage.getItem('workerToken');

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchData = useCallback(async () => {
    if (!workerId || !token) {
      navigate('/worker/car/tow-truck/login');
      return;
    }

    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [profileRes, activeRes, queueRes, statsRes] = await Promise.all([
        api.get(`/api/tow-truck/requests`, { headers, params: { city: workerProfile?.city } }), // For requests
        api.get(`/api/car/tow/active-jobs?worker_id=${workerId}`, { headers }),
        api.get(`/api/car/tow/requests`, { headers }),
        api.get(`/api/car/tow/earnings?worker_id=${workerId}`, { headers })
      ]);

      if (profileRes.data.success) {
        // ... (profile already set from workerData usually)
      }

      if (activeRes.data) {
        setActiveJob(activeRes.data[0] || null); // active-jobs returns a list
      }

      if (queueRes.data) {
        setPendingRequests(queueRes.data || []);
      }

      if (statsRes.data) {
        setStats(prev => ({
          ...prev,
          weeklyGoal: statsRes.data.total_earnings || 0
        }));
      }

    } catch (error) {
      console.error('Error fetching tow truck data:', error);
    } finally {
      setLoading(false);
    }
  }, [workerId, token, navigate]);

  useEffect(() => {
    fetchData();

    const socket = io(import.meta.env.VITE_API_URL);
    socket.emit('join_room', { worker_id: workerId, worker_type: 'tow_truck' });

    socket.on('new_tow_request', (request) => {
      setPendingRequests(prev => [request, ...prev]);
      showToast('New tow request received!');
    });

    return () => socket.disconnect();
  }, [fetchData, workerId]);

  const toggleStatus = async () => {
    try {
      const endpoint = isOnline ? '/api/car/tow/go-offline' : '/api/car/tow/go-online';
      await api.post(endpoint, {
        worker_id: workerId
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setIsOnline(!isOnline);
      showToast(`You are now ${!isOnline ? 'ONLINE' : 'OFFLINE'}`);
    } catch (err) {
      showToast('Failed to update status', 'error');
    }
  };

  const handleAccept = async (requestId) => {
    try {
      await api.post('/api/car/tow/accept', {
        worker_id: workerId,
        request_id: requestId
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      showToast('Job accepted!');
      fetchData();
    } catch (err) {
      showToast('Failed to accept job', 'error');
    }
  };

  const handleUpdateProgress = async () => {
    if (!activeJob) return;
    try {
      // Backend status flow: Accepted -> Started (needs OTP) -> Completed
      const endpoint = activeJob.status === 'accepted' ? '/api/car/tow/start' : '/api/car/tow/complete';
      const payload = activeJob.status === 'accepted' 
        ? { worker_id: workerId, job_id: activeJob.id, otp: '1234' } // Default OTP for testing
        : { worker_id: workerId, job_id: activeJob.id };

      await api.post(endpoint, payload, { headers: { Authorization: `Bearer ${token}` } });
      
      showToast('Job status updated!');
      fetchData();
    } catch (err) {
      showToast('Failed to update status', 'error');
    }
  };

  if (loading) return <div>Loading...</div>;

  const currentStep = activeJob ? (activeJob.status === 'EN_ROUTE' ? 1 : activeJob.status === 'LOADED' ? 2 : activeJob.status === 'COMPLETED' ? 3 : 0) : 0;

  return (
    <DashboardContainer>
      <TopNav>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Brand>ExpertEase</Brand>
          <SearchBar>
            <Search size={18} color="#7b7487" />
            <SearchInput placeholder="Search jobs, clients, or locations..." />
          </SearchBar>
        </div>
        <HeaderRight>
          <OnlineBadge>
            <StatusText>Online</StatusText>
            <ToggleBtn online={isOnline} onClick={toggleStatus}>
              {isOnline ? <CheckCircle size={24} /> : <X size={24} />}
            </ToggleBtn>
          </OnlineBadge>
          <Bell size={20} color="#7b7487" style={{ cursor: 'pointer' }} />
          <Avatar src="https://lh3.googleusercontent.com/aida-public/AB6AXuARfYlcMyyPPSt2_UuuTaBc5Zzt9-8NkyADVPaYCJ7qyQiqMJGNPu2kuRDboUjdwaUQMYa88dgwk6YVBJ3eiBCNiPkNHcMqsTaAscEdT56NCplpTxF4wUXBCFYcrQzWlaGflZdOOjpuMRHvcz3NbG7A1JbzST6teIgjK8ht9DaS_cHyBF_sXz0nxiAYHQsYpdz4Q8U7vfs3C3TBGysebv1Uy1SH82gpLqWnkl-OgfvvgOnaSjmybIcDAaICTuToeXTcwqYDXeWhzhAl" alt="Alex Miller" />
        </HeaderRight>
      </TopNav>

      <Sidebar>
        <SidebarProfile>
          <ProfileName>{workerProfile?.name || 'Alex Miller'}</ProfileName>
          <ProfileRole>Automobile Expert</ProfileRole>
        </SidebarProfile>
        <Nav>
          <NavItem active><LayoutDashboard size={20} /> Dashboard</NavItem>
          <NavItem><ListChecks size={20} /> Jobs Queue</NavItem>
          <NavItem><Wallet size={20} /> Earnings</NavItem>
          <NavItem><History size={20} /> History</NavItem>
          <NavItem><Settings size={20} /> Settings</NavItem>
        </Nav>
        <SidebarFooter>
          <NavItem><HelpCircle size={20} /> Support</NavItem>
          <NavItem onClick={() => { localStorage.clear(); navigate('/worker/car/services'); }}><LogOut size={20} /> Logout</NavItem>
        </SidebarFooter>
      </Sidebar>

      <Main>
        <ContentWrapper>
          <WelcomeSection>
            <div>
              <h1 style={{ fontSize: '36px', fontWeight: 'bold', color: '#191c1e' }}>Tow Dashboard</h1>
              <p style={{ color: '#4a4455', marginTop: '8px' }}>Real-time job management and fleet status for heavy recovery operations.</p>
            </div>
            <StatsRow>
              <MiniStatCard color="tertiary">
                <IconBox bg="tertiary"><Truck size={20} /></IconBox>
                <div>
                  <p style={{ fontSize: '10px', fontWeight: 'bold', color: '#7b7487', textTransform: 'uppercase' }}>Truck Status</p>
                  <p style={{ fontWeight: 'bold' }}>{stats.truckStatus}</p>
                </div>
              </MiniStatCard>
              <MiniStatCard color="primary">
                <IconBox bg="primary"><Timer size={20} /></IconBox>
                <div>
                  <p style={{ fontSize: '10px', fontWeight: 'bold', color: '#7b7487', textTransform: 'uppercase' }}>Shift Time</p>
                  <p style={{ fontWeight: 'bold' }}>{stats.shiftTime}</p>
                </div>
              </MiniStatCard>
            </StatsRow>
          </WelcomeSection>

          <DashboardGrid>
            <LeftCol>
              <ActiveJobCard>
                <CardHeader>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <JobBadge>Active Job</JobBadge>
                    <span style={{ fontSize: '14px', color: '#7b7487' }}>#{activeJob?.request_id || 'TW-99281'}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#005952', fontWeight: 'bold', fontSize: '14px' }}>
                    <span style={{ width: '8px', height: '8px', background: '#005952', borderRadius: '50%', animation: `${pulse} 2s infinite` }} />
                    In Progress
                  </div>
                </CardHeader>
                <MapArea>
                  <MapImage style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBgse1wmTVEVO-ZmrFKE4RdWSGPG7RDxcm-I-TDcUy-xPJeMW-EZqbqqoSKtZNehCH_tWH1dDnZYJfn_9oMV738Jk6QqPLFGkh5RDBYtuCAj9xvF2vpQGSwHsquBY9epC7BCiIpYqWYdrYPtLpSmhYqPtg5RmqF002FBGSVB2vHYAI8arH4YDfg9s5f0FsiWe2OUel6-nYXpnEOzg68vq1eSA51DPfFn7XQY2usmHpMQnHqRy3Zk5lebw3vdfKb8gDN1UgIEbK2d0g3')" }} />
                  <MapOverlay>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ width: '48px', height: '48px', background: '#f2f4f6', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <User size={24} color="#630ed4" />
                      </div>
                      <div>
                        <p style={{ fontWeight: 'bold' }}>{activeJob?.user_name || 'Sarah Jenkins'}</p>
                        <p style={{ fontSize: '12px', color: '#4a4455' }}>{activeJob?.car_model || 'Silver 2021 BMW X5'} • {activeJob?.issue || 'Flat Tire'}</p>
                      </div>
                    </div>
                    <button style={{ background: '#005952', color: 'white', border: 'none', padding: '8px 20px', borderRadius: '8px', fontWeight: 'bold', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                      <Phone size={16} /> Contact
                    </button>
                  </MapOverlay>
                </MapArea>
                <div style={{ padding: '32px' }}>
                  <Stepper>
                    <StepFill style={{ width: `${(currentStep / 3) * 100}%` }} />
                    <Step>
                      <StepIcon status={currentStep >= 0 ? (currentStep === 0 ? 'active' : 'completed') : 'pending'}>
                        {currentStep > 0 ? <Check size={20} /> : <Check size={20} />}
                      </StepIcon>
                      <StepLabel active={currentStep >= 0}>Accepted</StepLabel>
                    </Step>
                    <Step>
                      <StepIcon status={currentStep >= 1 ? (currentStep === 1 ? 'active' : 'completed') : 'pending'}>
                        <Navigation size={20} />
                      </StepIcon>
                      <StepLabel active={currentStep >= 1}>En Route</StepLabel>
                    </Step>
                    <Step>
                      <StepIcon status={currentStep >= 2 ? (currentStep === 2 ? 'active' : 'completed') : 'pending'}>
                        <Cog size={20} />
                      </StepIcon>
                      <StepLabel active={currentStep >= 2}>Loaded</StepLabel>
                    </Step>
                    <Step>
                      <StepIcon status={currentStep >= 3 ? (currentStep === 3 ? 'active' : 'completed') : 'pending'}>
                        <MapPin size={20} />
                      </StepIcon>
                      <StepLabel active={currentStep >= 3}>Delivered</StepLabel>
                    </Step>
                  </Stepper>

                  <JobFooter>
                    <LocationFlow>
                      <FlowIndicator>
                        <Dot type="pickup" />
                        <Line />
                        <Dot type="drop" />
                      </FlowIndicator>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div>
                          <p style={{ fontSize: '10px', fontWeight: 'bold', color: '#7b7487', textTransform: 'uppercase' }}>Pickup Location</p>
                          <p style={{ fontSize: '14px', fontWeight: '500' }}>{activeJob?.pickup_address || '4512 W. Belden Ave, Chicago, IL'}</p>
                        </div>
                        <div>
                          <p style={{ fontSize: '10px', fontWeight: 'bold', color: '#7b7487', textTransform: 'uppercase' }}>Drop-off Location</p>
                          <p style={{ fontSize: '14px', fontWeight: '500' }}>{activeJob?.dropoff_address || 'Precision Auto Body, Evanston, IL'}</p>
                        </div>
                      </div>
                    </LocationFlow>
                    <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                      <ActionBtn onClick={handleUpdateProgress}>
                        {currentStep === 1 ? 'Confirm Arrival at Pickup' : currentStep === 2 ? 'Confirm Drop-off' : 'Job Completed'}
                        <ArrowRight size={20} />
                      </ActionBtn>
                    </div>
                  </JobFooter>
                </div>
              </ActiveJobCard>
            </LeftCol>

            <RightCol>
              <PendingSection>
                <SectionTitle>
                  Pending Requests
                  <CountBadge>{pendingRequests.length} New</CountBadge>
                </SectionTitle>
                <div style={{ padding: '12px' }}>
                  {pendingRequests.length > 0 ? pendingRequests.map((req, i) => (
                    <RequestCard key={req.id || i} onClick={() => handleAccept(req.id)}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                        <span style={{ padding: '2px 8px', background: '#ffdbca', color: '#341100', fontSize: '10px', fontWeight: 'bold', borderRadius: '4px' }}>{req.service_type || 'Standard Tow'}</span>
                        <span style={{ color: '#630ed4', fontWeight: 'bold', fontSize: '12px' }}>₹{req.estimated_fare || '120.00'}</span>
                      </div>
                      <p style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>{req.issue || 'Broken Axle - N. Michigan Ave'}</p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: '#64748B' }}>
                        <MapPin size={14} /> {req.distance || '5.8'} miles away
                      </div>
                      <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                        <button style={{ flex: 1, padding: '8px', background: '#f2f4f6', border: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer' }}>Decline</button>
                        <button style={{ flex: 1, padding: '8px', background: '#005952', color: 'white', border: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer' }}>Accept</button>
                      </div>
                    </RequestCard>
                  )) : (
                    <div style={{ textAlign: 'center', padding: '32px' }}>
                      <CheckCircle size={48} color="#005952" style={{ margin: '0 auto 16px' }} />
                      <p style={{ fontWeight: 'bold', color: '#4a4455' }}>All clear!</p>
                    </div>
                  )}
                </div>
              </PendingSection>

              <GoalCard>
                <h4 style={{ fontFamily: 'Space Grotesk', fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>Weekly Goal</h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <span style={{ fontSize: '30px', fontWeight: 'bold' }}>₹{stats.weeklyGoal}</span>
                  <span style={{ fontSize: '12px', color: '#eaddff' }}>Goal: ₹{stats.target}</span>
                </div>
                <ProgressBar>
                  <ProgressFill style={{ width: `${(stats.weeklyGoal / stats.target) * 100}%` }} />
                </ProgressBar>
                <p style={{ fontSize: '10px', color: '#eaddff', textTransform: 'uppercase', fontWeight: 'bold', letterSpacing: '0.1em', marginTop: '16px' }}>
                  {Math.ceil((stats.target - stats.weeklyGoal) / 100)} more jobs to reach bonus
                </p>
              </GoalCard>
            </RightCol>
          </DashboardGrid>
        </ContentWrapper>
      </Main>

      <MobileNav>
        <MobileNavItem active><LayoutDashboard size={20} /> <span style={{ fontSize: '10px' }}>Home</span></MobileNavItem>
        <MobileNavItem><ListChecks size={20} /> <span style={{ fontSize: '10px' }}>Jobs</span></MobileNavItem>
        <MobileNavItem><Wallet size={20} /> <span style={{ fontSize: '10px' }}>Earnings</span></MobileNavItem>
        <MobileNavItem><User size={20} /> <span style={{ fontSize: '10px' }}>Profile</span></MobileNavItem>
      </MobileNav>

      {toast && (
        <Toast type={toast.type}>
          {toast.type === 'success' ? <CheckCircle size={18} /> : <X size={18} />}
          {toast.message}
        </Toast>
      )}
    </DashboardContainer>
  );
};

export default TowTruckHomepage;
