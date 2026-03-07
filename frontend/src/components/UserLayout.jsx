import React from 'react';
import { Outlet } from 'react-router-dom';
import BottomNav from './BottomNav';

const UserLayout = () => {
  return (
    <div className="user-layout" style={{ paddingBottom: '80px', minHeight: '100vh' }}>
      <Outlet />
      <BottomNav />
    </div>
  );
};

export default UserLayout;
