import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Sidebar from '../../../src/components/layout/Sidebar';

describe('Sidebar Component', () => {
    const renderSidebar = () => {
        return render(
            <BrowserRouter>
                <Sidebar />
            </BrowserRouter>
        );
    };

    test('renders sidebar with logo', () => {
        renderSidebar();
        expect(screen.getByText('Trivya')).toBeInTheDocument();
    });

    test('renders all navigation items', () => {
        renderSidebar();
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
        expect(screen.getByText('AI Variants')).toBeInTheDocument();
        expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
        expect(screen.getByText('Analytics')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
        expect(screen.getByText('Compliance')).toBeInTheDocument();
    });

    test('toggles collapse state', () => {
        renderSidebar();
        const collapseBtn = screen.getByLabelText('Toggle sidebar');

        // Initial state - expanded
        expect(screen.getByText('Dashboard')).toBeInTheDocument();

        // Click to collapse
        fireEvent.click(collapseBtn);

        // Button should change
        expect(collapseBtn).toBeInTheDocument();
    });

    test('displays user info', () => {
        renderSidebar();
        expect(screen.getByText('User Name')).toBeInTheDocument();
        expect(screen.getByText('Admin')).toBeInTheDocument();
    });

    test('highlights active navigation item', () => {
        renderSidebar();
        const dashboardLink = screen.getByText('Dashboard').closest('a');
        expect(dashboardLink).toHaveClass('active');
    });
});
