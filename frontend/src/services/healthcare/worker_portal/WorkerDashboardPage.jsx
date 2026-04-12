import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Calendar,
  Check,
  CheckCircle,
  CheckCircle2,
  ClipboardList,
  Clock,
  CreditCard,
  ExternalLink,
  Hash,
  History,
  LayoutDashboard,
  Loader2,
  LogOut,
  Mail,
  MapPin,
  MessageCircle,
  RefreshCw,
  SendHorizontal,
  Stethoscope,
  User,
  Video,
  X,
  XCircle,
  Phone,
} from 'lucide-react';
import api from '../../../shared/api';
import healthcareSocket from '../../healthcareSocket';
import './WorkerPortal.css';

const MAIN_TABS = [
  { key: 'dashboard', label: 'Home', icon: LayoutDashboard },
  { key: 'availability', label: 'Availability', icon: Calendar },
  { key: 'consults', label: 'Consultations', icon: ClipboardList },
  { key: 'video', label: 'Video Call', icon: Video },
  { key: 'profile', label: 'Profile', icon: User },
  { key: 'subscription', label: 'Plan', icon: CreditCard },
];

const CONSULT_SUBTABS = ['pending', 'accepted', 'video', 'history'];

const getHeaders = () => {
  const token = localStorage.getItem('worker_token');
  return { Authorization: `Bearer ${token}` };
};

const todayStr = () => new Date().toISOString().slice(0, 10);

const toastInit = { open: false, type: 'success', message: '' };

const WorkerDashboardPage = () => {
  const workerId = localStorage.getItem('worker_id');
  const specialization = localStorage.getItem('worker_specialization') || 'Healthcare Worker';

  const [tab, setTab] = useState('dashboard');
  const [consultSubtab, setConsultSubtab] = useState('pending');
  const [toast, setToast] = useState(toastInit);

  const [status, setStatus] = useState('offline');
  const [statusModal, setStatusModal] = useState(false);
  const [statusSaving, setStatusSaving] = useState(false);

  const [stats, setStats] = useState(null);
  const [todayAppointments, setTodayAppointments] = useState([]);
  const [dashLoading, setDashLoading] = useState(true);
  const [dashError, setDashError] = useState('');

  const [availability, setAvailability] = useState({});
  const [availabilityLoading, setAvailabilityLoading] = useState(true);
  const [availabilityError, setAvailabilityError] = useState('');
  const [slotAdd, setSlotAdd] = useState({ date: '', time_slot: '' });
  const [slotRemove, setSlotRemove] = useState({ date: '', time_slot: '' });
  const [slotBusy, setSlotBusy] = useState(false);

  const [requests, setRequests] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [videoAppointments, setVideoAppointments] = useState([]);
  const [history, setHistory] = useState([]);
  const [consultLoading, setConsultLoading] = useState(true);
  const [consultError, setConsultError] = useState('');

  const [otpModal, setOtpModal] = useState(null);
  const [paymentInfoModal, setPaymentInfoModal] = useState(null);

  const [messageModal, setMessageModal] = useState({ open: false, appointmentId: null, patientName: '' });
  const [messages, setMessages] = useState([]);
  const [msgInput, setMsgInput] = useState('');
  const [msgLoading, setMsgLoading] = useState(false);
  const [msgSending, setMsgSending] = useState(false);

  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState('');

  const [videoStart, setVideoStart] = useState({ appointment_id: '', otp: '' });
  const [videoEnd, setVideoEnd] = useState({ appointment_id: '' });
  const [videoJoin, setVideoJoin] = useState({ appointment_id: '' });
  const [videoBusy, setVideoBusy] = useState(false);
  const [videoSuccess, setVideoSuccess] = useState('');

  const [subscriptionCurrent, setSubscriptionCurrent] = useState(null);
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [subscriptionStats, setSubscriptionStats] = useState(null);
  const [subLoading, setSubLoading] = useState(true);
  const [subError, setSubError] = useState('');
  const [subBusy, setSubBusy] = useState(false);

  const showToast = (type, message) => {
    setToast({ open: true, type, message });
    window.setTimeout(() => setToast(toastInit), 3000);
  };

  const typeBadgeClass = (type) => (type === 'VIDEO' || String(type || '').toLowerCase() === 'video' ? { bg: '#F5F3FF', color: '#8E44AD' } : { bg: '#FDF7FF', color: '#9B59B6' });

  const fetchDashboard = async () => {
    if (!workerId) return;
    setDashLoading(true);
    setDashError('');
    try {
      const headers = getHeaders();
      const [statsRes, statusRes, appointmentsRes] = await Promise.all([
        api.get(`/worker/${workerId}/dashboard/stats`, { headers }),
        api.get(`/worker/${workerId}/status`, { headers }),
        api.get(`/worker/${workerId}/appointments`, { headers }),
      ]);
      setStats(statsRes.data || {});
      setStatus((statusRes.data?.status || 'offline').toLowerCase());

      const appts = appointmentsRes.data?.appointments || appointmentsRes.data || [];
      const today = todayStr();
      setTodayAppointments(appts.filter((a) => String(a.booking_date || '').slice(0, 10) === today));
    } catch (err) {
      setDashError('Failed to load. Tap to retry.');
    } finally {
      setDashLoading(false);
    }
  };

  const fetchAvailability = async () => {
    if (!workerId) return;
    setAvailabilityLoading(true);
    setAvailabilityError('');
    try {
      const { data } = await api.get(`/worker/${workerId}/availability`, { headers: getHeaders() });
      const slots = data?.availability || data?.slots || data || [];
      const grouped = {};
      slots.forEach((s) => {
        const d = s.date || s.booking_date || '';
        if (!grouped[d]) grouped[d] = [];
        grouped[d].push(s.time_slot || s.slot || '');
      });
      setAvailability(grouped);
    } catch (err) {
      setAvailabilityError('Failed to load. Tap to retry.');
    } finally {
      setAvailabilityLoading(false);
    }
  };

  const fetchConsultations = async () => {
    if (!workerId) return;
    setConsultLoading(true);
    setConsultError('');
    try {
      const headers = getHeaders();
      const [requestsRes, appointmentsRes, videoRes, historyRes] = await Promise.all([
        api.get(`/worker/${workerId}/requests`, { headers }),
        api.get(`/worker/${workerId}/appointments`, { headers }),
        api.get('/worker/video_appointments', { headers }),
        api.get(`/worker/${workerId}/history`, { headers }),
      ]);
      setRequests(requestsRes.data?.requests || requestsRes.data || []);
      setAppointments(appointmentsRes.data?.appointments || appointmentsRes.data || []);
      setVideoAppointments(videoRes.data?.appointments || videoRes.data || []);
      setHistory(historyRes.data?.appointments || historyRes.data || []);
    } catch (err) {
      setConsultError('Failed to load. Tap to retry.');
    } finally {
      setConsultLoading(false);
    }
  };

  const fetchProfile = async () => {
    if (!workerId) return;
    setProfileLoading(true);
    setProfileError('');
    try {
      const { data } = await api.get(`/worker/${workerId}`, { headers: getHeaders() });
      setProfile(data?.worker || data || {});
    } catch (err) {
      setProfileError('Failed to load. Tap to retry.');
    } finally {
      setProfileLoading(false);
    }
  };

  const fetchSubscription = async () => {
    if (!workerId) return;
    setSubLoading(true);
    setSubError('');
    try {
      const headers = getHeaders();
      const [currentRes, plansRes, statsRes] = await Promise.all([
        api.get(`/api/subscription/current?worker_id=${workerId}`, { headers }),
        api.get('/api/subscription/plans', { headers }),
        api.get(`/api/subscription/stats/${workerId}`, { headers }),
      ]);
      setSubscriptionCurrent(currentRes.data || null);
      setSubscriptionPlans(plansRes.data?.plans || plansRes.data || []);
      setSubscriptionStats(statsRes.data || null);
    } catch (err) {
      setSubError('Failed to load. Tap to retry.');
    } finally {
      setSubLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    fetchAvailability();
    fetchConsultations();
    fetchProfile();
    fetchSubscription();
    
    // Initialize Socket
    if (workerId) {
      healthcareSocket.connect();
      healthcareSocket.joinRoom('worker', workerId);

      const handleNewAppointment = (newAppt) => {
        console.log('🔔 Real-time new appointment:', newAppt);
        setRequests(prev => [newAppt, ...prev]);
        showToast('success', `New appointment from ${newAppt.user_name}`);
        
        // Browser notification
        if (Notification.permission === "granted") {
          new Notification("New Appointment Request", {
            body: `You have a new appointment from ${newAppt.user_name}`
          });
        }
      };

      healthcareSocket.on('new_appointment', handleNewAppointment);

      if (Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission();
      }

      return () => {
        healthcareSocket.off('new_appointment', handleNewAppointment);
        healthcareSocket.leaveRoom('worker', workerId);
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workerId]);

  const updateStatus = async (nextStatus) => {
    try {
      setStatusSaving(true);
      await api.post(`/worker/${workerId}/status`, { status: nextStatus }, { headers: getHeaders() });
      setStatus(nextStatus);
      setStatusModal(false);
      showToast('success', 'Status updated');
    } catch (err) {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setStatusSaving(false);
    }
  };

  const addSlot = async () => {
    if (!slotAdd.date || !slotAdd.time_slot) return;
    try {
      setSlotBusy(true);
      await api.post(`/worker/${workerId}/availability`, slotAdd, { headers: getHeaders() });
      setSlotAdd({ date: '', time_slot: '' });
      showToast('success', 'Slot added!');
      fetchAvailability();
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setSlotBusy(false);
    }
  };

  const removeSlot = async () => {
    if (!slotRemove.date || !slotRemove.time_slot) return;
    try {
      setSlotBusy(true);
      await api.delete(`/worker/${workerId}/availability`, { data: slotRemove, headers: getHeaders() });
      setSlotRemove({ date: '', time_slot: '' });
      showToast('success', 'Slot removed!');
      fetchAvailability();
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setSlotBusy(false);
    }
  };

  const respondToRequest = async (appointmentId, statusValue) => {
    if (statusValue === 'rejected') {
      const ok = window.confirm('Reject this appointment?');
      if (!ok) return;
    }
    try {
      const { data } = await api.post(
        '/worker/respond',
        { appointment_id: appointmentId, status: statusValue },
        { headers: getHeaders() }
      );
      showToast('success', statusValue === 'accepted' ? 'Appointment accepted' : 'Appointment rejected');
      if (data?.payment_required) {
        setPaymentInfoModal({ doctor_fee: data.doctor_fee });
      }
      if (data?.doctor_otp) {
        setOtpModal({ doctor_otp: data.doctor_otp, join_url: data.patient_join_url || data.join_url || '' });
      }
      fetchConsultations();
      fetchDashboard();
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    }
  };

  const openMessageModal = async (appointmentId, patientName) => {
    setMessageModal({ open: true, appointmentId, patientName });
    setMsgLoading(true);
    try {
      const { data } = await api.get(
        `/messages/${appointmentId}?sender_role=worker&worker_id=${workerId}`,
        { headers: getHeaders() }
      );
      setMessages(data?.messages || data || []);
    } catch {
      showToast('error', 'Failed to load messages');
    } finally {
      setMsgLoading(false);
    }
  };

  const sendMessage = async () => {
    const text = msgInput.trim();
    if (!text || !messageModal.appointmentId) return;
    try {
      setMsgSending(true);
      await api.post(
        '/messages/send',
        {
          appointment_id: Number(messageModal.appointmentId),
          sender_role: 'worker',
          worker_id: Number(workerId),
          message: text,
        },
        { headers: getHeaders() }
      );
      setMessages((prev) => [
        ...prev,
        {
          sender_role: 'worker',
          message: text,
          created_at: new Date().toISOString(),
        },
      ]);
      setMsgInput('');
    } catch {
      showToast('error', 'Failed to send message');
    } finally {
      setMsgSending(false);
    }
  };

  const startVideoWithOtp = async () => {
    if (!videoStart.appointment_id || !videoStart.otp) return;
    try {
      setVideoBusy(true);
      await api.post(
        '/appointment/video/start',
        {
          appointment_id: Number(videoStart.appointment_id),
          otp: Number(videoStart.otp),
        },
        { headers: getHeaders() }
      );
      setVideoSuccess('Consultation started!');
      showToast('success', 'Consultation started!');
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setVideoBusy(false);
    }
  };

  const completeConsultation = async () => {
    if (!videoEnd.appointment_id) return;
    try {
      setVideoBusy(true);
      await api.post('/appointment/complete', { appointment_id: Number(videoEnd.appointment_id) }, { headers: getHeaders() });
      showToast('success', 'Consultation completed!');
      fetchConsultations();
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setVideoBusy(false);
    }
  };

  const joinCall = (id) => {
    const base = import.meta.env.VITE_API_URL;
    window.open(`${base}/video-call/${id}?role=doctor`, '_blank');
  };

  const loadRazorpay = () =>
    new Promise((resolve) => {
      if (window.Razorpay) return resolve(true);
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });

  const subscribePlan = async (plan) => {
    try {
      setSubBusy(true);
      if (plan.price === 0 || String(plan.plan_name || '').toLowerCase().includes('free')) {
        await api.post('/api/subscription/confirm', { worker_id: Number(workerId), plan_id: Number(plan.plan_id || plan.id) }, { headers: getHeaders() });
        showToast('success', 'Free plan activated!');
        fetchSubscription();
        return;
      }

      const { data } = await api.post(
        '/api/subscription/create-order',
        { worker_id: Number(workerId), plan_id: Number(plan.plan_id || plan.id) },
        { headers: getHeaders() }
      );
      const ok = await loadRazorpay();
      if (!ok) throw new Error('Razorpay SDK failed');

      const rzp = new window.Razorpay({
        key: data.razorpay_key,
        amount: data.amount,
        currency: 'INR',
        name: 'ExpertEase',
        description: `${plan.plan_name} Subscription`,
        order_id: data.order_id,
        handler: async (response) => {
          await api.post(
            '/api/subscription/confirm',
            {
              worker_id: Number(workerId),
              order_id: response.razorpay_order_id,
              payment_id: response.razorpay_payment_id,
            },
            { headers: getHeaders() }
          );
          showToast('success', 'Subscription activated!');
          fetchSubscription();
        },
      });
      rzp.open();
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setSubBusy(false);
    }
  };

  const cancelSubscription = async () => {
    const ok = window.confirm("Cancel Subscription?\nYou'll keep access until your billing period ends.");
    if (!ok) return;
    try {
      setSubBusy(true);
      await api.post(`/api/subscription/cancel/${workerId}`, {}, { headers: getHeaders() });
      showToast('success', 'Subscription cancelled');
      fetchSubscription();
    } catch {
      showToast('error', 'Something went wrong. Try again.');
    } finally {
      setSubBusy(false);
    }
  };

  const doLogout = () => {
    const ok = window.confirm('Log out of worker portal?');
    if (!ok) return;
    localStorage.removeItem('worker_id');
    localStorage.removeItem('worker_token');
    localStorage.removeItem('worker_specialization');
    window.location.href = '/worker';
  };

  const acceptedAppointments = useMemo(
    () => appointments.filter((a) => String(a.status || '').toLowerCase() === 'accepted'),
    [appointments]
  );

  return (
    <div className="wp-page">
      <div className="wp-mobile-shell">
        <div className="wp-dash-fixed-header">
          <div className="wp-dash-header-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Stethoscope size={18} color="#FFC107" />
              <strong>Dr. Dashboard</strong>
            </div>
            <div className="wp-status-chip" onClick={() => setStatusModal(true)} style={{ color: status === 'online' ? '#16A34A' : '#94A3B8' }}>
              ● {status === 'online' ? 'Online' : 'Offline'}
            </div>
          </div>
        </div>

        <div className="wp-dashboard">
          {tab === 'dashboard' && (
            <div className="wp-tab-content">
              {dashError ? (
                <div className="wp-error-banner" onClick={fetchDashboard}>
                  <RefreshCw size={14} style={{ display: 'inline', marginRight: 6 }} />
                  Failed to load. Tap to retry.
                </div>
              ) : null}

              {dashLoading ? (
                <div className="wp-stats-grid">
                  {[1, 2, 3, 4].map((k) => <div key={k} className="wp-card wp-stat-card wp-skeleton" style={{ height: 110 }} />)}
                </div>
              ) : (
                <div className="wp-stats-grid">
                  {[
                    { key: 'pending_requests', label: 'Pending', icon: Clock, color: '#FFC107' },
                    { key: 'today_appointments', label: 'Today', icon: Calendar, color: '#8E44AD' },
                    { key: 'accepted', label: 'Accepted', icon: Check, color: '#16A34A' },
                    { key: 'total_appointments', label: 'Total', icon: Activity, color: '#9B59B6' },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <div key={item.key} className="wp-card wp-stat-card">
                        <div style={{ width: 40, height: 40, borderRadius: 999, background: `${item.color}1A`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Icon size={18} color={item.color} />
                        </div>
                        <div className="wp-stat-value">{stats?.[item.key] ?? 0}</div>
                        <div className="wp-stat-label">{item.label}</div>
                      </div>
                    );
                  })}
                </div>
              )}

              <div className="wp-card" style={{ padding: 16, marginBottom: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#0f172a' }}>Current Status</strong>
                  <span style={{ fontSize: 12, borderRadius: 16, padding: '4px 8px', background: status === 'online' ? '#DCFCE7' : '#F1F5F9', color: status === 'online' ? '#16A34A' : '#64748B' }}>
                    ● {status === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
                <button className="wp-input no-icon" style={{ marginTop: 12, height: 38, cursor: 'pointer' }} onClick={() => setStatusModal(true)}>
                  Change Status
                </button>
              </div>

              <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 10 }}>Today's Schedule</div>
              {todayAppointments.length === 0 ? (
                <div className="wp-card" style={{ padding: 18, textAlign: 'center', color: '#94a3b8' }}>No appointments today</div>
              ) : (
                todayAppointments.map((a, i) => {
                  const s = String(a.status || '').toLowerCase();
                  const leftIcon =
                    s === 'pending' ? <Clock size={15} color="#FFC107" /> :
                    s === 'accepted' ? <CheckCircle2 size={15} color="#16A34A" /> :
                    s === 'in_consultation' ? <Video size={15} color="#8E44AD" /> :
                    <Check size={15} color="#9B59B6" />;
                  const badge = typeBadgeClass(a.appointment_type || a.type);
                  return (
                    <div key={i} className="wp-card" style={{ padding: 12, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 32, height: 32, borderRadius: 999, background: '#F8FAFC', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{leftIcon}</div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>#{a.appointment_id || a.id}</div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{a.patient_name || 'Patient'}</div>
                        <div style={{ fontSize: 12, color: '#64748b' }}>{a.time_slot || 'Time TBD'}</div>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>{String(a.patient_symptoms || a.symptoms || '').slice(0, 40)}</div>
                      </div>
                      <div style={{ fontSize: 11, borderRadius: 12, padding: '4px 8px', background: badge.bg, color: badge.color }}>
                        {(a.appointment_type || a.type || 'CLINIC').toString().toUpperCase()}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {tab === 'availability' && (
            <div className="wp-tab-content">
              {availabilityError ? <div className="wp-error-banner" onClick={fetchAvailability}>Failed to load. Tap to retry.</div> : null}

              <div className="wp-card" style={{ padding: 16, marginBottom: 12 }}>
                <div className="wp-section-title" style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <Calendar size={16} color="#8E44AD" /> Add Time Slot
                </div>
                <div className="wp-field">
                  <label className="wp-label">Date</label>
                  <input className="wp-input no-icon" type="date" value={slotAdd.date} onChange={(e) => setSlotAdd((p) => ({ ...p, date: e.target.value }))} />
                </div>
                <div className="wp-field">
                  <label className="wp-label">Time Slot</label>
                  <input className="wp-input no-icon" placeholder="09:00-10:00" value={slotAdd.time_slot} onChange={(e) => setSlotAdd((p) => ({ ...p, time_slot: e.target.value }))} />
                  <div style={{ fontSize: 11, color: '#94a3b8' }}>Format: HH:MM-HH:MM</div>
                </div>
                <button className="wp-primary-btn" style={{ height: 44, background: '#8E44AD' }} onClick={addSlot} disabled={slotBusy}>
                  {slotBusy ? 'Adding...' : 'Add Slot'}
                </button>
              </div>

              <div className="wp-card" style={{ padding: 16, marginBottom: 12 }}>
                  <div className="wp-section-title" style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                    <X size={16} color="#DC2626" /> Remove Time Slot
                  </div>
                  <div className="wp-field">
                    <label className="wp-label">Date</label>
                    <input className="wp-input no-icon" type="date" value={slotRemove.date} onChange={(e) => setSlotRemove((p) => ({ ...p, date: e.target.value }))} />
                  </div>
                  <div className="wp-field">
                    <label className="wp-label">Time Slot</label>
                    <input className="wp-input no-icon" placeholder="09:00-10:00" value={slotRemove.time_slot} onChange={(e) => setSlotRemove((p) => ({ ...p, time_slot: e.target.value }))} />
                  </div>
                  <button className="wp-primary-btn" style={{ height: 44, background: '#FEE2E2', color: '#DC2626', border: '1px solid #FECACA' }} onClick={removeSlot} disabled={slotBusy}>
                    {slotBusy ? 'Removing...' : 'Remove Slot'}
                  </button>
                </div>

              <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 8 }}>Your Available Slots</div>
              {availabilityLoading ? (
                <div className="wp-card wp-skeleton" style={{ height: 80 }} />
              ) : Object.keys(availability).length === 0 ? (
                <div className="wp-card" style={{ padding: 18, textAlign: 'center', color: '#94a3b8' }}>
                  <Calendar size={30} />
                  <div>No slots added yet</div>
                </div>
              ) : (
                Object.entries(availability).map(([date, slots]) => (
                  <div key={date} className="wp-card" style={{ padding: 12, marginBottom: 10 }}>
                    <div style={{ fontWeight: 700, color: '#8E44AD', background: '#F5F3FF', borderRadius: 8, padding: '8px 10px', marginBottom: 10 }}>{date}</div>
                    <div>
                      {slots.map((slot, i) => (
                        <span key={i} style={{ display: 'inline-block', margin: '4px', background: '#FDF7FF', color: '#8E44AD', borderRadius: 20, padding: '6px 14px', fontSize: 13, border: '1px solid #eee1ff' }}>
                          {slot}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === 'consults' && (
            <div className="wp-tab-content">
              <div className="wp-subtabs">
                {CONSULT_SUBTABS.map((s) => (
                  <button key={s} className={`wp-subtab ${consultSubtab === s ? 'active' : ''}`} onClick={() => setConsultSubtab(s)}>
                    {s === 'pending' ? 'Pending' : s === 'accepted' ? 'Accepted' : s === 'video' ? 'Video' : 'History'}
                  </button>
                ))}
              </div>
              {consultError ? <div className="wp-error-banner" onClick={fetchConsultations}>Failed to load. Tap to retry.</div> : null}
              {consultLoading ? <div className="wp-card wp-skeleton" style={{ height: 120 }} /> : null}

              {!consultLoading && consultSubtab === 'pending' && (
                <div>
                  {requests.length === 0 ? (
                    <div className="wp-card" style={{ padding: 18, textAlign: 'center', color: '#94a3b8' }}>
                      <ClipboardList size={30} />
                      <div>No pending requests</div>
                    </div>
                  ) : (
                    requests.map((r, i) => {
                      const badge = typeBadgeClass(r.appointment_type || r.type);
                      return (
                        <div key={i} className="wp-card" style={{ padding: 16, marginBottom: 12 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <div style={{ color: '#94a3b8', fontSize: 11 }}>#Appt {r.appointment_id || r.id}</div>
                            <span style={{ fontSize: 11, borderRadius: 12, padding: '3px 8px', background: badge.bg, color: badge.color }}>{(r.appointment_type || r.type || 'clinic').toString().toUpperCase()}</span>
                          </div>
                          <div style={{ fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{r.patient_name || 'Patient'}</div>
                          <div style={{ fontSize: 12, color: '#64748b' }}>📅 {r.booking_date || '-'}</div>
                          <div style={{ marginTop: 10, background: '#FFFBEB', borderRadius: 10, padding: 10, fontSize: 13, color: '#64748b', fontStyle: 'italic' }}>
                            Symptoms: {r.patient_symptoms || r.symptoms || '-'}
                          </div>
                          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                            <button onClick={() => respondToRequest(r.appointment_id || r.id, 'accepted')} style={{ flex: 1, height: 40, borderRadius: 10, border: '1px solid #BBF7D0', background: '#DCFCE7', color: '#16A34A', fontWeight: 600 }}>
                              ✓ Accept
                            </button>
                            <button onClick={() => respondToRequest(r.appointment_id || r.id, 'rejected')} style={{ flex: 1, height: 40, borderRadius: 10, border: '1px solid #FECACA', background: '#FEE2E2', color: '#DC2626', fontWeight: 600 }}>
                              ✗ Reject
                            </button>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {!consultLoading && consultSubtab === 'accepted' && (
                <div>
                  {acceptedAppointments.length === 0 ? (
                    <div className="wp-card" style={{ padding: 18, textAlign: 'center', color: '#94a3b8' }}>No accepted consultations</div>
                  ) : (
                    acceptedAppointments.map((a, i) => {
                      const isVideo = String(a.appointment_type || '').toLowerCase() === 'video';
                      const badge = typeBadgeClass(a.appointment_type || a.type);
                      return (
                        <div key={i} className="wp-card" style={{ padding: 16, marginBottom: 10 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <div style={{ color: '#94a3b8', fontSize: 11 }}>#Appt {a.appointment_id || a.id}</div>
                            <span style={{ fontSize: 11, borderRadius: 12, padding: '3px 8px', background: badge.bg, color: badge.color }}>{(a.appointment_type || 'CLINIC').toString().toUpperCase()}</span>
                          </div>
                          <div style={{ fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{a.patient_name || 'Patient'}</div>
                          <div style={{ fontSize: 13, color: '#64748b' }}>📅 {a.booking_date || '-'}  🕐 {a.time_slot || '-'}</div>
                          {isVideo ? (
                            <button className="wp-primary-btn" style={{ marginTop: 10, height: 44, background: '#9B59B6' }} onClick={() => joinCall(a.appointment_id || a.id)}>
                              Join Video Consultation
                            </button>
                          ) : null}
                          <button
                            className="wp-primary-btn"
                            style={{ marginTop: 8, height: 40, background: '#FDF7FF', border: '1px solid #eee1ff', color: '#8E44AD' }}
                            onClick={() => openMessageModal(a.appointment_id || a.id, a.patient_name || 'Patient')}
                          >
                            Message Patient
                          </button>
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {!consultLoading && consultSubtab === 'video' && (
                <div>
                  {videoAppointments.length === 0 ? (
                    <div className="wp-card" style={{ padding: 18, textAlign: 'center', color: '#94a3b8' }}>No video consultations</div>
                  ) : (
                    videoAppointments.map((a, i) => (
                      <div key={i} className="wp-card" style={{ padding: 16, marginBottom: 10 }}>
                        <div style={{ color: '#94a3b8', fontSize: 11 }}>Consult #{a.appointment_id || a.id}</div>
                        <div style={{ fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{a.patient_name || 'Patient'}</div>
                        <span style={{ display: 'inline-block', marginTop: 6, borderRadius: 12, padding: '4px 8px', fontSize: 11, background: a.status === 'accepted' ? '#DCFCE7' : a.status === 'in_consultation' ? '#F5F3FF' : '#F1F5F9', color: a.status === 'accepted' ? '#16A34A' : a.status === 'in_consultation' ? '#8E44AD' : '#64748B' }}>
                          {a.status === 'in_consultation' ? 'In Progress' : (a.status || 'accepted')}
                        </span>
                        {String(a.status || '').toLowerCase() === 'accepted' ? (
                          <button className="wp-primary-btn" style={{ marginTop: 10, height: 44, background: '#9B59B6' }} onClick={() => joinCall(a.appointment_id || a.id)}>
                            Join Video Call
                          </button>
                        ) : null}
                      </div>
                    ))
                  )}
                </div>
              )}

              {!consultLoading && consultSubtab === 'history' && (
                <div>
                  {history.length === 0 ? (
                    <div className="wp-card" style={{ padding: 18, textAlign: 'center', color: '#94a3b8' }}>
                      <History size={30} />
                      <div>No completed consultations yet</div>
                    </div>
                  ) : (
                    history.map((h, i) => {
                      const badge = typeBadgeClass(h.appointment_type || h.type);
                      return (
                        <div key={i} className="wp-card" style={{ padding: 12, marginBottom: 10 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#94a3b8' }}>
                            <span>#{h.appointment_id || h.id}</span>
                            <span style={{ borderRadius: 12, padding: '2px 8px', background: badge.bg, color: badge.color }}>{(h.appointment_type || 'CLINIC').toString().toUpperCase()}</span>
                            <span style={{ borderRadius: 12, padding: '2px 8px', background: '#DCFCE7', color: '#16A34A' }}>Completed</span>
                          </div>
                          <div style={{ fontWeight: 700, color: '#0f172a', marginTop: 5 }}>{h.patient_name || 'Patient'}</div>
                          <div style={{ fontSize: 12, color: '#64748b' }}>📅 {h.booking_date || '-'}</div>
                          <div style={{ fontSize: 12, color: '#16A34A' }}>✓ {h.completed_date || h.updated_at || '-'}</div>
                        </div>
                      );
                    })
                  )}
                </div>
              )}
            </div>
          )}

          {tab === 'video' && (
            <div className="wp-tab-content">
              {videoSuccess ? <div className="wp-card" style={{ background: '#DCFCE7', borderColor: '#BBF7D0', color: '#166534', padding: 12, marginBottom: 10 }}>{videoSuccess}</div> : null}

              <div className="wp-card" style={{ padding: 16, marginBottom: 10 }}>
                <div className="wp-section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Video size={16} color="#8E44AD" /> Start Video Call
                </div>
                <div style={{ color: '#64748b', fontSize: 13, marginBottom: 10 }}>Enter OTP to begin consultation</div>
                <div className="wp-field">
                  <label className="wp-label">Appointment ID</label>
                  <input className="wp-input no-icon" type="number" value={videoStart.appointment_id} onChange={(e) => setVideoStart((p) => ({ ...p, appointment_id: e.target.value }))} />
                </div>
                <div className="wp-field">
                  <label className="wp-label">OTP</label>
                  <input className="wp-input no-icon" type="number" placeholder="6-digit OTP" value={videoStart.otp} onChange={(e) => setVideoStart((p) => ({ ...p, otp: e.target.value }))} />
                </div>
                <button className="wp-primary-btn" style={{ background: '#8E44AD', height: 44 }} onClick={startVideoWithOtp} disabled={videoBusy}>
                  {videoBusy ? 'Starting...' : 'Start Consultation'}
                </button>
              </div>

              <div className="wp-card" style={{ padding: 16, marginBottom: 10 }}>
                <div className="wp-section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircle2 size={16} color="#16A34A" /> Complete Consultation
                </div>
                <div style={{ color: '#64748b', fontSize: 13, marginBottom: 10 }}>Mark consultation as completed</div>
                <div className="wp-field">
                  <label className="wp-label">Appointment ID</label>
                  <input className="wp-input no-icon" type="number" value={videoEnd.appointment_id} onChange={(e) => setVideoEnd({ appointment_id: e.target.value })} />
                </div>
                <button className="wp-primary-btn" style={{ background: '#DCFCE7', color: '#16A34A', border: '1px solid #BBF7D0', height: 44 }} onClick={completeConsultation} disabled={videoBusy}>
                  {videoBusy ? 'Updating...' : 'Mark as Completed'}
                </button>
              </div>

              <div className="wp-card" style={{ padding: 16 }}>
                <div className="wp-section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <ExternalLink size={16} color="#9B59B6" /> Join Active Call
                </div>
                <div style={{ color: '#64748b', fontSize: 13, marginBottom: 10 }}>Open video call in browser</div>
                <div className="wp-field">
                  <label className="wp-label">Appointment ID</label>
                  <input className="wp-input no-icon" type="number" value={videoJoin.appointment_id} onChange={(e) => setVideoJoin({ appointment_id: e.target.value })} />
                </div>
                <button className="wp-primary-btn" style={{ background: '#9B59B6', height: 44 }} onClick={() => joinCall(videoJoin.appointment_id)}>
                  Join Call
                </button>
              </div>
            </div>
          )}

          {tab === 'profile' && (
            <div className="wp-tab-content">
              {profileError ? <div className="wp-error-banner" onClick={fetchProfile}>Failed to load. Tap to retry.</div> : null}
              {profileLoading ? (
                <div className="wp-card wp-skeleton" style={{ height: 180 }} />
              ) : (
                <>
                  <div className="wp-card" style={{ background: '#8E44AD', color: 'white', padding: 20, marginBottom: 12 }}>
                    <div style={{ width: 64, height: 64, borderRadius: '50%', background: '#9B59B6', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <User size={32} />
                    </div>
                    <div style={{ textAlign: 'center', marginTop: 12, fontSize: 18, fontWeight: 700 }}>{profile?.full_name || profile?.name || 'Doctor'}</div>
                    <div style={{ textAlign: 'center', marginTop: 4, color: '#FFC107', fontSize: 14 }}>{profile?.specialization || specialization}</div>
                    <div style={{ marginTop: 12, display: 'flex', justifyContent: 'center', gap: 16, fontSize: 13 }}>
                      <span>⭐ {profile?.rating || '4.8'}</span>
                      <span style={{ color: '#DCFCE7' }}>✓ Approved</span>
                      <span>{profile?.experience || 0} yrs exp</span>
                    </div>
                  </div>

                  <div className="wp-card" style={{ padding: 16 }}>
                    <div className="wp-section-title">Worker Details</div>
                    {[
                      { icon: Mail, label: 'Email', value: profile?.email || '-' },
                      { icon: Phone, label: 'Phone', value: profile?.phone || '-' },
                      { icon: MapPin, label: 'Location', value: profile?.clinic_location || '-' },
                      { icon: Hash, label: 'Worker ID', value: `#${workerId}` },
                      { icon: CreditCard, label: 'Wallet', value: `₹${Number(profile?.wallet_balance || 0).toLocaleString('en-IN')}` },
                    ].map((row, idx, arr) => {
                      const Icon = row.icon;
                      return (
                        <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: idx < arr.length - 1 ? '1px solid #F1F5F9' : 'none' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#64748b', fontSize: 13 }}>
                            <Icon size={16} color="#9B59B6" />
                            {row.label}
                          </div>
                          <div style={{ color: '#0f172a', fontWeight: 700, fontSize: 13 }}>{row.value}</div>
                        </div>
                      );
                    })}
                  </div>

                  <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <button className="wp-primary-btn" style={{ background: '#F8F7FF', border: '1px solid #eee1ff', color: '#8E44AD', height: 44 }} onClick={() => setTab('subscription')}>
                      View Subscription
                    </button>
                    <button className="wp-primary-btn" style={{ background: '#FEE2E2', border: '1px solid #FECACA', color: '#DC2626', height: 44 }} onClick={doLogout}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                        <LogOut size={16} /> Logout
                      </span>
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          {tab === 'subscription' && (
            <div className="wp-tab-content">
              {subError ? <div className="wp-error-banner" onClick={fetchSubscription}>Failed to load. Tap to retry.</div> : null}
              {subLoading ? (
                <div className="wp-card wp-skeleton" style={{ height: 140 }} />
              ) : (
                <>
                  <div className="wp-card" style={{ background: '#8E44AD', color: 'white', padding: 16, marginBottom: 12 }}>
                    <div style={{ fontSize: 12 }}>Current Plan</div>
                    <div style={{ fontSize: 20, fontWeight: 800 }}>{subscriptionCurrent?.plan_name || 'Free'}</div>
                    <div style={{ marginTop: 12, fontSize: 12 }}>📅 Expires: {subscriptionCurrent?.end_date || '-'}</div>
                    <div style={{ marginTop: 2, fontSize: 12 }}>🔢 {subscriptionCurrent?.days_remaining ?? 0} days left</div>
                    {subscriptionCurrent?.daily_limit === -1 ? (
                      <div style={{ marginTop: 12, fontSize: 12 }}>Unlimited</div>
                    ) : (
                      <>
                        <div style={{ marginTop: 12, fontSize: 12 }}>
                          Today: {subscriptionCurrent?.today_usage ?? 0}/{subscriptionCurrent?.daily_limit ?? 0}
                        </div>
                        <div style={{ height: 6, marginTop: 6, background: 'rgba(255,255,255,0.4)', borderRadius: 999 }}>
                          <div
                            style={{
                              height: 6,
                              width: `${Math.min(100, (((subscriptionCurrent?.today_usage || 0) / Math.max(1, subscriptionCurrent?.daily_limit || 1)) * 100))}%`,
                              background: '#FFC107',
                              borderRadius: 999,
                            }}
                          />
                        </div>
                        <div style={{ marginTop: 6, fontSize: 11 }}>
                          {(subscriptionCurrent?.remaining_today ?? 0)} appointments remaining today
                        </div>
                      </>
                    )}
                  </div>

                  <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: 10 }}>Available Plans</div>
                  {(subscriptionPlans || []).map((plan) => {
                    const planId = plan.plan_id || plan.id;
                    const isCurrent = Number(subscriptionCurrent?.plan_id || subscriptionCurrent?.id) === Number(planId);
                    const price = Number(plan.price || 0);
                    const badge =
                      price === 0
                        ? { bg: '#DCFCE7', color: '#16A34A', text: 'Free' }
                        : price <= 29.99
                          ? { bg: '#FDF7FF', color: '#8E44AD', text: `₹${price}/mo` }
                          : price <= 59.99
                            ? { bg: '#FEF3C7', color: '#D97706', text: `₹${price}/mo` }
                            : { bg: '#F5F3FF', color: '#9B59B6', text: `₹${price}/mo` };

                    return (
                      <div key={planId} className="wp-card" style={{ padding: 16, marginBottom: 10, border: isCurrent ? '2px solid #8E44AD' : '2px solid transparent' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div style={{ fontWeight: 700, color: '#0f172a', fontSize: 16 }}>{plan.plan_name}</div>
                          <span style={{ borderRadius: 12, padding: '4px 8px', background: badge.bg, color: badge.color, fontSize: 12 }}>
                            {badge.text}
                          </span>
                        </div>
                        <div style={{ color: '#64748b', fontSize: 12, marginTop: 4 }}>
                          Daily Limit: {plan.daily_limit === -1 ? 'Unlimited' : plan.daily_limit}
                        </div>
                        <div style={{ marginTop: 8, color: '#475569', fontSize: 13 }}>
                          {(plan.features || []).map((f, i) => (
                            <div key={i} style={{ marginBottom: 4 }}>✓ {f}</div>
                          ))}
                        </div>
                        <button
                          className="wp-primary-btn"
                          style={{ marginTop: 8, height: 40, background: isCurrent ? '#F1F5F9' : '#8E44AD', color: isCurrent ? '#64748B' : '#fff' }}
                          disabled={isCurrent || subBusy}
                          onClick={() => subscribePlan(plan)}
                        >
                          {isCurrent ? 'Current Plan' : price === 0 ? 'Activate Free Plan' : `Subscribe - ₹${price}/mo`}
                        </button>
                      </div>
                    );
                  })}

                  <button onClick={cancelSubscription} style={{ background: 'none', border: 'none', color: '#DC2626', textDecoration: 'underline', fontSize: 13, margin: '2px 0 12px', cursor: 'pointer' }}>
                    Cancel Subscription
                  </button>

                  <div className="wp-card" style={{ padding: 16 }}>
                    <div className="wp-section-title">Usage Statistics</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8 }}>
                      {[
                        ['Plan', subscriptionStats?.plan_name || '-'],
                        ['Daily Limit', subscriptionStats?.daily_limit ?? '-'],
                        ['Today Used', subscriptionStats?.today_usage ?? '-'],
                        ['Remaining', subscriptionStats?.remaining ?? '-'],
                      ].map(([l, v]) => (
                        <div key={l} style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 10, color: '#94a3b8' }}>{l}</div>
                          <div style={{ fontSize: 14, color: '#0f172a', fontWeight: 700 }}>{v}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        <div className="wp-bottom-tabs">
          {MAIN_TABS.map((t) => {
            const Icon = t.icon;
            return (
              <button key={t.key} className={`wp-bottom-tab ${tab === t.key ? 'active' : ''}`} onClick={() => setTab(t.key)}>
                <Icon size={16} />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {statusModal ? (
        <>
          <div className="wp-overlay" onClick={() => setStatusModal(false)} />
          <div className="wp-sheet" style={{ padding: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <strong>Update Status</strong>
              <button className="wp-back-btn" style={{ background: '#F1F5F9', color: '#64748b' }} onClick={() => setStatusModal(false)}>
                <X size={16} />
              </button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <button
                className="wp-card"
                style={{ padding: 14, border: status === 'online' ? '2px solid #16A34A' : '1px solid #E2E8F0', background: status === 'online' ? '#DCFCE7' : '#fff' }}
                onClick={() => setStatus('online')}
              >
                <CheckCircle2 size={22} color="#16A34A" />
                <div>Online</div>
              </button>
              <button
                className="wp-card"
                style={{ padding: 14, border: status === 'offline' ? '2px solid #64748B' : '1px solid #E2E8F0', background: status === 'offline' ? '#F1F5F9' : '#fff' }}
                onClick={() => setStatus('offline')}
              >
                <XCircle size={22} color="#64748B" />
                <div>Offline</div>
              </button>
            </div>
            <button className="wp-primary-btn" style={{ marginTop: 12 }} onClick={() => updateStatus(status)} disabled={statusSaving}>
              {statusSaving ? 'Updating...' : 'Update'}
            </button>
          </div>
        </>
      ) : null}

      {messageModal.open ? (
        <>
          <div className="wp-overlay" onClick={() => setMessageModal({ open: false, appointmentId: null, patientName: '' })} />
          <div className="wp-sheet">
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <strong>Chat - #{messageModal.appointmentId}</strong>
              <button className="wp-back-btn" style={{ background: '#F1F5F9', color: '#64748b' }} onClick={() => setMessageModal({ open: false, appointmentId: null, patientName: '' })}>
                <X size={16} />
              </button>
            </div>
            <div className="wp-msg-list">
              {msgLoading ? (
                <div className="wp-skeleton" style={{ height: 60 }} />
              ) : messages.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#94a3b8' }}>No messages yet</div>
              ) : (
                messages.map((m, i) => {
                  const isWorker = (m.sender_role || '').toLowerCase() === 'worker';
                  return (
                    <div key={i} className={`wp-msg-row ${isWorker ? 'worker' : 'patient'}`}>
                      <div className={isWorker ? 'wp-msg-bubble-worker' : 'wp-msg-bubble-patient'}>{m.message || m.text}</div>
                      <div className="wp-msg-time">{new Date(m.created_at || m.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                  );
                })
              )}
            </div>
            <div style={{ padding: 12, borderTop: '1px solid #E2E8F0', display: 'flex', gap: 8 }}>
              <textarea
                className="wp-textarea"
                style={{ height: 44, borderRadius: 24, paddingLeft: 16, paddingTop: 12 }}
                value={msgInput}
                onChange={(e) => setMsgInput(e.target.value)}
              />
              <button
                onClick={sendMessage}
                disabled={msgSending}
                style={{ width: 40, height: 40, borderRadius: '50%', border: 'none', background: '#8E44AD', color: '#fff' }}
              >
                <SendHorizontal size={16} />
              </button>
            </div>
          </div>
        </>
      ) : null}

      {otpModal ? (
        <>
          <div className="wp-overlay" onClick={() => setOtpModal(null)} />
          <div className="wp-sheet" style={{ padding: 16 }}>
            <div style={{ color: '#16A34A', fontWeight: 700, marginBottom: 8 }}>Appointment Accepted!</div>
            <div style={{ fontSize: 13, color: '#64748b' }}>Your OTP:</div>
            <div style={{ marginTop: 6, letterSpacing: 4, fontWeight: 800, color: '#8E44AD', background: '#F5F3FF', borderRadius: 12, padding: 16, textAlign: 'center', border: '1px solid #eee1ff' }}>
              {otpModal.doctor_otp}
            </div>
            {otpModal.join_url ? (
              <>
                <div style={{ marginTop: 10, fontSize: 13 }}>Patient Join URL:</div>
                <div style={{ fontSize: 12, color: '#334155', wordBreak: 'break-all' }}>{otpModal.join_url}</div>
              </>
            ) : null}
            <button className="wp-primary-btn" style={{ marginTop: 12 }} onClick={() => setOtpModal(null)}>Close</button>
          </div>
        </>
      ) : null}

      {paymentInfoModal ? (
        <>
          <div className="wp-overlay" onClick={() => setPaymentInfoModal(null)} />
          <div className="wp-sheet" style={{ padding: 16 }}>
            <strong>Payment Required</strong>
            <p style={{ color: '#64748b', fontSize: 13 }}>
              Patient will be prompted to pay ₹{paymentInfoModal.doctor_fee || 0}
              {' '}before the consultation starts.
            </p>
            <button className="wp-primary-btn" onClick={() => setPaymentInfoModal(null)}>Got it</button>
          </div>
        </>
      ) : null}

      {toast.open ? <div className={`wp-toast ${toast.type}`}>{toast.message}</div> : null}
    </div>
  );
};

export default WorkerDashboardPage;

