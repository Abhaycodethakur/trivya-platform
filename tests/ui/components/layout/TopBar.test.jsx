import React from 'react';
import { render, screen } from '@testing-library/react';
import TopBar from '../../components/layout/TopBar';

describe('TopBar Component', () => {
    test('renders top bar', () => {
        render(<TopBar />);
        expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    test('renders search input', () => {
        render(<TopBar />);
        const searchInput = screen.getByPlaceholderText('Search...');
        expect(searchInput).toBeInTheDocument();
    });

    test('displays notification badge', () => {
        render(<TopBar />);
        const notificationBadge = screen.getByText('3');
        expect(notificationBadge).toBeInTheDocument();
    });

    test('renders user menu', () => {
        render(<TopBar />);
        expect(screen.getByText('Admin')).toBeInTheDocument();
    });

    test('renders action buttons', () => {
        render(<TopBar />);
        const notificationBtn = screen.getByLabelText('Notifications');
        const helpBtn = screen.getByLabelText('Help');

        expect(notificationBtn).toBeInTheDocument();
        expect(helpBtn).toBeInTheDocument();
    });
});
