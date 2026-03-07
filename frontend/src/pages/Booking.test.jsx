import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import Booking from './Booking';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { doctorService, appointmentService } from '../shared/api';

// Mock API
vi.mock('../shared/api', () => ({
  doctorService: {
    getDoctorById: vi.fn(),
    getAvailability: vi.fn(),
  },
  appointmentService: {
    bookClinic: vi.fn(),
    bookVideo: vi.fn(),
  },
}));

// Mock Auth
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { user_id: 1, user_name: 'Test User' },
  }),
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Booking Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mocks
    doctorService.getDoctorById.mockResolvedValue({
      data: {
        worker: { id: 1, name: 'John Doe', specialization: 'Cardiologist', rating: 4.5 }
      }
    });
    
    doctorService.getAvailability.mockResolvedValue({
      data: {
        availability: [{ time_slot: '10:00 AM' }, { time_slot: '11:00 AM' }]
      }
    });
  });

  it('renders booking page and fetches doctor details', async () => {
    render(
      <MemoryRouter initialEntries={['/book/1']}>
        <Routes>
          <Route path="/book/:doctorId" element={<Booking />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Dr. John Doe')).toBeInTheDocument();
      expect(screen.getByText('Cardiologist')).toBeInTheDocument();
    });
  });

  it('allows selecting date and time slot', async () => {
    render(
      <MemoryRouter initialEntries={['/book/1']}>
        <Routes>
          <Route path="/book/:doctorId" element={<Booking />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Dr. John Doe')).toBeInTheDocument();
    });

    // Find date cards (we generated 7)
    // Just click the first one (today)
    // Note: The text is dynamic based on today's date.
    // We can just query by class or assume it's there.
    // The component defaults to today, so slots should be loaded/loading.
    
    await waitFor(() => {
        expect(doctorService.getAvailability).toHaveBeenCalled();
    });

    // Check for slots
    await waitFor(() => {
      expect(screen.getByText('10:00 AM')).toBeInTheDocument();
    });

    // Select a slot
    fireEvent.click(screen.getByText('10:00 AM'));
    
    // Check if active class is applied (implementation detail check or check state effect)
    // We can check if submit button is enabled if we also fill symptoms
  });

  it('submits booking form', async () => {
    appointmentService.bookClinic.mockResolvedValue({ data: { message: 'Success' } });

    render(
      <MemoryRouter initialEntries={['/book/1']}>
        <Routes>
          <Route path="/book/:doctorId" element={<Booking />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText('Dr. John Doe')).toBeInTheDocument());

    // Select slot
    await waitFor(() => expect(screen.getByText('10:00 AM')).toBeInTheDocument());
    fireEvent.click(screen.getByText('10:00 AM'));

    // Fill symptoms
    const textarea = screen.getByPlaceholderText(/Describe your symptoms/i);
    fireEvent.change(textarea, { target: { value: 'Headache' } });

    // Submit
    const submitBtn = screen.getByText('Confirm Booking');
    expect(submitBtn).not.toBeDisabled();
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(appointmentService.bookClinic).toHaveBeenCalledWith(expect.objectContaining({
        user_id: 1,
        worker_id: '1',
        symptoms: 'Headache',
        time_slot: '10:00 AM'
      }));
    });

    await waitFor(() => {
      expect(screen.getByText('Appointment booked successfully!')).toBeInTheDocument();
    });
  });
});
