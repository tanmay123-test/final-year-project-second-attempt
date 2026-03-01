import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import UserBookings from '../../../../housekeeping/arrival/frontend/pages/UserBookings';
import * as apiModule from '../../services/api';

vi.mock('../../services/api', () => {
  return {
    default: { get: vi.fn(), post: vi.fn() },
    housekeepingService: {
      getUserBookings: vi.fn(),
      cancelBooking: vi.fn()
    }
  };
});

describe('UserBookings worker name display', () => {
  it('shows worker name as title and service as subtitle in list view', async () => {
    apiModule.housekeepingService.getUserBookings.mockResolvedValue({
      data: {
        bookings: [
          {
            id: 10,
            service_type: 'Deep Cleaning',
            worker_id: 99,
            worker_name: 'Tanmay',
            booking_date: '2026-03-01',
            time_slot: '11:00 AM',
            status: 'ACCEPTED',
            price: 500,
            address: 'Mumbai'
          }
        ]
      }
    });

    render(
      <MemoryRouter>
        <UserBookings />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Tanmay')).toBeInTheDocument();
      expect(screen.getByText('Deep Cleaning')).toBeInTheDocument();
    });
  });

  it('shows fallback name when worker info missing', async () => {
    apiModule.housekeepingService.getUserBookings.mockResolvedValue({
      data: {
        bookings: [
          {
            id: 11,
            service_type: 'Bathroom Cleaning',
            booking_date: '2026-03-02',
            time_slot: '10:00 AM',
            status: 'PENDING',
            price: 300
          }
        ]
      }
    });

    render(
      <MemoryRouter>
        <UserBookings />
      </MemoryRouter>
    );

    await waitFor(() => {
      // Fallback text in title line should be present
      expect(screen.getByText('Assigned Provider')).toBeInTheDocument();
      expect(screen.getByText('Bathroom Cleaning')).toBeInTheDocument();
    });
  });

  it('opens and shows details view with worker name', async () => {
    apiModule.housekeepingService.getUserBookings.mockResolvedValue({
      data: {
        bookings: [
          {
            id: 12,
            service_type: 'Kitchen Cleaning',
            worker_id: 101,
            worker_name: 'Sync Test Cleaner',
            booking_date: '2026-03-03',
            time_slot: '12:00 PM',
            status: 'ASSIGNED',
            price: 450,
            address: 'NY'
          }
        ]
      }
    });

    render(
      <MemoryRouter>
        <UserBookings />
      </MemoryRouter>
    );

    // Wait for list, then open details
    await waitFor(() => {
      expect(screen.getByText('Sync Test Cleaner')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('View Details'));

    await waitFor(() => {
      expect(screen.getByText('Sync Test Cleaner')).toBeInTheDocument();
      expect(screen.getByText('Kitchen Cleaning')).toBeInTheDocument();
      expect(screen.getByText(/Date & Time:/)).toBeInTheDocument();
    });
  });
});

