import React from 'react';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import Layout from '../Layout';
import sidebarStyles from '../Sidebar.module.css';
import layoutStyles from '../Layout.module.scss';

describe('Layout component', () => {
  const originalInnerWidth = window.innerWidth;

  beforeEach(() => {
    window.innerWidth = originalInnerWidth;
  });

  afterAll(() => {
    window.innerWidth = originalInnerWidth;
  });

  const renderLayout = (children = null) => render(<Layout>{children}</Layout>);

  const getSidebarElement = () =>
    screen.getByRole('complementary', { name: /primary navigation/i });

  const getOverlayElement = () => document.querySelector(`.${layoutStyles.overlay}`);

  it('renders header, sidebar, and main content structure', () => {
    renderLayout(<div>Sample Content</div>);

    expect(document.querySelector(`.${layoutStyles.layout}`)).toBeInTheDocument();
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByText(/Trivya Command/i)).toBeInTheDocument();
    expect(getSidebarElement()).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('renders child components in the main content area', () => {
    renderLayout(
      <div>
        <p>Test Child</p>
      </div>
    );

    const mainRegion = screen.getByRole('main');
    expect(within(mainRegion).getByText('Test Child')).toBeInTheDocument();
  });

  describe('Responsive behavior', () => {
    it('keeps sidebar visible by default on desktop screens', () => {
      window.innerWidth = 1200;
      renderLayout();

      const sidebar = getSidebarElement();
      expect(sidebar).toHaveClass(sidebarStyles.sidebar);
      expect(sidebar).not.toHaveClass(sidebarStyles.open);
    });

    it('hides sidebar by default on mobile screens', () => {
      window.innerWidth = 500;
      renderLayout();

      const sidebar = getSidebarElement();
      expect(sidebar).toHaveClass(sidebarStyles.sidebar);
      expect(sidebar).not.toHaveClass(sidebarStyles.open);
      expect(getOverlayElement()).not.toBeInTheDocument();
    });
  });

  describe('Sidebar toggle interactions (mobile)', () => {
    it('toggles sidebar open and closed via header menu button', async () => {
      window.innerWidth = 500;
      const user = userEvent.setup();
      renderLayout();

      const toggleButton = screen.getByLabelText(/Toggle navigation menu/i);
      const sidebar = getSidebarElement();

      expect(sidebar).not.toHaveClass(sidebarStyles.open);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'false');

      await user.click(toggleButton);
      expect(sidebar).toHaveClass(sidebarStyles.open);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
      expect(getOverlayElement()).toBeInTheDocument();

      await user.click(toggleButton);
      expect(sidebar).not.toHaveClass(sidebarStyles.open);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
      expect(getOverlayElement()).not.toBeInTheDocument();
    });

    it('closes sidebar when overlay is clicked', async () => {
      window.innerWidth = 500;
      const user = userEvent.setup();
      renderLayout();

      const toggleButton = screen.getByLabelText(/Toggle navigation menu/i);
      await user.click(toggleButton);

      const sidebar = getSidebarElement();
      const overlay = getOverlayElement();
      expect(overlay).toBeInTheDocument();
      expect(sidebar).toHaveClass(sidebarStyles.open);

      await user.click(overlay);
      expect(sidebar).not.toHaveClass(sidebarStyles.open);
      expect(getOverlayElement()).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('provides appropriate navigation landmarks', () => {
      renderLayout();

      const navigation = screen.getByRole('navigation', {
        name: /primary navigation/i,
      });
      expect(navigation).toHaveAttribute('aria-label', 'Primary navigation');
    });

    it('ensures toggle button exposes correct aria attributes', async () => {
      window.innerWidth = 500;
      const user = userEvent.setup();
      renderLayout();

      const toggleButton = screen.getByLabelText(/Toggle navigation menu/i);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'false');

      await user.click(toggleButton);
      expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    });
  });
});
