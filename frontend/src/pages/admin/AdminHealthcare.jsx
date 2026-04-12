import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminHealthcare = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [pendingWorkers, setPendingWorkers] = useState([]);
  const [approvedWorkers, setApprovedWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [error, setError] = useState(null);

  const token = localStorage.getItem('token');
  const API_BASE_URL = 'http://localhost:5000';

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/healthcare/workers/pending`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setPendingWorkers(data.workers || []);

      const approvedResponse = await fetch(`${API_BASE_URL}/admin/healthcare/workers/approved`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const approvedData = await approvedResponse.json();
      setApprovedWorkers(approvedData.workers || []);
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch admin data:', err);
      setError('Failed to load healthcare workers.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (workerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/healthcare/workers/approve/${workerId}`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (response.ok) {
        alert('Worker approved successfully');
        fetchData(); // Refresh lists
      }
    } catch (err) {
      console.error('Approval failed:', err);
    }
  };

  const handleReject = async (workerId) => {
    const reason = prompt('Please enter rejection reason:');
    if (!reason) return;

    try {
      const response = await fetch(`${API_BASE_URL}/admin/healthcare/workers/reject/${workerId}`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rejection_reason: reason })
      });
      if (response.ok) {
        alert('Worker rejected');
        fetchData(); // Refresh lists
      }
    } catch (err) {
      console.error('Rejection failed:', err);
    }
  };

  const getDocUrl = (path) => {
    if (!path) return '#';
    if (path.startsWith('http')) return path;
    // Replace backslashes with forward slashes for URL and ensure leading slash
    const cleanPath = path.replace(/\\/g, '/');
    const finalPath = cleanPath.startsWith('/') ? cleanPath : `/${cleanPath}`;
    return `${API_BASE_URL}${finalPath}`;
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
    <div className="bg-surface text-on-surface antialiased min-h-screen">
      <style>{`
        .material-symbols-outlined {
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .font-body { font-family: 'Inter', sans-serif; }
        .font-headline, h1, h2, h3 { font-family: 'Manrope', sans-serif; }
        .doc-link {
          color: #8E44AD;
          text-decoration: underline;
          cursor: pointer;
          font-weight: 600;
        }
        .doc-link:hover {
          color: #7B3F99;
        }
      `}</style>

      {/* SideNavBar Shell */}
      <aside className="fixed left-0 top-0 h-screen overflow-y-auto py-8 px-4 w-64 hidden lg:flex flex-col bg-[#ede4ff] shadow-[0px_20px_40px_rgba(42,30,80,0.06)] z-50">
        <div className="mb-10 px-4">
          <h1 className="text-xl font-bold tracking-tight text-[#32284f]">Editorial Admin</h1>
          <p className="text-xs text-on-surface-variant mt-1 font-medium">The Digital Curator</p>
        </div>
        <nav className="flex-1 space-y-2">
          {/* Dashboard */}
          <Link to="/admin/dashboard" className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl">
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-medium">Dashboard</span>
          </Link>
          {/* Active State: Healthcare */}
          <Link to="/admin/healthcare" className="flex items-center gap-3 px-4 py-3 bg-white text-[#4c40df] font-bold rounded-xl shadow-sm">
            <span className="material-symbols-outlined">medical_services</span>
            <span className="font-medium">Healthcare</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl" to="/admin/car-service">
            <span className="material-symbols-outlined">directions_car</span>
            <span className="font-medium">Car Service</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl" to="/admin/housekeeping">
            <span className="material-symbols-outlined">cleaning_services</span>
            <span className="font-medium">Housekeeping</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl" to="/admin/freelance">
            <span className="material-symbols-outlined">work</span>
            <span className="font-medium">Freelance</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl" to="/admin/users">
            <span className="material-symbols-outlined">group</span>
            <span className="font-medium">Users</span>
          </Link>
        </nav>
        <div className="mt-auto px-4">
          <button onClick={handleLogout} className="flex items-center gap-3 w-full px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl text-left">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* TopAppBar Shell */}
      <header className="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-40 lg:pl-72 bg-[#fbf4ff]/50 backdrop-blur-md">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-black text-[#32284f]">The Editorial Admin</h2>
        </div>
        <div className="flex items-center gap-6">
          <div className="relative hidden sm:block">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
            <input className="bg-surface-container-low border-none rounded-full pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-primary/40 w-64 transition-all" placeholder="Search workers..." type="text"/>
          </div>
          <div className="flex items-center gap-4 text-[#60557f]">
            <button className="hover:text-[#4c40df] transition-all"><span className="material-symbols-outlined">notifications</span></button>
            <button className="hover:text-[#4c40df] transition-all"><span className="material-symbols-outlined">settings</span></button>
            <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-container">
              <img className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD_kE3eDHVJSs0A0vxRvSHCWa00bLAsJgFkBNypN8N8IqXXbPc3_jkiCuLlXCCeGd0jYqDSYp-wZrkd9i1zpno5BvY3XukpKXtJgUJMM0SVbfOXMiwff_nTKRsgZa5qtWh2o1j6ebAaFBpCSin8hCJUVU4TbGEJB-ypMxUimFaFS5fL5IFR5Ue531EyMk2Lh9FDaiXu0w5EwGMvnkmoyTNi5FGWGHXPLNNyfO8s76ZwBYbq08l1BSQRH9hftWQFHOeaFU955O9vJW2Z" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Canvas */}
      <main className="lg:pl-72 min-h-screen pb-24 lg:pb-12 px-6 lg:px-12 pt-8">
        {/* Editorial Header Section */}
        <header className="mb-10 max-w-5xl">
          <h1 className="text-4xl font-extrabold tracking-tight text-[#32284f] mb-2 headline-sm">Healthcare Verification</h1>
          <p className="text-on-surface-variant text-lg max-w-2xl font-body">Curate your medical staff network. Review credentials, verify licenses, and manage the elite circle of healthcare professionals.</p>
        </header>

        {/* Tab Navigation */}
        <div className="flex items-center gap-8 mb-8 border-b border-outline-variant/15 font-body">
          <button 
            className={`pb-4 transition-all flex items-center gap-2 ${activeTab === 'pending' ? 'text-[#4c40df] font-bold border-b-2 border-[#4c40df]' : 'text-[#60557f] font-medium'}`}
            onClick={() => setActiveTab('pending')}
          >
            Pending Approval
            <span className="bg-primary/10 px-2 py-0.5 rounded-full text-xs">{pendingWorkers.length}</span>
          </button>
          <button 
            className={`pb-4 transition-all flex items-center gap-2 ${activeTab === 'approved' ? 'text-[#4c40df] font-bold border-b-2 border-[#4c40df]' : 'text-[#60557f] font-medium'}`}
            onClick={() => setActiveTab('approved')}
          >
            Approved
            <span className="bg-primary/10 px-2 py-0.5 rounded-full text-xs">{approvedWorkers.length}</span>
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#8E44AD]"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 max-w-6xl font-body">
            {(activeTab === 'pending' ? pendingWorkers : approvedWorkers).map((worker) => (
              <div key={worker.id} className="bg-surface-container-lowest p-6 rounded-xl shadow-[0px_20px_40px_rgba(42,30,80,0.06)] group hover:scale-[1.01] transition-transform">
                <div className="flex flex-col md:flex-row gap-6">
                  {/* Profile Column */}
                  <div className="flex-shrink-0">
                    <div className="w-24 h-32 rounded-xl overflow-hidden bg-surface-container shadow-inner">
                      <img className="w-full h-full object-cover" src={getDocUrl(worker.documents?.profile_photo) || "https://via.placeholder.com/150"} alt={worker.full_name} />
                    </div>
                  </div>
                  {/* Info Column */}
                  <div className="flex-grow">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-xl font-bold text-on-surface font-headline">{worker.full_name}</h3>
                        <p className="text-[#4c40df] font-semibold text-sm">{worker.specialization}</p>
                      </div>
                      <span className="text-xs text-on-surface-variant font-medium bg-surface-container px-3 py-1 rounded-full">{worker.experience} yrs Exp.</span>
                    </div>
                    <div className="grid grid-cols-2 gap-y-3 gap-x-4 mt-4 text-sm">
                      <div className="flex items-center gap-2 text-on-surface-variant">
                        <span className="material-symbols-outlined text-base">location_on</span>
                        <span>{worker.clinic_location}</span>
                      </div>
                      <div className="flex items-center gap-2 text-on-surface-variant">
                        <span className="material-symbols-outlined text-base">calendar_today</span>
                        <span>Applied: {new Date(worker.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2 text-on-surface-variant">
                        <span className="material-symbols-outlined text-base">mail</span>
                        <span>{worker.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-on-surface-variant">
                        <span className="material-symbols-outlined text-base">phone</span>
                        <span>{worker.phone}</span>
                      </div>
                    </div>
                    {/* Documents Section */}
                    <div className="mt-6 pt-4 border-t border-outline-variant/10">
                      <p className="text-xs uppercase tracking-widest font-bold text-on-surface-variant mb-3">Document Verification</p>
                      <div className="flex flex-wrap gap-4">
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-green-600 text-lg">description</span>
                          <a href={getDocUrl(worker.documents?.aadhaar)} target="_blank" rel="noopener noreferrer" className="doc-link text-xs">Aadhaar Card</a>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-green-600 text-lg">school</span>
                          <a href={getDocUrl(worker.documents?.degree_certificate)} target="_blank" rel="noopener noreferrer" className="doc-link text-xs">Degree Certificate</a>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-green-600 text-lg">verified_user</span>
                          <a href={getDocUrl(worker.documents?.medical_license)} target="_blank" rel="noopener noreferrer" className="doc-link text-xs">Medical License</a>
                        </div>
                      </div>
                    </div>
                    {/* Actions */}
                    {activeTab === 'pending' && (
                      <div className="mt-8 flex gap-3">
                        <button 
                          onClick={() => handleApprove(worker.id)}
                          className="flex-1 bg-primary text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-primary/20 hover:opacity-90 active:scale-95 transition-all"
                        >
                          <span className="material-symbols-outlined text-lg">verified</span> Approve
                        </button>
                        <button 
                          onClick={() => handleReject(worker.id)}
                          className="flex-1 bg-white border-2 border-error/20 text-error py-3 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-error/5 active:scale-95 transition-all"
                        >
                          <span className="material-symbols-outlined text-lg">block</span> Reject
                        </button>
                      </div>
                    )}
                    {activeTab === 'approved' && (
                      <div className="mt-6 flex items-center gap-2 text-green-600 font-bold text-sm">
                        <span className="material-symbols-outlined text-lg">check_circle</span>
                        Verified Professional
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {(activeTab === 'pending' ? pendingWorkers : approvedWorkers).length === 0 && (
              <div className="col-span-full py-20 text-center text-on-surface-variant opacity-60">
                <span className="material-symbols-outlined text-6xl mb-4">folder_open</span>
                <p className="text-xl">No workers found in this category.</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* BottomNavBar Shell (Mobile Only) */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-t border-[#b3a6d5]/15 shadow-[0_-10px_25px_rgba(0,0,0,0.05)] rounded-t-2xl">
        <Link className="flex flex-col items-center justify-center text-[#60557f] p-2" to="/admin/dashboard">
          <span className="material-symbols-outlined">dashboard</span>
          <span className="text-[10px] font-medium font-body">Home</span>
        </Link>
        <Link className="flex flex-col items-center justify-center bg-[#ede4ff] text-[#4c40df] rounded-2xl p-2" to="/admin/healthcare">
          <span className="material-symbols-outlined">medical_services</span>
          <span className="text-[10px] font-medium font-body">Health</span>
        </Link>
        <a className="flex flex-col items-center justify-center text-[#60557f] p-2" href="#">
          <span className="material-symbols-outlined">directions_car</span>
          <span className="text-[10px] font-medium font-body">Auto</span>
        </a>
        <a className="flex flex-col items-center justify-center text-[#60557f] p-2" href="#">
          <span className="material-symbols-outlined">cleaning_services</span>
          <span className="text-[10px] font-medium font-body">Home</span>
        </a>
        <a className="flex flex-col items-center justify-center text-[#60557f] p-2" href="#">
          <span className="material-symbols-outlined">group</span>
          <span className="text-[10px] font-medium font-body">Users</span>
        </a>
      </nav>
    </div>
  );
};

export default AdminHealthcare;
