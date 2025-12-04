import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SmartBundleVisualizer from '../SmartBundleVisualizer';

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
}));

// Mock the slider's offsetWidth and offsetHeight
Object.defineProperties(window.HTMLDivElement.prototype, {
  offsetWidth: { get: () => 500 },
  offsetHeight: { get: () => 300 },
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('SmartBundleVisualizer', () => {
  it('renders without crashing', () => {
    render(<SmartBundleVisualizer />);
    expect(screen.getByText('Smart Bundle Visualizer')).toBeInTheDocument();
  });

  it('displays the initial slider with default value', () => {
    render(<SmartBundleVisualizer />);
    
    // Check slider is present with default value
    const slider = screen.getByRole('slider');
    expect(slider).toBeInTheDocument();
    expect(slider).toHaveAttribute('value', '200');
  });

  it('shows the compare bundles button', () => {
    render(<SmartBundleVisualizer />);
    expect(screen.getByText('Compare Bundles')).toBeInTheDocument();
  });
});
