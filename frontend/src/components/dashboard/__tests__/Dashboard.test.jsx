import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import Dashboard from '../Dashboard';
import styles from '../Dashboard.module.scss';

describe('Dashboard component', () => {
  const renderDashboard = () => render(<Dashboard />);

  test('renders the dashboard container and main heading', () => {
    const { container } = renderDashboard();

    const dashboardContainer = container.firstChild;
    expect(dashboardContainer).toBeInTheDocument();
    expect(dashboardContainer).toHaveClass(styles.dashboard);
    expect(screen.getByRole('heading', { name: /welcome back, alex!/i })).toBeInTheDocument();
  });

  test('renders all placeholder sections', () => {
    renderDashboard();

    expect(screen.getByText(/Activity Feed/i)).toBeInTheDocument();
    expect(screen.getByText(/Metrics Panel/i)).toBeInTheDocument();
    expect(screen.getByText(/Settings Panel/i)).toBeInTheDocument();
    expect(screen.getByText(/Usage Meter/i)).toBeInTheDocument();
  });
});
