import React, { useEffect, useMemo, useState } from 'react';
import { authService, appointmentService } from '../services/api';
import BottomNav from '../components/BottomNav';
import { UserRound, CalendarDays, CheckCircle2, Clock3, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const [info, setInfo] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const nav = useNavigate();

  useEffect(() => {
    let mounted = true;
    const run = async () => {
      try {
        const [i, a, p] = await Promise.all([
          authService.getUserInfo(),
          appointmentService.getUserAppointments(),
          profileService.getProfile(),
        ]);
        if (!mounted) return;
        setInfo({ ...i.data, email: p.data.email });
        setAppointments(a.data.appointments || []);
      } catch {
        console.error('Failed to load profile');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    run();
    return () => { mounted = false; };
  }, []);

  const stats = useMemo(() => {
    const total = appointments.length;
    const completed = appointments.filter(a => (a.status || '').toLowerCase() === 'completed').length;
    const upcoming = appointments.filter(a => !['completed','cancelled','rejected'].includes((a.status || '').toLowerCase())).length;
    return { total, completed, upcoming };
  }, [appointments]);

  const subtitle = info?.email ? `${info.email}` : (info?.username || '');

  return (
    <div className="profile-page">
      <div className="header">
        <h1>My Profile</h1>
        <div className="card">
          <div className="avatar"><UserRound size={28} /></div>
          <div className="meta">
            <div className="name">{info?.user_name || 'User'}</div>
            <div className="sub">{subtitle}</div>
            {info?.user_id ? <div className="sub">ID: {info.user_id}</div> : null}
          </div>
        </div>
      </div>

      <div className="stats">
        <div className="stat">
          <div className="icon"><CalendarDays size={20} /></div>
          <div className="num">{loading ? '–' : stats.total}</div>
          <div className="label">Total</div>
        </div>
        <div className="stat">
          <div className="icon"><CheckCircle2 size={20} /></div>
          <div className="num">{loading ? '–' : stats.completed}</div>
          <div className="label">Completed</div>
        </div>
        <div className="stat">
          <div className="icon"><Clock3 size={20} /></div>
          <div className="num">{loading ? '–' : stats.upcoming}</div>
          <div className="label">Upcoming</div>
        </div>
      </div>

      <div className="list">
        <button className="item" onClick={() => nav('/profile/settings')}><span>Settings</span><ChevronRight size={18} /></button>
        <button className="item" onClick={() => nav('/profile/help')}><span>Help & Support</span><ChevronRight size={18} /></button>
        <button className="item" onClick={() => nav('/profile/terms')}><span>Terms & Conditions</span><ChevronRight size={18} /></button>
      </div>
      
      <div className="logout-card">
        <button onClick={() => { localStorage.removeItem('token'); nav('/login'); }}>Logout</button>
      </div>

      <BottomNav />

      <style>{`
        .profile-page{min-height:100vh;background:var(--background-light);padding-bottom:80px}
        .header{background:linear-gradient(135deg,#8E44AD,#9B59B6);padding:1.2rem 1.25rem 3.5rem 1.25rem;color:#fff}
        .header h1{margin:0 0 1rem 0}
        .card{display:flex;align-items:center;gap:.9rem;background:#fff;color:#111;border-radius:16px;padding:1rem;box-shadow:0 6px 18px rgba(0,0,0,0.1)}
        .avatar{width:52px;height:52px;border-radius:14px;background:#F3E8FF;color:#6B21A8;display:flex;align-items:center;justify-content:center}
        .meta .name{font-weight:800;font-size:1.05rem}
        .meta .sub{color:#6B7280;font-size:.9rem}
        .stats{margin:-2.2rem 1.25rem 0 1.25rem;display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem}
        .stat{background:#fff;border-radius:16px;padding:.9rem;display:flex;flex-direction:column;align-items:center;box-shadow:0 6px 18px rgba(0,0,0,0.06)}
        .stat .icon{color:#8E44AD;background:#F4ECF7;border-radius:12px;padding:.4rem;margin-bottom:.3rem}
        .stat .num{font-size:1.25rem;font-weight:800}
        .stat .label{color:#6B7280;font-size:.9rem}
        .list{margin:1rem 1.25rem 0 1.25rem;background:#fff;border-radius:16px;box-shadow:0 6px 18px rgba(0,0,0,0.06);overflow:hidden}
        .item{width:100%;display:flex;align-items:center;justify-content:space-between;padding:1rem;border:none;background:#fff;border-bottom:1px solid #F3F4F6;cursor:pointer}
        .item:last-child{border-bottom:none}
        .logout-card{margin:1rem 1.25rem;background:#FEE2E2;border-radius:16px;padding:.6rem}
        .logout-card button{width:100%;background:transparent;border:none;color:#DC2626;font-weight:700;padding:.6rem}
      `}</style>
    </div>
  );
};

export default Profile;
