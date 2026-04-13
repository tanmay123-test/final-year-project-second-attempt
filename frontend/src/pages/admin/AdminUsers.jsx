import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminUsers = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    total_users: 0,
    active_now: 0,
    pending_invitations: 48 // Mock value as per HTML
  });

  const token = localStorage.getItem('token');
  const API_BASE_URL = 'http://localhost:5000';

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
        setStats(prev => ({
          ...prev,
          total_users: data.users?.length || 0,
          active_now: Math.floor((data.users?.length || 0) * 0.15) // Mock active count
        }));
      } else {
        setError('Failed to fetch users');
      }
    } catch (err) {
      console.error('Error fetching users:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
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

  const handleBlockUser = async (userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/block`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        fetchUsers(); // Refresh list
      }
    } catch (err) {
      console.error('Error blocking user:', err);
    }
  };

  const handleUnblockUser = async (userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/unblock`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        fetchUsers(); // Refresh list
      }
    } catch (err) {
      console.error('Error unblocking user:', err);
    }
  };

  const filteredUsers = users.filter(user => 
    user.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.username?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-surface text-on-surface min-h-screen font-body">
      <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet"/>
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
      
      <style>{`
        .material-symbols-outlined {
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        .headline-font { font-family: 'Manrope', sans-serif; }
        .tonal-glow-success {
          background-color: rgba(76, 175, 80, 0.1);
          color: #2e7d32;
        }
        .tonal-glow-error {
          background-color: rgba(180, 19, 64, 0.1);
          color: #b41340;
        }
      `}</style>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-0 h-screen overflow-y-auto py-8 px-4 w-64 hidden lg:flex flex-col bg-[#ede4ff] dark:bg-slate-900 shadow-[0px_20px_40px_rgba(42,30,80,0.06)] z-50">
        <div className="mb-10 px-4">
          <span className="text-xl font-bold tracking-tight text-[#32284f] dark:text-slate-100 headline-font">Editorial Admin</span>
          <p className="text-xs text-on-surface-variant mt-1">The Digital Curator</p>
        </div>
        <nav className="flex-1 space-y-2">
          <Link to="/admin/dashboard" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl group">
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-medium">Dashboard</span>
          </Link>
          <Link to="/admin/healthcare" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl">
            <span className="material-symbols-outlined">medical_services</span>
            <span className="font-medium">Healthcare</span>
          </Link>
          <Link to="/admin/car-service" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl">
            <span className="material-symbols-outlined">directions_car</span>
            <span className="font-medium">Car Service</span>
          </Link>
          <Link to="/admin/housekeeping" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl">
            <span className="material-symbols-outlined">cleaning_services</span>
            <span className="font-medium">Housekeeping</span>
          </Link>
          <Link to="/admin/freelance" className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50 transition-colors rounded-xl">
            <span className="material-symbols-outlined">work</span>
            <span className="font-medium">Freelance</span>
          </Link>
          <Link to="/admin/users" className="flex items-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 text-[#4c40df] font-bold rounded-xl shadow-sm scale-95 transition-transform">
            <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>group</span>
            <span className="font-medium">Users</span>
          </Link>
        </nav>
        <div className="mt-auto border-t border-outline-variant/15 pt-6">
          <button onClick={handleLogout} className="flex items-center gap-3 px-4 py-3 text-[#60557f] dark:text-slate-400 hover:bg-white/50 transition-colors rounded-xl w-full">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* TopAppBar */}
      <header className="flex justify-between items-center w-full px-6 py-4 sticky top-0 z-40 lg:pl-72 bg-[#fbf4ff]/50 dark:bg-slate-950/50 backdrop-blur-md">
        <div className="flex items-center gap-4 flex-1 max-w-xl">
          <div className="relative w-full">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm">search</span>
            <input 
              className="w-full bg-surface-container-low border-none rounded-full py-2.5 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/40 focus:bg-surface-container-lowest transition-all" 
              placeholder="Search members, roles, or status..." 
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        <div className="flex items-center gap-4 ml-6">
          <button className="p-2 text-on-surface-variant hover:text-[#4c40df] transition-all relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-2 right-2 w-2 h-2 bg-tertiary rounded-full"></span>
          </button>
          <button className="p-2 text-on-surface-variant hover:text-[#4c40df] transition-all">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <div className="h-10 w-10 rounded-full overflow-hidden ml-2 shadow-sm border-2 border-white">
            <img alt="Admin profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA3TggIsQ4hK6sILKxsOWQVo5TInZv7C-33ciav0_cUr3Z2PIfhppmQ3DSGcuh5QoHVezWkAFW12L3AKMT_jShEn8t99bb6kzfJGzkIcwk1vkECqHlalbViRwHu4AfDdCajeuUTL9EZsihQRe4LZXzbVL4JPpny0Db_JKrZzcz-A-hBewQiOU1t4eAGbv2XacaOn9yDmiX6ZbNG10o1C7a1wPIuyAYLJeyOlid5JTIRY9epvQcWn1pHsbNKcwdy4vG_QQQdO0MrA9FC"/>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="lg:pl-72 pt-4 pb-24 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-on-surface headline-font">User Management</h1>
            <p className="text-on-surface-variant mt-1">Review and manage your digital community member access.</p>
          </div>
          <div className="flex gap-3">
            <button className="px-5 py-2.5 rounded-full bg-secondary-container text-on-secondary-container text-sm font-semibold hover:opacity-90 transition-opacity">
              Export CSV
            </button>
            <button className="px-5 py-2.5 rounded-full bg-gradient-to-br from-primary to-primary-container text-white text-sm font-semibold shadow-md hover:shadow-lg transition-all">
              Invite User
            </button>
          </div>
        </div>

        {/* Bento Grid Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="bg-surface-container-lowest p-6 rounded-md shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1">Total Users</p>
              <h3 className="text-2xl font-black text-on-surface headline-font">{stats.total_users.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-surface-container rounded-xl text-primary">
              <span className="material-symbols-outlined">group</span>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-6 rounded-md shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1">Active Now</p>
              <h3 className="text-2xl font-black text-on-surface headline-font">{stats.active_now.toLocaleString()}</h3>
            </div>
            <div className="p-3 bg-surface-container rounded-xl text-tertiary">
              <span className="material-symbols-outlined">bolt</span>
            </div>
          </div>
          <div className="bg-surface-container-lowest p-6 rounded-md shadow-[0px_20px_40px_rgba(42,30,80,0.06)] flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1">Pending Invitations</p>
              <h3 className="text-2xl font-black text-on-surface headline-font">{stats.pending_invitations}</h3>
            </div>
            <div className="p-3 bg-surface-container rounded-xl text-secondary">
              <span className="material-symbols-outlined">mail</span>
            </div>
          </div>
        </div>

        {/* Member Directory Table */}
        <div className="bg-surface-container-lowest rounded-md shadow-[0px_20px_40px_rgba(42,30,80,0.06)] overflow-hidden">
          <div className="px-6 py-5 border-b border-outline-variant/10 flex items-center justify-between bg-surface-container-low/30">
            <span className="text-sm font-bold text-on-surface">Member Directory</span>
            <div className="flex gap-2">
              <button className="p-1.5 hover:bg-surface-container rounded-lg transition-colors text-on-surface-variant">
                <span className="material-symbols-outlined text-xl">filter_list</span>
              </button>
              <button className="p-1.5 hover:bg-surface-container rounded-lg transition-colors text-on-surface-variant">
                <span className="material-symbols-outlined text-xl">more_vert</span>
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            {loading ? (
              <div className="p-10 text-center text-on-surface-variant">Loading members...</div>
            ) : filteredUsers.length === 0 ? (
              <div className="p-10 text-center text-on-surface-variant">No members found.</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-[11px] font-black uppercase tracking-widest text-on-surface-variant border-b border-outline-variant/5">
                    <th className="px-6 py-4">User Details</th>
                    <th className="px-6 py-4">Username</th>
                    <th className="px-6 py-4">Join Date</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/5">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-surface-container-low/40 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary headline-font font-bold">
                            {user.name?.charAt(0) || 'U'}
                          </div>
                          <div>
                            <p className="text-sm font-bold text-on-surface leading-tight">{user.name}</p>
                            <p className="text-[11px] text-on-surface-variant">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-xs font-medium text-on-surface-variant">@{user.username}</td>
                      <td className="px-6 py-4 text-xs font-medium text-on-surface-variant">
                        {new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${user.is_verified ? 'tonal-glow-success' : 'tonal-glow-error'}`}>
                          {user.is_verified ? 'Active' : 'Unverified'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        {user.is_verified ? (
                          <button 
                            onClick={() => handleBlockUser(user.id)}
                            className="px-4 py-1.5 rounded-full border border-error/20 text-error text-[10px] font-bold uppercase tracking-wider hover:bg-error hover:text-white transition-all"
                          >
                            Block
                          </button>
                        ) : (
                          <button 
                            onClick={() => handleUnblockUser(user.id)}
                            className="px-4 py-1.5 rounded-full bg-surface-container text-on-surface-variant text-[10px] font-bold uppercase tracking-wider hover:bg-primary hover:text-white transition-all"
                          >
                            Unblock
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          {/* Pagination */}
          <div className="px-6 py-4 flex items-center justify-between border-t border-outline-variant/10 bg-surface-container-low/20">
            <span className="text-xs text-on-surface-variant">Showing 1 to {filteredUsers.length} of {users.length} members</span>
            <div className="flex items-center gap-1">
              <button className="p-2 hover:bg-surface-container rounded-lg text-on-surface-variant">
                <span className="material-symbols-outlined text-sm">chevron_left</span>
              </button>
              <button className="w-8 h-8 rounded-full bg-primary text-white text-xs font-bold">1</button>
              <button className="p-2 hover:bg-surface-container rounded-lg text-on-surface-variant">
                <span className="material-symbols-outlined text-sm">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* BottomNavBar (Mobile) */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-t border-[#b3a6d5]/15 shadow-[0_-10px_25px_rgba(0,0,0,0.05)] rounded-t-2xl">
        <Link to="/admin/dashboard" className="flex flex-col items-center justify-center text-[#60557f] p-2">
          <span className="material-symbols-outlined">dashboard</span>
          <span className="text-[10px] font-medium mt-1">Home</span>
        </Link>
        <Link to="/admin/healthcare" className="flex flex-col items-center justify-center text-[#60557f] p-2">
          <span className="material-symbols-outlined">medical_services</span>
          <span className="text-[10px] font-medium mt-1">Health</span>
        </Link>
        <Link to="/admin/car-service" className="flex flex-col items-center justify-center text-[#60557f] p-2">
          <span className="material-symbols-outlined">directions_car</span>
          <span className="text-[10px] font-medium mt-1">Auto</span>
        </Link>
        <Link to="/admin/housekeeping" className="flex flex-col items-center justify-center text-[#60557f] p-2">
          <span className="material-symbols-outlined">cleaning_services</span>
          <span className="text-[10px] font-medium mt-1">Home</span>
        </Link>
        <Link to="/admin/users" className="flex flex-col items-center justify-center bg-[#ede4ff] dark:bg-slate-800 text-[#4c40df] rounded-2xl p-2">
          <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>group</span>
          <span className="text-[10px] font-medium mt-1">Users</span>
        </Link>
      </nav>
    </div>
  );
};

export default AdminUsers;
