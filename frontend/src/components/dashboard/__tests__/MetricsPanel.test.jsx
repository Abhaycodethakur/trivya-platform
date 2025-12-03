import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import MetricsPanel from '../MetricsPanel';

describe('MetricsPanel', () => {
  const renderPanel = () => render(<MetricsPanel />);

  test('renders main heading and description', () => {
    renderPanel();

    expect(screen.getByRole('heading', { name: /performance metrics/i })).toBeInTheDocument();
    expect(
      screen.getByText(/These indicators summarize how your AI workforce is performing/i)
    ).toBeInTheDocument();
  });

  test('renders all metric cards with label, value, and trend', () => {
    renderPanel();

    const cards = screen.getAllByRole('article');
    expect(cards).toHaveLength(4);

    cards.forEach((card) => {
      const label = card.querySelector(`.${'metricLabel'}`);
      const value = card.querySelector(`.${'metricValue'}`);
      const trend = card.querySelector(`.${'metricTrend'}`);

      expect(label).toBeTruthy();
      expect(value).toBeTruthy();
      expect(trend).toBeTruthy();
    });
  });

  test('verifies placeholder metric content and trend indicators', () => {
    renderPanel();

    expect(screen.getByText(/Tickets Resolved/i)).toBeInTheDocument();
    expect(screen.getByText('1,248')).toBeInTheDocument();

    expect(screen.getByText(/Customer Satisfaction/i)).toBeInTheDocument();
    expect(screen.getByText('98.5%')).toBeInTheDocument();

    const upTrends = screen.getAllByText(/▲/i);
    const downTrends = screen.getAllByText(/▼/i);
    expect(upTrends.length).toBeGreaterThan(0);
    expect(downTrends.length).toBeGreaterThan(0);
  });
});
