import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SignupForm from '../../components/auth/SignupForm';

// Mock the Loading component
jest.mock('../../components/common/Loading', () => () => <div data-testid="loading-spinner">Loading...</div>);

describe('SignupForm Component', () => {
    const mockOnSignupSuccess = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders form elements correctly', () => {
        render(<SignupForm onSignupSuccess={mockOnSignupSuccess} />);

        expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/^Password/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument();
    });

    test('displays validation errors for empty inputs', async () => {
        render(<SignupForm onSignupSuccess={mockOnSignupSuccess} />);

        fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));

        expect(await screen.findByText(/Name is required/i)).toBeInTheDocument();
        expect(await screen.findByText(/Email is required/i)).toBeInTheDocument();
        expect(await screen.findByText(/Password is required/i)).toBeInTheDocument();
        expect(mockOnSignupSuccess).not.toHaveBeenCalled();
    });

    test('validates password match', async () => {
        render(<SignupForm onSignupSuccess={mockOnSignupSuccess} />);

        fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: 'password123' } });
        fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'mismatch' } });

        fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));

        expect(await screen.findByText(/Passwords do not match/i)).toBeInTheDocument();
    });

    test('calls onSignupSuccess with user data on successful registration', async () => {
        render(<SignupForm onSignupSuccess={mockOnSignupSuccess} />);

        fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'New User' } });
        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'new@example.com' } });
        fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: 'password123' } });
        fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password123' } });

        fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));

        await waitFor(() => {
            expect(mockOnSignupSuccess).toHaveBeenCalledWith(expect.objectContaining({
                email: 'new@example.com',
                name: 'New User'
            }));
        }, { timeout: 3000 });
    });

    test('displays error message on failed registration (existing email)', async () => {
        render(<SignupForm onSignupSuccess={mockOnSignupSuccess} />);

        // Use the specific email that triggers the mock error
        fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'Existing User' } });
        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'exists@example.com' } });
        fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: 'password123' } });
        fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'password123' } });

        fireEvent.click(screen.getByRole('button', { name: /Create Account/i }));

        expect(await screen.findByText(/Email already exists/i, {}, { timeout: 3000 })).toBeInTheDocument();
        expect(mockOnSignupSuccess).not.toHaveBeenCalled();
    });
});
