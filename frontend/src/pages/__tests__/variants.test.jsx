import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import VariantsPage from '../variants';

describe('VariantsPage', () => {
  const renderVariantsPage = () => render(<VariantsPage />);

  test('renders main heading and structure', () => {
    renderVariantsPage();

    expect(screen.getByRole('heading', { name: /choose your ai workforce/i })).toBeInTheDocument();
  });

  test('wraps content within Layout (header branding visible)', () => {
    renderVariantsPage();

    expect(screen.getByText(/Trivya Command/i)).toBeInTheDocument();
  });

  test('renders placeholder cards with labels', () => {
    renderVariantsPage();

    expect(screen.getAllByText(/Mini Trivya Card/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Trivya Card/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Trivya High Card/i)[0]).toBeInTheDocument();
  });

  test('each card includes titles, subtitles, and button', () => {
    renderVariantsPage();

    expect(
      screen.getAllByRole('heading', { name: /Mini Trivya/i })[0]
    ).toBeInTheDocument();
    expect(screen.getByText('The 24/7 Trainee')).toBeInTheDocument();

    expect(
      screen.getAllByRole('heading', { name: /^Trivya$/i })[0]
    ).toBeInTheDocument();
    expect(screen.getByText(/The Autonomous Junior/i)).toBeInTheDocument();

    expect(
      screen.getAllByRole('heading', { name: /Trivya High/i })[0]
    ).toBeInTheDocument();
    expect(screen.getByText(/The Elite Strategist/i)).toBeInTheDocument();

    const buttons = screen.getAllByRole('button', { name: /See Full Details/i });
    expect(buttons).toHaveLength(3);
  });
});
