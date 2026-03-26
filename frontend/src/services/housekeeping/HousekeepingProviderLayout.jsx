import React from 'react';
import { Outlet } from 'react-router-dom';
import ProviderBottomNav from './provider/components/ProviderBottomNav';
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

const HousekeepingProviderLayout = () => {
  return (
    <LayoutContainer>
      <ProviderBottomNav />
      <Outlet />
    </LayoutContainer>
  );
};

export default HousekeepingProviderLayout;
