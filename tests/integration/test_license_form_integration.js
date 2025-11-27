import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LicenseKeyForm from '../../../frontend/src/components/license/LicenseKeyForm';

describe('LicenseKeyForm Integration', () => {
    test('full license validation flow: input -> submit -> success', async () => {
        const handleValid = jest.fn();
        render(<LicenseKeyForm onLicenseValid={handleValid} />);

        // 1. Enter valid license key
        const input = screen.getByLabelText(/License Key/i);
        fireEvent.change(input, { target: { value: 'TRIVYA-GOLD-2024-KEY1' } });

        // 2. Submit form
        const submitButton = screen.getByRole('button', { name: /Validate License/i });
        fireEvent.click(submitButton);

        // 3. Verify loading state
        expect(submitButton).toBeDisabled();

        // 4. Verify success state and callback
        await waitFor(() => {
            expect(screen.getByText(/License validated successfully/i)).toBeInTheDocument();
        }, { timeout: 3000 });

        await waitFor(() => {
            expect(handleValid).toHaveBeenCalled();
        }, { timeout: 3000 });

        const licenseData = handleValid.mock.calls[0][0];
        expect(licenseData.type).toBe('Gold');
        expect(licenseData.isValid).toBe(true);
    });
});
