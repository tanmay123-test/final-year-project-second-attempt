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
  TrendingUp,
  TrendingDown,
  Download,
  Calendar,
  ArrowRight,
  Award,
  Zap,
  CheckCircle2,
  Clock,
  TrendingUp as TrendingUpIcon,
  CheckCircle,
  User as UserIcon
} from 'lucide-react';
import api from '../../../shared/api';

const MechanicEarnings = () => {
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [loading, setLoading] = useState(true);
  const [earningsData, setEarningsData] = useState({
    lifetime: 0,
    today: 0,
    week: 0,
    month: 0,
    jobsCount: 0,
    transactions: [],
    breakdown: []
  });
  const [workerData, setWorkerData] = useState({
    name: 'Loading...',
    role: 'Mechanic',
    avatar: 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?auto=format&fit=crop&q=80&w=100'
  });

  const token = localStorage.getItem('workerToken');

  const fetchData = useCallback(async () => {
    if (!token) {
      navigate('/worker/car/mechanic/auth');
      return;
    }

    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      
      const [profileRes, earningsRes] = await Promise.all([
        api.get('/api/car/mechanic/profile', { headers }),
        api.get('/api/car/mechanic/earnings', { headers })
      ]);

      if (profileRes.data.mechanic) {
        setWorkerData({
          name: profileRes.data.mechanic.name,
          role: profileRes.data.mechanic.role || 'Mechanic',
          avatar: profileRes.data.mechanic.profile_photo_path || workerData.avatar
        });
        setIsOnline(profileRes.data.mechanic.is_online);
      }

      if (earningsRes.data.success) {
        setEarningsData({
          lifetime: earningsRes.data.summary.lifetime_earnings || 0,
          today: earningsRes.data.summary.today_earnings || 0,
          week: earningsRes.data.summary.weekly_earnings || 0,
          month: earningsRes.data.summary.monthly_earnings || 0,
          jobsCount: earningsRes.data.summary.jobs_this_month || 0,
          transactions: earningsRes.data.transactions || [],
          breakdown: earningsRes.data.breakdown || []
        });
      }
    } catch (err) {
      console.error('Error fetching data:', err);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
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
          <button className="w-full flex items-center space-x-3 px-4 py-3 bg-violet-50 text-violet-600 rounded-lg font-bold text-sm">
            <Wallet size={18} />
            <span>Earnings</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/history')}
            className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all duration-200 font-medium text-sm"
          >
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

        <div className="pt-4 border-t border-slate-100 space-y-1">
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
          <div className="flex items-center gap-8">
            <div className="hidden md:flex items-center bg-slate-100 px-4 py-2 rounded-full gap-2 border border-slate-200">
              <Search size={16} className="text-slate-400" />
              <input 
                className="bg-transparent border-none focus:ring-0 text-sm w-64 outline-none" 
                placeholder="Search earnings..." 
                type="text"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-500 hover:bg-slate-100 transition-colors rounded-full relative">
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
            <div className="h-8 w-8 rounded-full overflow-hidden border border-slate-200 shadow-sm">
              <img 
                alt="Profile" 
                className="w-full h-full object-cover"
                src={workerData.avatar}
              />
            </div>
          </div>
        </header>

        {/* Content Canvas */}
        <div className="mt-16 p-6 md:p-8 space-y-8 flex-1">
          {/* Hero Card */}
          <section>
            <div className="bg-gradient-to-br from-violet-600 to-violet-800 rounded-3xl p-8 text-white flex flex-col md:flex-row justify-between items-start md:items-center relative overflow-hidden shadow-2xl shadow-violet-200">
              <div className="relative z-10">
                <p className="text-violet-100/80 font-medium mb-1 flex items-center gap-2 text-sm">
                  <Wallet size={16} />
                  Lifetime Earnings
                </p>
                <h1 className="text-5xl font-black tracking-tight">₹{earningsData.lifetime.toLocaleString('en-IN')}</h1>
                <p className="mt-4 bg-white/10 backdrop-blur-md inline-block px-4 py-1.5 rounded-full text-xs font-bold border border-white/10 uppercase tracking-wider">
                  Next Payout: {new Date(new Date().setDate(new Date().getDate() + 7)).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                </p>
              </div>
              <div className="mt-8 md:mt-0 relative z-10">
                <button className="bg-white text-violet-700 font-black px-8 py-4 rounded-2xl shadow-xl hover:scale-105 active:scale-95 transition-all">
                  Request Payout
                </button>
              </div>
              {/* Decorative elements */}
              <div className="absolute -right-10 -top-10 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
              <div className="absolute -left-10 -bottom-10 w-48 h-48 bg-black/5 rounded-full blur-2xl"></div>
            </div>
          </section>

          {/* Stats Grid */}
          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-2">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Today</p>
              <div className="flex items-end justify-between">
                <h3 className="text-2xl font-black text-slate-900">₹{earningsData.today.toLocaleString('en-IN')}</h3>
                <span className="text-emerald-600 font-bold text-xs flex items-center gap-0.5 bg-emerald-50 px-2 py-1 rounded-lg">
                  <TrendingUp size={14} /> 12%
                </span>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-2">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">This Week</p>
              <div className="flex items-end justify-between">
                <h3 className="text-2xl font-black text-slate-900">₹{earningsData.week.toLocaleString('en-IN')}</h3>
                <span className="text-emerald-600 font-bold text-xs flex items-center gap-0.5 bg-emerald-50 px-2 py-1 rounded-lg">
                  <TrendingUp size={14} /> 5%
                </span>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border-l-4 border-l-orange-500 border border-slate-100 shadow-sm flex flex-col gap-2">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">This Month</p>
              <div className="flex items-end justify-between">
                <h3 className="text-2xl font-black text-slate-900">₹{earningsData.month.toLocaleString('en-IN')}</h3>
                <span className="text-red-500 font-bold text-xs flex items-center gap-0.5 bg-red-50 px-2 py-1 rounded-lg">
                  <TrendingDown size={14} /> 2%
                </span>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col gap-2">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Jobs This Month</p>
              <div className="flex items-end justify-between">
                <h3 className="text-2xl font-black text-slate-900">{earningsData.jobsCount}</h3>
                <span className="bg-violet-100 text-violet-700 px-2 py-1 rounded text-[10px] font-black uppercase tracking-wider">Expert</span>
              </div>
            </div>
          </section>

          {/* Chart & Insights */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 bg-white p-8 rounded-3xl border border-slate-100 shadow-sm">
              <div className="flex justify-between items-center mb-10">
                <h2 className="font-black text-xl text-slate-900">Earnings Breakdown</h2>
                <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
                  <button className="px-4 py-1.5 rounded-lg text-xs font-bold bg-white text-violet-600 shadow-sm">Last 6 Months</button>
                  <button className="px-4 py-1.5 rounded-lg text-xs font-bold text-slate-500 hover:text-violet-600">Yearly</button>
                </div>
              </div>
              
              {/* Chart Area */}
              <div className="flex items-end justify-between h-56 gap-4 px-2">
                {earningsData.breakdown.length > 0 ? (
                  earningsData.breakdown.map((item, i) => (
                    <div key={i} className="flex flex-col items-center flex-1 group">
                      <div className="w-full bg-slate-100 rounded-t-xl h-48 group-hover:bg-violet-50 transition-all relative overflow-hidden cursor-pointer">
                        <div 
                          className={`absolute bottom-0 w-full ${item.active ? 'bg-violet-500' : 'bg-violet-200'} rounded-t-xl transition-all`}
                          style={{ height: `${(item.amount / Math.max(...earningsData.breakdown.map(b => b.amount))) * 100}%` }}
                        ></div>
                      </div>
                      <span className={`text-[10px] font-bold mt-4 tracking-widest ${item.active ? 'text-violet-600 font-black' : 'text-slate-400'}`}>{item.label}</span>
                    </div>
                  ))
                ) : (
                  <div className="w-full flex items-center justify-center text-slate-300 font-bold italic">No data available</div>
                )}
              </div>
            </div>

            <div className="bg-white p-8 rounded-3xl border border-slate-100 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-violet-100 rounded-xl text-violet-600">
                    <Award size={24} />
                  </div>
                  <h2 className="font-black text-xl text-slate-900">Worker Insight</h2>
                </div>
                <p className="text-sm text-slate-500 leading-relaxed">
                  Your earnings are <span className="text-violet-600 font-bold">consistent</span> this month. Keep up the great work to maintain your <span className="text-orange-500 font-bold">Expert</span> status.
                </p>
              </div>
              
              <div className="mt-8">
                <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-start gap-4">
                  <div className="p-1.5 bg-emerald-100 rounded-lg text-emerald-600">
                    <Zap size={18} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-emerald-900 mb-1">Expert Tip!</p>
                    <p className="text-[11px] text-emerald-700 leading-relaxed font-medium">Being online during peak hours (6pm-9pm) can increase your chances of getting high-value jobs.</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Transaction Table */}
          <section className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="p-8 flex justify-between items-center border-b border-slate-50">
              <h2 className="font-black text-xl text-slate-900">Transaction History</h2>
              <button className="text-violet-600 font-bold text-sm flex items-center gap-2 bg-violet-50 px-4 py-2 rounded-xl hover:bg-violet-100 transition-colors group">
                Download Report 
                <Download size={16} className="group-hover:translate-y-0.5 transition-transform" />
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-slate-50/50 text-slate-400 uppercase text-[10px] tracking-widest font-black">
                    <th className="px-8 py-5">Date</th>
                    <th className="px-6 py-5">Customer</th>
                    <th className="px-6 py-5">Job Type</th>
                    <th className="px-6 py-5">Gross</th>
                    <th className="px-6 py-5">Commission</th>
                    <th className="px-6 py-5">Net Earnings</th>
                    <th className="px-8 py-5">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {earningsData.transactions.length > 0 ? (
                    earningsData.transactions.map((txn) => (
                      <tr key={txn.id} className="hover:bg-slate-50/50 transition-colors group">
                        <td className="px-8 py-6 text-sm font-medium text-slate-500">{new Date(txn.created_at).toLocaleDateString()}</td>
                        <td className="px-6 py-6">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full overflow-hidden border border-slate-100 flex items-center justify-center bg-slate-50">
                              {txn.avatar ? <img alt={txn.user_name} className="w-full h-full object-cover" src={txn.avatar}/> : <UserIcon size={16} className="text-slate-400" />}
                            </div>
                            <span className="font-bold text-sm text-slate-900">{txn.user_name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-6">
                          <span className={`px-2.5 py-1 text-[10px] font-bold rounded-lg uppercase tracking-wider bg-slate-100 text-slate-600`}>
                            {txn.issue || 'Service'}
                          </span>
                        </td>
                        <td className="px-6 py-6 text-sm font-bold text-slate-900">₹{(txn.base_amount || 0).toLocaleString('en-IN')}</td>
                        <td className="px-6 py-6 text-sm font-bold text-red-500">- ₹{(txn.platform_commission || 0).toLocaleString('en-IN')}</td>
                        <td className="px-6 py-6 text-sm font-black text-emerald-600">₹{(txn.final_amount || 0).toLocaleString('en-IN')}</td>
                        <td className="px-8 py-6">
                          <span className={`px-4 py-1.5 rounded-full text-[10px] font-bold ${
                            txn.status === 'Paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                          }`}>
                            {txn.status || 'Paid'}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="px-8 py-12 text-center text-slate-400 font-medium italic">No transactions found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
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
          <button className="flex flex-col items-center text-violet-600">
            <Wallet size={20} />
            <span className="text-[10px] font-bold mt-1">Earn</span>
          </button>
          <button 
            onClick={() => navigate('/worker/car/mechanic/history')}
            className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
          >
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

export default MechanicEarnings;
