import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../../frontend/src/App';

// Mock all child components
jest.mock('../../../frontend/src/components/common/ErrorBoundary', () => ({ children }) => <div>{children}</div>);
jest.mock('../../../frontend/src/components/auth/LoginForm', () => ({ onLoginSuccess }) => (
    <div data-testid="login-form">
        <button onClick={() => onLoginSuccess({ id: 1, name: 'Test User', token: 'token' })}>
            Mock Login
        </button>
    </div>
));
jest.mock('../../../frontend/src/components/auth/SignupForm', () => ({ onSignupSuccess }) => (
    <div data-testid="signup-form">
        <button onClick={() => onSignupSuccess({ id: 2, name: 'New User', token: 'token' })}>
            Mock Signup
        </button>
    </div>
));
jest.mock('../../../frontend/src/components/license/LicenseKeyForm', () => ({ onLicenseValid }) => (
    <div data-testid="license-form">
        <button onClick={() => onLicenseValid({ type: 'Gold', expiryDate: '2025-12-31' })}>
            Mock License
        </button>
    </div>
));

describe('App Component', () => {
    test('renders login form by default', () => {
        render(<App />);
        expect(screen.getByTestId('login-form')).toBeInTheDocument();
        expect(screen.getByText(/Don't have an account/i)).toBeInTheDocument();
    });

    test('toggles between login and signup', () => {
        render(<App />);

        // Initially shows login
        expect(screen.getByTestId('login-form')).toBeInTheDocument();

        // Click to switch to signup
        fireEvent.click(screen.getByText(/Don't have an account/i));
        expect(screen.getByTestId('signup-form')).toBeInTheDocument();

        // Click to switch back to login
        fireEvent.click(screen.getByText(/Already have an account/i));
        expect(screen.getByTestId('login-form')).toBeInTheDocument();
    });

    test('shows license form after successful login', () => {
        render(<App />);

        // Click mock login button
        fireEvent.click(screen.getByText('Mock Login'));

        // Should now show license form
        expect(screen.getByTestId('license-form')).toBeInTheDocument();
    });

    test('shows dashboard after license validation', () => {
        render(<App />);

        // Login
        fireEvent.click(screen.getByText('Mock Login'));

        // Validate license
        fireEvent.click(screen.getByText('Mock License'));

        // Should show dashboard
        expect(screen.getByText(/Welcome to Trivya Platform/i)).toBeInTheDocument();
        expect(screen.getByText(/Test User/i)).toBeInTheDocument();
        expect(screen.getByText(/License Type: Gold/i)).toBeInTheDocument();
    });

    test('full flow: signup -> license -> dashboard', () => {
        render(<App />);

        // Switch to signup
        fireEvent.click(screen.getByText(/Don't have an account/i));

        // Signup
        fireEvent.click(screen.getByText('Mock Signup'));

        // Validate license
        fireEvent.click(screen.getByText('Mock License'));

        // Should show dashboard with new user
        expect(screen.getByText(/Welcome to Trivya Platform/i)).toBeInTheDocument();
        expect(screen.getByText(/New User/i)).toBeInTheDocument();
    });
});
