import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import BottomNav from '../../components/BottomNav';

describe('BottomNav Component', () => {
  it('renders all navigation items', () => {
    render(
      <MemoryRouter>
        <BottomNav />
      </MemoryRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('AI Care')).toBeInTheDocument();
    expect(screen.getByText('Explore')).toBeInTheDocument();
    expect(screen.getByText('Appointments')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
  });

  it('highlights the active tab', () => {
    render(
      <MemoryRouter initialEntries={['/doctors']}>
        <BottomNav />
      </MemoryRouter>
    );

    const exploreLink = screen.getByText('Explore').closest('a');
    expect(exploreLink).toHaveClass('active');
    
    const homeLink = screen.getByText('Home').closest('a');
    expect(homeLink).not.toHaveClass('active');
  });
});
