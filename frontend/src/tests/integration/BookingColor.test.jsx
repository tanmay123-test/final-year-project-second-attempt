import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import BookingFlow from '../../../../housekeeping/arrival/frontend/pages/BookingFlow';
import UserBookings from '../../../../housekeeping/arrival/frontend/pages/UserBookings';
import * as apiModule from '../../services/api';

// Mock API
vi.mock('../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  }
}));

// Mock Lucide Icons
vi.mock('lucide-react', async () => {
  const actual = await vi.importActual('lucide-react');
  return {
    ...actual,
    ArrowLeft: () => <div data-testid="icon-arrow-left" />,
    Clock: () => <div data-testid="icon-clock" />,
    Calendar: () => <div data-testid="icon-calendar" />,
    Check: () => <div data-testid="icon-check" />,
    CreditCard: () => <div data-testid="icon-credit-card" />,
    MapPin: () => <div data-testid="icon-map-pin" />,
    MoreVertical: () => <div data-testid="icon-more-vertical" />,
    ArrowRight: () => <div data-testid="icon-arrow-right" />,
    Home: () => <div data-testid="icon-home" />,
    Bot: () => <div data-testid="icon-bot" />,
    Search: () => <div data-testid="icon-search" />,
    User: () => <div data-testid="icon-user" />,
  };
});

describe('Housekeeping Color Scheme Verification', () => {
  const PRIMARY_COLOR = 'rgb(142, 68, 173)'; // #8E44AD
  const LIGHT_COLOR = 'rgb(243, 229, 245)'; // #F3E5F5

  describe('BookingFlow', () => {
    it('uses primary color for headers and active elements', async () => {
      apiModule.default.get.mockResolvedValue({
        data: {
          services: [
            { id: 1, name: 'General Cleaning', base_price: 500 }
          ]
        }
      });

      render(
        <MemoryRouter>
          <BookingFlow />
        </MemoryRouter>
      );

      // Check Header Color
      const header = screen.getByText('Select Service');
      expect(header).toHaveStyle({ color: PRIMARY_COLOR });

      // Click the service to trigger selection and move to Step 2
      const serviceName = await screen.findByText('General Cleaning');
      const serviceCard = serviceName.closest('div').parentElement;
      fireEvent.click(serviceCard);

      // Now we should be on Step 2: Booking Type
      // There are two "Booking Type" texts: one in the header and one in the step content.
      // We can use getAllByText and check if at least one is present, or just check for "Schedule" option.
      expect(screen.getAllByText('Booking Type').length).toBeGreaterThan(0);
      
      // Select 'Schedule' Booking Type
      const scheduleOption = screen.getByText('Schedule').closest('div');
      fireEvent.click(scheduleOption);
      
      // Click Continue to go to Step 3 (Schedule Service)
      const continueBtn = screen.getByText('Continue');
      fireEvent.click(continueBtn);

      // Now we should be on Step 3: Schedule Service
      expect(screen.getByText('Schedule Service')).toBeInTheDocument();

      // Find a date button (e.g., today's date)
      const today = new Date().getDate().toString();
      // There might be multiple elements with the date number, so be careful. 
      // The date button has the day number in bold.
      // Let's just pick the first button in the date list.
      const dateButtons = screen.getAllByRole('button');
      // The first button is "Back", then maybe date buttons.
      // Let's find by text.
      const dateBtn = screen.getByText(today).closest('button');
      
      // Click it to select
      fireEvent.click(dateBtn);

      // Check style of selected date button
      // Note: In React inline styles, colors are often normalized to RGB
      // The button styling logic:
      // backgroundColor: isSelected ? '#8E44AD' : 'white'
      // borderColor: isSelected ? '#8E44AD' : '#E5E7EB'
      // color: isSelected ? 'white' : '#374151'
      
      // We need to check if the styles are applied correctly.
      // Since we are mocking the time/date, let's just check the styles directly.
      expect(dateBtn).toHaveStyle({ backgroundColor: PRIMARY_COLOR });
    });
  });

  describe('UserBookings', () => {
    it('uses primary color for active tabs and status badges', async () => {
      apiModule.default.get.mockResolvedValue({
        data: {
          bookings: [
            {
              id: 1,
              service_type: 'Deep Cleaning',
              worker_name: 'John Doe',
              date: '2023-10-27',
              time: '10:00 AM',
              status: 'ACCEPTED',
              price: 1500
            }
          ]
        }
      });

      render(
        <MemoryRouter>
          <UserBookings />
        </MemoryRouter>
      );

      // Check Active Tab Color
      const activeTab = await screen.findByText('Active');
      expect(activeTab).toHaveStyle({ backgroundColor: PRIMARY_COLOR });
      expect(activeTab).toHaveStyle({ color: 'rgb(255, 255, 255)' });

      // Check Status Badge Color (ACCEPTED -> Blue #EFF6FF / #2563EB)
      // Wait for bookings to load
      const statusBadge = await screen.findByText('ACCEPTED');
      
      // Verify the specific color for ACCEPTED status
      // In UserBookings.jsx: if (['accepted', 'in_progress'].includes(status)) return { bg: '#EFF6FF', text: '#2563EB' };
      expect(statusBadge).toHaveStyle({ backgroundColor: 'rgb(239, 246, 255)' }); // #EFF6FF
      expect(statusBadge).toHaveStyle({ color: 'rgb(37, 99, 235)' }); // #2563EB
    });
  });
});
