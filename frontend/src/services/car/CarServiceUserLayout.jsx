import React, { useState } from 'react';
import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const CarServiceUserLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const isTowTruckRoute = location.pathname.includes('book-tow-truck');

  const isActive = (path) => {
    return location.pathname === path;
  };

  const navLinks = isTowTruckRoute ? [
    { label: 'Request', path: '/car-service/book-tow-truck' },
    { label: 'History', path: '/car-service/my-bookings' },
    { label: 'Garage', path: '/car-service/garage' },
    { label: 'Profile', path: '/profile' },
  ] : [
    { label: 'Browse', path: '/car-service/book-mechanic' },
    { label: 'Bookings', path: '/car-service/my-bookings' },
    { label: 'Messages', path: '/car-service/ai-mechanic' },
    { label: 'Dashboard', path: '/car-service/home' },
  ];

  return (
    <div className="min-h-screen bg-surface font-body text-on-surface antialiased">
      {/* Navbar */}
      <nav className="bg-[#f8f9ff]/80 dark:bg-[#191c20]/80 backdrop-blur-xl docked full-width top-0 sticky z-50 shadow-[0_12px_32px_rgba(25,28,32,0.04)]">
        <div className="flex justify-between items-center w-full px-6 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            {isTowTruckRoute && (
              <span 
                className="material-symbols-outlined text-primary cursor-pointer hover:bg-primary/5 p-2 rounded-full transition-all"
                onClick={() => navigate(-1)}
              >
                arrow_back
              </span>
            )}
            <div 
              className="text-2xl font-black tracking-tighter text-[#4d41df] dark:text-[#675df9] font-headline cursor-pointer"
              onClick={() => navigate('/services')}
            >
              {isTowTruckRoute ? 'TowAssist' : 'Expertease'}
            </div>
          </div>
          <div className="hidden md:flex items-center gap-8 font-manrope font-bold tracking-tight">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`${
                  isActive(link.path)
                    ? 'text-[#4d41df] dark:text-[#675df9] border-b-2 border-[#4d41df] font-bold'
                    : 'text-[#191c20] dark:text-[#f8f9ff] opacity-70 hover:text-[#4d41df] hover:opacity-100 transition-all'
                } py-1`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors scale-95 active:scale-90 transition-transform">notifications</button>
            <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors scale-95 active:scale-90 transition-transform">help_outline</button>
            <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors scale-95 active:scale-90 transition-transform">settings</button>
            <div className="w-10 h-10 rounded-full bg-surface-container-high overflow-hidden border-2 border-primary/20">
              <img 
                alt="User profile" 
                className="w-full h-full object-cover" 
                src={user?.profile_image || "https://lh3.googleusercontent.com/aida-public/AB6AXuDS3JGl-9KbpMYl6zh9LY2V4MfXmY3spfJMaCxVHF7r6e93mFgZJQHBVVViR8vxF-lDtq9kFXYn6lYv60lERtji_lrvnDSUHgjNKXzjR-omDZen3WrIBUF6F0ITjF0-OEKCsrB9wViol2BJmb_WQpqDGgxUkrB3EoxeWtu9nKQnd5KaP1iLfP-L4Q3SomxZU_cU8dm_qftFkAAxBHg0frLUmPN5qWYulb_MbuVICWtODN6eXRS0C_lBINStgouViJt4-PLIkDTZVmXs"}
              />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-80px)]">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 w-full flex justify-around items-center px-4 pb-safe pt-2 bg-white/80 dark:bg-[#191c20]/80 backdrop-blur-md z-50 rounded-t-xl shadow-[0_-4px_20px_rgba(25,28,32,0.06)] border-t border-[#c7c4d8]/15 md:hidden">
        {navLinks.map((link) => {
          let icon = 'home';
          if (link.label === 'Browse' || link.label === 'Request') icon = link.label === 'Request' ? 'location_on' : 'search';
          if (link.label === 'Bookings' || link.label === 'History') icon = link.label === 'History' ? 'history' : 'calendar_month';
          if (link.label === 'Messages' || link.label === 'Garage') icon = link.label === 'Garage' ? 'directions_car' : 'chat';
          if (link.label === 'Dashboard' || link.label === 'Profile') icon = link.label === 'Profile' ? 'person' : 'dashboard';

          return (
            <Link 
              key={link.path}
              to={link.path}
              className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all ${
                isActive(link.path) 
                  ? 'text-[#4d41df] dark:text-[#675df9] bg-[#4d41df]/10' 
                  : 'text-slate-500 dark:text-slate-400'
              }`}
            >
              <span className="material-symbols-outlined" style={{ fontVariationSettings: isActive(link.path) ? "'FILL' 1" : "'FILL' 0" }}>
                {icon}
              </span>
              <span className="font-inter text-[10px] font-medium uppercase tracking-wider">{link.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default CarServiceUserLayout;
