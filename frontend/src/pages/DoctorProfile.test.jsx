import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DoctorProfile from './DoctorProfile';
import { MemoryRouter } from 'react-router-dom';

// Mock AuthContext
const mockLogout = vi.fn();
const mockWorker = {
  worker_id: 1,
  name: 'Test User',
  specialization: 'Cardiologist'
};

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    worker: mockWorker,
    logout: mockLogout
  })
}));

// Mock DoctorBottomNav
vi.mock('../components/DoctorBottomNav', () => ({
  default: () => <div data-testid="doctor-bottom-nav">Doctor Bottom Nav</div>
}));

// Mock window.confirm
window.confirm = vi.fn(() => true);

describe('DoctorProfile Component', () => {
  it('renders doctor profile information', () => {
    render(
      <MemoryRouter>
        <DoctorProfile />
      </MemoryRouter>
    );

    expect(screen.getByText('Dr. Test User')).toBeInTheDocument();
    expect(screen.getByText('Cardiologist')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('DOC001')).toBeInTheDocument(); // Formatted ID
  });

  it('renders menu items', () => {
    render(
      <MemoryRouter>
        <DoctorProfile />
      </MemoryRouter>
    );

    expect(screen.getByText('View Full Details')).toBeInTheDocument();
    expect(screen.getByText('Subscription & Billing')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Help & Support')).toBeInTheDocument();
  });

  it('handles logout', () => {
    render(
      <MemoryRouter>
        <DoctorProfile />
      </MemoryRouter>
    );

    const logoutBtn = screen.getByText('Logout');
    fireEvent.click(logoutBtn);

    expect(window.confirm).toHaveBeenCalled();
    expect(mockLogout).toHaveBeenCalled();
  });
});
