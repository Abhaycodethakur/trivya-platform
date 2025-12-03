import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import SettingsPanel from '../SettingsPanel';

describe('SettingsPanel', () => {
  const renderPanel = () => render(<SettingsPanel />);

  describe('Structure', () => {
    test('renders quick settings region, heading, and description', () => {
      renderPanel();

      const region = screen.getByRole('region', { name: /quick settings/i });
      expect(region).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: /quick settings/i })).toBeInTheDocument();
      expect(
        screen.getByText(/Fine-tune how Trivya behaves across teams/i)
      ).toBeInTheDocument();
    });
  });

  describe('Settings list rendering', () => {
    test('renders all placeholder setting buttons', () => {
      renderPanel();
      const buttons = screen.getAllByTestId('setting-option');
      expect(buttons).toHaveLength(4);
      buttons.forEach((button) => expect(button.tagName).toBe('BUTTON'));
    });
  });

  describe('Content verification', () => {
    test('includes expected labels, descriptions, and chevrons', () => {
      renderPanel();

      const firstButton = screen.getAllByTestId('setting-option')[0];
      expect(firstButton).toHaveTextContent('⚙️');
      expect(firstButton).toHaveTextContent(/General Settings/i);
      expect(firstButton).toHaveTextContent(/Configure brand, contact/i);

      expect(screen.getByText(/Team Management/i)).toBeInTheDocument();
      expect(screen.getAllByText('↗').length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    test('icons are hidden from screen readers and buttons are interactive', async () => {
      const user = userEvent.setup();
      renderPanel();

      const icons = screen.getAllByText(/⚙️|👥|🔔|🛡️/);
      icons.forEach((icon) => expect(icon).toHaveAttribute('aria-hidden', 'true'));

      const buttons = screen.getAllByTestId('setting-option');
      await user.click(buttons[0]);
      expect(buttons[0]).toHaveFocus();
    });
  });
});
