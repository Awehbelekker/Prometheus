/**
 * Tests for EmptyState component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import EmptyState from '../EmptyState';

describe('EmptyState', () => {
  it('should render portfolio variant', () => {
    render(<EmptyState variant="portfolio" />);
    
    expect(screen.getByText(/no portfolio data/i)).toBeInTheDocument();
  });

  it('should render trades variant', () => {
    render(<EmptyState variant="trades" />);
    
    expect(screen.getByText(/no trades yet/i)).toBeInTheDocument();
  });

  it('should render achievements variant', () => {
    render(<EmptyState variant="achievements" />);
    
    expect(screen.getByText(/no achievements/i)).toBeInTheDocument();
  });

  it('should render custom variant with custom text', () => {
    const customTitle = 'Custom Title';
    const customDescription = 'Custom Description';
    
    render(
      <EmptyState
        variant="custom"
        title={customTitle}
        description={customDescription}
      />
    );
    
    expect(screen.getByText(customTitle)).toBeInTheDocument();
    expect(screen.getByText(customDescription)).toBeInTheDocument();
  });

  it('should call onAction when action button is clicked', () => {
    const mockAction = jest.fn();
    
    render(
      <EmptyState
        variant="portfolio"
        onAction={mockAction}
      />
    );
    
    const actionButton = screen.getByRole('button');
    fireEvent.click(actionButton);
    
    expect(mockAction).toHaveBeenCalledTimes(1);
  });

  it('should not render action button when onAction is not provided', () => {
    render(<EmptyState variant="portfolio" />);
    
    const buttons = screen.queryAllByRole('button');
    expect(buttons).toHaveLength(0);
  });

  it('should render with custom action text', () => {
    const customActionLabel = 'Custom Action';

    render(
      <EmptyState
        variant="portfolio"
        actionLabel={customActionLabel}
        onAction={() => {}}
      />
    );

    expect(screen.getByText(customActionLabel)).toBeInTheDocument();
  });

  it('should render all variants without errors', () => {
    const variants = [
      'portfolio',
      'trades',
      'achievements',
      'analytics',
      'positions',
      'notifications',
      'users',
      'custom'
    ] as const;

    variants.forEach((variant) => {
      const { unmount } = render(<EmptyState variant={variant} />);
      // Check that component renders without crashing
      expect(screen.getByRole('heading')).toBeInTheDocument();
      unmount();
    });
  });

  it('should have correct styling classes', () => {
    const { container } = render(<EmptyState variant="portfolio" />);
    
    const emptyStateBox = container.firstChild;
    expect(emptyStateBox).toBeInTheDocument();
  });
});

