import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrivyaCard from '../TrivyaCard';

describe('TrivyaCard', () => {
  const mockOnSeeDetails = jest.fn();
  
  const renderComponent = (props = {}) => {
    return render(
      <TrivyaCard 
        onSeeDetails={mockOnSeeDetails}
        isSelected={false}
        {...props}
      />
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    renderComponent();
    expect(screen.getByText('Trivya')).toBeInTheDocument();
  });

  it('displays all key information correctly', () => {
    renderComponent();
    
    // Check title and subtitle
    expect(screen.getByText('Trivya')).toBeInTheDocument();
    expect(screen.getByText('The Junior Agent')).toBeInTheDocument();
    
    // Check value proposition
    expect(screen.getByText(/Replaces 3 junior agents—resolves 70% of issues without you/i)).toBeInTheDocument();
    
    // Check features
    expect(screen.getByText('Everything Mini does')).toBeInTheDocument();
    expect(screen.getByText('3 simultaneous calls')).toBeInTheDocument();
    expect(screen.getByText('"Thinks for you"')).toBeInTheDocument();
    
    // Check advantage
    expect(screen.getByText(/Detects patterns, suggests KB updates, cuts review time by 80%/i)).toBeInTheDocument();
    
    // Check savings
    expect(screen.getByText(/Auto-saves you: ~\$18,000\/month in junior agent salaries/i)).toBeInTheDocument();
    
    // Check price
    expect(screen.getByText('$2,500')).toBeInTheDocument();
    expect(screen.getByText('(Custom quote after assessment)')).toBeInTheDocument();
    
    // Check button
    expect(screen.getByRole('button', { name: /see full details/i })).toBeInTheDocument();
  });

  it('calls onSeeDetails when button is clicked', () => {
    renderComponent();
    const button = screen.getByRole('button', { name: /see full details/i });
    
    fireEvent.click(button);
    
    expect(mockOnSeeDetails).toHaveBeenCalledTimes(1);
  });

  it('applies selected styles when isSelected is true', () => {
    const { container } = renderComponent({ isSelected: true });
    
    // Check if the card has the selected border color
    const card = container.firstChild;
    expect(card).toHaveStyle('border: 1px solid #00D4FF');
  });

  it('does not apply selected styles when isSelected is false', () => {
    const { container } = renderComponent({ isSelected: false });
    
    const card = container.firstChild;
    expect(card).toHaveStyle('border: 1px solid #1E1E24');
  });

  it('is accessible', () => {
    renderComponent();
    
    // Check for button with proper aria label
    expect(screen.getByRole('button', { 
      name: /see full details of trivya plan/i 
    })).toBeInTheDocument();
    
    // Check for proper heading structure
    const title = screen.getByRole('heading', { level: 3, name: /trivya/i });
    expect(title).toBeInTheDocument();
    
    // Check for proper ARIA attributes
    expect(title).toHaveAttribute('id', 'trivya-card-title');
    expect(screen.getByRole('article')).toHaveAttribute('aria-labelledby', 'trivya-card-title');
  });
});
