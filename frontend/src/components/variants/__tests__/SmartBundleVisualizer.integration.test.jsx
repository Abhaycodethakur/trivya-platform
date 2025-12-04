import React, { useState } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import SmartBundleVisualizer from '../SmartBundleVisualizer';

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
  },
}));

// Mock the parent component that would use SmartBundleVisualizer
const ParentComponent = () => {
  const [selectedBundle, setSelectedBundle] = useState(null);
  
  return (
    <div>
      <h1>Trivya Pricing</h1>
      <SmartBundleVisualizer onBundleSelect={setSelectedBundle} />
      {selectedBundle && (
        <div data-testid="selected-bundle">
          Selected: {selectedBundle.name} - {selectedBundle.price}
        </div>
      )}
    </div>
  );
};

describe('SmartBundleVisualizer Integration', () => {
  beforeEach(() => {
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
  });

  it('integrates with parent component state', async () => {
    render(<ParentComponent />);
    
    // Initial state - no bundle selected
    expect(screen.queryByTestId('selected-bundle')).not.toBeInTheDocument();
    
    // Find and interact with the component
    const slider = screen.getByRole('slider');
    
    // Change ticket volume to 300
    fireEvent.change(slider, { target: { value: '300' } });
    
    // Check that Trivya is recommended
    const recommendationText = screen.getByText(/Recommended:/);
    expect(recommendationText).toHaveTextContent(/Trivya/);
    
    // Open the comparison table
    const compareButton = screen.getByText('Compare Bundles');
    await userEvent.click(compareButton);
    
    // Verify the comparison table is visible
    expect(screen.getByText('Feature')).toBeInTheDocument();
    
    // Close the comparison table
    await userEvent.click(compareButton);
    expect(screen.queryByText('Feature')).not.toBeInTheDocument();
  });

  it('handles the full user flow', async () => {
    render(<ParentComponent />);
    
    // 1. Initial load - check default state
    expect(screen.getByText('Smart Bundle Visualizer')).toBeInTheDocument();
    expect(screen.getByText(/Estimated Daily Ticket Volume/)).toBeInTheDocument();
    
    // 2. Change the ticket volume
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '450' } });
    
    // 3. Verify the recommendation updates
    await waitFor(() => {
      const recommendationText = screen.getByText(/Recommended:/);
      expect(recommendationText).toHaveTextContent(/Trivya High/);
    });
    
    // 4. Open the comparison table
    const compareButton = screen.getByText('Compare Bundles');
    await userEvent.click(compareButton);
    
    // 5. Verify the comparison table shows the correct bundles
    await waitFor(() => {
      const featureHeader = screen.getByText('Feature');
      const table = featureHeader.closest('table');
      expect(table).toHaveTextContent('Trivya');
      expect(table).toHaveTextContent('Trivya High');
    });
  });

  it('toggles the comparison table when the button is clicked', () => {
    render(<ParentComponent />);
    
    // Initially hidden
    expect(screen.queryByText('Feature')).not.toBeInTheDocument();
    
    // Click to show comparison
    const compareButton = screen.getByText('Compare Bundles');
    fireEvent.click(compareButton);
    
    // Should be visible
    expect(screen.getByText('Feature')).toBeInTheDocument();
    
    // Click to hide comparison
    fireEvent.click(compareButton);
    
    // Should be hidden again
    expect(screen.queryByText('Feature')).not.toBeInTheDocument();
  });
});
