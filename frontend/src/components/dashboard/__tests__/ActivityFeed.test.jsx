import React from 'react';
import { render, screen, within } from '@testing-library/react';
import '@testing-library/jest-dom';

import ActivityFeed from '../ActivityFeed';

describe('ActivityFeed', () => {
  const renderFeed = () => render(<ActivityFeed />);

  describe('Structure', () => {
    test('renders main region and header copy', () => {
      renderFeed();

      const region = screen.getByRole('region', { name: /live activity feed/i });
      expect(region).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /activity feed/i })).toBeInTheDocument();
      expect(
        screen.getByText(/Monitor escalations, successful resolutions/i)
      ).toBeInTheDocument();
    });
  });

  describe('Activity list rendering', () => {
    test('renders all placeholder activity entries with status indicators', () => {
      renderFeed();

      const entries = screen.getAllByTestId('activity-entry');
      expect(entries).toHaveLength(6);

      const statusDots = screen.getAllByTestId('status-indicator');
      expect(statusDots).toHaveLength(entries.length);

      expect(screen.getByText('AI resolved FAQ #1234')).toBeInTheDocument();
      expect(screen.getByText('Escalated ticket #5678 to human')).toBeInTheDocument();

      const processingStatuses = statusDots.filter(
        (dot) => dot.dataset.status === 'processing'
      );
      expect(processingStatuses.length).toBeGreaterThan(0);
    });
  });

  describe('Activity content verification', () => {
    test('first entry shows expected label and timestamp', () => {
      renderFeed();

      const entries = screen.getAllByTestId('activity-entry');
      const firstEntry = entries[0];
      expect(within(firstEntry).getByText('AI resolved FAQ #1234')).toBeInTheDocument();
      expect(within(firstEntry).getByText('2 minutes ago')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('status dots expose aria labels for different states', () => {
      renderFeed();

      expect(screen.getAllByLabelText(/success status indicator/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/warning status indicator/i).length).toBeGreaterThan(0);
      expect(screen.getAllByLabelText(/processing status indicator/i).length).toBeGreaterThan(0);
    });
  });
});
