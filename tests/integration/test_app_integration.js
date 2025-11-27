import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../../frontend/src/App';

// Mock the Loading component
jest.mock('../../frontend/src/components/common/Loading', () => () => <div data-testid="loading-spinner">Loading...</div>);

describe('App Integration - Full Flow', () => {
    test('complete user journey: login -> license -> dashboard', async () => {
        render(<App />);

        // 1. Should start at login
        expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();

        // 2. Fill in login credentials
        fireEvent.change(screen.getByLabelText(/Email Address/i), {
            target: { value: 'test@example.com' }
        });
        fireEvent.change(screen.getByLabelText(/Password/i), {
            target: { value: 'password' }
        });

        // 3. Submit login
        fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

        // 4. Wait for transition to license form
        await waitFor(() => {
            expect(screen.getByText(/Activate Trivya/i)).toBeInTheDocument();
        }, { timeout: 3000 });

        // 5. Enter license key
        fireEvent.change(screen.getByLabelText(/License Key/i), {
            target: { value: 'TRIVYA-GOLD-2024-KEY1' }
        });

        // 6. Submit license
        fireEvent.click(screen.getByRole('button', { name: /Validate License/i }));

        // 7. Wait for transition to dashboard
        await waitFor(() => {
            expect(screen.getByText(/Welcome to Trivya Platform/i)).toBeInTheDocument();
        }, { timeout: 5000 });

        // 8. Verify dashboard shows user info
        expect(screen.getByText(/Test User/i)).toBeInTheDocument();
        expect(screen.getByText(/License Type: Gold/i)).toBeInTheDocument();
    });
});
