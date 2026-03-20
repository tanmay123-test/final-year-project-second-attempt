import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Wrench, 
  Fuel, 
  Truck, 
  Brain, 
  Home,
  Settings,
  Calendar,
  DollarSign,
  ChevronLeft,
  User,
  LogOut,
  Bell,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const CarServiceHomepage = () => {
  const navigate = useNavigate();
  const [selectedService, setSelectedService] = useState(null);
  const [workerData, setWorkerData] = useState(null);
  const [stats, setStats] = useState({
    activeJobs: 0,
    completedJobs: 0,
    earnings: 0,
    rating: 0
  });

  useEffect(() => {
    // Get worker data from localStorage
    const workerId = localStorage.getItem('worker_id');
    const workerEmail = localStorage.getItem('worker_email');
    
    if (workerId && workerEmail) {
      setWorkerData({
        id: workerId,
        email: workerEmail,
        name: workerEmail.split('@')[0] // Extract name from email
      });
      
      // Simulate fetching stats
      setStats({
        activeJobs: Math.floor(Math.random() * 5),
        completedJobs: Math.floor(Math.random() * 50) + 10,
        earnings: Math.floor(Math.random() * 5000) + 1000,
        rating: (Math.random() * 2 + 3).toFixed(1)
      });
    }
  }, []);

  const carServices = [
    {
      id: 'mechanic',
      label: 'Mechanic Services',
      icon: Wrench,
      description: 'Vehicle repair and maintenance',
      path: '/worker/car/mechanic/dashboard',
      gradient: 'linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%)',
      glassColor: 'rgba(59, 130, 246, 0.1)',
      borderColor: 'rgba(59, 130, 246, 0.3)',
      hoverColor: 'rgba(59, 130, 246, 0.2)'
    },
    {
      id: 'fuel_delivery',
      label: 'Fuel Delivery',
      icon: Fuel,
      description: 'Emergency fuel delivery',
      path: '/worker/car/fuel-delivery/dashboard',
      gradient: 'linear-gradient(135deg, #FB923C 0%, #EA580C 100%)',
      glassColor: 'rgba(251, 146, 60, 0.1)',
      borderColor: 'rgba(251, 146, 60, 0.3)',
      hoverColor: 'rgba(251, 146, 60, 0.2)'
    },
    {
      id: 'tow_truck',
      label: 'Tow Truck',
      icon: Truck,
      description: 'Vehicle towing and recovery',
      path: '/worker/car/tow-truck/dashboard',
      gradient: 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
      glassColor: 'rgba(16, 185, 129, 0.1)',
      borderColor: 'rgba(16, 185, 129, 0.3)',
      hoverColor: 'rgba(16, 185, 129, 0.2)'
    },
    {
      id: 'automobile_expert',
      label: 'Automobile Expert',
      icon: Brain,
      description: 'Expert consultation services',
      path: '/worker/car/automobile-expert/dashboard',
      gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
      glassColor: 'rgba(139, 92, 246, 0.1)',
      borderColor: 'rgba(139, 92, 246, 0.3)',
      hoverColor: 'rgba(139, 92, 246, 0.2)'
    }
  ];

  const handleLogout = () => {
    localStorage.removeItem('worker_id');
    localStorage.removeItem('worker_email');
    localStorage.removeItem('token');
    navigate('/worker/car/login');
  };

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon size={20} className="text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <ChevronLeft size={20} className="text-gray-600" />
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <Wrench size={16} className="text-white" />
                </div>
                <h1 className="text-xl font-bold text-gray-900">Car Services</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button className="p-2 rounded-lg hover:bg-gray-100 relative">
                <Bell size={20} className="text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 rounded-lg hover:bg-gray-100">
                <Settings size={20} className="text-gray-600" />
              </button>
              <div className="flex items-center space-x-2 pl-3 border-l border-gray-200">
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                  <User size={16} className="text-gray-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {workerData?.name || 'Worker'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {workerData?.email || 'Loading...'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-red-50 text-red-600"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {workerData?.name || 'Worker'}!
          </h2>
          <p className="text-gray-600">
            Manage your car service operations and track your performance
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Clock}
            label="Active Jobs"
            value={stats.activeJobs}
            color="bg-blue-500"
          />
          <StatCard
            icon={CheckCircle}
            label="Completed"
            value={stats.completedJobs}
            color="bg-green-500"
          />
          <StatCard
            icon={DollarSign}
            label="Earnings"
            value={`₹${stats.earnings}`}
            color="bg-yellow-500"
          />
          <StatCard
            icon={TrendingUp}
            label="Rating"
            value={`⭐ ${stats.rating}`}
            color="bg-purple-500"
          />
        </div>

        {/* Service Selection */}
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Select Service</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {carServices.map((service) => {
              const Icon = service.icon;
              return (
                <button
                  key={service.id}
                  onClick={() => navigate(service.path)}
                  className="group relative p-6 rounded-2xl border transition-all duration-300 hover:scale-105"
                  style={{
                    background: service.glassColor,
                    borderColor: service.borderColor,
                    borderWidth: '1px'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = service.hoverColor;
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = service.glassColor;
                  }}
                >
                  <div className="flex flex-col items-center text-center space-y-3">
                    <div
                      className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-lg"
                      style={{ background: service.gradient }}
                    >
                      <Icon size={28} className="text-white" />
                    </div>
                    <h4 className="font-semibold text-gray-900">{service.label}</h4>
                    <p className="text-sm text-gray-600">{service.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {[1, 2, 3].map((item) => (
              <div key={item} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Wrench size={16} className="text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Job #{item}00{item}</p>
                    <p className="text-sm text-gray-500">Vehicle repair service</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Completed
                  </span>
                  <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CarServiceHomepage;
