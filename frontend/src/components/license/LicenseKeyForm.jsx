import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styles from './LicenseKeyForm.module.css';
import Loading from '../common/Loading';
import * as licenseService from '../../services/__mocks__/licenseService';

/**
 * LicenseKeyForm Component
 * 
 * Handles product license validation.
 * Features:
 * - Input masking/formatting
 * - Validation against mock service
 * - Loading and error states
 */
const LicenseKeyForm = ({ onLicenseValid }) => {
    const [licenseKey, setLicenseKey] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const handleChange = (e) => {
        // Basic formatting: Uppercase and remove non-alphanumeric chars (except dashes)
        const val = e.target.value.toUpperCase();
        setLicenseKey(val);
        setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!licenseKey.trim()) {
            setError('Please enter your license key.');
            return;
        }

        setIsLoading(true);
        setError(null);
        setSuccess(null);

        try {
            const result = await licenseService.validateLicense(licenseKey);
            setSuccess('License validated successfully!');

            // Short delay to show success message before callback
            setTimeout(() => {
                if (onLicenseValid) {
                    onLicenseValid(result);
                }
            }, 1000);

        } catch (err) {
            setError(err.message || 'Failed to validate license.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Activate Trivya</h2>
            <p className={styles.subtitle}>
                Enter your product license key to unlock the full potential of the Trivya Platform.
            </p>

            <form onSubmit={handleSubmit} noValidate aria-busy={isLoading}>
                <div className={styles.formGroup}>
                    <label htmlFor="licenseKey" className={styles.label}>License Key</label>
                    <input
                        id="licenseKey"
                        type="text"
                        className={`${styles.input} ${error ? styles.errorInput : ''}`}
                        value={licenseKey}
                        onChange={handleChange}
                        placeholder="TRIVYA-XXXX-XXXX-XXXX"
                        disabled={isLoading || !!success}
                        aria-invalid={!!error}
                        aria-describedby={error ? "license-error" : (success ? "license-success" : undefined)}
                        autoComplete="off"
                    />

                    {error && (
                        <div id="license-error" className={styles.errorMessage} role="alert">
                            {error}
                        </div>
                    )}

                    {success && (
                        <div id="license-success" className={styles.successMessage} role="status">
                            {success}
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    className={styles.submitButton}
                    disabled={isLoading || !!success}
                >
                    {isLoading ? <Loading size="small" type="spinner" /> : (success ? 'Activated' : 'Validate License')}
                </button>
            </form>
        </div>
    );
};

LicenseKeyForm.propTypes = {
    /**
     * Callback function called when license is successfully validated.
     * Receives the license details object.
     */
    onLicenseValid: PropTypes.func,
};

export default LicenseKeyForm;
