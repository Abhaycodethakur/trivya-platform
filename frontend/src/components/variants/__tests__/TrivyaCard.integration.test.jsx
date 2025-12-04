import React, { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import TrivyaCard from '../TrivyaCard';

// Mock parent component that uses TrivyaCard
const TestPage = () => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const handleSeeDetails = (cardId) => {
    setSelectedCard(cardId);
    setModalOpen(true);
  };

  return (
    <div>
      <div data-testid="modal" style={{ display: modalOpen ? 'block' : 'none' }}>
        <h2>Details for {selectedCard}</h2>
        <button onClick={() => setModalOpen(false)}>Close</button>
      </div>
      
      <div className="card-container" style={{ display: 'flex', gap: '20px' }}>
        <TrivyaCard 
          onSeeDetails={() => handleSeeDetails('trivya')}
          isSelected={selectedCard === 'trivya'}
          data-testid="trivya-card"
        />
      </div>
    </div>
  );
};

describe('TrivyaCard Integration', () => {
  it('handles click interaction within parent component', () => {
    render(<TestPage />);
    
    // Initially, modal should be closed
    const modal = screen.getByTestId('modal');
    expect(modal).not.toBeVisible();
    
    // Click the "See Full Details" button
    const seeDetailsButton = screen.getByRole('button', { name: /see full details/i });
    fireEvent.click(seeDetailsButton);
    
    // After clicking, modal should be open with correct content
    expect(modal).toBeVisible();
    expect(screen.getByText('Details for trivya')).toBeInTheDocument();
    
    // The card should be marked as selected
    const card = screen.getByRole('article');
    expect(card).toHaveStyle('border: 1px solid #00D4FF');
    
    // Test closing the modal
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    // Modal should be closed again
    expect(modal).not.toBeVisible();
  });

  it('renders correctly within parent layout', () => {
    render(<TestPage />);
    
    // Check if the card is rendered with the correct content
    expect(screen.getByText('Trivya')).toBeInTheDocument();
    expect(screen.getByText('The Junior Agent')).toBeInTheDocument();
    
    // Check if the card has the correct styles
    const card = screen.getByRole('article');
    expect(card).toHaveStyle('border-radius: 16px');
    expect(card).toHaveStyle('background: #0A0A0B');
    
    // Check if the card is responsive
    expect(card).toHaveStyle('width: 100%');
  });

  it('maintains proper spacing in the parent layout', () => {
    const { container } = render(<TestPage />);
    const cardContainer = container.querySelector('.card-container');
    
    // Check if the parent container has proper spacing
    expect(cardContainer).toHaveStyle('display: flex');
    expect(cardContainer).toHaveStyle('gap: 20px');
    
    // Check if the card maintains its internal spacing
    const card = screen.getByRole('article');
    expect(card).toHaveStyle('padding: 2rem');
  });
});
