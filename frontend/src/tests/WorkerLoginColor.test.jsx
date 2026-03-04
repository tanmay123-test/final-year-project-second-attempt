import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import WorkerLogin from '../pages/WorkerLogin';
import WorkerSignup from '../pages/WorkerSignup';
import { AuthContext } from '../context/AuthContext';
import { doctorService, workerService } from '../services/api';

// Mock AuthContext
const mockLogin = vi.fn();
const mockAuthValue = {
  login: mockLogin,
  user: null,
  loading: false,
  workerLogin: vi.fn()
};

// Mock API services for Signup
vi.mock('../services/api', () => ({
  doctorService: {
    getSpecializations: vi.fn().mockResolvedValue({ data: { specializations: ['Cardiology'] } })
  },
  workerService: {
    register: vi.fn(),
    registerHealthcare: vi.fn()
  },
  authService: {
    login: vi.fn(),
    getUserInfo: vi.fn()
  }
}));

const renderWithAuth = (Component, serviceType) => {
  return render(
    <AuthContext.Provider value={mockAuthValue}>
      <MemoryRouter initialEntries={[`/worker/${serviceType}/login`]}>
        <Routes>
          <Route 
            path="/worker/housekeeping/login" 
            element={<WorkerLogin serviceType="housekeeping" />} 
          />
          <Route 
            path="/worker/money/login" 
            element={<WorkerLogin serviceType="money" />} 
          />
           <Route 
            path="/worker/housekeeping/signup" 
            element={<WorkerSignup serviceType="housekeeping" />} 
          />
          <Route 
            path="/worker/money/signup" 
            element={<WorkerSignup serviceType="money" />} 
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>
  );
};

describe('WorkerLogin Color Consistency', () => {
  it('should use purple gradient for housekeeping login', () => {
    const { container } = renderWithAuth(WorkerLogin, 'housekeeping');
    const button = screen.getByRole('button', { name: /sign in/i });
    expect(button).toHaveStyle({ background: 'var(--medical-gradient)' });
    const iconContainer = container.querySelector('.auth-icon');
    expect(iconContainer).toHaveStyle({ background: 'var(--medical-gradient)' });
    const link = screen.getByRole('link', { name: /join as a provider/i });
    expect(link).toHaveStyle({ color: '#8E44AD' });
  });

  it('should use service color (green) for money login', () => {
    const { container } = renderWithAuth(WorkerLogin, 'money');
    const button = screen.getByRole('button', { name: /sign in/i });
    expect(button).toHaveStyle({ background: '#2ECC71' });
    const iconContainer = container.querySelector('.auth-icon');
    expect(iconContainer).toHaveStyle({ background: '#2ECC71' });
    const link = screen.getByRole('link', { name: /join as a provider/i });
    expect(link).toHaveStyle({ color: '#2ECC71' });
  });
});

describe('WorkerSignup Color Consistency', () => {
  const renderSignup = (serviceType) => {
    return render(
      <AuthContext.Provider value={mockAuthValue}>
        <MemoryRouter initialEntries={[`/worker/${serviceType}/signup`]}>
          <Routes>
            <Route 
              path="/worker/housekeeping/signup" 
              element={<WorkerSignup serviceType="housekeeping" />} 
            />
            <Route 
              path="/worker/money/signup" 
              element={<WorkerSignup serviceType="money" />} 
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>
    );
  };

  it('should use purple gradient for housekeeping signup', () => {
    const { container } = renderSignup('housekeeping');
    
    const button = screen.getByRole('button', { name: /register/i });
    expect(button).toHaveStyle({ background: 'var(--medical-gradient)' });
    
    const iconContainer = container.querySelector('.auth-icon');
    expect(iconContainer).toHaveStyle({ background: 'var(--medical-gradient)' });

    const link = screen.getByRole('link', { name: /login/i });
    expect(link).toHaveStyle({ color: '#8E44AD' });
  });

  it('should use service color (green) for money signup', () => {
    const { container } = renderSignup('money');
    
    const button = screen.getByRole('button', { name: /register/i });
    expect(button).toHaveStyle({ background: '#2ECC71' });
    
    const iconContainer = container.querySelector('.auth-icon');
    expect(iconContainer).toHaveStyle({ background: '#2ECC71' });

    const link = screen.getByRole('link', { name: /login/i });
    expect(link).toHaveStyle({ color: '#2ECC71' });
  });
});
