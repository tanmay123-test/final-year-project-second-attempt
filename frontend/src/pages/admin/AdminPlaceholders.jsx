import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AdminPlaceholder = ({ title, icon }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();

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
    <div className="bg-[#fbf4ff] text-[#32284f] min-h-screen">
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@700;800&display=swap" rel="stylesheet" />
      <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
      
      <style>{`
        body { font-family: 'Inter', sans-serif; }
        h1, h2, h3, h4, .brand-font { font-family: 'Manrope', sans-serif; letter-spacing: -0.02em; }
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
      `}</style>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-0 h-screen overflow-y-auto py-8 px-4 w-64 hidden lg:flex flex-col bg-[#ede4ff] dark:bg-slate-900 shadow-[0px_20px_40px_rgba(42,30,80,0.06)] z-50">
        <div className="mb-10 px-4">
          <h1 className="text-xl font-bold tracking-tight text-[#32284f] dark:text-slate-100 brand-font">Editorial Admin</h1>
          <p className="text-[10px] text-[#60557f] uppercase tracking-widest mt-1">The Digital Curator</p>
        </div>
        <nav className="flex-1 space-y-2">
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl" to="/admin/dashboard">
            <span className="material-symbols-outlined">dashboard</span>
            <span className="font-medium">Dashboard</span>
          </Link>
          <Link className="flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 transition-colors rounded-xl" to="/admin/healthcare">
            <span className="material-symbols-outlined">medical_services</span>
            <span className="font-medium">Healthcare</span>
          </Link>
          <Link className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${title === 'Car Service' ? 'bg-white text-[#4c40df] font-bold shadow-sm' : 'text-[#60557f] hover:bg-white/50'}`} to="/admin/car-service">
            <span className="material-symbols-outlined" style={{fontVariationSettings: title === 'Car Service' ? "'FILL' 1" : ""}}>directions_car</span>
            <span className="font-medium">Car Service</span>
          </Link>
          <Link className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${title === 'Housekeeping' ? 'bg-white text-[#4c40df] font-bold shadow-sm' : 'text-[#60557f] hover:bg-white/50'}`} to="/admin/housekeeping">
            <span className="material-symbols-outlined" style={{fontVariationSettings: title === 'Housekeeping' ? "'FILL' 1" : ""}}>cleaning_services</span>
            <span className="font-medium">Housekeeping</span>
          </Link>
          <Link className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${title === 'Freelance' ? 'bg-white text-[#4c40df] font-bold shadow-sm' : 'text-[#60557f] hover:bg-white/50'}`} to="/admin/freelance">
            <span className="material-symbols-outlined" style={{fontVariationSettings: title === 'Freelance' ? "'FILL' 1" : ""}}>work</span>
            <span className="font-medium">Freelance</span>
          </Link>
          <Link className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${title === 'Users' ? 'bg-white text-[#4c40df] font-bold shadow-sm' : 'text-[#60557f] hover:bg-white/50'}`} to="/admin/users">
            <span className="material-symbols-outlined" style={{fontVariationSettings: title === 'Users' ? "'FILL' 1" : ""}}>group</span>
            <span className="font-medium">Users</span>
          </Link>
        </nav>
        <div className="mt-auto border-t border-[#b3a6d5]/10 pt-4">
          <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 text-[#60557f] hover:bg-white/50 rounded-xl transition-all">
            <span className="material-symbols-outlined">logout</span>
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      <main className="lg:ml-64 p-12 flex flex-col items-center justify-center min-h-screen">
        <span className="material-symbols-outlined text-8xl text-[#4c40df] mb-6" style={{fontVariationSettings: "'FILL' 1"}}>{icon}</span>
        <h1 className="text-4xl font-black mb-2">{title} Management</h1>
        <p className="text-[#60557f] text-lg">This module is being perfectly curated. Functional working coming soon.</p>
        <Link to="/admin/dashboard" className="mt-8 px-6 py-3 bg-[#4c40df] text-white font-bold rounded-xl shadow-lg hover:opacity-90 transition-all">Back to Dashboard</Link>
      </main>
    </div>
  );
};

export const AdminCarService = () => <AdminPlaceholder title="Car Service" icon="directions_car" />;
