import React, { useContext } from 'react';
import { render, waitFor, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { AuthProvider, AuthContext } from '../../context/AuthContext';
import * as api from '../../services/api';

// Mock API services
vi.mock('../../services/api', () => ({
  authService: {
    getUserInfo: vi.fn(),
    login: vi.fn(),
  },
  workerService: {
    verifyToken: vi.fn(),
    login: vi.fn(),
  }
}));

// Test Component to access context
const TestComponent = () => {
  const { user, worker, loading } = useContext(AuthContext);
  if (loading) return <div>Loading...</div>;
  return (
    <div>
      <div data-testid="user">{user ? user.username : 'No User'}</div>
      <div data-testid="worker">{worker ? worker.email : 'No Worker'}</div>
    </div>
  );
};

describe('AuthContext Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should authenticate user if user token is valid', async () => {
    localStorage.setItem('token', 'valid-user-token');
    api.authService.getUserInfo.mockResolvedValue({ data: { username: 'testuser' } });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('testuser'));
    expect(screen.getByTestId('worker')).toHaveTextContent('No Worker');
  });

  it('should authenticate worker if user token fails but worker token is valid', async () => {
    localStorage.setItem('token', 'valid-worker-token');
    // User info fails
    api.authService.getUserInfo.mockRejectedValue({ response: { status: 401 } });
    // Worker info succeeds
    api.workerService.verifyToken.mockResolvedValue({ 
      data: { id: 1, email: 'worker@test.com', name: 'Test Worker' } 
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => expect(screen.getByTestId('worker')).toHaveTextContent('worker@test.com'));
    expect(screen.getByTestId('user')).toHaveTextContent('No User');
  });

  it('should clear auth if both fail', async () => {
    localStorage.setItem('token', 'invalid-token');
    api.authService.getUserInfo.mockRejectedValue({ response: { status: 401 } });
    api.workerService.verifyToken.mockRejectedValue({ response: { status: 401 } });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => expect(screen.getByTestId('user')).toHaveTextContent('No User'));
    expect(screen.getByTestId('worker')).toHaveTextContent('No Worker');
    expect(localStorage.getItem('token')).toBeNull();
  });
});
