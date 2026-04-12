import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminDashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_workers: 0,
    pending_approvals: 0,
    total_users: 0,
    active_services: 0,
    services: {
      healthcare: { total: 0, pending: 0 },
      car_service: { total: 0, pending: 0 },
      housekeeping: { total: 0, pending: 0 },
      freelance: { total: 0, pending: 0 },
      money_management: { total: 0, pending: 0 }
    }
  });
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('token');
  const API_BASE_URL = 'http://localhost:5000';

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <div className="bg-surface text-on-surface min-h-screen">
      <style>{`
        .material-symbols-outlined {
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .font-body { font-family: 'Inter', sans-serif; }
        .font-headline, h1, h2, h3 { font-family: 'Manrope', sans-serif; }
      `}</style>
      {/* Desktop Sidebar */}
      <aside className="fixed left-0 top-0 h-screen overflow-y-auto py-8 px-4 w-64 hidden lg:flex flex-col bg-[#ede4ff] dark:bg-slate-900 shadow-[0px_20px_40px_rgba(42,30,80,0.06)] z-50">
        <div className="mb-10 px-4">
          <span className="text-xl font-bold tracking-tight text-[#32284f] dark:text-slate-100 font-headline">Editorial Admin</span>
          <p className="text-[10px] text-on-surface-variant uppercase tracking-widest mt-1 font-body">The Digital Curator</p>
        </div>
        <nav className="flex-1 space-y-1 font-body">
          {/* Dashboard (Active) */}
          <Link className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 text-[#4c40df] font-bold rounded-xl shadow-sm transition-all scale-95 active:scale-90" to="/admin/dashboard">
            <span className="material-symbols-outlined">dashboard</span>
            <span>Dashboard</span>
          </Link>
          {/* Healthcare */}
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl" to="/admin/healthcare">
            <span className="material-symbols-outlined">medical_services</span>
            <span>Healthcare</span>
          </Link>
          {/* Car Service */}
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl" to="/admin/car-service">
            <span className="material-symbols-outlined">directions_car</span>
            <span>Car Service</span>
          </Link>
          {/* Housekeeping */}
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl" to="/admin/housekeeping">
            <span className="material-symbols-outlined">cleaning_services</span>
            <span>Housekeeping</span>
          </Link>
          {/* Freelance */}
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl" to="/admin/freelance">
            <span className="material-symbols-outlined">work</span>
            <span>Freelance</span>
          </Link>
          {/* Users */}
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl" to="/admin/users">
            <span className="material-symbols-outlined">group</span>
            <span>Users</span>
          </Link>
        </nav>
        <div className="mt-auto border-t border-outline-variant/10 pt-6">
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl text-left font-body">
            <span className="material-symbols-outlined">logout</span>
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Top App Bar */}
      <header className="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-40 lg:pl-72 bg-[#fbf4ff]/50 dark:bg-slate-950/50 backdrop-blur-md">
        <div>
          <h1 className="text-lg font-black text-[#32284f] dark:text-white tracking-tight">The Editorial Admin</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative hidden sm:block">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
            <input className="pl-10 pr-4 py-2 bg-surface-container-low border-none rounded-full text-sm focus:ring-2 focus:ring-primary/40 w-64 transition-all" placeholder="Search data..." type="text"/>
          </div>
          <button className="w-10 h-10 flex items-center justify-center rounded-full text-[#60557f] hover:bg-surface-container transition-all">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="w-10 h-10 flex items-center justify-center rounded-full text-[#60557f] hover:bg-surface-container transition-all">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <img alt="User profile" className="w-8 h-8 rounded-full border border-outline-variant/20 object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCtEn1A95scoUemYdcriTdMBL5Dmilo1iNLwR6CZjJ1KxQx0zJXWwsUfJK7w_IFnEtBVJc1rMr4klGlBrAqPujuwQLlcPtde_1Bhp0qxh__kIy4DryoirRMPXOiL3_oN2tUEjsHkSVrrX6ai8dsYH_VFTSmXa6wFbSqprGXz4bpS17g1FcKz9lDP49U7wzxYdhCjWtM7T0IK-xYfpgvlTNHpvSrb9brkWfg2qNE22Vyl3XurL-keNIu6fNMycz_ahXT6at7JhNPY8td" />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="lg:pl-72 p-6 pb-32">
        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {/* Total Workers (Blue) */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] group hover:translate-y-[-4px] transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">engineering</span>
              </div>
              <span className="text-primary text-xs font-bold px-2 py-1 bg-primary/5 rounded-lg">+0%</span>
            </div>
            <h3 className="text-on-surface-variant text-sm font-medium">Total Workers</h3>
            <p className="text-2xl font-black text-on-surface mt-1">{loading ? '...' : stats.total_workers}</p>
          </div>
          {/* Pending Approvals (Orange) */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] group hover:translate-y-[-4px] transition-all border-l-4 border-[#ff9100]/20">
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-2xl bg-[#ff9100]/10 flex items-center justify-center text-[#ff9100]">
                <span className="material-symbols-outlined">pending_actions</span>
              </div>
              {stats.pending_approvals > 0 && (
                <div className="flex items-center gap-2">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ff9100] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-[#ff9100]"></span>
                  </span>
                  <span className="text-[#ff9100] text-xs font-bold uppercase tracking-tighter">Urgent</span>
                </div>
              )}
            </div>
            <h3 className="text-on-surface-variant text-sm font-medium">Pending Approvals</h3>
            <p className="text-2xl font-black text-on-surface mt-1">{loading ? '...' : stats.pending_approvals}</p>
          </div>
          {/* Total Users (Green) */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] group hover:translate-y-[-4px] transition-all">
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-600">
                <span className="material-symbols-outlined">group</span>
              </div>
              <span className="text-emerald-600 text-xs font-bold px-2 py-1 bg-emerald-50 rounded-lg">+0%</span>
            </div>
            <h3 className="text-on-surface-variant text-sm font-medium">Total Users</h3>
            <p className="text-2xl font-black text-on-surface mt-1">{loading ? '...' : stats.total_users}</p>
          </div>
          {/* Active Services (Purple) */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] group hover:translate-y-[-4px] transition-all bg-gradient-to-br from-white to-[#fbf4ff]">
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">hub</span>
              </div>
              <span className="material-symbols-outlined text-primary/40">more_vert</span>
            </div>
            <h3 className="text-on-surface-variant text-sm font-medium">Active Services</h3>
            <p className="text-2xl font-black text-on-surface mt-1">{loading ? '...' : stats.active_services} Sections</p>
          </div>
        </div>

        {/* Section Title */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold tracking-tight text-on-surface">Service Directory</h2>
          <div className="flex items-center gap-2">
            <span className="text-xs text-on-surface-variant font-medium">Sort by:</span>
            <button className="text-xs font-bold text-primary flex items-center gap-1 bg-primary/5 px-3 py-1.5 rounded-full">
              Priority
              <span className="material-symbols-outlined text-[16px]">expand_more</span>
            </button>
          </div>
        </div>

        {/* Bento Grid Services */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Healthcare Card */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex flex-col justify-between min-h-[220px]">
            <div>
              <div className="flex justify-between items-start">
                <div className="p-3 bg-red-50 text-red-500 rounded-xl">
                  <span className="material-symbols-outlined">medical_services</span>
                </div>
                {stats.services.healthcare.pending > 0 ? (
                  <span className="bg-[#ff9100]/10 text-[#ff9100] text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    {stats.services.healthcare.pending} PENDING
                  </span>
                ) : (
                  <span className="bg-emerald-50 text-emerald-600 text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    ALL CLEAR
                  </span>
                )}
              </div>
              <h3 className="mt-4 font-headline text-lg font-bold">Healthcare Workers</h3>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Total Pool</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.healthcare.total}</p>
                </div>
                <div className="w-[1px] h-8 bg-outline-variant/15"></div>
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Pending</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.healthcare.pending}</p>
                </div>
              </div>
            </div>
            <button 
              onClick={() => navigate('/admin/healthcare')}
              className="mt-6 w-full py-3 bg-surface-container text-primary font-bold rounded-xl text-sm hover:bg-primary/10 transition-colors"
            >
              Manage Fleet
            </button>
          </div>
          {/* Car Service Card */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex flex-col justify-between min-h-[220px]">
            <div>
              <div className="flex justify-between items-start">
                <div className="p-3 bg-blue-50 text-blue-500 rounded-xl">
                  <span className="material-symbols-outlined">directions_car</span>
                </div>
                {stats.services.car_service.pending > 0 ? (
                  <span className="bg-[#ff9100]/10 text-[#ff9100] text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    {stats.services.car_service.pending} PENDING
                  </span>
                ) : (
                  <span className="bg-emerald-50 text-emerald-600 text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    ALL CLEAR
                  </span>
                )}
              </div>
              <h3 className="mt-4 font-headline text-lg font-bold">Car Service Workers</h3>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Total Pool</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.car_service.total}</p>
                </div>
                <div className="w-[1px] h-8 bg-outline-variant/15"></div>
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Pending</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.car_service.pending}</p>
                </div>
              </div>
            </div>
            <button className="mt-6 w-full py-3 bg-surface-container text-primary font-bold rounded-xl text-sm hover:bg-primary/10 transition-colors">Manage Fleet</button>
          </div>
          {/* Housekeeping Card */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex flex-col justify-between min-h-[220px]">
            <div>
              <div className="flex justify-between items-start">
                <div className="p-3 bg-amber-50 text-amber-500 rounded-xl">
                  <span className="material-symbols-outlined">cleaning_services</span>
                </div>
                {stats.services.housekeeping.pending > 0 ? (
                  <span className="bg-[#ff9100]/10 text-[#ff9100] text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    {stats.services.housekeeping.pending} PENDING
                  </span>
                ) : (
                  <span className="bg-emerald-50 text-emerald-600 text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    ALL CLEAR
                  </span>
                )}
              </div>
              <h3 className="mt-4 font-headline text-lg font-bold">Housekeeping Workers</h3>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Total Pool</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.housekeeping.total}</p>
                </div>
                <div className="w-[1px] h-8 bg-outline-variant/15"></div>
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Pending</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.housekeeping.pending}</p>
                </div>
              </div>
            </div>
            <button className="mt-6 w-full py-3 bg-surface-container text-primary font-bold rounded-xl text-sm hover:bg-primary/10 transition-colors">Manage Fleet</button>
          </div>
          {/* Freelancers Card */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex flex-col justify-between min-h-[220px]">
            <div>
              <div className="flex justify-between items-start">
                <div className="p-3 bg-violet-50 text-violet-500 rounded-xl">
                  <span className="material-symbols-outlined">work</span>
                </div>
                {stats.services.freelance.pending > 0 ? (
                  <span className="bg-[#ff9100]/10 text-[#ff9100] text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    {stats.services.freelance.pending} PENDING
                  </span>
                ) : (
                  <span className="bg-emerald-50 text-emerald-600 text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    ALL CLEAR
                  </span>
                )}
              </div>
              <h3 className="mt-4 font-headline text-lg font-bold">Freelance Pros</h3>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Total Pool</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.freelance.total}</p>
                </div>
                <div className="w-[1px] h-8 bg-outline-variant/15"></div>
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Pending</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.freelance.pending}</p>
                </div>
              </div>
            </div>
            <button className="mt-6 w-full py-3 bg-surface-container text-primary font-bold rounded-xl text-sm hover:bg-primary/10 transition-colors">Manage Fleet</button>
          </div>
          {/* Money Service Card */}
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex flex-col justify-between min-h-[220px]">
            <div>
              <div className="flex justify-between items-start">
                <div className="p-3 bg-emerald-50 text-emerald-500 rounded-xl">
                  <span className="material-symbols-outlined">payments</span>
                </div>
                {stats.services.money_management.pending > 0 ? (
                  <span className="bg-[#ff9100]/10 text-[#ff9100] text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    {stats.services.money_management.pending} PENDING
                  </span>
                ) : (
                  <span className="bg-emerald-50 text-emerald-600 text-[10px] font-black px-2 py-1 rounded-full flex items-center gap-1">
                    ALL CLEAR
                  </span>
                )}
              </div>
              <h3 className="mt-4 font-headline text-lg font-bold">Money Service</h3>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Total Pool</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.money_management.total}</p>
                </div>
                <div className="w-[1px] h-8 bg-outline-variant/15"></div>
                <div>
                  <p className="text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">Pending</p>
                  <p className="text-lg font-black text-on-surface">{loading ? '...' : stats.services.money_management.pending}</p>
                </div>
              </div>
            </div>
            <button className="mt-6 w-full py-3 bg-surface-container text-primary font-bold rounded-xl text-sm hover:bg-primary/10 transition-colors">Manage Fleet</button>
          </div>
          {/* Add Service Placeholder (Bento Grid Design) */}
          <div className="border-2 border-dashed border-outline-variant/30 p-6 rounded-xl flex flex-col items-center justify-center min-h-[220px] hover:border-primary/40 transition-all cursor-pointer group">
            <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant group-hover:bg-primary group-hover:text-white transition-all">
              <span className="material-symbols-outlined">add</span>
            </div>
            <p className="mt-4 font-headline font-bold text-on-surface-variant">Configure New Section</p>
            <p className="text-xs text-on-surface-variant/60 text-center mt-1">Scale your ecosystem with custom data models</p>
          </div>
        </div>
      </main>

      {/* Mobile Bottom NavBar */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-t border-[#b3a6d5]/15 shadow-[0_-10px_25px_rgba(0,0,0,0.05)] rounded-t-2xl">
        <Link className="flex flex-col items-center justify-center bg-[#ede4ff] dark:bg-slate-800 text-[#4c40df] rounded-2xl p-2 min-w-[64px]" to="/admin/dashboard">
          <span className="material-symbols-outlined">dashboard</span>
          <span className="text-[10px] font-medium font-body">Home</span>
        </Link>
        <Link className="flex flex-col items-center justify-center text-[#60557f] p-2 min-w-[64px] active:bg-[#fbf4ff]" to="/admin/healthcare">
          <span className="material-symbols-outlined">medical_services</span>
          <span className="text-[10px] font-medium font-body">Health</span>
        </Link>
        <a className="flex flex-col items-center justify-center text-[#60557f] p-2 min-w-[64px] active:bg-[#fbf4ff]" href="#">
          <span className="material-symbols-outlined">directions_car</span>
          <span className="text-[10px] font-medium font-body">Auto</span>
        </a>
        <a className="flex flex-col items-center justify-center text-[#60557f] p-2 min-w-[64px] active:bg-[#fbf4ff]" href="#">
          <span className="material-symbols-outlined">cleaning_services</span>
          <span className="text-[10px] font-medium font-body">Home</span>
        </a>
        <a className="flex flex-col items-center justify-center text-[#60557f] p-2 min-w-[64px] active:bg-[#fbf4ff]" href="#">
          <span className="material-symbols-outlined">group</span>
          <span className="text-[10px] font-medium font-body">Users</span>
        </a>
      </nav>
    </div>
  );
};

export default AdminDashboard;
