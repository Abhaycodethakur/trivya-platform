import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrivyaHighCard from '../TrivyaHighCard';

describe('TrivyaHighCard', () => {
  const mockOnSeeDetails = jest.fn();
  
  const renderComponent = (props = {}) => {
    return render(
      <TrivyaHighCard 
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
    expect(screen.getByText('Trivya High')).toBeInTheDocument();
  });

  it('displays all key information correctly', () => {
    renderComponent();
    
    // Check title and subtitle
    expect(screen.getByText('Trivya High')).toBeInTheDocument();
    expect(screen.getByText('The Senior Agent')).toBeInTheDocument();
    
    // Check value proposition
    expect(screen.getByText(/Replaces 3 senior agents—eliminates 80% of support workload/i)).toBeInTheDocument();
    
    // Check features
    expect(screen.getByText('Everything Trivya does')).toBeInTheDocument();
    expect(screen.getByText('5 simultaneous calls')).toBeInTheDocument();
    expect(screen.getByText('Video support')).toBeInTheDocument();
    expect(screen.getByText('Strategic Intelligence')).toBeInTheDocument();
    
    // Check advantage
    expect(screen.getByText(/Makes decisions, predicts churn, coordinates with teams/i)).toBeInTheDocument();
    
    // Check savings
    expect(screen.getByText(/Auto-saves you: ~\$28,000\/month in senior agent salaries/i)).toBeInTheDocument();
    
    // Check price
    expect(screen.getByText('$4,000')).toBeInTheDocument();
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
    expect(card).toHaveStyle('border: 1px solid rgba(0, 212, 255, 0.7)');
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
      name: /see full details of trivya high plan/i 
    })).toBeInTheDocument();
    
    // Check for proper heading structure
    const title = screen.getByRole('heading', { level: 3, name: /trivya high/i });
    expect(title).toBeInTheDocument();
    
    // Check for proper ARIA attributes
    expect(title).toHaveAttribute('id', 'trivya-high-card-title');
    expect(screen.getByRole('article')).toHaveAttribute('aria-labelledby', 'trivya-high-card-title');
  });
});
