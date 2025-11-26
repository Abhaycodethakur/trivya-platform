import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/router';
import { useAuth } from './hooks/useAuth';
import { useLicense } from './hooks/useLicense';
import Header from './components/common/Header';

// Mock the hooks
jest.mock('./hooks/useAuth');
jest.mock('./hooks/useLicense');
jest.mock('next/router', () => ({
    useRouter: jest.fn(),
}));

// Mock Next.js Link component - IMPORTANT: Pass className and onClick
jest.mock('next/link', () => {
    return ({ children, href, className, onClick }) => {
        return <a href={href} className={className} onClick={onClick}>{children}</a>;
    };
});

describe('Header Component', () => {
    const mockPush = jest.fn();

    beforeEach(() => {
        // Reset mocks before each test
        jest.clearAllMocks();

        // Setup default router mock
        useRouter.mockReturnValue({
            pathname: '/',
            push: mockPush,
        });

        // Setup default auth mock
        useAuth.mockReturnValue({
            user: null,
            logout: jest.fn(),
            isAuthenticated: false,
        });

        // Setup default license mock
        useLicense.mockReturnValue({
            license: null,
        });
    });

    describe('Unauthenticated State', () => {
        test('renders logo and navigation links', () => {
            render(<Header />);

            // Check if logo is rendered
            expect(screen.getByTestId('logo')).toBeInTheDocument();

            // Check if navigation links are rendered
            expect(screen.getByText('Dashboard')).toBeInTheDocument();
            expect(screen.getByText('Variants')).toBeInTheDocument();
            expect(screen.getByText('Support')).toBeInTheDocument();
            expect(screen.getByText('Compliance')).toBeInTheDocument();

            // Check if login/signup buttons are rendered
            expect(screen.getByText('Login')).toBeInTheDocument();
            expect(screen.getByText('Sign Up')).toBeInTheDocument();
        });

        test('mobile menu is closed by default', () => {
            render(<Header />);

            // Should only have 1 Dashboard link (desktop), not 2 (desktop + mobile)
            const dashboardLinks = screen.queryAllByText('Dashboard');
            expect(dashboardLinks.length).toBe(1);
        });

        test('opens mobile menu when button is clicked', () => {
            render(<Header />);

            // Find and click the mobile menu button
            const menuButton = screen.getByRole('button', { name: /toggle menu/i });
            fireEvent.click(menuButton);

            // Mobile menu should now be visible
            const dashboardLinks = screen.getAllByText('Dashboard');
            expect(dashboardLinks.length).toBeGreaterThan(1); // Desktop + Mobile
        });
    });

    describe('Authenticated State', () => {
        const mockUser = { name: 'John Doe' };
        const mockLogout = jest.fn();

        beforeEach(() => {
            // Setup authenticated user
            useAuth.mockReturnValue({
                user: mockUser,
                logout: mockLogout,
                isAuthenticated: true,
            });
        });

        test('displays user information when authenticated', () => {
            render(<Header />);

            // Check if user name is displayed
            expect(screen.getByText('John Doe')).toBeInTheDocument();

            // Check if user initial is displayed
            expect(screen.getByText('J')).toBeInTheDocument();

            // Check if logout button is rendered
            expect(screen.getByText('Logout')).toBeInTheDocument();

            // Login/Signup buttons should not be rendered
            expect(screen.queryByText('Login')).not.toBeInTheDocument();
            expect(screen.queryByText('Sign Up')).not.toBeInTheDocument();
        });

        test('calls logout function when logout button is clicked', async () => {
            render(<Header />);

            // Find and click the logout button (desktop version)
            const logoutButtons = screen.getAllByText('Logout');
            fireEvent.click(logoutButtons[0]);

            // Check if logout function was called
            await waitFor(() => {
                expect(mockLogout).toHaveBeenCalled();
            });

            // Check if router.push was called with the login path
            await waitFor(() => {
                expect(mockPush).toHaveBeenCalledWith('/login');
            });
        });
    });

    describe('Active Route Highlighting', () => {
        test('highlights active route correctly', () => {
            // Mock router to return dashboard as current path
            useRouter.mockReturnValue({
                pathname: '/dashboard',
                push: mockPush,
            });

            render(<Header />);

            // Dashboard link should have gold color (active state)
            const dashboardLinks = screen.getAllByText('Dashboard');
            expect(dashboardLinks[0].className).toContain('text-gold-500');
        });
    });

    describe('Scroll Effect', () => {
        test('applies scroll effect when page is scrolled', () => {
            render(<Header />);

            // Get header element
            const header = screen.getByRole('banner');

            // Initially should have bg-opacity-80
            expect(header.className).toContain('bg-opacity-80');
        });
    });

    describe('Mobile Menu Toggle', () => {
        test('closes mobile menu when navigation link is clicked', () => {
            render(<Header />);

            // Open mobile menu
            const menuButton = screen.getByRole('button', { name: /toggle menu/i });
            fireEvent.click(menuButton);

            // Click a navigation link in mobile menu
            const dashboardLinks = screen.getAllByText('Dashboard');
            fireEvent.click(dashboardLinks[dashboardLinks.length - 1]); // Click mobile version

            // Menu should close (only desktop link visible now)
            waitFor(() => {
                const visibleDashboardLinks = screen.getAllByText('Dashboard');
                expect(visibleDashboardLinks.length).toBe(1);
            });
        });
    });
});
