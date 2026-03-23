import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Car, 
  Wrench, 
  Bot, 
  Calendar, 
  User, 
  Brain, 
  ArrowRight,
  TrendingUp,
  Clock,
  CheckCircle,
  ShieldCheck
} from 'lucide-react';

const CarServiceHome = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      id: 'book-mechanic',
      title: 'Book Mechanic',
      description: 'Find and book local mechanics for repair and maintenance',
      icon: Wrench,
      color: 'bg-primary',
      path: '/car-service/book-mechanic'
    },
    {
      id: 'ai-mechanic',
      title: 'AI Mechanic',
      description: 'Get instant AI-powered diagnostics for your vehicle',
      icon: Bot,
      color: 'bg-secondary',
      path: '/car-service/ai-mechanic'
    },
    {
      id: 'garage',
      title: 'My Garage',
      description: 'Manage your vehicle fleet and maintenance history',
      icon: Car,
      color: 'bg-tertiary',
      path: '/car-service/garage'
    },
    {
      id: 'ask-expert',
      title: 'Ask Expert',
      description: 'Consult with high-performance automobile specialists',
      icon: Brain,
      color: 'bg-primary-container',
      path: '/car-service/ask-expert'
    }
  ];

  const stats = [
    { label: 'Active Bookings', value: '2', icon: Clock, color: 'text-primary' },
    { label: 'Completed', value: '12', icon: CheckCircle, color: 'text-tertiary' },
    { label: 'Reliability', value: '99%', icon: ShieldCheck, color: 'text-secondary' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 pt-12 pb-32">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-16">
        <div className="max-w-2xl">
          <h1 className="font-headline font-extrabold text-5xl tracking-tight text-on-surface mb-6">
            Welcome to <span className="text-primary">Expertease</span> Car Care
          </h1>
          <p className="text-on-surface-variant text-lg font-body leading-relaxed">
            Your premium destination for vehicle maintenance. From instant diagnostics to expert repairs, we keep your performance machines at their peak.
          </p>
        </div>
        
        <div className="flex gap-4">
          {stats.map((stat, idx) => (
            <div key={idx} className="bg-surface-container-low p-6 rounded-2xl border border-outline-variant/15 min-w-[140px]">
              <div className={`${stat.color} mb-2`}>
                <stat.icon size={24} />
              </div>
              <div className="text-2xl font-black text-on-surface">{stat.value}</div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-outline">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => navigate(item.path)}
            className="group relative bg-surface-container-lowest p-8 rounded-3xl border border-outline-variant/15 shadow-[0_12px_32px_rgba(25,28,32,0.04)] hover:bg-surface-bright transition-all text-left overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-surface-container-low rounded-full -mr-16 -mt-16 group-hover:scale-110 transition-transform"></div>
            
            <div className="relative z-10">
              <div className={`${item.color} w-14 h-14 rounded-2xl flex items-center justify-center text-white mb-6 shadow-lg`}>
                <item.icon size={28} />
              </div>
              <h3 className="text-2xl font-headline font-bold text-on-surface mb-2">{item.title}</h3>
              <p className="text-on-surface-variant font-body mb-8 max-w-xs">{item.description}</p>
              
              <div className="flex items-center gap-2 text-primary font-bold group-hover:gap-4 transition-all">
                <span>Get Started</span>
                <ArrowRight size={18} />
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Quick Actions / Recent Bookings Preview */}
      <div className="bg-surface-container-lowest p-8 rounded-3xl border border-outline-variant/15 shadow-[0_12px_32px_rgba(25,28,32,0.04)]">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-xl font-headline font-bold text-on-surface">Recent Activity</h3>
          <button 
            onClick={() => navigate('/car-service/my-bookings')}
            className="text-primary font-bold text-sm hover:underline"
          >
            View All Bookings
          </button>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-surface-container-low rounded-2xl border border-outline-variant/10">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                <Wrench size={20} />
              </div>
              <div>
                <p className="font-bold text-on-surface">Porsche 911 Service</p>
                <p className="text-xs text-on-surface-variant">Scheduled for Tomorrow • 09:30 AM</p>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full bg-secondary-container/15 text-secondary text-[10px] font-bold uppercase">Pending</span>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-surface-container-low rounded-2xl border border-outline-variant/10">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-tertiary/10 flex items-center justify-center text-tertiary">
                <CheckCircle size={20} />
              </div>
              <div>
                <p className="font-bold text-on-surface">BMW M4 Competition</p>
                <p className="text-xs text-on-surface-variant">Completed Oct 20, 2023</p>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full bg-tertiary-container/10 text-tertiary text-[10px] font-bold uppercase">Completed</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarServiceHome;
