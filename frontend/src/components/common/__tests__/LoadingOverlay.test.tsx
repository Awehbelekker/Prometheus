/**
 * Tests for LoadingOverlay component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoadingOverlay from '../LoadingOverlay';

describe('LoadingOverlay', () => {
  it('should render when open is true', () => {
    render(<LoadingOverlay open={true} />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should not render when open is false', () => {
    render(<LoadingOverlay open={false} />);
    
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });

  it('should display custom message', () => {
    const message = 'Loading data...';
    render(<LoadingOverlay open={true} message={message} />);
    
    expect(screen.getByText(message)).toBeInTheDocument();
  });

  it('should display default message when no message provided', () => {
    render(<LoadingOverlay open={true} />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should show progress when progress prop is provided', () => {
    render(<LoadingOverlay open={true} progress={50} />);
    
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
  });

  it('should show indeterminate progress when no progress prop', () => {
    render(<LoadingOverlay open={true} />);
    
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
  });

  it('should display progress percentage', () => {
    const progress = 75;
    render(<LoadingOverlay open={true} progress={progress} />);
    
    expect(screen.getByText(`${progress}%`)).toBeInTheDocument();
  });

  it('should have backdrop styling', () => {
    const { container } = render(<LoadingOverlay open={true} />);
    
    const backdrop = container.querySelector('[role="presentation"]');
    expect(backdrop).toBeInTheDocument();
  });

  it('should handle progress value of 0', () => {
    render(<LoadingOverlay open={true} progress={0} />);
    
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('should handle progress value of 100', () => {
    render(<LoadingOverlay open={true} progress={100} />);
    
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});

