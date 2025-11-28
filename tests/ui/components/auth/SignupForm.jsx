import React, { useState } from 'react';
import PropTypes from 'prop-types';
import styles from './SignupForm.module.css';
import Loading from '../common/Loading';
import * as authService from '../../services/__mocks__/authService';

/**
 * SignupForm Component
 * 
 * Handles new user registration.
 * Includes validation for name, email, password, and password confirmation.
 */
const SignupForm = ({ onSignupSuccess }) => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [validationErrors, setValidationErrors] = useState({});

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear validation error for this field when user types
        if (validationErrors[name]) {
            setValidationErrors(prev => ({
                ...prev,
                [name]: null
            }));
        }
    };

    const validateForm = () => {
        const errors = {};

        if (!formData.name.trim()) {
            errors.name = 'Name is required';
        } else if (formData.name.length < 2) {
            errors.name = 'Name must be at least 2 characters';
        }

        if (!formData.email) {
            errors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            errors.email = 'Please enter a valid email address';
        }

        if (!formData.password) {
            errors.password = 'Password is required';
        } else if (formData.password.length < 8) {
            errors.password = 'Password must be at least 8 characters';
        }

        if (formData.password !== formData.confirmPassword) {
            errors.confirmPassword = 'Passwords do not match';
        }

        setValidationErrors(errors);
        return Object.keys(errors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);

        try {
            const user = await authService.signup(formData.name, formData.email, formData.password);
            if (onSignupSuccess) {
                onSignupSuccess(user);
            }
        } catch (err) {
            setError(err.message || 'An unexpected error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <h2 className={styles.title}>Create Account</h2>

            {error && (
                <div className={styles.globalError} role="alert">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} noValidate aria-busy={isLoading}>
                <div className={styles.formGroup}>
                    <label htmlFor="name" className={styles.label}>Full Name</label>
                    <input
                        id="name"
                        name="name"
                        type="text"
                        className={`${styles.input} ${validationErrors.name ? styles.errorInput : ''}`}
                        value={formData.name}
                        onChange={handleChange}
                        disabled={isLoading}
                        aria-invalid={!!validationErrors.name}
                        aria-describedby={validationErrors.name ? "name-error" : undefined}
                    />
                    {validationErrors.name && (
                        <span id="name-error" className={styles.errorMessage}>
                            {validationErrors.name}
                        </span>
                    )}
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="email" className={styles.label}>Email Address</label>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        className={`${styles.input} ${validationErrors.email ? styles.errorInput : ''}`}
                        value={formData.email}
                        onChange={handleChange}
                        disabled={isLoading}
                        aria-invalid={!!validationErrors.email}
                        aria-describedby={validationErrors.email ? "email-error" : undefined}
                    />
                    {validationErrors.email && (
                        <span id="email-error" className={styles.errorMessage}>
                            {validationErrors.email}
                        </span>
                    )}
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="password" className={styles.label}>Password</label>
                    <input
                        id="password"
                        name="password"
                        type="password"
                        className={`${styles.input} ${validationErrors.password ? styles.errorInput : ''}`}
                        value={formData.password}
                        onChange={handleChange}
                        disabled={isLoading}
                        aria-invalid={!!validationErrors.password}
                        aria-describedby={validationErrors.password ? "password-error" : undefined}
                    />
                    {validationErrors.password && (
                        <span id="password-error" className={styles.errorMessage}>
                            {validationErrors.password}
                        </span>
                    )}
                </div>

                <div className={styles.formGroup}>
                    <label htmlFor="confirmPassword" className={styles.label}>Confirm Password</label>
                    <input
                        id="confirmPassword"
                        name="confirmPassword"
                        type="password"
                        className={`${styles.input} ${validationErrors.confirmPassword ? styles.errorInput : ''}`}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        disabled={isLoading}
                        aria-invalid={!!validationErrors.confirmPassword}
                        aria-describedby={validationErrors.confirmPassword ? "confirm-password-error" : undefined}
                    />
                    {validationErrors.confirmPassword && (
                        <span id="confirm-password-error" className={styles.errorMessage}>
                            {validationErrors.confirmPassword}
                        </span>
                    )}
                </div>

                <button
                    type="submit"
                    className={styles.submitButton}
                    disabled={isLoading}
                >
                    {isLoading ? <Loading size="small" type="spinner" /> : 'Create Account'}
                </button>
            </form>
        </div>
    );
};

SignupForm.propTypes = {
    /**
     * Callback function called upon successful registration with user data.
     */
    onSignupSuccess: PropTypes.func,
};

export default SignupForm;
