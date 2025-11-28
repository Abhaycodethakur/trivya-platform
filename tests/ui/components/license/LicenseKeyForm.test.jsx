import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LicenseKeyForm from '../../components/license/LicenseKeyForm';
import * as licenseService from '../../services/__mocks__/licenseService';

// Mock the Loading component
jest.mock('../../components/common/Loading', () => () => <div data-testid="loading-spinner">Loading...</div>);

describe('LicenseKeyForm Component', () => {
    const mockOnLicenseValid = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders form elements correctly', () => {
        render(<LicenseKeyForm onLicenseValid={mockOnLicenseValid} />);

        expect(screen.getByText(/Activate Trivya/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/License Key/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Validate License/i })).toBeInTheDocument();
    });

    test('displays error for empty submission', async () => {
        render(<LicenseKeyForm onLicenseValid={mockOnLicenseValid} />);

        fireEvent.click(screen.getByRole('button', { name: /Validate License/i }));

        expect(await screen.findByText(/Please enter your license key/i)).toBeInTheDocument();
        expect(mockOnLicenseValid).not.toHaveBeenCalled();
    });

    test('handles successful validation', async () => {
        render(<LicenseKeyForm onLicenseValid={mockOnLicenseValid} />);

        const input = screen.getByLabelText(/License Key/i);
        fireEvent.change(input, { target: { value: 'TRIVYA-TEST-1234-5678' } });

        fireEvent.click(screen.getByRole('button', { name: /Validate License/i }));

        // Should show loading
        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

        // Should show success message
        expect(await screen.findByText(/License validated successfully/i, {}, { timeout: 3000 })).toBeInTheDocument();

        // Should call callback after delay
        await waitFor(() => {
            expect(mockOnLicenseValid).toHaveBeenCalledWith(expect.objectContaining({
                isValid: true,
                type: 'Enterprise'
            }));
        }, { timeout: 5000 });
    });

    test('handles invalid license key', async () => {
        render(<LicenseKeyForm onLicenseValid={mockOnLicenseValid} />);

        const input = screen.getByLabelText(/License Key/i);
        fireEvent.change(input, { target: { value: 'INVALID-KEY' } });

        fireEvent.click(screen.getByRole('button', { name: /Validate License/i }));

        expect(await screen.findByText(/Invalid license key/i, {}, { timeout: 3000 })).toBeInTheDocument();
        expect(mockOnLicenseValid).not.toHaveBeenCalled();
    });

    test('auto-capitalizes input', () => {
        render(<LicenseKeyForm onLicenseValid={mockOnLicenseValid} />);

        const input = screen.getByLabelText(/License Key/i);
        fireEvent.change(input, { target: { value: 'trivya-lower-case' } });

        expect(input.value).toBe('TRIVYA-LOWER-CASE');
    });
});
