import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Home, Package, Fuel, History, Target, User } from 'lucide-react';

const BASE = '/worker/car/fuel-delivery';

const navItems = [
  { path: `${BASE}/home`, label: 'dashboard', icon: Home },
  { path: `${BASE}/requests`, label: 'Jobs', icon: Package },
  { path: `${BASE}/active-delivery`, label: 'Active Delivery', icon: Fuel },
  { path: `${BASE}/history`, label: 'Delivery History & Earnings', icon: History },
  { path: `${BASE}/performance`, label: 'Performance, Reputation & Safety', icon: Target },
  { path: `${BASE}/profile`, label: 'profile', icon: User },
];

export default function FuelDeliveryLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const pathname = location.pathname;

  return (
    <>
      <style>{`
        .fuel-delivery-layout-content {
          min-height: 100vh;
          padding-bottom: 72px;
        }
        .fuel-delivery-bottom-nav {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: white;
          border-top: 1px solid #e0e0e0;
          display: flex;
          justify-content: space-around;
          padding: 8px 0;
          z-index: 1000;
          padding-bottom: max(8px, env(safe-area-inset-bottom));
        }
        .fuel-delivery-nav-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
          padding: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
          border-radius: 8px;
          min-width: 50px;
          border: none;
          background: none;
          color: #666;
        }
        .fuel-delivery-nav-item:hover {
          background: #f5f5f5;
        }
        .fuel-delivery-nav-item.active {
          color: #ff6b35;
        }
        .fuel-delivery-nav-item svg {
          color: inherit;
        }
        .fuel-delivery-nav-item.active svg {
          color: #ff6b35;
        }
        .fuel-delivery-nav-label {
          font-size: 11px;
          color: inherit;
          margin-top: 2px;
        }
        .fuel-delivery-nav-item.active .fuel-delivery-nav-label {
          color: #ff6b35;
        }
      `}</style>
      <div className="fuel-delivery-layout-content">
        <Outlet />
      </div>
      <nav className="fuel-delivery-bottom-nav" aria-label="Fuel delivery worker navigation">
        {navItems.map(({ path, label, icon: Icon }) => {
          const isActive = pathname === path;
          return (
            <button
              key={path}
              type="button"
              className={`fuel-delivery-nav-item ${isActive ? 'active' : ''}`}
              onClick={() => navigate(path)}
              aria-current={isActive ? 'page' : undefined}
            >
              <Icon size={20} />
              <span className="fuel-delivery-nav-label">{label}</span>
            </button>
          );
        })}
      </nav>
    </>
  );
}
