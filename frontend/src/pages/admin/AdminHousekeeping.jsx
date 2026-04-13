import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminHousekeeping = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [pendingWorkers, setPendingWorkers] = useState([]);
  const [approvedWorkers, setApprovedWorkers] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    active_bookings: 0
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [error, setError] = useState(null);
  const [showToast, setShowToast] = useState(false);
  const [toastMsg, setToastMsg] = useState('');

  const token = localStorage.getItem('token');
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch pending workers for housekeeping
      const pendingRes = await fetch(`${API_BASE_URL}/admin/workers/pending?service=housekeeping`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const pendingData = await pendingRes.json();
      setPendingWorkers(Array.isArray(pendingData) ? pendingData : []);

      // Fetch approved workers for housekeeping
      const approvedRes = await fetch(`${API_BASE_URL}/admin/workers/approved?service=housekeeping`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const approvedData = await approvedRes.json();
      setApprovedWorkers(Array.isArray(approvedData) ? approvedData : []);

      // Mock stats for UI consistency with provided HTML
      setStats({
        total: (Array.isArray(pendingData) ? pendingData.length : 0) + (Array.isArray(approvedData) ? approvedData.length : 0) + 1200,
        pending: Array.isArray(pendingData) ? pendingData.length : 0,
        active_bookings: 84
      });
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch admin data:', err);
      setError('Failed to load housekeeping workers.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (workerId, name) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/workers/${workerId}/approve`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        setToastMsg(`Worker ${name} approved successfully!`);
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
        fetchData();
      }
    } catch (err) {
      console.error('Approval failed:', err);
    }
  };

  const handleReject = async (workerId) => {
    const reason = prompt('Please enter rejection reason:');
    if (!reason) return;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/workers/${workerId}/reject`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rejection_reason: reason })
      });
      if (response.ok) {
        alert('Worker rejected');
        fetchData();
      }
    } catch (err) {
      console.error('Rejection failed:', err);
    }
  };

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
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@700;800&display=swap" rel="stylesheet" />
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
      
      <style>{`
        body { font-family: 'Inter', sans-serif; }
        h1, h2, h3, h4, .brand-font { font-family: 'Manrope', sans-serif; letter-spacing: -0.02em; }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .primary-gradient {
            background: linear-gradient(135deg, #4c40df 0%, #9995ff 100%);
        }
        .bg-surface { background-color: #fbf4ff; }
        .text-on-surface { color: #32284f; }
        .text-on-surface-variant { color: #60557f; }
        .bg-surface-container-lowest { background-color: #ffffff; }
        .bg-surface-container-low { background-color: #f5eeff; }
        .bg-surface-container { background-color: #ede4ff; }
        .bg-surface-container-high { background-color: #e8ddff; }
        .border-outline-variant { border-color: #b3a6d5; }
        .text-primary { color: #4c40df; }
        .text-tertiary { color: #983670; }
        .bg-primary-container { background-color: #d8caff; }
        .text-on-primary-container { color: #16007d; }
      `}</style>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-0 h-screen overflow-y-auto py-8 px-4 w-64 hidden lg:flex flex-col bg-[#ede4ff] dark:bg-slate-900 shadow-[0px_20px_40px_rgba(42,30,80,0.06)] z-50">
        <div className="mb-10 px-4">
          <h1 className="text-xl font-bold tracking-tight text-[#32284f] dark:text-slate-100 brand-font">Editorial Admin</h1>
          <p className="text-[10px] text-on-surface-variant uppercase tracking-widest mt-1">The Digital Curator</p>
        </div>
        <nav className="flex-1 space-y-2">
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl" to="/admin/dashboard">
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-medium">Dashboard</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl" to="/admin/healthcare">
            <span className="material-symbols-outlined">medical_services</span>
            <span className="font-medium">Healthcare</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl" to="/admin/car-service">
            <span className="material-symbols-outlined">directions_car</span>
            <span className="font-medium">Car Service</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 text-[#4c40df] font-bold rounded-xl shadow-sm scale-95 active:scale-90 transition-transform" to="/admin/housekeeping">
            <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>cleaning_services</span>
            <span className="font-medium">Housekeeping</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl" to="/admin/freelance">
            <span className="material-symbols-outlined">work</span>
            <span className="font-medium">Freelance</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl" to="/admin/users">
            <span className="material-symbols-outlined">group</span>
            <span className="font-medium">Users</span>
          </Link>
        </nav>
        <div className="mt-auto border-t border-outline-variant/10 pt-4">
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 rounded-xl transition-all">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* TopAppBar */}
      <header className="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-40 lg:pl-72 bg-[#fbf4ff]/50 dark:bg-slate-950/50 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-black text-[#32284f] dark:text-white brand-font">Housekeeping Management</h2>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center bg-surface-container-low px-4 py-2 rounded-full w-64 focus-within:bg-white focus-within:shadow-sm transition-all">
            <span className="material-symbols-outlined text-on-surface-variant text-sm">search</span>
            <input className="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-on-surface-variant/60 ml-2 outline-none" placeholder="Search workers..." type="text"/>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 text-on-surface-variant hover:text-[#4c40df] transition-all">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="p-2 text-on-surface-variant hover:text-[#4c40df] transition-all">
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="lg:ml-64 p-6 pb-24 lg:pb-8">
        <div className="max-w-7xl mx-auto">
          {/* Tab Navigation */}
          <div className="flex gap-8 mb-8 border-b border-outline-variant/15">
            <button 
              className={`pb-4 text-sm font-bold transition-all ${activeTab === 'pending' ? 'text-[#4c40df] border-b-2 border-[#4c40df]' : 'text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('pending')}
            >
              Pending Approval
              <span className="ml-2 px-2 py-0.5 bg-primary-container text-on-primary-container rounded-full text-xs">{pendingWorkers.length}</span>
            </button>
            <button 
              className={`pb-4 text-sm font-medium transition-all ${activeTab === 'approved' ? 'text-[#4c40df] border-b-2 border-[#4c40df]' : 'text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('approved')}
            >
              Approved
            </button>
          </div>

          {/* Dashboard Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-on-surface-variant mb-1 uppercase tracking-tight">Total Cleaners</p>
                <h3 className="text-2xl font-black text-on-surface">{stats.total}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center text-primary">
                <span className="material-symbols-outlined">group</span>
              </div>
            </div>
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex items-center justify-between border-l-4 border-tertiary">
              <div>
                <p className="text-xs font-medium text-on-surface-variant mb-1 uppercase tracking-tight">Verification Queue</p>
                <h3 className="text-2xl font-black text-on-surface">{stats.pending}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-tertiary-container/20 flex items-center justify-center text-tertiary">
                <span className="material-symbols-outlined">verified_user</span>
              </div>
            </div>
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-on-surface-variant mb-1 uppercase tracking-tight">Active Bookings</p>
                <h3 className="text-2xl font-black text-on-surface">{stats.active_bookings}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-secondary-container/30 flex items-center justify-center text-secondary">
                <span className="material-symbols-outlined">event_available</span>
              </div>
            </div>
          </div>

          {/* Workers List */}
          {loading ? (
            <div className="flex justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {(activeTab === 'pending' ? pendingWorkers : approvedWorkers).map((worker) => (
                <div key={worker.id} className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] group hover:translate-y-[-4px] transition-all duration-300">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex gap-4">
                      {worker.profile_photo_path ? (
                        <img 
                          src={`${API_BASE_URL}/${worker.profile_photo_path}`} 
                          alt={worker.name} 
                          className="w-14 h-14 rounded-xl object-cover shadow-sm"
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = '';
                            e.target.className = 'w-14 h-14 rounded-xl bg-surface-container flex items-center justify-center text-primary text-xl font-bold';
                            e.target.parentElement.innerHTML = `<div class="w-14 h-14 rounded-xl bg-surface-container flex items-center justify-center text-primary text-xl font-bold">${worker.name?.charAt(0) || 'W'}</div>`;
                          }}
                        />
                      ) : (
                        <div className="w-14 h-14 rounded-xl bg-surface-container flex items-center justify-center text-primary text-xl font-bold">
                          {worker.name?.charAt(0) || 'W'}
                        </div>
                      )}
                      <div>
                        <h4 className="font-bold text-on-surface">{worker.name}</h4>
                        <p className="text-xs text-on-surface-variant">{worker.specialization || 'Housekeeper'}</p>
                        <div className="flex items-center gap-1 mt-1 text-[#60557f]">
                          <span className="material-symbols-outlined text-[14px]">location_on</span>
                          <span className="text-[11px]">{worker.city || 'Location N/A'}</span>
                        </div>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-[10px] font-bold rounded uppercase tracking-wider ${worker.status === 'pending' ? 'bg-surface-container text-tertiary' : 'bg-green-100 text-green-700'}`}>
                      {worker.status}
                    </span>
                  </div>
                  <div className="space-y-4">
                    <div className="flex gap-2 flex-wrap">
                      {(worker.skills || 'Deep Clean, Eco-friendly').split(',').map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-surface-container-low text-on-surface-variant text-[10px] rounded-md font-medium">{skill.trim()}</span>
                      ))}
                    </div>
                    <div className="grid grid-cols-2 gap-4 py-4 border-y border-outline-variant/10">
                      <div>
                        <p className="text-[10px] uppercase text-on-surface-variant mb-1">Experience</p>
                        <p className="text-sm font-bold">{worker.experience_years || '0'} Years</p>
                      </div>
                      <div>
                        <p className="text-[10px] uppercase text-on-surface-variant mb-1">Verification</p>
                        <div className="flex gap-2">
                          {worker.aadhaar_path && (
                            <a href={`${API_BASE_URL}/${worker.aadhaar_path}`} target="_blank" rel="noreferrer" title="Aadhaar Card">
                              <span className="material-symbols-outlined text-primary text-sm hover:scale-110 transition-transform">badge</span>
                            </a>
                          )}
                          {worker.police_verification_path && (
                            <a href={`${API_BASE_URL}/${worker.police_verification_path}`} target="_blank" rel="noreferrer" title="Police Verification">
                              <span className="material-symbols-outlined text-tertiary text-sm hover:scale-110 transition-transform">policy</span>
                            </a>
                          )}
                          {!worker.aadhaar_path && !worker.police_verification_path && (
                            <span className="text-[10px] text-on-surface-variant/50 italic">No Docs</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-3 pt-2">
                      {worker.status === 'pending' ? (
                        <>
                          <button 
                            onClick={() => handleApprove(worker.id, worker.name)}
                            className="flex-1 py-2 px-4 bg-primary text-on-primary text-xs font-bold rounded-lg primary-gradient shadow-md active:scale-95 transition-transform"
                          >
                            Approve
                          </button>
                          <button 
                            onClick={() => handleReject(worker.id)}
                            className="px-4 py-2 bg-surface-container-high text-on-surface text-xs font-bold rounded-lg hover:bg-surface-variant transition-colors"
                          >
                            Reject
                          </button>
                        </>
                      ) : (
                        <button 
                          className="flex-1 py-2 px-4 bg-surface-container-high text-on-surface text-xs font-bold rounded-lg hover:bg-surface-variant transition-colors"
                        >
                          View Details
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {((activeTab === 'pending' ? pendingWorkers : approvedWorkers).length === 0) && (
                <div className="col-span-full text-center py-20 text-on-surface-variant">
                  No {activeTab} workers found.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Toast Success State */}
        {showToast && (
          <div className="fixed bottom-24 lg:bottom-10 right-6 z-50 animate-bounce">
            <div className="bg-primary-container text-on-primary-container px-6 py-4 rounded-2xl shadow-xl flex items-center gap-3">
              <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>check_circle</span>
              <p className="text-sm font-bold">{toastMsg}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminHousekeeping;
