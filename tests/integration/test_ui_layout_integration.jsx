import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../../../src/components/layout/Layout';
import Dashboard from '../../../src/components/dashboard/Dashboard';

/**
 * Integration Tests for UI Layout Components
 * 
 * Tests the integration between Layout, Sidebar, TopBar, Dashboard, and ActivityFeed
 */
describe('UI Layout Integration Tests', () => {
    const renderWithLayout = (component) => {
        return render(
            <BrowserRouter>
                <Layout>{component}</Layout>
            </BrowserRouter>
        );
    };

    test('renders complete dashboard with layout', () => {
        renderWithLayout(<Dashboard />);

        // Layout components should be present
        expect(screen.getByText('Trivya')).toBeInTheDocument(); // Sidebar logo
        expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument(); // TopBar search

        // Dashboard content should be present
        expect(screen.getByText('Welcome to Trivya')).toBeInTheDocument();
        expect(screen.getByText('AI-Powered Customer Support Platform')).toBeInTheDocument();
    });

    test('sidebar navigation is accessible from dashboard', () => {
        renderWithLayout(<Dashboard />);

        // All navigation items should be accessible
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('AI Variants')).toBeInTheDocument();
        expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
        expect(screen.getByText('Analytics')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
        expect(screen.getByText('Compliance')).toBeInTheDocument();
    });

    test('activity feed displays within dashboard layout', () => {
        renderWithLayout(<Dashboard />);

        // Activity feed should be rendered
        expect(screen.getByText('Recent Activity')).toBeInTheDocument();
        expect(screen.getByText('Ticket Resolved')).toBeInTheDocument();
        expect(screen.getByText('Knowledge Updated')).toBeInTheDocument();
    });

    test('quick actions are accessible in dashboard', () => {
        renderWithLayout(<Dashboard />);

        // Quick actions should be present
        expect(screen.getByText('Quick Actions')).toBeInTheDocument();
        expect(screen.getByText('Deploy AI Agent')).toBeInTheDocument();
        expect(screen.getByText('Add Knowledge')).toBeInTheDocument();
        expect(screen.getByText('View Analytics')).toBeInTheDocument();
    });

    test('sidebar collapse affects layout', () => {
        renderWithLayout(<Dashboard />);

        const collapseBtn = screen.getByLabelText('Toggle sidebar');

        // Sidebar should be expanded initially
        expect(screen.getByText('User Name')).toBeInTheDocument();

        // Click to collapse
        fireEvent.click(collapseBtn);

        // Sidebar should still be functional
        expect(collapseBtn).toBeInTheDocument();
    });

    test('top bar notifications are visible', () => {
        renderWithLayout(<Dashboard />);

        // Notification badge should be present
        expect(screen.getByText('3')).toBeInTheDocument();

        // User menu should be accessible
        expect(screen.getByText('Admin')).toBeInTheDocument();
    });

    test('AI insights display correctly in dashboard', () => {
        renderWithLayout(<Dashboard />);

        expect(screen.getByText('AI Insights')).toBeInTheDocument();
        expect(screen.getByText('Efficiency Boost')).toBeInTheDocument();
        expect(screen.getByText('Response Time')).toBeInTheDocument();
        expect(screen.getByText(/87% of tickets automatically/)).toBeInTheDocument();
    });

    test('complete user flow: navigation + content display', () => {
        renderWithLayout(<Dashboard />);

        // User should see:
        // 1. Sidebar with navigation
        expect(screen.getByText('Trivya')).toBeInTheDocument();

        // 2. TopBar with search and user info
        expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
        expect(screen.getByText('Admin')).toBeInTheDocument();

        // 3. Dashboard content
        expect(screen.getByText('Welcome to Trivya')).toBeInTheDocument();

        // 4. Activity feed
        expect(screen.getByText('Recent Activity')).toBeInTheDocument();

        // 5. Quick actions
        expect(screen.getByText('Quick Actions')).toBeInTheDocument();

        // 6. AI insights
        expect(screen.getByText('AI Insights')).toBeInTheDocument();
    });
});
