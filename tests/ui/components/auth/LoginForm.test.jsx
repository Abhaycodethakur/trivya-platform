import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from '../../../../../frontend/src/components/auth/LoginForm';
import * as authService from '../../../../../frontend/src/services/__mocks__/authService';

// Mock the Loading component to simplify testing
jest.mock('../../../../../frontend/src/components/common/Loading', () => () => <div data-testid="loading-spinner">Loading...</div>);

describe('LoginForm Component', () => {
    const mockOnLoginSuccess = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders form elements correctly', () => {
        render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);

        expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    });

    test('displays validation errors for empty inputs', async () => {
        render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);

        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        expect(await screen.findByText(/Email is required/i)).toBeInTheDocument();
        expect(await screen.findByText(/Password is required/i)).toBeInTheDocument();
        expect(mockOnLoginSuccess).not.toHaveBeenCalled();
    });

    test('displays validation error for invalid email', async () => {
        render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);

        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'invalid-email' } });
        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        expect(await screen.findByText(/Please enter a valid email address/i)).toBeInTheDocument();
    });

    test('calls onLoginSuccess with user data on successful login', async () => {
        render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);

        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'test@example.com' } });
        fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password' } });

        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        await waitFor(() => {
            expect(mockOnLoginSuccess).toHaveBeenCalledWith(expect.objectContaining({
                email: 'test@example.com',
                name: 'Test User'
            }));
        });
    });

    test('displays error message on failed login', async () => {
        render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);

        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'wrong@example.com' } });
        fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrongpassword' } });

        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        expect(await screen.findByText(/Invalid credentials/i)).toBeInTheDocument();
        expect(mockOnLoginSuccess).not.toHaveBeenCalled();
    });

    test('shows loading state during submission', async () => {
        render(<LoginForm onLoginSuccess={mockOnLoginSuccess} />);

        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'test@example.com' } });
        fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password' } });

        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
        expect(screen.getByRole('button')).toBeDisabled();

        await waitFor(() => {
            expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
        });
    });
});
