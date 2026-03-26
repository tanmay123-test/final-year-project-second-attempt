import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ListChecks, 
  Wallet, 
  History, 
  Settings as SettingsIcon, 
  HelpCircle, 
  LogOut, 
  Bell, 
  User, 
  Clock, 
  Shield, 
  Info,
  Edit2,
  Trash2,
  Plus,
  Save,
  X,
  Smartphone
} from 'lucide-react';
import api from '../../../shared/api';

const MechanicSettings = () => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('profile');
  const [isOnline, setIsOnline] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [formData, setFormData] = useState({
    fullName: '',
    phone: '',
    specialization: 'Mechanic',
    serviceRadius: 10,
    bio: '',
    avatar: 'https://images.unsplash.com/photo-1560179707-f14e90ef3623?auto=format&fit=crop&q=80&w=100',
    availability: {
      monday: { enabled: true, start: '09:00', end: '17:00' },
      tuesday: { enabled: true, start: '09:00', end: '17:00' },
      wednesday: { enabled: true, start: '09:00', end: '17:00' },
      thursday: { enabled: true, start: '09:00', end: '17:00' },
      friday: { enabled: true, start: '09:00', end: '17:00' },
      saturday: { enabled: false, start: '09:00', end: '17:00' },
      sunday: { enabled: false, start: '09:00', end: '17:00' }
    }
  });

  const token = localStorage.getItem('workerToken');

  const fetchProfile = useCallback(async () => {
    if (!token) {
      navigate('/worker/car/mechanic/auth');
      return;
    }

    try {
      setLoading(true);
      const res = await api.get('/api/car/mechanic/profile', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.data.mechanic) {
        const m = res.data.mechanic;
        setFormData(prev => ({
          ...prev,
          fullName: m.name || '',
          phone: m.phone || '',
          specialization: m.specialization || m.role || 'Mechanic',
          serviceRadius: m.service_radius || 10,
          bio: m.bio || '',
          avatar: m.profile_photo_path || prev.avatar
        }));
        setIsOnline(m.is_online);
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    } finally {
      setLoading(false);
    }
  }, [navigate, token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

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

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put('/api/car/service/worker/profile', {
        name: formData.fullName,
        phone: formData.phone,
        specialization: formData.specialization,
        service_radius: formData.serviceRadius,
        bio: formData.bio
      }, { headers: { Authorization: `Bearer ${token}` } });
      
      alert('Settings saved successfully!');
    } catch (err) {
      console.error('Error saving settings:', err);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const categories = [
    { id: 'profile', label: 'Profile', icon: <User size={20} /> },
    { id: 'availability', label: 'Availability', icon: <Clock size={20} /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell size={20} /> },
    { id: 'security', label: 'Security', icon: <Shield size={20} /> },
    { id: 'about', label: 'About', icon: <Info size={20} /> },
  ];

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
            alt={formData.fullName} 
            className="w-10 h-10 rounded-xl object-cover border-2 border-white shadow-sm" 
            src={formData.avatar}
          />
          <div>
            <p className="font-bold text-sm text-slate-900">{formData.fullName}</p>
            <p className="text-xs text-slate-500">{formData.specialization}</p>
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
          <button 
            onClick={() => navigate('/worker/car/mechanic/history')}
            className="w-full flex items-center space-x-3 px-4 py-3 text-slate-600 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-all duration-200 font-medium text-sm"
          >
            <History size={18} />
            <span>History</span>
          </button>
          <button className="w-full flex items-center space-x-3 px-4 py-3 bg-violet-50 text-violet-600 rounded-lg font-bold text-sm">
            <SettingsIcon size={18} />
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
            <h2 className="font-bold text-xl tracking-tight text-slate-900">Settings</h2>
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
            <div className="w-8 h-8 rounded-full overflow-hidden border border-slate-200 shadow-sm">
              <img src={formData.avatar} alt="Profile" className="w-full h-full object-cover" />
            </div>
          </div>
        </header>

        {/* Content Canvas */}
        <div className="mt-16 p-6 md:p-10 bg-slate-50 min-h-screen">
          <div className="max-w-6xl mx-auto">
            <header className="mb-10">
              <h1 className="text-3xl md:text-4xl font-black tracking-tight text-slate-900 mb-2">Settings</h1>
              <p className="text-slate-500 font-medium">Manage your professional profile and working preferences.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Settings Categories Sidebar */}
              <div className="lg:col-span-3 space-y-2">
                {categories.map((cat) => (
                  <button 
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`w-full flex items-center gap-4 px-4 py-4 rounded-2xl font-bold text-left transition-all ${
                      activeCategory === cat.id 
                        ? 'bg-white text-violet-600 shadow-sm border border-slate-100' 
                        : 'text-slate-500 hover:bg-slate-100'
                    }`}
                  >
                    {cat.icon}
                    <span>{cat.label}</span>
                  </button>
                ))}
              </div>

              {/* Right Panel Content */}
              <div className="lg:col-span-9 space-y-8">
                {/* Profile Section */}
                {activeCategory === 'profile' && (
                  <section className="bg-white rounded-3xl p-8 border border-slate-100 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                      <h2 className="text-2xl font-black text-slate-900">Profile Information</h2>
                      <span className="px-3 py-1 bg-violet-100 text-violet-700 text-[10px] font-black rounded-full uppercase tracking-wider">Expert Status</span>
                    </div>

                    <div className="flex flex-col md:flex-row gap-10">
                      <div className="flex-shrink-0 flex flex-col items-center gap-4">
                        <div className="relative group">
                          <img 
                            src={formData.avatar} 
                            alt="Profile" 
                            className="w-32 h-32 rounded-2xl object-cover border-4 border-slate-50 shadow-sm"
                          />
                          <button className="absolute -bottom-2 -right-2 p-2 bg-violet-600 text-white rounded-xl shadow-lg hover:bg-violet-700 transition-colors">
                            <Edit2 size={16} />
                          </button>
                        </div>
                        <p className="text-[10px] text-slate-400 font-bold text-center max-w-[120px]">JPG, GIF or PNG. Max size of 2MB</p>
                      </div>

                      <div className="flex-grow grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest">Full Name</label>
                          <input 
                            type="text" 
                            value={formData.fullName}
                            onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                            className="w-full bg-slate-50 border-none rounded-2xl px-5 py-4 focus:bg-white focus:ring-2 focus:ring-violet-500/20 transition-all font-bold text-slate-900 outline-none" 
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest">Phone Number</label>
                          <input 
                            type="tel" 
                            value={formData.phone}
                            onChange={(e) => setFormData({...formData, phone: e.target.value})}
                            className="w-full bg-slate-50 border-none rounded-2xl px-5 py-4 focus:bg-white focus:ring-2 focus:ring-violet-500/20 transition-all font-bold text-slate-900 outline-none" 
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest">Specialization</label>
                          <select 
                            value={formData.specialization}
                            onChange={(e) => setFormData({...formData, specialization: e.target.value})}
                            className="w-full bg-slate-50 border-none rounded-2xl px-5 py-4 focus:bg-white focus:ring-2 focus:ring-violet-500/20 transition-all font-bold text-slate-900 outline-none appearance-none"
                          >
                            <option>Mechanic</option>
                            <option>Automobile Expert</option>
                            <option>Heavy Machinery</option>
                            <option>Electric Vehicles</option>
                            <option>Classic Car Restoration</option>
                          </select>
                        </div>
                        <div className="space-y-2">
                          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest">Service Radius (km)</label>
                          <input 
                            type="number" 
                            value={formData.serviceRadius}
                            onChange={(e) => setFormData({...formData, serviceRadius: parseInt(e.target.value)})}
                            className="w-full bg-slate-50 border-none rounded-2xl px-5 py-4 focus:bg-white focus:ring-2 focus:ring-violet-500/20 transition-all font-bold text-slate-900 outline-none" 
                          />
                        </div>
                        <div className="md:col-span-2 space-y-2">
                          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest">Bio</label>
                          <textarea 
                            rows="3"
                            value={formData.bio}
                            onChange={(e) => setFormData({...formData, bio: e.target.value})}
                            className="w-full bg-slate-50 border-none rounded-2xl px-5 py-4 focus:bg-white focus:ring-2 focus:ring-violet-500/20 transition-all font-bold text-slate-900 outline-none resize-none"
                          ></textarea>
                        </div>
                      </div>
                    </div>

                    <div className="mt-10 flex justify-end gap-4">
                      <button className="px-8 py-4 bg-slate-100 text-slate-500 font-bold rounded-2xl hover:bg-slate-200 transition-colors">Cancel</button>
                      <button 
                        onClick={handleSave}
                        disabled={saving}
                        className="px-10 py-4 bg-violet-600 text-white font-black rounded-2xl shadow-xl shadow-violet-100 hover:bg-violet-700 active:scale-95 transition-all flex items-center gap-2"
                      >
                        {saving ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> : <Save size={20} />}
                        Save Changes
                      </button>
                    </div>
                  </section>
                )}

                {/* Availability Section */}
                {activeCategory === 'availability' && (
                  <section className="bg-white rounded-3xl p-8 border border-slate-100 shadow-sm">
                    <div className="mb-8">
                      <h2 className="text-2xl font-black text-slate-900">Weekly Availability</h2>
                      <p className="text-slate-500 font-medium text-sm mt-1">Set your active working hours for clients to book you.</p>
                    </div>

                    <div className="space-y-4">
                      {Object.entries(formData.availability).map(([day, data]) => (
                        <div key={day} className={`flex flex-wrap items-center justify-between p-5 rounded-2xl transition-all border ${
                          data.enabled ? 'bg-white border-slate-100 shadow-sm' : 'bg-slate-50/50 border-transparent opacity-60'
                        }`}>
                          <div className="flex items-center gap-4 w-40">
                            <input 
                              type="checkbox" 
                              checked={data.enabled}
                              onChange={(e) => {
                                const newAvailability = { ...formData.availability };
                                newAvailability[day].enabled = e.target.checked;
                                setFormData({ ...formData, availability: newAvailability });
                              }}
                              className="w-6 h-6 rounded-lg text-violet-600 focus:ring-violet-500 bg-slate-100 border-none cursor-pointer"
                            />
                            <span className={`font-bold capitalize ${data.enabled ? 'text-slate-900' : 'text-slate-400'}`}>{day}</span>
                          </div>

                          {data.enabled ? (
                            <div className="flex items-center gap-4">
                              <input 
                                type="time" 
                                value={data.start}
                                onChange={(e) => {
                                  const newAvailability = { ...formData.availability };
                                  newAvailability[day].start = e.target.value;
                                  setFormData({ ...formData, availability: newAvailability });
                                }}
                                className="bg-slate-100 border-none rounded-xl px-4 py-2.5 text-sm font-bold focus:bg-white focus:ring-2 focus:ring-violet-500/20 outline-none"
                              />
                              <span className="text-slate-400 font-bold text-xs uppercase tracking-widest">to</span>
                              <input 
                                type="time" 
                                value={data.end}
                                onChange={(e) => {
                                  const newAvailability = { ...formData.availability };
                                  newAvailability[day].end = e.target.value;
                                  setFormData({ ...formData, availability: newAvailability });
                                }}
                                className="bg-slate-100 border-none rounded-xl px-4 py-2.5 text-sm font-bold focus:bg-white focus:ring-2 focus:ring-violet-500/20 outline-none"
                              />
                            </div>
                          ) : (
                            <div className="flex items-center px-4 py-2.5">
                              <span className="text-slate-400 italic text-sm font-medium">Unavailable</span>
                            </div>
                          )}

                          <button className={`p-2 transition-colors ${data.enabled ? 'text-slate-300 hover:text-red-500' : 'opacity-0 pointer-events-none'}`}>
                            <Trash2 size={20} />
                          </button>
                        </div>
                      ))}
                    </div>

                    <button className="mt-8 flex items-center gap-2 text-violet-600 font-black text-sm hover:translate-x-1 transition-all">
                      <Plus size={20} />
                      <span>Add specific date exception</span>
                    </button>
                  </section>
                )}

                {/* Danger Zone */}
                <section className="border-2 border-red-100 bg-red-50/30 rounded-3xl p-8">
                  <h2 className="text-xl font-black text-red-600 mb-6 flex items-center gap-2">
                    <Trash2 size={20} />
                    Danger Zone
                  </h2>
                  <div className="flex flex-col md:flex-row items-center justify-between gap-6 bg-white p-6 rounded-2xl border border-red-100">
                    <div>
                      <p className="font-black text-slate-900">Deactivate Account</p>
                      <p className="text-sm text-slate-500 font-medium">Temporarily hide your profile from search results. You can reactivate at any time.</p>
                    </div>
                    <button className="w-full md:w-auto px-8 py-3 border-2 border-red-500 text-red-600 font-black rounded-2xl hover:bg-red-500 hover:text-white transition-all shadow-sm active:scale-95">
                      Deactivate
                    </button>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </div>

        {/* Mobile BottomNavBar */}
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
          <button 
            onClick={() => navigate('/worker/car/mechanic/history')}
            className="flex flex-col items-center text-slate-400 hover:text-violet-600 transition-colors"
          >
            <History size={20} />
            <span className="text-[10px] font-bold mt-1">History</span>
          </button>
          <button className="flex flex-col items-center text-violet-600">
            <SettingsIcon size={20} />
            <span className="text-[10px] font-bold mt-1">Settings</span>
          </button>
        </nav>
      </main>
    </div>
  );
};

export default MechanicSettings;
