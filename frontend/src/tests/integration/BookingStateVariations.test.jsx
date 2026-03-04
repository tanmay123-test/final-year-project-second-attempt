import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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

describe('BookingFlow State Variations', () => {
  const HOVER_BORDER_COLOR = 'rgb(215, 189, 226)'; // #D7BDE2
  const DEFAULT_BORDER_COLOR = 'rgb(243, 244, 246)'; // #F3F4F6
  const DISABLED_BG_COLOR = 'rgb(209, 213, 219)'; // #D1D5DB
  const PRIMARY_COLOR = 'rgb(142, 68, 173)'; // #8E44AD

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

  it('changes service card border color on hover', async () => {
    render(
      <MemoryRouter>
        <BookingFlow />
      </MemoryRouter>
    );

    const serviceName = await screen.findByText('General Cleaning');
    // Navigate up to the card container
    // Structure: Card > Flex > TextContainer > Name
    // Name (h3) -> TextContainer (div) -> Flex (div) -> Card (div)
    const serviceCard = serviceName.closest('div').parentElement.parentElement;

    // Simulate Hover
    fireEvent.mouseEnter(serviceCard);
    expect(serviceCard).toHaveStyle({ borderColor: HOVER_BORDER_COLOR });

    // Simulate Mouse Leave
    fireEvent.mouseLeave(serviceCard);
    expect(serviceCard).toHaveStyle({ borderColor: DEFAULT_BORDER_COLOR });
  });

  it('shows disabled state on confirm button during submission', async () => {
    // Delay API response to catch loading state
    let resolvePost;
    const postPromise = new Promise(resolve => { resolvePost = resolve; });
    apiModule.default.post.mockReturnValue(postPromise);

    render(
      <MemoryRouter>
        <BookingFlow />
      </MemoryRouter>
    );

    // 1. Select Service (advances to Step 2)
    const serviceName = await screen.findByText('General Cleaning');
    fireEvent.click(serviceName.closest('div').parentElement);

    // 2. Select Date & Time
    const today = new Date().getDate().toString();
    const dateBtn = screen.getByText(today).closest('button');
    fireEvent.click(dateBtn);
    
    const timeBtn = screen.getByText('10:00 AM');
    fireEvent.click(timeBtn);

    // 3. Click Continue to go to Step 3
    const continueBtn = screen.getByText('Continue');
    fireEvent.click(continueBtn);

    // 4. Find Confirm & Pay button
    const confirmBtn = await screen.findByText('Confirm & Pay');
    const confirmBtnElement = confirmBtn.closest('button');

    // 5. Click Confirm & Pay
    fireEvent.click(confirmBtnElement);

    // 6. Check Disabled State
    expect(confirmBtnElement).toBeDisabled();
    expect(confirmBtnElement).toHaveStyle({ backgroundColor: DISABLED_BG_COLOR });
    
    // Resolve promise to finish test cleanly
    resolvePost({ data: { success: true } });
    await waitFor(() => expect(apiModule.default.post).toHaveBeenCalled());
  });
});
