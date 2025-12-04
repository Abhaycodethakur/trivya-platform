import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MiniTrivyaCard from '../MiniTrivyaCard';

describe('MiniTrivyaCard', () => {
  const mockOnSeeDetails = jest.fn();
  
  const renderComponent = (props = {}) => {
    return render(
      <MiniTrivyaCard 
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
    expect(screen.getByText('Mini Trivya')).toBeInTheDocument();
  });

  it('displays all key information correctly', () => {
    renderComponent();
    
    // Check title and subtitle
    expect(screen.getByText('Mini Trivya')).toBeInTheDocument();
    expect(screen.getByText('The 24/7 Trainee')).toBeInTheDocument();
    
    // Check features
    expect(screen.getByText('Email, Chat, Social Media, SMS')).toBeInTheDocument();
    expect(screen.getByText('2 Phone Calls at once')).toBeInTheDocument();
    
    // Check limitation
    expect(screen.getByText(/CANNOT make decisions – only collects data for human review/i)).toBeInTheDocument();
    
    // Check value prop
    expect(screen.getByText(/Auto-saves you: ~\$13,000\/month in trainee salaries/i)).toBeInTheDocument();
    
    // Check price
    expect(screen.getByText('$1,000')).toBeInTheDocument();
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
      name: /see full details of mini trivya plan/i 
    })).toBeInTheDocument();
    
    // Check for proper heading structure
    const title = screen.getByRole('heading', { level: 3, name: /mini trivya/i });
    expect(title).toBeInTheDocument();
  });
});
