import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import DoctorLogin from '../../pages/DoctorLogin';

// Mock AuthContext
const mockWorkerLogin = vi.fn();
const mockUseAuth = vi.fn();

vi.mock('../../context/AuthContext', () => ({
  useAuth: () => mockUseAuth(),
}));

describe('DoctorLogin Unit Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue({
      workerLogin: mockWorkerLogin,
    });
  });

  it('renders login form with correct elements', () => {
    render(
      <MemoryRouter>
        <DoctorLogin />
      </MemoryRouter>
    );

    expect(screen.getByText('Doctor Portal')).toBeInTheDocument();
    expect(screen.getByText('Login with your registered email')).toBeInTheDocument();
    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('validates input fields are required', () => {
    render(
      <MemoryRouter>
        <DoctorLogin />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText('Email Address');

    expect(emailInput).toBeRequired();
  });

  it('calls workerLogin with correct credentials on submit', async () => {
    mockWorkerLogin.mockResolvedValueOnce({});

    render(
      <MemoryRouter>
        <DoctorLogin />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Email Address'), {
      target: { value: 'doctor@example.com' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockWorkerLogin).toHaveBeenCalledWith('doctor@example.com');
    });
  });

  it('displays error message on failed login', async () => {
    const errorMessage = 'Failed to login. Please check your email.';
    mockWorkerLogin.mockRejectedValueOnce({
      response: { data: { error: errorMessage } },
    });

    render(
      <MemoryRouter>
        <DoctorLogin />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Email Address'), {
      target: { value: 'doctor@invalid.com' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('navigates to dashboard on successful login', async () => {
    mockWorkerLogin.mockResolvedValueOnce({});

    render(
      <MemoryRouter initialEntries={['/doctor/login']}>
        <Routes>
          <Route path="/doctor/login" element={<DoctorLogin />} />
          <Route path="/worker/dashboard" element={<div>Worker Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText('Email Address'), {
      target: { value: 'doctor@example.com' },
    });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText('Worker Dashboard')).toBeInTheDocument();
    });
  });
});
