import React, { useState, useEffect } from 'react';
import { Search, Bell, Home, Bot, Compass, Calendar, User, ChevronRight, Activity, Heart, Baby, Bone } from 'lucide-react';
import SpecializationCard from '../components/SpecializationCard';
import DoctorCard from '../components/DoctorCard';
import { getSpecializations, getTopDoctors } from '../services/healthcareServiceOrganized.js';

console.log('[CLI] Healthcare Dashboard component initialized (using organized database)');

const HealthcareDashboard = () => {
  const [specializations, setSpecializations] = useState([]);
  const [topDoctors, setTopDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const specializationIcons = {
    'General': Activity,
    'Cardiology': Heart,
    'Dermatology': Heart,
    'Pediatrics': Baby,
    'Orthopedics': Bone
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [specializationsData, doctorsData] = await Promise.all([
        getSpecializations(),
        getTopDoctors()
      ]);
      setSpecializations(specializationsData);
      setTopDoctors(doctorsData);
    } catch (error) {
      console.error('[CLI] Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50" style={{ minHeight: '100vh', paddingBottom: '80px' }}>
      {/* Header Section */}
      <div 
        className="px-6 pt-8 pb-10 text-white relative"
        style={{
          background: 'linear-gradient(135deg, #7B4BB7 0%, #9C6BD4 100%)',
          paddingTop: '32px',
          paddingBottom: '40px',
          borderBottomLeftRadius: '30px',
          borderBottomRightRadius: '30px'
        }}
      >
        <div className="flex justify-between items-start mb-6">
          <div>
            <p className="text-lg font-medium" style={{ opacity: 0.9 }}>Welcome back 👋</p>
            <h1 className="text-3xl font-bold mt-2">John</h1>
            <p className="text-sm mt-1 opacity-80">Your health, our priority</p>
          </div>
          <div className="relative">
            <Bell className="w-6 h-6 text-white" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="px-6 -mt-6">
        <div className="relative max-w-2xl mx-auto">
          <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search doctors, specializations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-14 pr-6 py-4 bg-white rounded-2xl shadow-lg focus:outline-none focus:ring-2 focus:ring-purple-200 text-gray-700 placeholder-gray-400 border border-gray-100"
            style={{
              padding: '16px',
              paddingLeft: '56px',
              fontSize: '16px'
            }}
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-6 mt-8">
        <div className="grid grid-cols-4 gap-4 max-w-md mx-auto">
          <button className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Calendar className="w-5 h-5 text-purple-600" />
            </div>
            <span className="text-xs text-gray-600">Book</span>
          </button>
          <button className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-blue-600" />
            </div>
            <span className="text-xs text-gray-600">AI Care</span>
          </button>
          <button className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <Compass className="w-5 h-5 text-green-600" />
            </div>
            <span className="text-xs text-gray-600">Find</span>
          </button>
          <button className="flex flex-col items-center gap-2 p-3 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-orange-600" />
            </div>
            <span className="text-xs text-gray-600">Profile</span>
          </button>
        </div>
      </div>

      {/* Specializations Section */}
      <div className="px-6 mt-10">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Specializations</h2>
            <p className="text-sm text-gray-500 mt-1">Find doctors by specialty</p>
          </div>
          <button className="text-purple-600 font-medium flex items-center gap-2 px-4 py-2 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            View All <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
          {loading ? (
            Array(5).fill(0).map((_, index) => (
              <div key={index} className="flex-shrink-0 w-28 h-28 bg-gray-200 rounded-2xl animate-pulse"></div>
            ))
          ) : (
            specializations.map((spec, index) => {
              const IconComponent = specializationIcons[spec.name] || Activity;
              return (
                <SpecializationCard
                  key={index}
                  name={spec.name}
                  icon={IconComponent}
                />
              );
            })
          )}
        </div>
      </div>

      {/* Top Doctors Section */}
      <div className="px-6 mt-10">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Top Doctors</h2>
            <p className="text-sm text-gray-500 mt-1">Highly rated specialists near you</p>
          </div>
          <button className="text-purple-600 font-medium flex items-center gap-2 px-4 py-2 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            See All <ChevronRight className="w-4 h-4" />
          </button>
        </div>
        
        {/* Desktop: Grid Layout | Mobile: Single Column */}
        <div className="grid gap-6" style={{ 
          gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))'
        }}>
          {loading ? (
            Array(3).fill(0).map((_, index) => (
              <div key={index} className="bg-white rounded-2xl p-6 shadow-sm animate-pulse">
                <div className="flex gap-4">
                  <div className="w-16 h-16 bg-gray-200 rounded-full"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            topDoctors.map((doctor, index) => (
              <DoctorCard key={index} doctor={doctor} />
            ))
          )}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
        <div className="flex justify-around py-3 max-w-md mx-auto">
          <button className="flex flex-col items-center gap-1 py-2 px-4 relative">
            <Home className="w-5 h-5" style={{ color: '#7B4BB7' }} />
            <span className="text-xs font-medium" style={{ color: '#7B4BB7' }}>Home</span>
            <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-purple-600 rounded-full"></div>
          </button>
          <button className="flex flex-col items-center gap-1 py-2 px-4">
            <Bot className="w-5 h-5" style={{ color: '#8C8C8C' }} />
            <span className="text-xs font-medium" style={{ color: '#8C8C8C' }}>AI Care</span>
          </button>
          <button className="flex flex-col items-center gap-1 py-2 px-4">
            <Compass className="w-5 h-5" style={{ color: '#8C8C8C' }} />
            <span className="text-xs font-medium" style={{ color: '#8C8C8C' }}>Explore</span>
          </button>
          <button className="flex flex-col items-center gap-1 py-2 px-4">
            <Calendar className="w-5 h-5" style={{ color: '#8C8C8C' }} />
            <span className="text-xs font-medium" style={{ color: '#8C8C8C' }}>Appointments</span>
          </button>
          <button className="flex flex-col items-center gap-1 py-2 px-4">
            <User className="w-5 h-5" style={{ color: '#8C8C8C' }} />
            <span className="text-xs font-medium" style={{ color: '#8C8C8C' }}>Profile</span>
          </button>
        </div>
      </div>

      <style jsx>{`
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        
        /* Desktop Styles */
        @media (min-width: 768px) {
          .px-6 {
            padding-left: 3rem;
            padding-right: 3rem;
          }
          
          .mt-10 {
            margin-top: 4rem;
          }
          
          .grid {
            max-width: 1200px;
            margin: 0 auto;
          }
          
          .grid-cols-4 {
            grid-template-columns: repeat(4, 1fr);
            max-width: 600px;
          }
        }
        
        /* Mobile Styles */
        @media (max-width: 767px) {
          .grid {
            grid-template-columns: 1fr !important;
          }
          
          .grid-cols-4 {
            grid-template-columns: repeat(4, 1fr) !important;
            max-width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default HealthcareDashboard;
