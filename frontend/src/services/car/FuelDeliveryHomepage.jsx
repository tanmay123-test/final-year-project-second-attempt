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
  MessageSquare,
  Droplet,
  Fuel,
  TrendingUp,
  Truck,
  MapPin,
  CheckCircle,
  Navigation,
  ChevronRight,
  Info,
  Clock,
  Zap,
  MoreVertical,
  Menu,
  X
} from 'lucide-react';

// Animations
const slideIn = keyframes({
  from: { transform: 'translateX(-100%)' },
  to: { transform: 'translateX(0)' },
});

const fadeIn = keyframes({
  from: { opacity: 0 },
  to: { opacity: 1 },
});

const pulse = keyframes({
  '0%, 100%': { opacity: 1 },
  '50%': { opacity: 0.5 },
});

const bounce = keyframes({
  '0%, 100%': { transform: 'translateY(0)' },
  '50%': { transform: 'translateY(-10px)' },
});

// Styled Components
const DashboardContainer = styled('div', {
  minHeight: '100vh',
  display: 'flex',
  background: '#F8FAFC',
  fontFamily: '$body',
});

const SidebarOverlay = styled('div', {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.4)',
  backdropFilter: 'blur(4px)',
  zIndex: 100,
  animation: `${fadeIn} 0.2s ease-out`,
  '@md': { display: 'none' },
});

const Sidebar = styled('aside', {
  position: 'fixed',
  left: 0,
  top: 0,
  height: '100vh',
  width: '280px',
  background: 'white',
  borderRight: '1px solid #E2E8F0',
  padding: '32px 16px',
  display: 'flex',
  flexDirection: 'column',
  zIndex: 110,
  transition: 'transform 0.3s ease-in-out',
  variants: {
    isOpen: {
      true: { transform: 'translateX(0)' },
      false: { transform: 'translateX(-100%)' },
    },
  },
  '@md': {
    width: '256px',
    transform: 'translateX(0)',
    zIndex: 50,
  },
});

const Brand = styled('div', {
  fontSize: '24px',
  fontWeight: 'bold',
  color: '#F97316',
  fontFamily: '$heading',
  letterSpacing: '-0.05em',
  marginBottom: '40px',
  paddingX: '16px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
});

const CloseButton = styled('button', {
  background: 'none',
  border: 'none',
  color: '#64748B',
  cursor: 'pointer',
  padding: '4px',
  '@md': { display: 'none' },
});

const UserProfile = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  paddingX: '16px',
  marginBottom: '32px',
});

const AvatarWrapper = styled('div', {
  position: 'relative',
});

const Avatar = styled('img', {
  width: '44px',
  height: '44px',
  borderRadius: 'full',
  border: '2px solid rgba(249, 115, 22, 0.2)',
  objectFit: 'cover',
});

const StatusDot = styled('div', {
  position: 'absolute',
  bottom: 0,
  right: 0,
  width: '12px',
  height: '12px',
  background: '#22C55E',
  border: '2px solid white',
  borderRadius: 'full',
});

const UserInfo = styled('div', {
  display: 'flex',
  flexDirection: 'column',
});

const UserName = styled('p', {
  fontSize: '14px',
  fontWeight: 'bold',
  color: '#0F172A',
});

const UserRole = styled('p', {
  fontSize: '10px',
  fontWeight: 'bold',
  color: '#64748B',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
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
  fontWeight: 'bold',
  color: '#64748B',
  transition: 'all 0.2s',
  cursor: 'pointer',
  textDecoration: 'none',
  '&:hover': {
    background: '#F8FAFC',
    color: '#0F172A',
  },
  variants: {
    active: {
      true: {
        background: '#FFF7ED',
        color: '#F97316',
        borderRight: '4px solid #F97316',
      },
    },
  },
});

const SidebarFooter = styled('div', {
  paddingTop: '24px',
  borderTop: '1px solid #E2E8F0',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
});

const Header = styled('header', {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  height: '64px',
  background: 'rgba(255, 255, 255, 0.8)',
  backdropFilter: 'blur(12px)',
  borderBottom: '1px solid #E2E8F0',
  padding: '0 16px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  zIndex: 40,
  '@md': { 
    left: '256px', 
    padding: '0 32px' 
  },
});

const MenuButton = styled('button', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '40px',
  height: '40px',
  background: 'none',
  border: 'none',
  color: '#64748B',
  cursor: 'pointer',
  '@md': { display: 'none' },
});

const ActiveBadge = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  background: '#FFF7ED',
  padding: '4px 10px',
  borderRadius: 'full',
  border: '1px solid #FFEDD5',
  '@sm': { gap: '8px', padding: '6px 12px' },
});

const PulseDot = styled('span', {
  width: '8px',
  height: '8px',
  borderRadius: 'full',
  background: '#F97316',
  animation: `${pulse} 2s infinite`,
});

const HeaderActions = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  '@md': { gap: '24px' },
});

const OnlineToggle = styled('div', {
  display: 'none',
  alignItems: 'center',
  gap: '12px',
  background: '#F1F5F9',
  padding: '6px 12px',
  borderRadius: 'full',
  '@sm': { display: 'flex' },
});

const ToggleSwitch = styled('button', {
  width: '32px',
  height: '16px',
  borderRadius: 'full',
  position: 'relative',
  cursor: 'pointer',
  border: 'none',
  transition: 'all 0.2s',
  variants: {
    online: {
      true: { background: '#F97316' },
      false: { background: '#CBD5E1' },
    },
  },
});

const ToggleHandle = styled('div', {
  position: 'absolute',
  top: '2px',
  width: '12px',
  height: '12px',
  background: 'white',
  borderRadius: 'full',
  transition: 'all 0.2s',
  variants: {
    online: {
      true: { right: '2px' },
      false: { left: '2px' },
    },
  },
});

const Main = styled('main', {
  marginLeft: 0,
  padding: '80px 16px 40px',
  flex: 1,
  '@md': { 
    marginLeft: '256px',
    padding: '96px 32px 48px',
  },
});

const ContentWrapper = styled('div', {
  maxWidth: '1400px',
  margin: '0 auto',
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
  '@lg': { 
    display: 'grid',
    gridTemplateColumns: 'repeat(12, 1fr)',
    gap: '32px',
  },
});

const LeftCol = styled('div', {
  gridColumn: 'span 12',
  '@lg': { gridColumn: 'span 8' },
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
  '@md': { gap: '32px' },
});

const RightCol = styled('div', {
  gridColumn: 'span 12',
  '@lg': { gridColumn: 'span 4' },
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
  '@md': { gap: '32px' },
});

const StatsGrid = styled('section', {
  display: 'flex',
  gap: '16px',
  overflowX: 'auto',
  paddingBottom: '8px',
  scrollbarWidth: 'none',
  '&::-webkit-scrollbar': { display: 'none' },
  '@md': { 
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '24px',
    overflowX: 'visible',
    paddingBottom: 0,
  },
});

const StatCard = styled('div', {
  background: 'white',
  borderRadius: '16px',
  padding: '20px',
  border: '1px solid #E2E8F0',
  boxShadow: '0 2px 12px -2px rgba(0, 0, 0, 0.04)',
  minWidth: '240px',
  flexShrink: 0,
  '@md': { 
    padding: '24px',
    minWidth: 'auto',
  },
});

const StatHeader = styled('div', {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '16px',
});

const StatLabel = styled('span', {
  fontSize: '12px',
  fontWeight: 'bold',
  color: '#64748B',
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
});

const StatIcon = styled('div', {
  width: '40px',
  height: '40px',
  borderRadius: '12px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  variants: {
    type: {
      orange: { background: '#FFF7ED', color: '#F97316' },
      blue: { background: '#EFF6FF', color: '#3B82F6' },
      green: { background: '#F0FDF4', color: '#16A34A' },
    },
  },
});

const StatValue = styled('h2', {
  fontSize: '30px',
  fontWeight: 'bold',
  fontFamily: '$heading',
});

const StatTrend = styled('div', {
  fontSize: '11px',
  fontWeight: 'bold',
  marginTop: '8px',
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
});

const ActiveRequestCard = styled('section', {
  background: 'white',
  borderRadius: '24px',
  padding: '20px',
  border: '1px solid #E2E8F0',
  boxShadow: '0 2px 12px -2px rgba(0, 0, 0, 0.04)',
  position: 'relative',
  overflow: 'hidden',
  '@md': { padding: '32px' },
});

const CardHeader = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  marginBottom: '24px',
  '@sm': {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px',
  },
});

const CardTitle = styled('h3', {
  fontSize: '20px',
  fontWeight: 'bold',
  fontFamily: '$heading',
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  '@md': { fontSize: '24px' },
});

const StatusPill = styled('span', {
  fontSize: '10px',
  fontWeight: '900',
  padding: '6px 16px',
  borderRadius: 'full',
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
  border: '1px solid',
  width: 'fit-content',
  variants: {
    status: {
      enRoute: { background: '#FFF7ED', color: '#F97316', borderColor: '#FFEDD5' },
      waiting: { background: '#F1F5F9', color: '#64748B', borderColor: '#E2E8F0' },
    },
  },
});

const Grid2Col = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1fr',
  gap: '32px',
  '@md': { 
    gridTemplateColumns: '1fr 1fr',
    gap: '48px',
  },
});

const InfoItem = styled('div', {
  display: 'flex',
  gap: '16px',
  marginBottom: '20px',
  '@md': { 
    gap: '20px',
    marginBottom: '24px',
  },
});

const InfoIcon = styled('div', {
  width: '40px',
  height: '40px',
  borderRadius: '12px',
  background: '#F8FAFC',
  border: '1px solid #E2E8F0',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
  color: '#F97316',
  '@md': {
    width: '48px',
    height: '48px',
    borderRadius: '16px',
  },
});

const InfoLabel = styled('p', {
  fontSize: '10px',
  fontWeight: '900',
  color: '#64748B',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  marginBottom: '4px',
});

const InfoValue = styled('p', {
  fontSize: '14px',
  fontWeight: 'bold',
  color: '#0F172A',
  lineHeight: '1.2',
  '@md': { fontSize: '16px' },
});

const DeliveryTimeline = styled('div', {
  position: 'relative',
  paddingLeft: '40px',
  display: 'flex',
  flexDirection: 'column',
  gap: '32px',
  '@md': { gap: '40px' },
  '&::before': {
    content: '""',
    position: 'absolute',
    left: '16px',
    top: '4px',
    bottom: '4px',
    width: '4px',
    background: '#F1F5F9',
    borderRadius: 'full',
  },
});

const TimelineStep = styled('div', {
  position: 'relative',
});

const StepIcon = styled('div', {
  position: 'absolute',
  left: '-32px',
  width: '24px',
  height: '24px',
  borderRadius: 'full',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1,
  variants: {
    active: {
      true: { background: '#F97316', boxShadow: '0 0 0 4px #FFF7ED' },
      false: { background: '#E2E8F0', boxShadow: '0 0 0 4px #F8FAFC' },
    },
  },
});

const StepTitle = styled('p', {
  fontSize: '14px',
  fontWeight: 'bold',
  variants: {
    active: {
      true: { color: '#F97316' },
      false: { color: '#64748B' },
    },
  },
});

const StepTime = styled('p', {
  fontSize: '11px',
  fontWeight: '500',
  color: '#64748B',
});

const ActionButton = styled('button', {
  flex: 1,
  background: '#F97316',
  color: 'white',
  fontWeight: 'bold',
  padding: '16px 0',
  borderRadius: '16px',
  border: 'none',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '8px',
  boxShadow: '0 10px 15px -3px rgba(249, 115, 22, 0.2)',
  transition: 'all 0.2s',
  '&:hover': { background: '#EA580C' },
});

const MapCard = styled('div', {
  background: 'white',
  borderRadius: '24px',
  border: '1px solid #E2E8F0',
  overflow: 'hidden',
  boxShadow: '0 2px 12px -2px rgba(0, 0, 0, 0.04)',
});

const MapPlaceholder = styled('div', {
  height: '224px',
  background: '#F1F5F9',
  position: 'relative',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
});

const MapImage = styled('img', {
  width: '100%',
  height: '100%',
  objectFit: 'cover',
  filter: 'grayscale(0.6)',
  opacity: 0.6,
});

const MapMarker = styled('div', {
  position: 'absolute',
  width: '40px',
  height: '40px',
  background: '#F97316',
  borderRadius: 'full',
  border: '4px solid white',
  boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
  animation: `${bounce} 2s infinite`,
});

const MapOverlay = styled('div', {
  position: 'absolute',
  bottom: '16px',
  left: '16px',
  right: '16px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
});

const LocationBadge = styled('span', {
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(4px)',
  padding: '6px 12px',
  borderRadius: 'full',
  fontSize: '10px',
  fontWeight: 'bold',
  border: '1px solid #E2E8F0',
});

const InventorySection = styled('div', {
  padding: '24px',
});

const InventoryItem = styled('div', {
  marginBottom: '20px',
});

const InventoryLabel = styled('div', {
  display: 'flex',
  justifyContent: 'space-between',
  fontSize: '11px',
  fontWeight: 'bold',
  marginBottom: '8px',
});

const ProgressBar = styled('div', {
  height: '8px',
  background: '#F1F5F9',
  borderRadius: 'full',
  overflow: 'hidden',
});

const ProgressFill = styled('div', {
  height: '100%',
  borderRadius: 'full',
  variants: {
    type: {
      orange: { background: '#F97316' },
      blue: { background: '#3B82F6' },
      purple: { background: '#A855F7' },
    },
  },
});

const PendingSection = styled('section', {
  marginTop: '32px',
});

const RequestCard = styled('div', {
  background: 'white',
  borderRadius: '16px',
  padding: '20px',
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
  border: '1px solid #E2E8F0',
  boxShadow: '0 2px 12px -2px rgba(0, 0, 0, 0.04)',
  marginBottom: '16px',
  transition: 'all 0.2s',
  '&:hover': { borderColor: 'rgba(249, 115, 22, 0.3)' },
  '@sm': {
    padding: '24px',
    flexDirection: 'row',
    alignItems: 'center',
    gap: '24px',
  },
});

const CustomerAvatar = styled('img', {
  width: '56px',
  height: '56px',
  borderRadius: 'full',
  objectFit: 'cover',
  ring: '2px solid #F1F5F9',
  '@sm': {
    width: '64px',
    height: '64px',
  },
});

const RequestActions = styled('div', {
  display: 'flex',
  gap: '12px', 
  width: '100%',
  '@sm': {
    flexDirection: 'column',
    gap: '8px',
    minWidth: '120px',
    width: 'auto',
  },
});

const AcceptBtn = styled('button', {
  flex: 1,
  background: '#F97316',
  color: 'white', 
  fontWeight: 'bold',
  fontSize: '14px',
  padding: '12px 0',
  borderRadius: '12px',
  border: 'none',
  cursor: 'pointer',
  '&:hover': { background: '#EA580C' },
  '@sm': { padding: '10px 0' },
});

const DeclineBtn = styled('button', {
  flex: 1,
  background: 'transparent', 
  color: '#64748B',
  fontWeight: 'bold',
  fontSize: '14px',
  padding: '12px 0',
  borderRadius: '12px',
  border: '1px solid #E2E8F0',
  cursor: 'pointer',
  '&:hover': { background: '#F8FAFC' },
  '@sm': { 
    padding: '10px 0',
    border: '1px solid transparent',
  },
});

const EarningsBreakdown = styled('div', {
  background: 'white', 
  borderRadius: '24px',
  padding: '24px', 
  border: '1px solid #E2E8F0',
});

const BreakDownItem = styled('div', {
  display: 'flex', 
  justifyContent: 'space-between',
  alignItems: 'center',
  paddingBottom: '16px',
  marginBottom: '16px',
  borderBottom: '1px solid #F8FAFC',
  '&:last-child': { borderBottom: 'none', marginBottom: 0, paddingBottom: 0 },
});

const IconButton = styled('button', {
  background: 'none',
  border: 'none',
  color: '#64748B',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '4px',
  variants: {
    hideMobile: {
      true: {
        display: 'none',
        '@sm': { display: 'flex' },
      },
    },
  },
});

const FuelDeliveryHomepage = () => {
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeRequest, setActiveRequest] = useState(null);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [stats, setStats] = useState({
    todayJobs: 12,
    deliveredLiters: 420,
    earnings: 114.50
  });
  const [agentProfile, setAgentProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const agentId = localStorage.getItem('workerId');
  const token = localStorage.getItem('workerToken');

  const fetchData = useCallback(async () => {
    if (!agentId || !token) {
      navigate('/worker/car/fuel-delivery/login');
      return;
    }

    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [profileRes, activeRes, queueRes, statsRes] = await Promise.all([
        api.get(`/api/fuel-delivery/agent/${agentId}/status`, { headers }),
        api.get(`/api/fuel-delivery/active-delivery/${agentId}`, { headers }),
        api.get(`/api/fuel-delivery/queue/available?agent_id=${agentId}`, { headers }),
        api.get(`/api/fuel-delivery/agent/${agentId}/active-jobs`, { headers })
      ]);

      if (profileRes.data.success) {
        setAgentProfile(profileRes.data.agent);
        setIsOnline(profileRes.data.agent.online_status === 'ONLINE_AVAILABLE');
      }

      if (activeRes.data.success) {
        setActiveRequest(activeRes.data.delivery);
      }

      if (queueRes.data.success) {
        setPendingRequests(queueRes.data.requests || []);
      }

      if (statsRes.data.success) {
        setStats(prev => ({
          ...prev,
          todayJobs: statsRes.data.jobsAccepted || 0,
          earnings: statsRes.data.earnings || 0
        }));
      }

    } catch (error) {
      console.error('Error fetching fuel delivery data:', error);
    } finally {
      setLoading(false);
    }
  }, [agentId, token, navigate]);

  useEffect(() => {
    fetchData();

    const socket = io(import.meta.env.VITE_API_URL);
    socket.emit('join_room', { worker_id: agentId, worker_type: 'fuel_delivery' });

    socket.on('new_fuel_request', (request) => {
      setPendingRequests(prev => [request, ...prev]);
    });

    return () => socket.disconnect();
  }, [fetchData, agentId]);

  const handleToggleStatus = async () => {
    try {
      const newStatus = isOnline ? 'OFFLINE' : 'ONLINE_AVAILABLE';
      const res = await api.post('/api/fuel-delivery/status', {
        agent_id: agentId,
        status: newStatus
      }, { headers: { Authorization: `Bearer ${token}` } });

      if (res.data.success) {
        setIsOnline(!isOnline);
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const handleAcceptRequest = async (requestId) => {
    try {
      const res = await api.post('/api/fuel-delivery/queue/assign', {
        agent_id: agentId,
        request_id: requestId
      }, { headers: { Authorization: `Bearer ${token}` } });

      if (res.data.success) {
        fetchData(); // Refresh to show active request
      }
    } catch (error) {
      console.error('Error accepting request:', error);
    }
  };

  const handleMarkDelivered = async () => {
    if (!activeRequest) return;
    try {
      const res = await api.post('/api/fuel-delivery/delivery/complete', {
        agent_id: agentId,
        request_id: activeRequest.request_id
      }, { headers: { Authorization: `Bearer ${token}` } });

      if (res.data.success) {
        setActiveRequest(null);
        fetchData();
      }
    } catch (error) {
      console.error('Error completing delivery:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <DashboardContainer>
      {isSidebarOpen && <SidebarOverlay onClick={() => setIsSidebarOpen(false)} />}
      
      <Sidebar isOpen={isSidebarOpen}>
        <Brand>
          ExpertEase
          <CloseButton onClick={() => setIsSidebarOpen(false)}>
            <X size={24} />
          </CloseButton>
        </Brand>
        <UserProfile>
          <AvatarWrapper>
            <Avatar src="https://lh3.googleusercontent.com/aida-public/AB6AXuD2VMj4J0o2tp1cSVO_WiqEDqfCFikVF8HAw6ffDObLVp-0GX5wrH8rZMUp74AbBT422jO6-bauy0j_Ygpm3vf-zrlaeRoAD0Sb494Vc3aCtPp6JCfF4Ylo5b71a37wBIOVdY_CZ1bk-14-N2M2arnA-zhG6zfh6jw_T1Z0txePwVS41lSupL2ISjI1Fahrk7s4Qi1TA8XpONm5kJlAxt1Ds82SQb6JZFHhPWdBg7886eu3o9AANCloCI_lWsUQJ7x9e9WaGctZwrNo" alt="Arjun Sharma" />
            <StatusDot />
          </AvatarWrapper>
          <UserInfo>
            <UserName>{agentProfile?.name || 'Arjun Sharma'}</UserName>
            <UserRole>Fuel Expert</UserRole>
          </UserInfo>
        </UserProfile>

        <Nav>
          <NavItem active onClick={() => setIsSidebarOpen(false)}><LayoutDashboard size={20} />Dashboard</NavItem>
          <NavItem onClick={() => setIsSidebarOpen(false)}><ListChecks size={20} />Jobs Queue</NavItem>
          <NavItem onClick={() => setIsSidebarOpen(false)}><Wallet size={20} />Earnings</NavItem>
          <NavItem onClick={() => setIsSidebarOpen(false)}><History size={20} />History</NavItem>
          <NavItem onClick={() => setIsSidebarOpen(false)}><Settings size={20} />Settings</NavItem>
        </Nav>

        <SidebarFooter>
          <NavItem onClick={() => setIsSidebarOpen(false)}><HelpCircle size={20} />Support</NavItem>
          <NavItem onClick={() => { localStorage.clear(); navigate('/worker/car/services'); }}><LogOut size={20} />Logout</NavItem>
        </SidebarFooter>
      </Sidebar>

      <Header>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <MenuButton onClick={() => setIsSidebarOpen(true)}>
            <Menu size={24} />
          </MenuButton>
          <ActiveBadge>
            <PulseDot />
            <span style={{ fontSize: '10px', fontWeight: '900', color: '#F97316', textTransform: 'uppercase' }}>Active Duty</span>
          </ActiveBadge>
        </div>

        <HeaderActions>
          <OnlineToggle>
            <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#64748B' }}>Online</span>
            <ToggleSwitch online={isOnline} onClick={handleToggleStatus}>
              <ToggleHandle online={isOnline} />
            </ToggleSwitch>
          </OnlineToggle>
          <IconButton><Bell size={20} /></IconButton>
          <IconButton hideMobile><MessageSquare size={20} /></IconButton>
        </HeaderActions>
      </Header>

      <Main>
        <ContentWrapper>
          <LeftCol>
            <StatsGrid>
              <StatCard>
                <StatHeader>
                  <StatLabel>Today's Jobs</StatLabel>
                  <StatIcon type="orange"><Fuel size={20} /></StatIcon>
                </StatHeader>
                <StatValue>{stats.todayJobs}</StatValue>
                <StatTrend style={{ color: '#16A34A' }}><TrendingUp size={14} /> +15% vs Average</StatTrend>
              </StatCard>

              <StatCard>
                <StatHeader>
                  <StatLabel>Delivered</StatLabel>
                  <StatIcon type="blue"><Droplet size={20} /></StatIcon>
                </StatHeader>
                <StatValue>{stats.deliveredLiters}L</StatValue>
                <StatTrend style={{ color: '#64748B' }}>Target: 500L today</StatTrend>
              </StatCard>

              <StatCard>
                <StatHeader>
                  <StatLabel>Earnings</StatLabel>
                  <StatIcon type="green"><Wallet size={20} /></StatIcon>
                </StatHeader>
                <StatValue>₹{stats.earnings}</StatValue>
                <StatTrend style={{ color: '#16A34A' }}><CheckCircle size={14} /> Payments Verified</StatTrend>
              </StatCard>
            </StatsGrid>

            <ActiveRequestCard>
              <CardHeader>
                <CardTitle><Truck size={24} color="#F97316" /> Active Delivery Request</CardTitle>
                <StatusPill status={activeRequest ? "enRoute" : "waiting"}>
                  {activeRequest ? "En Route" : "No Active Order"}
                </StatusPill>
              </CardHeader>

              {activeRequest ? (
                <Grid2Col>
                  <div>
                    <InfoItem>
                      <InfoIcon><MapPin size={20} /></InfoIcon>
                      <div>
                        <InfoLabel>Delivery Location</InfoLabel>
                        <InfoValue>{activeRequest.delivery_address}</InfoValue>
                        <p style={{ fontSize: '12px', fontWeight: 'bold', color: '#F97316', marginTop: '6px' }}>ETA: 8 mins (2.4 miles)</p>
                      </div>
                    </InfoItem>

                    <InfoItem>
                      <InfoIcon><Fuel size={20} /></InfoIcon>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <div>
                            <InfoLabel>Fuel Details</InfoLabel>
                            <InfoValue>{activeRequest.fuel_type} (XP95)</InfoValue>
                          </div>
                          <div style={{ textAlign: 'right' }}>
                            <InfoLabel>Quantity</InfoLabel>
                            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#F97316' }}>{activeRequest.quantity_liters} Liters</p>
                          </div>
                        </div>
                      </div>
                    </InfoItem>

                    <div style={{ display: 'flex', gap: '16px', marginTop: '24px' }}>
                      <ActionButton onClick={handleMarkDelivered}>
                        <CheckCircle size={20} /> Mark Delivered
                      </ActionButton>
                      <button style={{ width: '64px', height: '64px', borderRadius: '16px', background: 'white', border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748B' }}>
                        <Navigation size={24} />
                      </button>
                    </div>
                  </div>

                  <div>
                    <InfoLabel style={{ marginBottom: '24px' }}>Delivery Progress</InfoLabel>
                    <DeliveryTimeline>
                      <TimelineStep>
                        <StepIcon active><CheckCircle size={14} color="white" /></StepIcon>
                        <StepTitle active>Accepted</StepTitle>
                        <StepTime>10:42 AM • Order confirmed</StepTime>
                      </TimelineStep>
                      <TimelineStep>
                        <StepIcon active={activeRequest.status === 'ARRIVING' || activeRequest.status === 'DELIVERING'}><Truck size={14} color="white" /></StepIcon>
                        <StepTitle active={activeRequest.status === 'ARRIVING' || activeRequest.status === 'DELIVERING'}>En Route</StepTitle>
                        <StepTime>10:48 AM • Approaching destination</StepTime>
                      </TimelineStep>
                      <TimelineStep>
                        <StepIcon active={activeRequest.status === 'COMPLETED'} />
                        <StepTitle active={activeRequest.status === 'COMPLETED'}>Delivered</StepTitle>
                        <StepTime>Estimated in 8 mins</StepTime>
                      </TimelineStep>
                    </DeliveryTimeline>
                  </div>
                </Grid2Col>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px 0' }}>
                  <Info size={48} color="#CBD5E1" style={{ marginBottom: '16px' }} />
                  <p style={{ fontWeight: 'bold', color: '#64748B' }}>No active delivery request at the moment.</p>
                </div>
              )}
            </ActiveRequestCard>

            <PendingSection>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
                <div>
                  <h3 style={{ fontSize: '24px', fontWeight: 'bold', fontFamily: 'Space Grotesk' }}>Pending Requests</h3>
                  <p style={{ fontSize: '14px', color: '#64748B', marginTop: '4px' }}>Nearby customers awaiting fuel assistance</p>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {['Petrol', 'Diesel', 'Premium'].map(type => (
                    <span key={type} style={{ padding: '4px 12px', background: 'white', border: '1px solid #E2E8F0', borderRadius: '8px', fontSize: '11px', fontWeight: 'bold', color: '#64748B', cursor: 'pointer' }}>{type}</span>
                  ))}
                </div>
              </div>

              {pendingRequests.length > 0 ? pendingRequests.map((req, idx) => (
                <RequestCard key={req.id || idx}>
                  <CustomerAvatar src={`https://i.pravatar.cc/150?u=${req.user_id}`} alt={req.user_name} />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <h4 style={{ fontSize: '18px', fontWeight: 'bold' }}>{req.user_name}</h4>
                      <span style={{ background: '#FEF2F2', color: '#DC2626', fontSize: '10px', fontWeight: '900', padding: '4px 12px', borderRadius: 'full', border: '1px solid #FEE2E2' }}>URGENT</span>
                    </div>
                    <p style={{ fontSize: '12px', color: '#64748B', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <MapPin size={14} /> 2.4 km away • {req.address || 'Location Area'}
                    </p>
                    <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
                      <span style={{ fontSize: '10px', fontWeight: 'bold', background: '#FFF7ED', color: '#F97316', padding: '4px 10px', borderRadius: '6px', border: '1px solid #FFEDD5' }}>{req.quantity}L {req.fuel_type}</span>
                      <span style={{ fontSize: '10px', fontWeight: 'bold', background: '#F8FAFC', color: '#64748B', padding: '4px 10px', borderRadius: '6px', border: '1px solid #E2E8F0' }}>EST. FARE: ₹{req.quantity * 100 + 50}</span>
                    </div>
                  </div>
                  <RequestActions>
                    <AcceptBtn onClick={() => handleAcceptRequest(req.id)}>Accept</AcceptBtn>
                    <DeclineBtn>Decline</DeclineBtn>
                  </RequestActions>
                </RequestCard>
              )) : (
                <div style={{ background: 'white', borderRadius: '16px', padding: '48px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                  <CheckCircle size={48} color="#22C55E" style={{ margin: '0 auto 16px' }} />
                  <p style={{ fontWeight: 'bold' }}>You're all caught up!</p>
                </div>
              )}
            </PendingSection>
          </LeftCol>

          <RightCol>
            <MapCard>
              <MapPlaceholder>
                <MapImage src="https://lh3.googleusercontent.com/aida-public/AB6AXuCt2jKHoip433eICO3oak5cNghrauuBeTIklkYahhSJyyWvdv-JlrmWBjApUU2KVQszZ06QBM-UiCwmj1Wmo-6NqsenAKuOSOoQwOZupvmoajLO0OzqxVCuQrXuxXrJtzCxhTxloelpB4l9AjG2-mGjx0U3mu1c4lVzv7wwFsE8wBacCGX-NzPlUNA55DVG1Ep-EfYabwlD4ArW5qBAkeHoEEJQD8IwEyiku9LTsD8mtcGEe_UGzJ4v0ZPCOoMGV-wDEHv2Kb1m_-jD" alt="Map" />
                <MapMarker><Truck size={16} /></MapMarker>
                <MapOverlay>
                  <LocationBadge>Sector 62, Austin</LocationBadge>
                  <button style={{ width: '32px', height: '32px', borderRadius: 'full', background: 'white', border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
                    <MapPin size={14} />
                  </button>
                </MapOverlay>
              </MapPlaceholder>
              <InventorySection>
                <h4 style={{ fontSize: '10px', fontWeight: '900', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '24px' }}>Active Fuel Inventory</h4>
                <InventoryItem>
                  <InventoryLabel>
                    <span>Petrol (91 Octane)</span>
                    <span style={{ color: '#F97316' }}>120L / 500L</span>
                  </InventoryLabel>
                  <ProgressBar><ProgressFill type="orange" style={{ width: '24%' }} /></ProgressBar>
                </InventoryItem>
                <InventoryItem>
                  <InventoryLabel>
                    <span>Diesel (BS-VI)</span>
                    <span style={{ color: '#3B82F6' }}>380L / 500L</span>
                  </InventoryLabel>
                  <ProgressBar><ProgressFill type="blue" style={{ width: '76%' }} /></ProgressBar>
                </InventoryItem>
                <InventoryItem>
                  <InventoryLabel>
                    <span>Premium (XP100)</span>
                    <span style={{ color: '#A855F7' }}>45L / 100L</span>
                  </InventoryLabel>
                  <ProgressBar><ProgressFill type="purple" style={{ width: '45%' }} /></ProgressBar>
                </InventoryItem>
                <button style={{ width: '100%', marginTop: '24px', padding: '12px 0', background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold', color: '#64748B', cursor: 'pointer' }}>Refill Tank Request</button>
              </InventorySection>
            </MapCard>

            <EarningsBreakdown>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'Space Grotesk', marginBottom: '24px' }}>Earnings Breakdown</h3>
              <BreakDownItem>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '12px', background: '#FFF7ED', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#F97316' }}><Fuel size={18} /></div>
                  <span style={{ fontSize: '14px', fontWeight: '600' }}>Fuel Surcharge</span>
                </div>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>₹74.00</span>
              </BreakDownItem>
              <BreakDownItem>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '12px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#3B82F6' }}><Navigation size={18} /></div>
                  <span style={{ fontSize: '14px', fontWeight: '600' }}>Travel Pay</span>
                </div>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>₹22.50</span>
              </BreakDownItem>
              <BreakDownItem>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '12px', background: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16A34A' }}><Zap size={18} /></div>
                  <span style={{ fontSize: '14px', fontWeight: '600' }}>Tips</span>
                </div>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>₹18.00</span>
              </BreakDownItem>

              <div style={{ background: '#FFF7ED', padding: '16px', borderRadius: '16px', marginTop: '24px', border: '1px solid #FFEDD5' }}>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <Clock size={16} color="#F97316" style={{ marginTop: '2px' }} />
                  <p style={{ fontSize: '11px', color: '#9A3412', lineHeight: '1.5' }}>
                    Next payout scheduled for <span style={{ fontWeight: 'bold' }}>Monday, 24th Oct</span>. Funds will be transferred to your linked bank account.
                  </p>
                </div>
              </div>
            </EarningsBreakdown>
          </RightCol>
        </ContentWrapper>
      </Main>
    </DashboardContainer>
  );
};

export default FuelDeliveryHomepage;
