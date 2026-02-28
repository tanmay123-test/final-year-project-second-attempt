import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import ProviderDashboard from '../../../housekeeping/provider/frontend/pages/ProviderDashboard';
import ProviderSchedule from '../../../housekeeping/provider/frontend/pages/ProviderSchedule';
import ProviderEarnings from '../../../housekeeping/provider/frontend/pages/ProviderEarnings';
import ProviderProfile from '../../../housekeeping/provider/frontend/pages/ProviderProfile';

// Mock dependencies
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

// Mock Lucide icons
vi.mock('lucide-react', () => ({
  User: () => <div data-testid="icon-user" />,
  Phone: () => <div data-testid="icon-phone" />,
  Mail: () => <div data-testid="icon-mail" />,
  MapPin: () => <div data-testid="icon-map-pin" />,
  DollarSign: () => <div data-testid="icon-dollar-sign" />,
  LogOut: () => <div data-testid="icon-log-out" />,
  Clock: () => <div data-testid="icon-clock" />,
  Check: () => <div data-testid="icon-check" />,
  X: () => <div data-testid="icon-x" />,
  Navigation: () => <div data-testid="icon-navigation" />,
  TrendingUp: () => <div data-testid="icon-trending-up" />,
  Calendar: () => <div data-testid="icon-calendar" />,
  Home: () => <div data-testid="icon-home" />,
  Briefcase: () => <div data-testid="icon-briefcase" />
}));

// Mock ProviderBottomNav to avoid complexity
vi.mock('../../../housekeeping/provider/frontend/components/ProviderBottomNav', () => ({
  default: () => <div data-testid="provider-bottom-nav" />
}));

describe('Provider Pages Color Consistency', () => {
  const mockWorker = {
    name: 'Test Worker',
    phone: '1234567890',
    email: 'test@worker.com'
  };

  const mockAuthValue = {
    worker: mockWorker,
    logout: vi.fn(),
    workerLogin: vi.fn()
  };

  const renderWithAuth = (Component) => {
    return render(
      <AuthContext.Provider value={mockAuthValue}>
        <MemoryRouter>
          {Component}
        </MemoryRouter>
      </AuthContext.Provider>
    );
  };

  it('ProviderDashboard uses purple theme', () => {
    renderWithAuth(<ProviderDashboard />);
    
    // Check header gradient/background
    // Structure: h1 -> div(flex) -> div(gradient)
    const headerTitle = screen.getByText('Worker Dashboard');
    const header = headerTitle.closest('div').parentElement;
    
    const style = header.getAttribute('style');
    // Check for either Hex or RGB format (JSDOM/React might normalize to RGB)
    const hasPurple = style.includes('#8E44AD') || style.includes('rgb(142, 68, 173)');
    expect(hasPurple).toBe(true);
  });

  it('ProviderSchedule uses purple theme', () => {
    renderWithAuth(<ProviderSchedule />);
    
    // Check header background
    const headerTitle = screen.getByText('Schedule');
    const headerContainer = headerTitle.closest('div');
    const style = headerContainer.getAttribute('style');
    const hasPurple = style.includes('#8E44AD') || style.includes('rgb(142, 68, 173)');
    expect(hasPurple).toBe(true);
  });

  it('ProviderEarnings uses purple theme', () => {
    renderWithAuth(<ProviderEarnings />);
    
    // Check header background
    const headerTitle = screen.getByText('Earnings');
    const headerContainer = headerTitle.closest('div');
    const style = headerContainer.getAttribute('style');
    const hasPurple = style.includes('#8E44AD') || style.includes('rgb(142, 68, 173)');
    expect(hasPurple).toBe(true);
  });

  it('ProviderProfile uses purple theme', () => {
    renderWithAuth(<ProviderProfile />);
    
    // Check header gradient
    const headerTitle = screen.getByText('Test Worker');
    const headerContainer = headerTitle.closest('div');
    const style = headerContainer.getAttribute('style');
    const hasPurple = style.includes('#8E44AD') || style.includes('rgb(142, 68, 173)');
    expect(hasPurple).toBe(true);
    
    // Check Status color
    const statusValue = screen.getByText('Active');
    const statusStyle = statusValue.getAttribute('style');
    const statusHasPurple = statusStyle.includes('#8E44AD') || statusStyle.includes('rgb(142, 68, 173)');
    expect(statusHasPurple).toBe(true);
  });
});
