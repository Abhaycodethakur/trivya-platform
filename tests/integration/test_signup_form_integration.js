import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SignupForm from '../../../frontend/src/components/auth/SignupForm';

describe('SignupForm Integration', () => {
    test('full signup flow: input -> submit -> success', async () => {
        const handleSuccess = jest.fn();
        render(<SignupForm onSignupSuccess={handleSuccess} />);

        // 1. Fill in registration details
        fireEvent.change(screen.getByLabelText(/Full Name/i), { target: { value: 'Integration User' } });
        fireEvent.change(screen.getByLabelText(/Email Address/i), { target: { value: 'integration@example.com' } });
        fireEvent.change(screen.getByLabelText(/^Password/i), { target: { value: 'securePass123' } });
        fireEvent.change(screen.getByLabelText(/Confirm Password/i), { target: { value: 'securePass123' } });

        // 2. Submit form
        const submitButton = screen.getByRole('button', { name: /Create Account/i });
        fireEvent.click(submitButton);

        // 3. Wait for async operation to complete
        expect(submitButton).toBeDisabled();

        // 4. Verify success callback
        await waitFor(() => {
            expect(handleSuccess).toHaveBeenCalled();
        }, { timeout: 3000 }); // Allow enough time for the 1.5s delay

        const userData = handleSuccess.mock.calls[0][0];
        expect(userData.name).toBe('Integration User');
        expect(userData.email).toBe('integration@example.com');
    });
});
