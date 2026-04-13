import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminFreelance = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' or 'approved'
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    total_workers: 0,
    pending_review: 0,
    active_projects: 892, // Mock value
    platform_rating: 4.9
  });

  const token = localStorage.getItem('token');
  const API_BASE_URL = 'http://localhost:5000';

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/workers/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(prev => ({ ...prev, ...data }));
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchWorkers = async () => {
    setLoading(true);
    try {
      // For freelance, we might want to filter by service if there are multiple worker types
      // Assuming 'freelance' is a service type or we just get all and filter locally
      const status = activeTab === 'pending' ? 'pending' : 'approved';
      const response = await fetch(`${API_BASE_URL}/admin/workers/?status=${status}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setWorkers(data.workers || []);
      } else {
        setError('Failed to fetch workers');
      }
    } catch (err) {
      console.error('Error fetching workers:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    fetchWorkers();
  }, [activeTab]);

  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  const handleApprove = async (workerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/workers/${workerId}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        fetchWorkers();
        fetchStats();
        // Show success notification (simplified)
        alert('Worker approved successfully!');
      }
    } catch (err) {
      console.error('Error approving worker:', err);
    }
  };

  const handleDecline = async (workerId) => {
    if (!window.confirm('Are you sure you want to decline this application?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/admin/workers/${workerId}/reject`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rejection_reason: 'Does not meet platform requirements' })
      });
      if (response.ok) {
        fetchWorkers();
        fetchStats();
      }
    } catch (err) {
      console.error('Error rejecting worker:', err);
    }
  };

  const filteredWorkers = workers.filter(worker => 
    worker.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    worker.specialization?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    worker.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-surface text-on-surface min-h-screen font-body">
      <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
      
      <style>{`
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
        .headline-font { font-family: 'Manrope', sans-serif; }
      `}</style>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-0 h-screen overflow-y-auto py-8 px-4 w-64 hidden lg:flex flex-col bg-[#ede4ff] dark:bg-slate-900 shadow-[0px_20px_40px_rgba(42,30,80,0.06)] z-50">
        <div className="mb-10 px-4">
          <h1 className="text-xl font-bold tracking-tight text-[#32284f] dark:text-slate-100 headline-font">Editorial Admin</h1>
          <p className="text-xs text-on-surface-variant font-medium mt-1">The Digital Curator</p>
        </div>
        <nav className="flex-1 space-y-2">
          <Link to="/admin/dashboard" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl group">
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-medium">Dashboard</span>
          </Link>
          <Link to="/admin/healthcare" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl group">
            <span className="material-symbols-outlined">medical_services</span>
            <span className="font-medium">Healthcare</span>
          </Link>
          <Link to="/admin/car-service" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl group">
            <span className="material-symbols-outlined">directions_car</span>
            <span className="font-medium">Car Service</span>
          </Link>
          <Link to="/admin/housekeeping" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl group">
            <span className="material-symbols-outlined">cleaning_services</span>
            <span className="font-medium">Housekeeping</span>
          </Link>
          <Link to="/admin/freelance" className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 text-[#4c40df] font-bold rounded-xl shadow-sm scale-95 transition-transform">
            <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>work</span>
            <span className="font-medium">Freelance</span>
          </Link>
          <Link to="/admin/users" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl group">
            <span className="material-symbols-outlined">group</span>
            <span className="font-medium">Users</span>
          </Link>
        </nav>
        <div className="mt-auto border-t border-outline-variant/15 pt-6">
          <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl w-full text-left">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:pl-64 min-h-screen">
        {/* TopAppBar */}
        <header className="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-40 bg-[#fbf4ff]/50 dark:bg-slate-950/50 backdrop-blur-md">
          <div>
            <h2 className="text-lg font-black text-[#32284f] dark:text-white headline-font">Freelance Professionals</h2>
            <div className="flex items-center gap-2 text-xs text-on-surface-variant">
              <span>ExpertEase</span>
              <span className="material-symbols-outlined text-[10px]">chevron_right</span>
              <span>Admin</span>
              <span className="material-symbols-outlined text-[10px]">chevron_right</span>
              <span className="text-primary font-semibold">Freelance</span>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex relative items-center">
              <input 
                className="pl-10 pr-4 py-2 bg-surface-container-low border-none rounded-full text-sm w-64 focus:ring-2 focus:ring-primary/40 transition-all" 
                placeholder="Search professionals..." 
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <span className="material-symbols-outlined absolute left-3 text-on-surface-variant text-sm">search</span>
            </div>
            <div className="flex items-center gap-4">
              <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors relative">
                <span className="material-symbols-outlined text-on-surface-variant">notifications</span>
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-tertiary rounded-full"></span>
              </button>
              <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors">
                <span className="material-symbols-outlined text-on-surface-variant">settings</span>
              </button>
              <div className="h-8 w-px bg-outline-variant/30 mx-2"></div>
              <img alt="Admin profile" className="w-10 h-10 rounded-full object-cover border-2 border-white shadow-sm" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDom1XRf5pBouZK-BYk_o6W_0ywxsT4TMFJixNz2F4VzQpx1B5x7Vov-SD1HRi9fcWIVCssgqQKLg2HdwfKphcTC4Le6JOlJUuGtlpgKDC39j2kG_63HFSr4zTtI_EPLOKhv3xMWdeTld4Wj45DX5qzKCOqUvbjHgFlrhBACh13L53HLC7THp2qPYinnK69rA1t2Pk70K-GrGYQAdFjsrwAckKGR9JJDt6lVQQkcM-bNAQRGcK24unVtQ8_V0ttVBtFXP_gzWHUTYI7"/>
            </div>
          </div>
        </header>

        {/* Stats Section */}
        <section className="px-6 py-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_10px_30px_rgba(42,30,80,0.03)]">
            <p className="text-on-surface-variant text-xs font-semibold uppercase tracking-wider mb-2">Total Workers</p>
            <div className="flex items-end justify-between">
              <h3 className="text-3xl font-black text-on-surface headline-font">{stats.total_workers.toLocaleString()}</h3>
              <span className="text-green-500 text-xs font-bold bg-green-50 px-2 py-1 rounded-lg flex items-center gap-1">
                <span className="material-symbols-outlined text-xs">trending_up</span> 12%
              </span>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_10px_30px_rgba(42,30,80,0.03)]">
            <p className="text-on-surface-variant text-xs font-semibold uppercase tracking-wider mb-2">Pending Review</p>
            <div className="flex items-end justify-between">
              <h3 className="text-3xl font-black text-on-surface headline-font">{stats.pending_review}</h3>
              <span className="text-tertiary text-xs font-bold bg-tertiary-container/20 px-2 py-1 rounded-lg">High Priority</span>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_10px_30px_rgba(42,30,80,0.03)]">
            <p className="text-on-surface-variant text-xs font-semibold uppercase tracking-wider mb-2">Active Projects</p>
            <div className="flex items-end justify-between">
              <h3 className="text-3xl font-black text-on-surface headline-font">{stats.active_projects}</h3>
              <span className="text-primary text-xs font-bold bg-primary-container/20 px-2 py-1 rounded-lg">Live</span>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_10px_30px_rgba(42,30,80,0.03)]">
            <p className="text-on-surface-variant text-xs font-semibold uppercase tracking-wider mb-2">Platform Rating</p>
            <div className="flex items-end justify-between">
              <h3 className="text-3xl font-black text-on-surface headline-font">{stats.platform_rating}</h3>
              <div className="flex text-yellow-400">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="material-symbols-outlined text-sm" style={{fontVariationSettings: i < Math.floor(stats.platform_rating) ? "'FILL' 1" : "'FILL' 0"}}>star</span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Tabs Section */}
        <section className="px-6 py-4">
          <div className="flex items-center gap-8 border-b border-outline-variant/30">
            <button 
              onClick={() => setActiveTab('pending')}
              className={`pb-4 transition-all flex items-center gap-2 font-bold ${activeTab === 'pending' ? 'text-[#4c40df] border-b-2 border-primary' : 'text-on-surface-variant border-b-2 border-transparent hover:text-primary'}`}
            >
              Pending Approval 
              <span className={`px-2 py-0.5 rounded-full text-[10px] ${activeTab === 'pending' ? 'bg-primary/10' : 'bg-surface-container'}`}>
                {activeTab === 'pending' ? workers.length : stats.pending_review}
              </span>
            </button>
            <button 
              onClick={() => setActiveTab('approved')}
              className={`pb-4 transition-all flex items-center gap-2 font-bold ${activeTab === 'approved' ? 'text-[#4c40df] border-b-2 border-primary' : 'text-on-surface-variant border-b-2 border-transparent hover:text-primary'}`}
            >
              Approved 
              <span className={`px-2 py-0.5 rounded-full text-[10px] ${activeTab === 'approved' ? 'bg-primary/10' : 'bg-surface-container'}`}>
                {activeTab === 'approved' ? workers.length : stats.approved_workers}
              </span>
            </button>
          </div>
        </section>

        {/* Worker Cards Grid */}
        <section className="px-6 pb-24 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-6">
          {loading ? (
            <div className="col-span-full py-12 text-center text-on-surface-variant font-medium">Loading professionals...</div>
          ) : filteredWorkers.length === 0 ? (
            <div className="col-span-full py-12 text-center text-on-surface-variant font-medium">No professionals found in this category.</div>
          ) : (
            filteredWorkers.map(worker => (
              <div key={worker.id} className="bg-surface-container-lowest rounded-xl overflow-hidden shadow-[0px_20px_40px_rgba(42,30,80,0.04)] hover:shadow-[0px_20px_40px_rgba(42,30,80,0.08)] transition-all group flex flex-col">
                <div className="p-6 flex gap-4">
                  <div className="relative flex-shrink-0">
                    {worker.profile_photo_path ? (
                      <img 
                        src={`${API_BASE_URL}/${worker.profile_photo_path}`} 
                        alt={worker.full_name} 
                        className="w-20 h-20 rounded-2xl object-cover shadow-sm"
                        onError={(e) => {
                          e.target.onerror = null;
                          e.target.src = '';
                          e.target.className = 'w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center text-primary text-xl font-bold';
                          e.target.parentElement.innerHTML = `<div class="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center text-primary text-xl font-bold headline-font">${worker.full_name?.charAt(0) || 'F'}</div>`;
                        }}
                      />
                    ) : (
                      <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center text-primary text-xl font-bold headline-font">
                        {worker.full_name?.charAt(0) || 'F'}
                      </div>
                    )}
                    <span className={`absolute -bottom-1 -right-1 w-6 h-6 border-2 border-white rounded-full flex items-center justify-center shadow-sm ${worker.status === 'approved' ? 'bg-green-500' : 'bg-orange-500'}`}>
                      <span className="material-symbols-outlined text-[14px] text-white">
                        {worker.status === 'approved' ? 'check' : 'pending'}
                      </span>
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <h4 className="text-lg font-bold text-on-surface headline-font">{worker.full_name}</h4>
                      <span className="text-[10px] uppercase font-black text-primary tracking-widest bg-primary-container/10 px-2 py-1 rounded">
                        {worker.specialization || worker.service}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-1 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">location_on</span> {worker.clinic_location || 'Remote'}
                    </p>
                    <p className="text-xs text-on-surface-variant mt-1 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">history_edu</span> {worker.experience || 0} Years Exp.
                    </p>
                  </div>
                </div>
                <div className="px-6 pb-4">
                  <div className="bg-surface-container-low rounded-lg p-3 space-y-2">
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-on-surface-variant flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">article</span> ID Verification</span>
                      <span className={`${worker.status === 'approved' ? 'text-green-600' : 'text-orange-600'} font-bold flex items-center gap-1`}>
                        {worker.status === 'approved' ? 'Verified' : 'Under Review'} 
                        <span className="material-symbols-outlined text-[14px]">{worker.status === 'approved' ? 'check_circle' : 'schedule'}</span>
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-on-surface-variant flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">folder_zip</span> Documents</span>
                      <div className="flex gap-2">
                        {worker.aadhaar_path && (
                          <a href={`${API_BASE_URL}/${worker.aadhaar_path}`} target="_blank" rel="noreferrer" className="text-primary font-bold hover:underline" title="Aadhaar Card">Aadhaar</a>
                        )}
                        {worker.portfolio_path && (
                          <a href={`${API_BASE_URL}/${worker.portfolio_path}`} target="_blank" rel="noreferrer" className="text-primary font-bold hover:underline" title="Portfolio">Portfolio</a>
                        )}
                        {worker.skill_certificate_path && (
                          <a href={`${API_BASE_URL}/${worker.skill_certificate_path}`} target="_blank" rel="noreferrer" className="text-primary font-bold hover:underline" title="Skill Certificate">Certificate</a>
                        )}
                        {!worker.aadhaar_path && !worker.portfolio_path && !worker.skill_certificate_path && (
                          <span className="text-on-surface-variant/50 italic">No Docs</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                {activeTab === 'pending' && (
                  <div className="px-6 py-4 flex gap-3 mt-auto border-t border-outline-variant/10">
                    <button 
                      onClick={() => handleApprove(worker.id)}
                      className="flex-1 py-2 rounded-full text-xs font-bold bg-primary text-white hover:bg-primary-dim transition-colors shadow-sm"
                    >
                      Approve 
                    </button>
                    <button 
                      onClick={() => handleDecline(worker.id)}
                      className="flex-1 py-2 rounded-full text-xs font-bold bg-surface-container text-on-surface hover:bg-surface-container-high transition-colors"
                    >
                      Decline 
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </section>
      </main>
    </div>
  );
};

export default AdminFreelance;
