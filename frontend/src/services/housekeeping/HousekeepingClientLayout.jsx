import React from 'react';
import { Outlet } from 'react-router-dom';
import HousekeepingNavigation from './arrival/HousekeepingNavigation';
import { styled } from '../../stitches.config';

const LayoutContainer = styled('div', {
  minHeight: '100vh',
  backgroundColor: '#F9FAFB',
  paddingBottom: '80px', // Space for bottom nav on mobile
  
  '@md': {
    paddingBottom: 0,
    paddingTop: '64px', // Space for top nav on desktop
  },
});

const HousekeepingClientLayout = () => {
  return (
    <LayoutContainer>
      <HousekeepingNavigation />
      <Outlet />
    </LayoutContainer>
  );
};

export default HousekeepingClientLayout;
