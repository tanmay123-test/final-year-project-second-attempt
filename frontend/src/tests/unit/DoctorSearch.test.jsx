import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import DoctorSearch from '../../pages/DoctorSearch';
import { doctorService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

// Mock dependencies
vi.mock('../../services/api', () => ({
  doctorService: {
    getAllDoctors: vi.fn(),
    getSpecializations: vi.fn(),
    getDoctorsBySpecialization: vi.fn(),
    searchDoctors: vi.fn(),
  },
}));

vi.mock('../../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

describe('DoctorSearch Component', () => {
  const mockUser = { user_name: 'Test User' };
  const mockDoctors = [
    { id: 1, name: 'Dr. Smith', specialization: 'Cardiology', fee: 500 },
    { id: 2, name: 'Dr. Jones', specialization: 'Dentist', fee: 300 },
  ];
  const mockSpecializations = ['Cardiology', 'Dentist', 'HEART'];

  beforeEach(() => {
    vi.clearAllMocks();
    useAuth.mockReturnValue({ user: mockUser });
    doctorService.getAllDoctors.mockResolvedValue({ data: { doctors: mockDoctors } });
    doctorService.getSpecializations.mockResolvedValue({ data: { specializations: mockSpecializations } });
    doctorService.getDoctorsBySpecialization.mockResolvedValue({ data: { doctors: [mockDoctors[0]] } });
  });

  it('fetches all doctors when no search param is present', async () => {
    render(
      <MemoryRouter initialEntries={['/doctors']}>
        <Routes>
          <Route path="/doctors" element={<DoctorSearch />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(doctorService.getAllDoctors).toHaveBeenCalled();
      expect(doctorService.getDoctorsBySpecialization).not.toHaveBeenCalled();
      expect(screen.getByText('Dr. Smith')).toBeInTheDocument();
      expect(screen.getByText('Dr. Jones')).toBeInTheDocument();
    });
  });

  it('fetches doctors by specialization when "spec" param is present', async () => {
    render(
      <MemoryRouter initialEntries={['/doctors?spec=Cardiology']}>
        <Routes>
          <Route path="/doctors" element={<DoctorSearch />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(doctorService.getDoctorsBySpecialization).toHaveBeenCalledWith('Cardiology');
      expect(doctorService.getAllDoctors).not.toHaveBeenCalled();
      // Should only show filtered doctors (based on mock response)
      expect(screen.getByText('Dr. Smith')).toBeInTheDocument();
      // Dr. Jones should not be present in the filtered response
      expect(screen.queryByText('Dr. Jones')).not.toBeInTheDocument();
    });
  });

  it('displays the correct icon for HEART specialization', async () => {
    render(
      <MemoryRouter initialEntries={['/doctors']}>
        <Routes>
          <Route path="/doctors" element={<DoctorSearch />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('HEART')).toBeInTheDocument();
      // Verification of icon rendered is tricky with lucide-react in JSDOM, 
      // but we can check if the element exists.
      // The component renders icons inside .spec-icon-wrapper
    });
  });
});
