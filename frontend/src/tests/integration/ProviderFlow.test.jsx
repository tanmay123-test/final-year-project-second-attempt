import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProviderDashboard from '../../../../housekeeping/provider/frontend/pages/ProviderDashboard';
import ProviderSchedule from '../../../../housekeeping/provider/frontend/pages/ProviderSchedule';
import ProviderProfile from '../../../../housekeeping/provider/frontend/pages/ProviderProfile';
import ProviderEarnings from '../../../../housekeeping/provider/frontend/pages/ProviderEarnings';
import * as apiModule from '../../services/api';

// Mock API
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  }
}));

// Mock AuthContext
const mockWorker = {
  worker_id: 1,
  name: 'John Cleaner',
  email: 'john@example.com',
  role: 'housekeeping'
};

const mockLogout = vi.fn();

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({
    worker: mockWorker,
    logout: mockLogout,
    loading: false
  })
}));

// Mock Lucide Icons to avoid rendering issues
vi.mock('lucide-react', async () => {
  const actual = await vi.importActual('lucide-react');
  return {
    ...actual,
    Clock: () => <div data-testid="icon-clock" />,
    MapPin: () => <div data-testid="icon-map-pin" />,
    Calendar: () => <div data-testid="icon-calendar" />,
    Check: () => <div data-testid="icon-check" />,
    X: () => <div data-testid="icon-x" />,
    DollarSign: () => <div data-testid="icon-dollar-sign" />,
    Briefcase: () => <div data-testid="icon-briefcase" />,
    TrendingUp: () => <div data-testid="icon-trending-up" />,
    User: () => <div data-testid="icon-user" />,
    Settings: () => <div data-testid="icon-settings" />,
    LogOut: () => <div data-testid="icon-logout" />,
    LayoutGrid: () => <div data-testid="icon-layout-grid" />,
    Wallet: () => <div data-testid="icon-wallet" />,
    Star: () => <div data-testid="icon-star" />,
    ChevronRight: () => <div data-testid="icon-chevron-right" />,
    HelpCircle: () => <div data-testid="icon-help-circle" />,
    Shield: () => <div data-testid="icon-shield" />,
    FileText: () => <div data-testid="icon-file-text" />,
  };
});

// Mock ProviderBottomNav to avoid routing complexity in unit tests if needed, 
// but we want to test integration so we can leave it or mock if it causes issues.
// For now let's mock it to focus on page content, as Nav usually requires Router context which we provide.
// Actually, let's keep it real if possible, but simpler to mock for page isolation.
vi.mock('../../../../housekeeping/provider/frontend/components/ProviderBottomNav', () => ({
  default: () => <div data-testid="provider-bottom-nav">Bottom Nav</div>
}));

describe('Provider Housekeeping Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ProviderDashboard', () => {
    it('renders dashboard with stats and requests', async () => {
      // Mock API responses
      apiModule.default.get.mockImplementation((url) => {
        if (url === '/housekeeping/worker/status') {
          return Promise.resolve({ data: { is_online: true } });
        }
        if (url === '/housekeeping/my-bookings') {
          return Promise.resolve({
            data: {
              bookings: [
                {
                  id: 101,
                  service: 'Sofa Cleaning',
                  status: 'ASSIGNED', // Pending request
                  date: '2026-02-25',
                  time: '03:00 PM',
                  address: '123 Main St',
                  price: 500
                }
              ]
            }
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(
        <MemoryRouter>
          <ProviderDashboard />
        </MemoryRouter>
      );

      // Check Header
      expect(screen.getByText('Worker Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Online')).toBeInTheDocument();

      // Check Stats (Mock values in component for now, but ensure they render)
      expect(screen.getByText('Today')).toBeInTheDocument();
      expect(screen.getByText('Jobs Today')).toBeInTheDocument();

      // Check Requests
      await waitFor(() => {
        expect(screen.getByText('Sofa Cleaning')).toBeInTheDocument();
        expect(screen.getByText('123 Main St')).toBeInTheDocument();
        expect(screen.getByText('₹500')).toBeInTheDocument();
      });

      // Check Action Buttons
      expect(screen.getByText('Accept')).toBeInTheDocument();
      expect(screen.getByText('Decline')).toBeInTheDocument();
    });

    it('toggles online status', async () => {
      apiModule.default.get.mockImplementation((url) => {
        if (url === '/housekeeping/worker/status') return Promise.resolve({ data: { is_online: false } });
        if (url === '/housekeeping/my-bookings') return Promise.resolve({ data: { bookings: [] } });
        return Promise.resolve({});
      });
      apiModule.default.post.mockResolvedValue({});

      render(
        <MemoryRouter>
          <ProviderDashboard />
        </MemoryRouter>
      );

      // Initial state
      await waitFor(() => {
        expect(screen.getByText('Offline')).toBeInTheDocument();
      });

      // Toggle
      const toggle = screen.getByRole('checkbox');
      fireEvent.click(toggle);

      // Verify API call
      await waitFor(() => {
        expect(apiModule.default.post).toHaveBeenCalledWith('/housekeeping/worker/status', { is_online: true });
      });
    });
  });

  describe('ProviderSchedule', () => {
    it('renders schedule with job list and lifecycle actions', async () => {
      apiModule.default.get.mockImplementation((url) => {
        if (url === '/housekeeping/my-bookings') {
          return Promise.resolve({
            data: {
              bookings: [
                {
                  id: 201,
                  service: 'Deep Cleaning',
                  status: 'ACCEPTED',
                  date: '2026-02-26',
                  time: '10:00 AM',
                  address: '456 Park Ave',
                  price: 1200
                },
                {
                  id: 202,
                  service: 'Kitchen Cleaning',
                  status: 'IN_PROGRESS',
                  date: '2026-02-26',
                  time: '02:00 PM',
                  address: '789 Broadway',
                  price: 800
                }
              ]
            }
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
      apiModule.default.post.mockResolvedValue({});

      render(
        <MemoryRouter>
          <ProviderSchedule />
        </MemoryRouter>
      );

      expect(screen.getByText('Schedule')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.getByText('Deep Cleaning')).toBeInTheDocument();
        expect(screen.getByText('accepted')).toBeInTheDocument();
        expect(screen.getByText('Kitchen Cleaning')).toBeInTheDocument();
        expect(screen.getByText('in progress')).toBeInTheDocument();
      });

      // Test Start Job Action
      const startBtn = screen.getByText('Start Job');
      fireEvent.click(startBtn);
      expect(apiModule.default.post).toHaveBeenCalledWith('/housekeeping/worker/update-status', {
        booking_id: 201,
        status: 'IN_PROGRESS'
      });

      // Test Complete Job Action
      const completeBtn = screen.getByText('Complete Job');
      fireEvent.click(completeBtn);
      expect(apiModule.default.post).toHaveBeenCalledWith('/housekeeping/worker/update-status', {
        booking_id: 202,
        status: 'COMPLETED'
      });
    });
  });

  describe('ProviderProfile', () => {
    it('renders profile and handles logout', async () => {
      render(
        <MemoryRouter>
          <ProviderProfile />
        </MemoryRouter>
      );

      expect(screen.getByText('John Cleaner')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();

      // Find logout button (Sign Out text)
      const logoutBtn = screen.getByText('Sign Out');
      fireEvent.click(logoutBtn);

      expect(mockLogout).toHaveBeenCalled();
    });
  });

  describe('ProviderEarnings', () => {
    it('renders earnings stats', () => {
      render(
        <MemoryRouter>
          <ProviderEarnings />
        </MemoryRouter>
      );

      expect(screen.getByText('Total Balance')).toBeInTheDocument();
      expect(screen.getByText('Transaction History')).toBeInTheDocument();
    });
  });
});
