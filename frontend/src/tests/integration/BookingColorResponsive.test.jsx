import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import BookingFlow from '../../../../housekeeping/arrival/frontend/pages/BookingFlow';
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
  };
});

describe('BookingFlow Responsive Color Verification', () => {
  const PRIMARY_COLOR = 'rgb(142, 68, 173)'; // #8E44AD
  
  const setupViewport = (width, height) => {
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: width });
    Object.defineProperty(window, 'innerHeight', { writable: true, configurable: true, value: height });
    window.dispatchEvent(new Event('resize'));
  };

  beforeEach(() => {
    vi.clearAllMocks();
    apiModule.default.get.mockResolvedValue({
      data: {
        services: [
          { id: 1, name: 'General Cleaning', base_price: 500 }
        ]
      }
    });
  });

  const verifyColors = async (viewportName) => {
    render(
      <MemoryRouter>
        <BookingFlow />
      </MemoryRouter>
    );

    // Verify Header Color
    const header = await screen.findByText('Select Service');
    expect(header).toHaveStyle({ color: PRIMARY_COLOR });

    // Select Service to go to Step 2
    const serviceName = screen.getByText('General Cleaning');
    fireEvent.click(serviceName.closest('div').parentElement);

    // Verify Schedule Header
    expect(screen.getByText('Schedule Service')).toHaveStyle({ color: PRIMARY_COLOR });

    // Verify Date Selection (Active)
    const today = new Date().getDate().toString();
    const dateBtn = screen.getByText(today).closest('button');
    fireEvent.click(dateBtn);
    
    expect(dateBtn).toHaveStyle({ backgroundColor: PRIMARY_COLOR });
    expect(dateBtn).toHaveStyle({ borderColor: PRIMARY_COLOR });
    expect(dateBtn).toHaveStyle({ color: 'rgb(255, 255, 255)' });

    // Verify Time Selection (Active)
    const timeBtn = screen.getByText('10:00 AM');
    fireEvent.click(timeBtn);
    expect(timeBtn).toHaveStyle({ borderColor: PRIMARY_COLOR });
    expect(timeBtn).toHaveStyle({ color: PRIMARY_COLOR });
  };

  it('maintains brand colors on Desktop (1920x1080)', async () => {
    setupViewport(1920, 1080);
    await verifyColors('Desktop');
  });

  it('maintains brand colors on Tablet (768x1024)', async () => {
    setupViewport(768, 1024);
    await verifyColors('Tablet');
  });

  it('maintains brand colors on Mobile (375x667)', async () => {
    setupViewport(375, 667);
    await verifyColors('Mobile');
  });
});
