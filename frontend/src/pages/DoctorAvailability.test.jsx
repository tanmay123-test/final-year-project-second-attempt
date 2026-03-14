import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DoctorAvailability from './DoctorAvailability';
import { AuthProvider } from '../context/AuthContext';
import { MemoryRouter } from 'react-router-dom';
import * as apiModule from '../services/api';

// Mock the API module
vi.mock('../services/api', () => ({
  workerService: {
    getAvailability: vi.fn(),
    addAvailability: vi.fn(),
    removeAvailability: vi.fn(),
  },
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  }
}));

// Mock AuthContext
const mockWorker = {
  worker_id: 1,
  email: 'doctor@example.com',
  name: 'Dr. Test',
  role: 'doctor'
};

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    worker: mockWorker,
    loading: false
  }),
  AuthProvider: ({ children }) => <div>{children}</div>
}));

// Mock DoctorBottomNav to avoid routing issues in test
vi.mock('../components/DoctorBottomNav', () => ({
  default: () => <div data-testid="doctor-bottom-nav">Doctor Bottom Nav</div>
}));

describe('DoctorAvailability Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders availability page and fetches slots', async () => {
    const mockSlots = [
      { date: '2025-02-12', time_slot: '10:00 AM' },
      { date: '2025-02-12', time_slot: '02:00 PM' }
    ];

    apiModule.workerService.getAvailability.mockResolvedValue({
      data: { availability: mockSlots }
    });

    render(
      <MemoryRouter>
        <DoctorAvailability />
      </MemoryRouter>
    );

    // Check header
    expect(screen.getByText('Availability')).toBeInTheDocument();
    expect(screen.getByText('Manage your available dates and time slots')).toBeInTheDocument();

    // Check loading state or slots
    await waitFor(() => {
      expect(screen.getByText('10:00 AM')).toBeInTheDocument();
      expect(screen.getByText('02:00 PM')).toBeInTheDocument();
    });

    // Verify API call
    expect(apiModule.workerService.getAvailability).toHaveBeenCalledWith(1, expect.any(String));
  });

  it('adds a new time slot', async () => {
    apiModule.workerService.getAvailability.mockResolvedValue({ data: { availability: [] } });
    apiModule.workerService.addAvailability.mockResolvedValue({ data: { msg: 'Added' } });

    render(
      <MemoryRouter>
        <DoctorAvailability />
      </MemoryRouter>
    );

    // Select time
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '9:00 AM' } });

    // Click add
    const addButton = screen.getByText('Add Slot');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(apiModule.workerService.addAvailability).toHaveBeenCalledWith(1, expect.any(String), '9:00 AM');
    });
  });

  it('removes a time slot', async () => {
    const mockSlots = [{ date: '2025-02-12', time_slot: '10:00 AM' }];
    apiModule.workerService.getAvailability.mockResolvedValue({ data: { availability: mockSlots } });
    apiModule.workerService.removeAvailability.mockResolvedValue({ data: { msg: 'Removed' } });
    
    // Mock window.confirm
    window.confirm = vi.fn(() => true);

    render(
      <MemoryRouter>
        <DoctorAvailability />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('10:00 AM')).toBeInTheDocument();
    });

    const removeButton = screen.getByTitle('Remove slot');
    fireEvent.click(removeButton);

    expect(window.confirm).toHaveBeenCalled();
    
    await waitFor(() => {
      expect(apiModule.workerService.removeAvailability).toHaveBeenCalledWith(1, expect.any(String), '10:00 AM');
    });
  });
});
