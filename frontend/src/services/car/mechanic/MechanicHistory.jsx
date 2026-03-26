import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
  CheckCircle,
  Star,
  Filter,
  ChevronDown,
  Wrench,
  Droplets,
  Car,
  X
} from 'lucide-react';
import api from '../../../shared/api';

const MechanicHistory = () => {
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({
    total_jobs: 0,
    completion_rate: 0,
    average_rating: 0
  });
  const [workerData, setWorkerData] = useState({
    name: 'Loading...',
    role: 'Mechanic',
    avatar: 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?auto=format&fit=crop&q=80&w=100'
  });
  const [error, setError] = useState(null);

  const token = localStorage.getItem('workerToken');

  const fetchData = useCallback(async () => {
    if (!token) {
      navigate('/worker/car/mechanic/auth');
      return;
    }

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      
      const [profileRes, historyRes, statsRes] = await Promise.all([
        api.get('/api/car/mechanic/profile', { headers }),
        api.get('/api/car/mechanic/earnings/history', { headers }),
        api.get('/api/car/mechanic/stats', { headers })
      ]);

      if (profileRes.data.mechanic) {
        setWorkerData({
          name: profileRes.data.mechanic.name,
          role: profileRes.data.mechanic.role || 'Mechanic',
          avatar: profileRes.data.mechanic.profile_photo_path || workerData.avatar
        });
        setIsOnline(profileRes.data.mechanic.is_online);
      }

      if (historyRes.data.success) {
        setHistory(historyRes.data.history || []);
      }

      if (statsRes.data.success) {
        setStats({
          total_jobs: statsRes.data.stats.total_jobs || 0,
          completion_rate: statsRes.data.stats.completion_rate || 0,
          average_rating: statsRes.data.stats.average_rating || 0
        });
      }

    } catch (err) {
      setError('Failed to load history data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [navigate, token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const toggleStatus = async () => {
    try {
      const newStatus = !isOnline;
      await api.put('/api/car/mechanic/status', {
        is_online: newStatus
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setIsOnline(newStatus);
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/worker/car/services');
  };

  const getJobIcon = (type) => {
    const t = type?.toLowerCase() || '';
    if (t.includes('engine')) return <Wrench size={28} />;
    if (t.includes('oil') || t.includes('fluid')) return <Droplets size={28} />;
    if (t.includes('tire')) return <Wrench size={28} />;
    return <Car size={28} />;
  };

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETED': return 'bg-emerald-100 text-emerald-700';
      case 'CANCELLED': return 'bg-red-100 text-red-700';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-slate-50">
      <div className="w-12 h-12 border-4 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
    </div>;
  }

  return (
    <div className="bg-slate-50 font-sans text-slate-900 flex min-h-screen">
      {/* SideNavBar */}
      <aside className="hidden md:flex flex-col h-screen w-64 fixed left-0 top-0 bg-white border-r border-slate-200 py-8 px-4 space-y-2 z-40">
        <div className="px-4 mb-8">
          <h1 className="text-xl font-black text-violet-600 tracking-tighter">ExpertEase</h1>
        </div>
        
        <div className="flex items-center space-x-3 px-4 py-4 mb-6 bg-slate-50 rounded-xl border border-slate-100">
          <img 
            alt={workerData.name} 
            className="w-10 h-10 rounded-full object-cover border-2 border-white shadow-sm" 
            src={workerData.avatar}
          />
          <div>
            <p className="font-bold text-sm text-slate-900">{workerData.name}</p>
            <p className="text-xs text-slate-500">{workerData.role}</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1">
          <button 
            onClick={() => navigate('/worker/car/mechanic/dashboard')}
            className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all duration-200 font-medium text-sm"
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/jobs-queue')}
            className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all duration-200 font-medium text-sm"
          >
            <ListChecks size={18} />
            <span>Jobs Queue</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/earnings')}
            className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all duration-200 font-medium text-sm"
          >
            <Wallet size={18} />
            <span>Earnings</span>
          </button>
          <button className="w-full flex items-center space-x-3 px-4 py-3 bg-violet-50 text-violet-600 rounded-lg font-bold text-sm">
            <History size={18} />
            <span>History</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/settings')}
            className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all duration-200 font-medium text-sm"
          >
            <Settings size={18} />
            <span>Settings</span>
          </button>
        </nav>

        <div className="pt-4 border-t border-slate-100">
          <button 
            onClick={toggleStatus}
            className={`w-full font-bold py-3 rounded-xl mb-4 transition-all shadow-md ${
              isOnline ? 'bg-violet-600 text-white shadow-violet-200 hover:bg-violet-700' : 'bg-slate-200 text-slate-500 shadow-none'
            }`}
          >
            {isOnline ? 'Go Offline' : 'Go Online'}
          </button>
          <button className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 transition-colors text-sm font-medium">
            <HelpCircle size={18} />
            <span>Support</span>
          </button>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center space-x-3 px-4 py-3 text-red-500 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 md:ml-64 relative flex flex-col">
        {/* TopAppBar */}
        <header className="fixed top-0 right-0 left-0 md:left-64 z-30 bg-white/80 backdrop-blur-md border-b border-slate-200 h-16 flex justify-between items-center px-6">
          <div className="flex items-center flex-1 max-w-md">
            <div className="relative w-full">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                className="w-full bg-slate-100 border-none rounded-full py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-violet-500 transition-all outline-none" 
                placeholder="Search jobs, cars, or customers..." 
                type="text"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-full relative transition-colors">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
            <button 
              onClick={toggleStatus}
              className={`flex items-center transition-colors ${isOnline ? 'text-green-500' : 'text-slate-400'}`}
            >
              <div className={`w-10 h-5 rounded-full relative transition-colors ${isOnline ? 'bg-green-100' : 'bg-slate-200'}`}>
                <div className={`absolute top-1 w-3 h-3 rounded-full transition-all ${isOnline ? 'right-1 bg-green-500' : 'left-1 bg-slate-400'}`}></div>
              </div>
            </button>
            <div className="w-8 h-8 rounded-full overflow-hidden border border-slate-200">
              <img src={workerData.avatar} alt="Profile" className="w-full h-full object-cover" />
            </div>
          </div>
        </header>

        {/* Content Canvas */}
        <div className="mt-16 p-6 md:p-8 space-y-8 flex-1">
          <div className="max-w-6xl mx-auto">
            {/* Page Title */}
            <div className="mb-10">
              <h1 className="text-4xl font-black tracking-tight text-slate-900">Job History</h1>
              <p className="text-slate-500 mt-2 font-medium">Manage and review your past service interactions.</p>
            </div>

            {/* Bento Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm transition-all hover:-translate-y-1">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-violet-100 rounded-xl text-violet-600">
                    <History size={24} />
                  </div>
                </div>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Total Jobs</h3>
                <p className="text-3xl font-black text-slate-900 mt-1">{stats.total_jobs}</p>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm transition-all hover:-translate-y-1">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-emerald-100 rounded-xl text-emerald-600">
                    <CheckCircle size={24} />
                  </div>
                </div>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Completion Rate</h3>
                <p className="text-3xl font-black text-slate-900 mt-1">{stats.completion_rate}%</p>
                <div className="w-full bg-slate-100 h-2 rounded-full mt-4 overflow-hidden">
                  <div className="bg-emerald-50 h-full rounded-full" style={{ width: `${stats.completion_rate}%` }}></div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm transition-all hover:-translate-y-1">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-amber-100 rounded-xl text-amber-600">
                    <Star size={24} fill="currentColor" />
                  </div>
                </div>
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Average Rating</h3>
                <p className="text-3xl font-black text-slate-900 mt-1">{stats.average_rating}</p>
                <div className="flex mt-3 gap-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <Star key={s} size={14} className={s <= Math.round(stats.average_rating) ? "text-amber-500" : "text-slate-200"} fill="currentColor" />
                  ))}
                </div>
              </div>
            </div>

            {/* Filters & Controls */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <div className="flex items-center space-x-2 overflow-x-auto no-scrollbar pb-2 md:pb-0">
                <button className="px-5 py-2.5 bg-violet-600 text-white rounded-full text-sm font-bold whitespace-nowrap shadow-lg shadow-violet-100">All Jobs</button>
                <button className="px-5 py-2.5 bg-white text-slate-500 border border-slate-100 rounded-full text-sm font-bold whitespace-nowrap hover:bg-slate-50 transition-colors">Completed</button>
                <button className="px-5 py-2.5 bg-white text-slate-500 border border-slate-100 rounded-full text-sm font-bold whitespace-nowrap hover:bg-slate-50 transition-colors">Cancelled</button>
              </div>
            </div>

            {/* Job History List */}
            <div className="space-y-6">
              {history.length > 0 ? (
                history.map((job) => (
                  <div key={job.id} className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-all group cursor-pointer">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                      <div className="flex items-start space-x-5">
                        <div className="w-14 h-14 bg-violet-50 rounded-2xl flex items-center justify-center shrink-0 text-violet-600">
                          {getJobIcon(job.issue_type || job.issue)}
                        </div>
                        <div>
                          <div className="flex items-center gap-3 mb-1">
                            <h4 className="text-lg font-black text-slate-900">{job.issue || 'Service Job'}</h4>
                            <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider ${getStatusColor(job.status || 'COMPLETED')}`}>
                              {job.status || 'COMPLETED'}
                            </span>
                          </div>
                          <p className="text-sm text-slate-500 font-medium">
                            {job.car_model || 'Unknown Vehicle'} • <span className="text-slate-900 font-bold">{job.user_name || 'Customer'}</span>
                          </p>
                          <div className="flex items-center mt-3 gap-4">
                            <div className="flex items-center text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-lg">
                              <Star size={14} fill="currentColor" className="mr-1" />
                              {job.rating || '5.0'}
                            </div>
                            {job.review && (
                              <p className="text-xs italic text-slate-400 font-medium">"{job.review}"</p>
                            )}
                          </div>
                          <p className="text-[10px] text-slate-400 mt-2 font-bold uppercase tracking-widest">
                            {new Date(job.created_at).toLocaleDateString('en-IN', { 
                              day: 'numeric', month: 'short', year: 'numeric' 
                            })}
                          </p>
                        </div>
                      </div>
                      <div className="flex lg:flex-col items-end justify-between lg:justify-center gap-2 shrink-0">
                        <p className="text-2xl font-black text-slate-900 tracking-tight">₹{job.final_amount || 0}</p>
                        <button className="text-violet-600 font-black text-[10px] uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">View Details</button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-200">
                  <History size={48} className="mx-auto text-slate-300 mb-4" />
                  <h3 className="text-xl font-bold text-slate-900">No job history found</h3>
                  <p className="text-slate-500">You haven't completed any jobs yet.</p>
                </div>
              )}
            </div>

            {/* Load More */}
            {history.length > 0 && (
              <div className="mt-12 mb-20 flex justify-center">
                <button className="px-10 py-4 bg-white border border-slate-100 text-slate-900 font-black text-xs uppercase tracking-widest rounded-2xl hover:bg-slate-50 transition-all flex items-center gap-3 shadow-sm active:scale-95">
                  <ChevronDown size={20} />
                  <span>Load Previous Jobs</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Bottom Navigation */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-md flex justify-around items-center px-4 z-40 border-t border-slate-200">
          <button 
            onClick={() => navigate('/worker/car/mechanic/dashboard')}
            className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
          >
            <LayoutDashboard size={20} />
            <span className="text-[10px] font-bold mt-1">Dash</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/jobs-queue')}
            className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
          >
            <ListChecks size={20} />
            <span className="text-[10px] font-bold mt-1">Queue</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/earnings')}
            className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
          >
            <Wallet size={20} />
            <span className="text-[10px] font-bold mt-1">Earn</span>
          </button>
          <button className="flex flex-col items-center text-violet-600">
            <History size={20} />
            <span className="text-[10px] font-bold mt-1">History</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/settings')}
            className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
          >
            <Settings size={20} />
            <span className="text-[10px] font-bold mt-1">Settings</span>
          </button>
        </nav>
      </main>
    </div>
  );
};

export default MechanicHistory;
