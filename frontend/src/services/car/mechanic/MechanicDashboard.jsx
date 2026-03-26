import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';
import { 
  styled, 
  css, 
  keyframes 
} from '../../../stitches.config';
import api from '../../../shared/api';
import { 
  LayoutDashboard, 
  ListChecks, 
  Wallet, 
  History, 
  Settings, 
  HelpCircle, 
  LogOut, 
  Search, 
  Bell, 
  Star, 
  CheckCircle2, 
  Zap, 
  ArrowRight,
  Plus,
  Clock,
  MapPin,
  Car as CarIcon,
  Wrench,
  ClipboardList,
  User as UserIcon,
  Package,
  FileEdit,
  CheckCircle,
  X,
  ChevronRight
} from 'lucide-react';

// Animations
const pulse = keyframes({
  '0%, 100%': { opacity: 1 },
  '50%': { opacity: 0.5 },
});

const slideIn = keyframes({
  from: { transform: 'translateY(20px)', opacity: 0 },
  to: { transform: 'translateY(0)', opacity: 1 },
});

const fadeIn = keyframes({
  from: { opacity: 0, transform: 'translateY(10px)' },
  to: { opacity: 1, transform: 'translateY(0)' },
});

// Styled Components
const DashboardContainer = styled('div', {
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  background: '$background',
});

const TopNav = styled('header', {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  height: '64px',
  background: 'rgba(255, 255, 255, 0.85)',
  backdropFilter: 'blur(12px)',
  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  paddingX: '$6',
  zIndex: 100,
});

const Brand = styled('div', {
  color: '#7c3aed',
  fontFamily: '$heading',
  fontWeight: 'bold',
  fontSize: '22px',
});

const SearchContainer = styled('div', {
  display: 'none',
  '@md': {
    display: 'flex',
    alignItems: 'center',
    background: '#f2f4f6',
    borderRadius: '$full',
    padding: '8px 16px',
    width: '320px',
    marginLeft: '$8',
  },
});

const SearchInput = styled('input', {
  background: 'transparent',
  border: 'none',
  marginLeft: '$2',
  fontSize: '14px',
  width: '100%',
  '&:focus': { outline: 'none' },
});

const NavRight = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '$4',
});

const StatusToggle = styled('button', {
  display: 'flex',
  alignItems: 'center',
  gap: '$2',
  padding: '6px 12px',
  borderRadius: '$full',
  border: 'none',
  cursor: 'pointer',
  fontWeight: 600,
  fontSize: '12px',
  transition: 'all 0.2s',
  variants: {
    online: {
      true: { background: '#e8fdf5', color: '#005952' },
      false: { background: '#f1f5f9', color: '#64748b' },
    },
  },
});

const Avatar = styled('div', {
  width: '36px',
  height: '36px',
  borderRadius: '$full',
  background: '$blueGradient',
  color: 'white',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontWeight: 'bold',
  fontSize: '14px',
});

const LayoutBody = styled('div', {
  display: 'flex',
  marginTop: '64px',
  flex: 1,
});

const Sidebar = styled('aside', {
  display: 'none',
  '@lg': {
    display: 'flex',
    flexDirection: 'column',
    width: '256px',
    background: '#f8fafc',
    height: 'calc(100vh - 64px)',
    position: 'sticky',
    top: '64px',
    padding: '$6',
  },
});

const SidebarProfile = styled('div', {
  marginBottom: '$8',
});

const ProfileName = styled('h3', {
  fontFamily: '$heading',
  fontWeight: 'bold',
  fontSize: '18px',
  color: '$textPrimary',
});

const ProfileRole = styled('p', {
  fontSize: '14px',
  color: '$textSecondary',
});

const NavItem = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
  padding: '12px 16px',
  borderRadius: '$lg',
  cursor: 'pointer',
  fontSize: '14px',
  color: '$textSecondary',
  transition: 'all 0.2s',
  '&:hover': {
    color: '$primary',
    transform: 'translateX(4px)',
  },
  variants: {
    active: {
      true: {
        background: 'white',
        color: '$primary',
        boxShadow: '$sm',
        fontWeight: 600,
      },
    },
    logout: {
      true: {
        color: '#ba1a1a',
        marginTop: 'auto',
        '&:hover': {
          color: '#ba1a1a',
          background: 'rgba(186, 26, 26, 0.05)',
        },
      },
    },
  },
});

const MainContent = styled('main', {
  flex: 1,
  padding: '20px',
  background: '#f2f4f6',
  '@md': { padding: '40px' },
});

const WelcomeSection = styled('div', {
  marginBottom: '$10',
});

const Title = styled('h1', {
  fontFamily: '$heading',
  fontSize: '36px',
  fontWeight: 'bold',
  color: '#191c1e',
  marginBottom: '$2',
});

const Subtitle = styled('p', {
  color: '#4a4455',
  fontSize: '16px',
});

const StatsGrid = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1fr',
  gap: '$6',
  marginBottom: '$10',
  '@sm': { gridTemplateColumns: 'repeat(2, 1fr)' },
  '@lg': { gridTemplateColumns: 'repeat(4, 1fr)' },
});

const StatCard = styled('div', {
  background: 'white',
  borderRadius: '$lg',
  padding: '$6',
  transition: 'all 0.2s',
  '&:hover': { transform: 'translateY(-2px)' },
});

const StatHeader = styled('div', {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '$4',
});

const IconBox = styled('div', {
  width: '40px',
  height: '40px',
  borderRadius: '$md',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
});

const Badge = styled('span', {
  fontSize: '12px',
  fontWeight: 'bold',
});

const StatLabel = styled('p', {
  fontSize: '14px',
  color: '$textSecondary',
  marginBottom: '$1',
});

const StatValue = styled('h4', {
  fontFamily: '$heading',
  fontSize: '24px',
  fontWeight: 'bold',
  color: '#191c1e',
});

const MainGrid = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1fr',
  gap: '$6',
  '@lg': { gridTemplateColumns: '2fr 1fr' },
});

const LeftCol = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  gap: '$6',
});

const ActiveJobCard = styled('div', {
  background: 'white',
  borderRadius: '$xl',
  padding: '32px',
  position: 'relative',
  overflow: 'hidden',
  boxShadow: '$sm',
  animation: `${slideIn} 0.4s ease-out`,
});

const DecorativeBlob = styled('div', {
  position: 'absolute',
  top: 0,
  right: 0,
  width: '128px',
  height: '128px',
  background: 'rgba(124, 58, 237, 0.05)',
  borderBottomLeftRadius: '100%',
});

const JobBadge = styled('span', {
  background: '$primary',
  color: 'white',
  padding: '4px 12px',
  borderRadius: '$full',
  fontSize: '12px',
  fontWeight: 'bold',
  letterSpacing: '0.05em',
});

const ToolsGrid = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1fr',
  gap: '$6',
  '@md': { gridTemplateColumns: '1fr 1fr' },
});

const ToolCard = styled('div', {
  background: 'rgba(255, 255, 255, 0.5)',
  backdropFilter: 'blur(8px)',
  border: '1px solid rgba(255, 255, 255, 0.5)',
  borderRadius: '$lg',
  padding: '$6',
});

const QueueCard = styled('div', {
  background: 'white',
  borderRadius: '$xl',
  padding: '$5',
  borderLeft: '4px solid #e2e8f0',
  boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  marginBottom: '$4',
  variants: {
    urgent: {
      true: { borderLeftColor: '#fd761a' },
    },
  },
});

const ForecastContainer = styled('div', {
  background: 'white',
  borderRadius: '$xl',
  padding: '$6',
});

const ChartArea = styled('div', {
  display: 'flex',
  alignItems: 'flex-end',
  gap: '6px',
  height: '96px',
  marginTop: '$4',
});

const ChartBar = styled('div', {
  flex: 1,
  background: '$primaryDark',
  borderTopLeftRadius: '2px',
  borderTopRightRadius: '2px',
  transition: 'height 0.3s ease',
});

const MobileNav = styled('nav', {
  display: 'flex',
  position: 'fixed',
  bottom: 0,
  left: 0,
  right: 0,
  height: '64px',
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  boxShadow: '0 -4px 10px rgba(0,0,0,0.05)',
  alignItems: 'center',
  justifyContent: 'space-around',
  zIndex: 100,
  '@md': { display: 'none' },
});

const FAB = styled('div', {
  width: '56px',
  height: '56px',
  background: '$primaryDark',
  borderRadius: '$full',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'white',
  marginTop: '-40px',
  border: '4px solid #f7f9fb',
  boxShadow: '0 4px 14px rgba(99, 14, 212, 0.4)',
});

const Toast = styled('div', {
  position: 'fixed',
  bottom: '80px',
  right: '24px',
  padding: '12px 24px',
  borderRadius: '$lg',
  color: 'white',
  fontWeight: 500,
  zIndex: 1000,
  animation: `${fadeIn} 0.3s ease-out`,
  variants: {
    type: {
      success: { background: '#005952' },
      error: { background: '#ba1a1a' },
    },
  },
});

const Skeleton = styled('div', {
  background: '#e2e8f0',
  borderRadius: '$lg',
  animation: `${pulse} 1.5s infinite`,
});

// Helper for time
const timeAgo = (date) => {
  if (!date) return '0m';
  const seconds = Math.floor((new Date() - new Date(date)) / 1000);
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h`;
};

const MechanicDashboard = () => {
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [loading, setLoading] = useState(true);
  const [workerProfile, setWorkerProfile] = useState({
    name: 'Loading...',
    role: 'Mechanic',
    avatar: 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?auto=format&fit=crop&q=80&w=100'
  });
  const [earnings, setEarnings] = useState({
    today_jobs: 0,
    this_week: 0
  });
  const [pendingJobs, setPendingJobs] = useState([]);
  const [activeJob, setActiveJob] = useState(null);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);

  const workerId = localStorage.getItem('workerId');
  const token = localStorage.getItem('workerToken');

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchData = useCallback(async () => {
    if (!token || !workerId) {
      navigate('/worker/car/mechanic/auth');
      return;
    }

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      
      const [profileRes, pendingRes, earningsRes, activeRes, statsRes] = await Promise.all([
        api.get('/api/car/mechanic/profile', { headers }),
        api.get('/api/car/mechanic/jobs', { headers }),
        api.get('/api/car/mechanic/earnings', { headers }),
        api.get('/api/car/mechanic/active-job', { headers }).catch(() => ({ data: { active_job: null } })),
        api.get('/api/car/mechanic/stats', { headers }).catch(() => ({ data: { stats: {} } }))
      ]);

      if (profileRes.data.mechanic) {
        setWorkerProfile(profileRes.data.mechanic);
        setIsOnline(profileRes.data.mechanic.is_online);
      }
      setPendingJobs(pendingRes.data.pending_jobs || []);
      setEarnings(earningsRes.data.earnings || {});
      setActiveJob(activeRes?.data?.active_job || null);

    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [navigate, token, workerId]);

  useEffect(() => {
    fetchData();

    const socket = io(import.meta.env.VITE_API_URL);
    socket.emit('join_room', { worker_id: workerId, worker_type: 'mechanic' });

    socket.on('new_job_request', (job) => {
      setPendingJobs(prev => [job, ...prev]);
      showToast('New job request received!', 'success');
    });

    socket.on('job_cancelled', (data) => {
      setPendingJobs(prev => prev.filter(j => j.id !== data.job_id));
    });

    return () => socket.disconnect();
  }, [fetchData, workerId]);

  const toggleStatus = async () => {
    try {
      const newStatus = !isOnline;
      await api.put('/api/car/mechanic/status', {
        is_online: newStatus
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setIsOnline(newStatus);
      setWorkerProfile(prev => prev ? { ...prev, is_online: newStatus } : null);
      showToast(`You are now ${newStatus ? 'ONLINE' : 'OFFLINE'}`);
    } catch (err) {
      showToast('Failed to update status', 'error');
    }
  };

  const handleAccept = async (jobId) => {
    try {
      await api.post('/api/car/mechanic/job/accept', {
        job_id: jobId
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setPendingJobs(prev => prev.filter(j => j.id !== jobId));
      fetchData(); // Refetch to get updated active job
      showToast('Job accepted!');
    } catch (err) {
      showToast('Failed to accept job', 'error');
    }
  };

  const handleDecline = async (jobId) => {
    try {
      await api.post('/api/car/mechanic/job/reject', {
        job_id: jobId
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setPendingJobs(prev => prev.filter(j => j.id !== jobId));
      showToast('Job declined');
    } catch (err) {
      showToast('Failed to decline job', 'error');
    }
  };

  const handleComplete = async () => {
    if (!activeJob) return;
    try {
      // Backend requires photos and OTP for real completion, 
      // but for this UI we'll try to just mark it as complete
      await api.post('/api/car/mechanic/job/complete', {
        job_id: activeJob.id
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setActiveJob(null);
      fetchData(); // Refetch to update earnings and pending
      showToast('Job completed successfully!');
    } catch (err) {
      // If photos are missing, the backend will return 400
      showToast(err.response?.data?.error || 'Failed to complete job', 'error');
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/worker/car/services');
  };

  if (loading) {
    return (
      <DashboardContainer>
        <TopNav>
          <Brand>ExpertEase</Brand>
        </TopNav>
        <LayoutBody>
          <Sidebar />
          <MainContent>
            <Skeleton css={{ height: '48px', width: '300px', marginBottom: '$4' }} />
            <Skeleton css={{ height: '24px', width: '450px', marginBottom: '$10' }} />
            <StatsGrid>
              {[1, 2, 3, 4].map(i => <Skeleton key={i} css={{ height: '140px' }} />)}
            </StatsGrid>
          </MainContent>
        </LayoutBody>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <TopNav>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Brand>ExpertEase</Brand>
          <SearchContainer>
            <Search size={18} color="#64748b" />
            <SearchInput placeholder="Search jobs or tools..." />
          </SearchContainer>
        </div>
        <NavRight>
          <StatusToggle online={isOnline} onClick={toggleStatus}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              background: isOnline ? '#00a651' : '#64748b' 
            }} />
            {isOnline ? 'ONLINE' : 'OFFLINE'}
          </StatusToggle>
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '8px', color: '#64748b' }}>
            <Bell size={20} />
          </button>
          <Avatar>{workerProfile?.name?.split(' ').map(n => n[0]).join('')}</Avatar>
        </NavRight>
      </TopNav>

      <LayoutBody>
        <Sidebar>
          <SidebarProfile>
            <ProfileName>{workerProfile?.name}</ProfileName>
            <ProfileRole>Mechanic</ProfileRole>
          </SidebarProfile>
          
          <NavItem active><LayoutDashboard size={20} /> Dashboard</NavItem>
          <NavItem onClick={() => navigate('/worker/car/mechanic/jobs-queue')}><ListChecks size={20} /> Jobs Queue</NavItem>
          <NavItem onClick={() => navigate('/worker/car/mechanic/earnings')}><Wallet size={20} /> Earnings</NavItem>
          <NavItem onClick={() => navigate('/worker/car/mechanic/history')}><History size={20} /> History</NavItem>
          <NavItem onClick={() => navigate('/worker/car/mechanic/settings')}><Settings size={20} /> Settings</NavItem>
          
          <NavItem css={{ marginTop: 'auto' }}><HelpCircle size={20} /> Support</NavItem>
          <NavItem logout onClick={handleLogout}><LogOut size={20} /> Logout</NavItem>
        </Sidebar>

        <MainContent>
          {error && (
            <div style={{ background: '#ba1a1a', color: 'white', padding: '12px 20px', borderRadius: '8px', marginBottom: '24px' }}>
              {error}
            </div>
          )}

          <WelcomeSection>
            <Title>Worker Console</Title>
            <Subtitle>
              Good morning, {workerProfile?.name?.split(' ')[0]}. You have {pendingJobs.length} pending requests that need your immediate attention.
            </Subtitle>
          </WelcomeSection>

          <StatsGrid>
            <StatCard>
              <StatHeader>
                <IconBox css={{ background: '#eaddff' }}><Wrench size={20} color="#630ed4" /></IconBox>
                <Badge css={{ color: '#005952' }}>+12% vs last week</Badge>
              </StatHeader>
              <StatLabel>Today's Jobs</StatLabel>
              <StatValue>{earnings.today_jobs || 0}</StatValue>
            </StatCard>

            <StatCard>
              <StatHeader>
                <IconBox css={{ background: '#ffdbca' }}><ClipboardList size={20} color="#9d4300" /></IconBox>
                <Badge css={{ color: pendingJobs.some(j => j.urgency) ? '#ba1a1a' : '#005952' }}>
                  {pendingJobs.some(j => j.urgency) ? 'High Urgency' : 'Incoming'}
                </Badge>
              </StatHeader>
              <StatLabel>Pending Requests</StatLabel>
              <StatValue>{pendingJobs.length.toString().padStart(2, '0')}</StatValue>
            </StatCard>

            <StatCard>
              <StatHeader>
                <IconBox css={{ background: '#89f5e7' }}><Wallet size={20} color="#005952" /></IconBox>
                <Badge css={{ color: '#005952' }}>Paid Out</Badge>
              </StatHeader>
              <StatLabel>Weekly Earnings</StatLabel>
              <StatValue>₹{earnings.this_week?.toLocaleString() || '0'}</StatValue>
            </StatCard>

            <StatCard>
              <StatHeader>
                <IconBox css={{ background: '#eaddff' }}><Star size={20} color="#630ed4" fill="#630ed4" /></IconBox>
                <Badge css={{ color: '#7c3aed' }}>Top Tier</Badge>
              </StatHeader>
              <StatLabel>Worker Rating</StatLabel>
              <StatValue>{workerProfile?.rating || '4.92'} / 5.0</StatValue>
            </StatCard>
          </StatsGrid>

          <MainGrid>
            <LeftCol>
              {activeJob ? (
                <ActiveJobCard>
                  <DecorativeBlob />
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                    <JobBadge>ACTIVE JOB</JobBadge>
                    <span style={{ color: '#94a3b8', fontSize: '14px' }}>Started {timeAgo(activeJob.started_at)} ago</span>
                  </div>

                  <div style={{ display: 'flex', gap: '24px', marginBottom: '32px' }}>
                    {activeJob.vehicle_photo ? (
                      <img src={activeJob.vehicle_photo} alt="Vehicle" style={{ width: '128px', height: '128px', borderRadius: '12px', objectCover: 'cover' }} />
                    ) : (
                      <div style={{ width: '128px', height: '128px', borderRadius: '12px', background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Car size={48} color="#94a3b8" />
                      </div>
                    )}
                    <div>
                      <h2 style={{ fontFamily: 'Space Grotesk', fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                        {activeJob.issue || activeJob.job_type}
                      </h2>
                      <p style={{ color: '#4a4455', lineHeight: 1.6, marginBottom: '16px' }}>{activeJob.description}</p>
                      <div style={{ display: 'flex', gap: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#4a4455', fontSize: '14px' }}>
                          <UserIcon size={16} color="#7c3aed" /> {activeJob.user_name}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#4a4455', fontSize: '14px' }}>
                          <Car size={16} color="#7c3aed" /> {activeJob.car_model || 'Vehicle'}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div style={{ borderTop: '1px solid #f8fafc', paddingTop: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <button style={{ background: 'none', border: 'none', color: '#630ed4', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                      <ClipboardList size={18} /> View Full History
                    </button>
                    <button 
                      onClick={handleComplete}
                      style={{ 
                        background: 'linear-gradient(#630ed4, #7c3aed)', 
                        color: 'white', 
                        padding: '12px 32px', 
                        borderRadius: '12px', 
                        border: 'none', 
                        fontWeight: 'bold',
                        boxShadow: '0 4px 14px rgba(124, 58, 237, 0.35)',
                        cursor: 'pointer'
                      }}
                    >
                      Mark Complete
                    </button>
                  </div>
                </ActiveJobCard>
              ) : (
                <ActiveJobCard style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '64px' }}>
                  <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
                    <Wrench size={32} color="#94a3b8" />
                  </div>
                  <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#191c1e' }}>No active job</h3>
                  <p style={{ color: '#64748b' }}>Accept a request from the queue to get started</p>
                </ActiveJobCard>
              )}

              <ToolsGrid>
                <ToolCard>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                    <Package size={20} color="#fd761a" />
                    <h3 style={{ fontWeight: 'bold', fontSize: '16px' }}>Required Parts</h3>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {(activeJob?.parts_needed || [
                      { name: 'Synthetic Oil (5W-30)', status: 'IN STOCK' },
                      { name: 'Oil Filter - OEM', status: 'IN STOCK' },
                      { name: 'Intake Gasket Set', status: 'ORDERED' }
                    ]).map((part, i) => (
                      <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '14px', color: '#191c1e' }}>{part.name}</span>
                        <span style={{ 
                          fontSize: '10px', 
                          fontWeight: 'bold', 
                          padding: '2px 8px', 
                          borderRadius: '4px',
                          background: part.status === 'IN STOCK' ? '#e8fdf5' : '#fff7ed',
                          color: part.status === 'IN STOCK' ? '#005952' : '#9a3412'
                        }}>
                          {part.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </ToolCard>

                <ToolCard>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                    <FileEdit size={20} color="#005952" />
                    <h3 style={{ fontWeight: 'bold', fontSize: '16px' }}>Quick Notes</h3>
                  </div>
                  <div style={{ background: '#f2f4f6', padding: '16px', borderRadius: '8px', minHeight: '80px', marginBottom: '12px' }}>
                    <p style={{ fontSize: '14px', color: '#64748b', fontStyle: 'italic' }}>
                      {activeJob?.notes || "Check spark plug gaps before re-assembling the intake manifold."}
                    </p>
                  </div>
                  <button style={{ background: 'none', border: 'none', color: '#7c3aed', fontWeight: 'bold', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                    <Plus size={14} /> ADD NOTE
                  </button>
                </ToolCard>
              </ToolsGrid>
            </LeftCol>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3 style={{ fontWeight: 'bold', fontSize: '20px' }}>Job Queue</h3>
                  <span style={{ background: '#eaddff', color: '#630ed4', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>
                    {pendingJobs.length} NEW
                  </span>
                </div>

                {pendingJobs.length > 0 ? (
                  pendingJobs.map(job => (
                    <QueueCard key={job.id} urgent={job.urgency}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                        <div>
                          <p style={{ fontWeight: 'bold', fontSize: '14px', color: '#191c1e', marginBottom: '2px' }}>{job.issue || job.job_type}</p>
                          <p style={{ fontSize: '12px', color: '#64748b' }}>
                            {job.distance} miles away {job.urgency && '• urgent'}
                          </p>
                        </div>
                        <span style={{ color: '#fd761a', fontWeight: 'bold', fontSize: '14px' }}>₹{job.estimated_fare}</span>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button 
                          onClick={() => handleAccept(job.id)}
                          style={{ flex: 1, background: '#005952', color: 'white', border: 'none', padding: '8px', borderRadius: '8px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer' }}
                        >
                          ACCEPT
                        </button>
                        <button 
                          onClick={() => handleDecline(job.id)}
                          style={{ padding: '8px 12px', border: '1px solid #ba1a1a', color: '#ba1a1a', background: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 'bold', cursor: 'pointer' }}
                        >
                          DECLINE
                        </button>
                      </div>
                    </QueueCard>
                  ))
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px 20px', background: 'white', borderRadius: '16px' }}>
                    <CheckCircle size={48} color="#005952" style={{ marginBottom: '12px' }} />
                    <p style={{ fontWeight: 'bold', color: '#191c1e' }}>You're all caught up!</p>
                  </div>
                )}
              </div>

              <ForecastContainer>
                <h3 style={{ fontFamily: 'Space Grotesk', fontWeight: 'bold', fontSize: '14px', color: '#191c1e' }}>Availability Forecast</h3>
                <ChartArea>
                  {[40, 60, 100, 80, 30, 50, 20].map((h, i) => (
                    <ChartBar key={i} style={{ height: `${h}%`, opacity: h / 100 }} />
                  ))}
                </ChartArea>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px' }}>
                  {['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'].map(day => (
                    <span key={day} style={{ fontSize: '10px', color: '#94a3b8', fontWeight: 'bold' }}>{day}</span>
                  ))}
                </div>
              </ForecastContainer>
            </div>
          </MainGrid>
        </MainContent>
      </LayoutBody>

      <MobileNav>
        <NavItem active style={{ flexDirection: 'column', padding: '8px' }} onClick={() => navigate('/worker/car/mechanic/dashboard')}>
          <LayoutDashboard size={20} />
          <span style={{ fontSize: '10px' }}>Dashboard</span>
        </NavItem>
        <NavItem style={{ flexDirection: 'column', padding: '8px' }} onClick={() => navigate('/worker/car/mechanic/jobs-queue')}>
          <ListChecks size={20} />
          <span style={{ fontSize: '10px' }}>Queue</span>
        </NavItem>
        <FAB><Plus size={24} /></FAB>
        <NavItem style={{ flexDirection: 'column', padding: '8px' }} onClick={() => navigate('/worker/car/mechanic/earnings')}>
          <Wallet size={20} />
          <span style={{ fontSize: '10px' }}>Earnings</span>
        </NavItem>
        <NavItem style={{ flexDirection: 'column', padding: '8px' }} onClick={() => navigate('/worker/car/mechanic/settings')}>
          <Settings size={20} />
          <span style={{ fontSize: '10px' }}>Settings</span>
        </NavItem>
      </MobileNav>

      {toast && (
        <Toast type={toast.type}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {toast.type === 'success' ? <CheckCircle size={18} /> : <X size={18} />}
            {toast.message}
          </div>
        </Toast>
      )}
    </DashboardContainer>
  );
};

export default MechanicDashboard;
