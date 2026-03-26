import React, { useState, useEffect } from 'react';
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
  MapPin, 
  Car, 
  User as UserIcon, 
  ArrowRight,
  RefreshCw,
  Map,
  Fuel
} from 'lucide-react';
import api from '../../../shared/api';

const MechanicJobsQueue = () => {
  const navigate = useNavigate();
  const [isOnline, setIsOnline] = useState(true);
  const [jobs, setPendingJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [workerData, setWorkerData] = useState({
    name: 'Loading...',
    role: 'Mechanic',
    avatar: 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?auto=format&fit=crop&q=80&w=100'
  });

  useEffect(() => {
    fetchJobs();
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/api/car/mechanic/profile');
      if (res.data.mechanic) {
        setWorkerData({
          name: res.data.mechanic.name,
          role: res.data.mechanic.role || 'Mechanic',
          avatar: res.data.mechanic.profile_photo_path || workerData.avatar
        });
        setIsOnline(res.data.mechanic.status === 'ONLINE');
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    }
  };

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/car/mechanic/jobs');
      setPendingJobs(res.data.jobs || []);
    } catch (err) {
      console.error('Error fetching jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptJob = async (jobId) => {
    try {
      await api.post('/api/car/mechanic/job/accept', { job_id: jobId });
      navigate('/worker/car/mechanic/dashboard');
    } catch (err) {
      console.error('Error accepting job:', err);
      alert('Failed to accept job');
    }
  };

  const handleRejectJob = async (jobId) => {
    try {
      await api.post('/api/car/mechanic/job/reject', { job_id: jobId });
      fetchJobs();
    } catch (err) {
      console.error('Error rejecting job:', err);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/worker/car/services');
  };

  const toggleStatus = async () => {
    try {
      const newStatus = !isOnline;
      const token = localStorage.getItem('workerToken');
      await api.put('/api/car/mechanic/status', {
        is_online: newStatus
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      setIsOnline(newStatus);
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

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
            className="w-full flex items-center space-x-3 px-4 py-3 bg-violet-50 text-violet-600 rounded-lg font-bold text-sm"
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
          <div className="flex items-center space-x-4">
            <h2 className="font-bold text-xl tracking-tight text-slate-900">Jobs Queue</h2>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative hidden sm:block">
              <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                className="bg-slate-100 border-none rounded-full pl-10 pr-4 py-2 text-sm w-64 focus:ring-2 focus:ring-violet-500 transition-all outline-none" 
                placeholder="Search tasks..." 
                type="text"
              />
            </div>
            <button className="p-2 text-slate-500 hover:bg-slate-100 rounded-full relative transition-colors">
              <Bell size={20} />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
            <button 
              onClick={() => setIsOnline(!isOnline)}
              className={`flex items-center transition-colors ${isOnline ? 'text-green-500' : 'text-slate-400'}`}
            >
              <div className={`w-10 h-5 rounded-full relative transition-colors ${isOnline ? 'bg-green-100' : 'bg-slate-200'}`}>
                <div className={`absolute top-1 w-3 h-3 rounded-full transition-all ${isOnline ? 'right-1 bg-green-500' : 'left-1 bg-slate-400'}`}></div>
              </div>
            </button>
          </div>
        </header>

        {/* Content Canvas */}
        <div className="mt-16 p-6 md:p-8 space-y-8 flex-1">
          {/* Page Header & Tab Navigation */}
          <section className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-violet-600 mb-1">Worker Terminal</p>
                <h1 className="text-3xl md:text-4xl font-black tracking-tight text-slate-900">Available Jobs</h1>
              </div>
              <div className="flex bg-slate-100 p-1 rounded-xl w-fit border border-slate-200">
                <button className="px-6 py-2 rounded-lg text-sm font-bold bg-white text-violet-600 shadow-sm border border-slate-100">Pending (4)</button>
                <button className="px-6 py-2 rounded-lg text-sm font-medium text-slate-500 hover:text-violet-600 transition-colors">Active</button>
                <button className="px-6 py-2 rounded-lg text-sm font-medium text-slate-500 hover:text-violet-600 transition-colors">Completed Today</button>
              </div>
            </div>
          </section>

          {/* Jobs Grid */}
          <section className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-6">
            {jobs.length > 0 ? (
              jobs.map((job) => (
                <div key={job.id} className="bg-white rounded-2xl p-6 flex flex-col justify-between border border-slate-100 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300">
                  <div className="space-y-4">
                    <div className="flex justify-between items-start">
                      <div className="flex flex-col">
                        <span className={`text-white text-[10px] font-bold px-2.5 py-1 rounded-full w-fit mb-3 uppercase tracking-wider ${
                          job.priority === 'URGENT' ? 'bg-red-500' : 'bg-violet-500'
                        }`}>
                          {job.priority || 'Maintenance'}
                        </span>
                        <h3 className="text-xl font-bold text-slate-900 leading-tight">{job.issue || 'General Repair'}</h3>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Estimated Fare</p>
                        <p className="text-2xl font-black text-violet-600">₹{job.estimated_earning || '0'}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-y-3 gap-x-4 pt-2">
                      <div className="flex items-center space-x-2.5 text-slate-600">
                        <Car size={16} className="text-slate-400" />
                        <span className="text-sm font-medium">{job.car_model || 'Unknown Vehicle'}</span>
                      </div>
                      <div className="flex items-center space-x-2.5 text-slate-600">
                        <UserIcon size={16} className="text-slate-400" />
                        <span className="text-sm font-medium">{job.user_name || 'Customer'}</span>
                      </div>
                      <div className="flex items-center space-x-2.5 text-slate-600">
                        <MapPin size={16} className="text-slate-400" />
                        <span className="text-sm font-medium">{job.user_city || 'Local Area'}</span>
                      </div>
                      <div className="flex items-center space-x-2.5 text-slate-600">
                        <RefreshCw size={16} className="text-slate-400" />
                        <span className="text-sm font-medium">{job.distance_km || '0.5'} km away</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-3 mt-8">
                    <button 
                      onClick={() => handleRejectJob(job.id)}
                      className="flex-1 bg-slate-50 text-red-500 font-bold py-3 rounded-xl hover:bg-red-50 border border-slate-100 transition-colors"
                    >
                      Decline
                    </button>
                    <button 
                      onClick={() => handleAcceptJob(job.id)}
                      className="flex-[2] bg-violet-600 text-white font-bold py-3 rounded-xl hover:bg-violet-700 shadow-lg shadow-violet-100 active:scale-95 transition-all"
                    >
                      Accept Job
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full py-20 flex flex-col items-center justify-center bg-white rounded-3xl border border-dashed border-slate-200">
                <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                  <ListChecks size={40} className="text-slate-300" />
                </div>
                <h3 className="text-xl font-bold text-slate-900">No pending jobs</h3>
                <p className="text-slate-500 mt-1">Check back later or try moving to a busier zone.</p>
              </div>
            )}
          </section>

          {/* Bottom Information Panel (Bento style) */}
          <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="col-span-1 md:col-span-2 bg-slate-900 rounded-3xl p-8 flex flex-col md:flex-row items-center justify-between overflow-hidden relative border border-slate-800 shadow-xl">
              <div className="z-10 max-w-sm">
                <h4 className="text-2xl font-bold text-white mb-3">Route Optimization</h4>
                <p className="text-slate-400 text-sm leading-relaxed mb-6">We've calculated the best route for your current pending jobs to maximize your fuel efficiency and minimize travel time.</p>
                <button className="text-violet-400 font-bold text-sm flex items-center gap-2 hover:gap-3 transition-all group">
                  View Suggested Route 
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
              <div className="absolute right-0 top-0 h-full w-1/2 opacity-30 pointer-events-none bg-gradient-to-l from-violet-500/20 to-transparent">
                {/* Decorative map image placeholder */}
                <div className="w-full h-full bg-[url('https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&q=80&w=1000')] bg-cover opacity-50"></div>
              </div>
            </div>
            
            <div className="bg-amber-100 text-amber-900 rounded-3xl p-8 flex flex-col justify-center border border-amber-200 shadow-sm relative overflow-hidden group">
              <div className="absolute -right-4 -top-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
                <Fuel size={120} />
              </div>
              <Fuel size={32} className="mb-4 text-amber-600" />
              <h4 className="text-xl font-bold">Fuel Rewards</h4>
              <p className="text-sm mt-2 text-amber-800 leading-relaxed">Complete 2 more jobs today to unlock your <span className="font-bold">₹500</span> fuel voucher.</p>
              <div className="mt-6 w-full bg-amber-200/50 rounded-full h-2 overflow-hidden">
                <div className="bg-amber-600 h-full w-[60%] rounded-full"></div>
              </div>
            </div>
          </section>
        </div>

        {/* FAB (Floating Action Button) */}
        <button className="fixed bottom-8 right-8 w-14 h-14 bg-violet-600 text-white rounded-full shadow-2xl flex items-center justify-center hover:scale-110 hover:bg-violet-700 active:scale-95 transition-all z-50">
          <Map size={24} />
        </button>
      </main>

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
          className="flex flex-col items-center text-violet-600"
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
        <button 
          onClick={() => navigate('/worker/car/mechanic/history')}
          className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
        >
          <History size={20} />
          <span className="text-[10px] font-bold mt-1">History</span>
        </button>
        <button 
          onClick={() => navigate('/worker/car/mechanic/profile')}
          className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
        >
          <UserIcon size={20} />
          <span className="text-[10px] font-bold mt-1">Profile</span>
        </button>
      </nav>
    </div>
  );
};

export default MechanicJobsQueue;
