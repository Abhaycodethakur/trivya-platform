import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from '../../../frontend/src/components/auth/LoginForm';

// We are using the real mock service implementation here, not a jest mock, 
// to test the integration between the component and the service logic.

describe('LoginForm Integration', () => {
    test('full login flow: input -> submit -> success', async () => {
        const handleSuccess = jest.fn();
        render(<LoginForm onLoginSuccess={handleSuccess} />);

        // 1. Fill in credentials
        const emailInput = screen.getByLabelText(/Email Address/i);
        const passwordInput = screen.getByLabelText(/Password/i);

        fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
        fireEvent.change(passwordInput, { target: { value: 'password' } });

        // 2. Submit form
        const submitButton = screen.getByRole('button', { name: /Sign In/i });
        fireEvent.click(submitButton);

        // 3. Wait for async operation to complete
        // The button should be disabled initially
        expect(submitButton).toBeDisabled();

        // 4. Verify success callback
        await waitFor(() => {
            expect(handleSuccess).toHaveBeenCalled();
        }, { timeout: 2000 }); // Allow enough time for the 1s delay

        const userData = handleSuccess.mock.calls[0][0];
        expect(userData.email).toBe('test@example.com');
    });
});
